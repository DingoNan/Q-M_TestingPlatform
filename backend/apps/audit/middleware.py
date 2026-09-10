import json
import logging

from django.core import serializers as django_serializers
from django.contrib.contenttypes.models import ContentType

from apps.audit.models import AuditLog
from apps.audit.registry import get_model_for_url, get_module_cn, COMPOSITE_PK_SEGMENT

logger = logging.getLogger('audit')

# 需要跳过的路径前缀
SKIP_PATHS = (
    '/static/', '/media/', '/admin/', '/upload_files/',
    '/restframework/', '/api_mock/', '/swagger/', '/redoc/',
    '/favicon.ico', '/django_q/',
)

# 需要记录的 HTTP 方法
WRITE_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')

# 请求体/响应体最大记录长度
MAX_BODY_LENGTH = 10000


class AuditLogMiddleware:
    """审计日志中间件 — 自动记录所有写操作"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 预处理：在视图执行前准备审计数据
        audit_data = self._prepare_audit_data(request)

        # 执行请求
        response = self.get_response(request)

        # 后处理：创建审计日志
        if audit_data:
            self._create_audit_log(request, response, audit_data)

        return response

    def _prepare_audit_data(self, request):
        """在视图执行前准备审计数据"""
        # 只记录写操作
        if request.method not in WRITE_METHODS:
            return None

        path = request.path
        # 跳过特定路径
        if any(path.startswith(skip) for skip in SKIP_PATHS):
            return None

        audit_data = {
            'method': request.method,
            'path': path,
            'ip': self._get_client_ip(request),
        }

        # 解析 URL → 模块、模型类、对象ID
        module, model_class, object_id = self._parse_url(path)
        audit_data['module'] = module
        audit_data['object_id'] = object_id or ''

        if model_class:
            try:
                audit_data['content_type'] = ContentType.objects.get_for_model(model_class)
            except Exception:
                pass

        # 确定操作类型
        audit_data['action'] = self._determine_action(request, path)

        # 获取项目ID（从请求参数/请求体中）
        project_id = self._get_project_id(request)
        if project_id:
            audit_data['project_id'] = project_id

        # 捕获 before_data（仅对更新/删除操作，且能确定模型和对象ID时）
        if model_class and object_id and request.method in ('PUT', 'PATCH', 'DELETE'):
            try:
                obj = model_class.objects.filter(pk=object_id).first()
                if obj:
                    audit_data['before_data'] = django_serializers.serialize(
                        'json', [obj], ensure_ascii=False
                    )
                    # 如果请求中未携带 project_id，尝试从对象上解析（支持直接字段或 env/service 关联）
                    if not project_id:
                        project_id = self._resolve_project_id_from_obj(obj)
                        if project_id:
                            audit_data['project_id'] = project_id
            except Exception as e:
                logger.warning('捕获 before_data 失败: %s', e)

        # 捕获请求体
        try:
            if request.body:
                audit_data['request_body'] = request.body.decode('utf-8')[:MAX_BODY_LENGTH]
        except Exception:
            audit_data['request_body'] = ''

        # 生成操作描述
        audit_data['description'] = self._generate_description(audit_data)

        return audit_data

    def _create_audit_log(self, request, response, audit_data):
        """在视图执行后创建审计日志"""
        try:
            user = getattr(request, 'user', None)
            username = ''
            if user and hasattr(user, 'username') and not getattr(user, 'is_anonymous', True):
                username = user.username

            # 捕获响应体
            response_body = ''
            if hasattr(response, 'content') and response.content:
                try:
                    response_body = response.content.decode('utf-8')[:MAX_BODY_LENGTH]
                except Exception:
                    response_body = ''

            status_code = getattr(response, 'status_code', 200)

            # 获取项目对象
            project = None
            project_id = audit_data.get('project_id')
            if project_id:
                try:
                    from apps.projects.models import Project
                    project = Project.objects.filter(id=project_id, is_delete=False).first()
                except Exception:
                    pass

            # 捕获 after_data（新增/修改操作后，如果能确定模型和对象ID）
            after_data = ''
            model_class = None
            if audit_data.get('content_type'):
                try:
                    model_class = audit_data['content_type'].model_class()
                except Exception:
                    pass
            object_id = audit_data.get('object_id', '')

            # 对于新增操作，尝试从响应体中提取对象ID
            if audit_data['action'] == AuditLog.Action.CREATE and not object_id and response_body:
                extracted_id = self._extract_object_id(response_body)
                if extracted_id:
                    object_id = str(extracted_id)
                    audit_data['object_id'] = object_id

            # 获取操作后的对象数据
            if model_class and object_id and audit_data['action'] in ('create', 'update'):
                try:
                    obj = model_class.objects.filter(pk=object_id).first()
                    if obj:
                        after_data = django_serializers.serialize(
                            'json', [obj], ensure_ascii=False
                        )
                        # 如果仍未获取到 project_id，尝试从操作后的对象上解析
                        # （适用于 EnvService 等无直接 project 字段的模型）
                        if not project_id:
                            project_id = self._resolve_project_id_from_obj(obj)
                except Exception as e:
                    logger.warning('捕获 after_data 失败: %s', e)

            # 如果通过对象解析到了 project_id，补充获取项目对象
            if not project and project_id:
                try:
                    from apps.projects.models import Project
                    project = Project.objects.filter(id=project_id, is_delete=False).first()
                except Exception:
                    pass

            # 如果操作的目标就是项目模型，用 object_id 补充获取 project
            if not project and model_class and object_id:
                try:
                    from apps.projects.models import Project
                    if model_class == Project:
                        project = Project.objects.filter(id=object_id, is_delete=False).first()
                except Exception:
                    pass

            AuditLog.objects.create(
                user=user if user and not getattr(user, 'is_anonymous', True) else None,
                username=username,
                action=audit_data.get('action', ''),
                method=audit_data.get('method', ''),
                path=audit_data.get('path', ''),
                ip=audit_data.get('ip'),
                module=audit_data.get('module', ''),
                project=project,
                request_body=audit_data.get('request_body', ''),
                response_body=response_body,
                before_data=audit_data.get('before_data', ''),
                after_data=after_data,
                status_code=status_code,
                description=audit_data.get('description', ''),
                content_type=audit_data.get('content_type'),
                object_id=object_id,
            )
        except Exception as e:
            logger.error('创建审计日志失败: %s', e)

    @staticmethod
    def _get_client_ip(request):
        """获取客户端真实IP"""
        xff = request.META.get('HTTP_X_FORWARDED_FOR')
        if xff:
            return xff.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    @staticmethod
    def _parse_url(path):
        """解析URL，返回 (模块名, 模型类, 对象ID)"""
        path = path.strip('/')
        if not path:
            return '', None, None

        segments = path.split('/')

        # 如果最后一段是数字（含下划线分隔的复合ID，如步骤ID 4_7_11），则是对象ID
        object_id = None
        if segments and segments[-1].replace('_', '').isdigit():
            object_id = segments[-1]
            segments = segments[:-1]

        # 尝试匹配最长前缀
        url_prefix = '/'.join(segments)
        model_class = get_model_for_url(url_prefix)

        # 复合ID模型：从复合对象ID中提取真实主键段（如步骤 4_7_11 → step_id 7）
        # 使 before_data 捕获与版本回退能正确定位对象
        if object_id and '_' in object_id:
            pk_idx = COMPOSITE_PK_SEGMENT.get(url_prefix)
            if pk_idx is not None:
                parts = object_id.split('_')
                if pk_idx < len(parts):
                    object_id = parts[pk_idx]

        # 模块名取最后一段
        module_segment = segments[-1] if segments else ''
        module = get_module_cn(module_segment)

        return module, model_class, object_id

    @staticmethod
    def _get_project_id(request):
        """从请求中获取项目ID（兼容 query param / project_id / project 字段名）"""
        # 1. 查询参数：project_id
        project_id = request.GET.get('project_id')
        if project_id:
            return project_id

        # 2. 请求体
        try:
            if request.body:
                body = json.loads(request.body.decode('utf-8'))
                if isinstance(body, dict):
                    # 先尝试 project_id
                    project_id = body.get('project_id')
                    if project_id:
                        return project_id
                    # 再尝试 project（ForeignKey 常用命名：可能是数字 ID 或 {id: ...} 对象）
                    project = body.get('project')
                    if project:
                        if isinstance(project, dict):
                            sub_id = project.get('id')
                            if sub_id:
                                return sub_id
                        else:
                            return project
        except Exception:
            pass

        return None

    @staticmethod
    def _resolve_project_id_from_obj(obj):
        """从对象上解析项目ID（支持直接 project_id 字段，或通过 env/service 关联模型获取）"""
        if obj is None:
            return None
        # 1. 直接 project_id 字段
        pid = getattr(obj, 'project_id', None)
        if pid:
            return pid
        # 2. 通过 env 关联（EnvService/EnvDb/EnvPlant 等无直接 project 字段的模型）
        env = getattr(obj, 'env', None)
        if env is not None:
            pid = getattr(env, 'project_id', None)
            if pid:
                return pid
        # 3. 通过 service 关联
        service = getattr(obj, 'service', None)
        if service is not None:
            pid = getattr(service, 'project_id', None)
            if pid:
                return pid
        return None

    @staticmethod
    def _determine_action(request, path):
        """根据HTTP方法和路径确定操作类型"""
        # 特殊路径处理
        if 'login' in path:
            return AuditLog.Action.LOGIN
        if 'logout' in path:
            return AuditLog.Action.LOGOUT

        method = request.method
        if method == 'POST':
            return AuditLog.Action.CREATE
        elif method in ('PUT', 'PATCH'):
            return AuditLog.Action.UPDATE
        elif method == 'DELETE':
            return AuditLog.Action.DELETE
        return ''

    @staticmethod
    def _generate_description(audit_data):
        """生成操作描述（去掉模块名末尾的"管理"/"配置"/"列表"后缀，如"标签管理"→"标签"、"用户列表"→"用户"）"""
        action = audit_data.get('action', '')
        module = audit_data.get('module', '')
        path = audit_data.get('path', '')

        # 权限校验接口：非真实CRUD操作，固定描述
        if 'check_permission' in path:
            return '权限校验'

        action_map = {
            'create': '新增',
            'update': '修改',
            'delete': '删除',
            'login': '登录',
            'logout': '登出',
        }

        action_text = action_map.get(action, action)
        if module:
            # 去掉"管理"/"配置"/"列表"后缀，使描述变为"新增标签"而非"新增标签管理"
            module_name = module
            for suffix in ('管理', '配置', '列表'):
                if module_name.endswith(suffix) and len(module_name) > len(suffix):
                    module_name = module_name[:-len(suffix)]
                    break
            return f'{action_text}{module_name}'
        return action_text

    @staticmethod
    def _extract_object_id(response_body):
        """从响应体中提取对象ID"""
        try:
            data = json.loads(response_body)
            # CustomRender 格式: {code, msg, result: {id: ...}} 或 {code, msg, results: [...]}
            if isinstance(data, dict):
                result = data.get('result')
                if isinstance(result, dict):
                    obj_id = result.get('id')
                    if obj_id:
                        return obj_id
                results = data.get('results')
                if isinstance(results, list) and results:
                    first = results[0]
                    if isinstance(first, dict) and 'id' in first:
                        return first['id']
                # 直接在顶层
                obj_id = data.get('id')
                if obj_id:
                    return obj_id
        except Exception:
            pass
        return None
