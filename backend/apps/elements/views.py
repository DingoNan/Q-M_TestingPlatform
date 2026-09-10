import json
import uuid
import logging
from django_q.tasks import async_task
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from utils.base import BasePageNumberPagination
from apps.elements.filters import ElementFilter
from apps.elements.models import Element
from apps.elements.serializers import ElementSerializers
from apps.envs.models import Module, EnvPlant, Plant
from apps.projects.models import Project, AiConfig
from apps.messages.models import Message
from utils.base_view import BaseModelViewSet

logger = logging.getLogger('elements')


class ElementViewSet(BaseModelViewSet):
    serializer_class = ElementSerializers
    queryset = Element.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ElementFilter

    @action(methods=['post'], detail=False)
    def batch_update(self, request, *args, **kwargs):
        """
        批量更新元素字段（暂支持：status）
        单个修改也走此接口（ids 长度为 1）
        """
        user = request.user
        ids = request.data.get('ids', [])
        if not ids:
            return Response(data={'error': 'ids不能为空'}, status=400)

        elements = Element.objects.filter(id__in=ids, is_delete=False)
        if not elements.exists():
            return Response(data={'error': '未找到对应元素'}, status=404)

        update_fields = []
        status = request.data.get('status')
        if status is not None:
            elements.update(status=status, update_by_id=user.id)
            update_fields.append('status')

        return Response(data={'msg': '成功', 'count': elements.count(), 'fields': update_fields}, status=200)

    @action(methods=['post'], detail=False)
    def batch_delete(self, request, *args, **kwargs):
        """
        批量删除元素
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response(data={'error': 'ids不能为空'}, status=400)

        elements = Element.objects.filter(id__in=ids, is_delete=False)
        count = elements.count()
        elements.delete()
        return Response(data={'msg': '成功', 'count': count}, status=200)


@api_view(['POST'])
def import_element(request: Request):
    """
    处置json导出过程中，json类型转化成数组
    """
    data = request.data.get('value')
    try:
        data = json.loads(data)
    except Exception:
        return Response(data={"msg": "格式错误，请传入 JSON 对象或数组"}, status=400)

    # 1. 非空校验
    if not data:
        return Response(data={"msg": "导入内容不能为空"}, status=400)

    # # 2. 格式校验
    # if not isinstance(data, (dict, list)):
    #     return Response(data={"msg": "格式错误，请传入 JSON 对象或数组"}, status=400)

    # 3. 执行导入
    if isinstance(data, list):
        for element_obj in data:
            try:
                Element.objects.create(project_id=element_obj["project"], module_id=element_obj["module"],
                                       name=element_obj["name"], type=element_obj["type"], web=element_obj.get("web", {}),
                                       ios=element_obj.get("ios", {}), android=element_obj.get("android", {}),
                                       create_by=request.user, update_by=request.user)
            except Exception as e:
                pass

    else:
        Element.objects.create(project_id=data["project"], module_id=data["module"],
                               name=data["name"], type=data["type"], web=data.get("web", {}),
                               ios=data.get("ios", {}), android=data.get("android", {}),
                               create_by=request.user, update_by=request.user)

    # 4. 统计
    total = len(data) if isinstance(data, list) else 1

    return Response(data={
        "msg": f"导入完成",
        "total": total,
    }, status=200)


@api_view(['POST'])
def ai_generate_elements(request: Request):
    """
    提交 AI 自动生成元素 异步任务
    请求: { project_id, env_id, ai_config_id, need_login, module 或 plant }
    - module: 单个模块；plant: 平台，执行该平台下所有模块
    """
    env_id = request.data.get('env_id')
    ai_config_id = request.data.get('ai_config_id')
    project_id = (request.query_params.get('project')
                  or request.data.get('project_id')
                  or request.data.get('project'))
    need_login = request.data.get('need_login', False)
    try:
        vector_threshold = float(request.data.get('vector_threshold', 0.6))
    except (TypeError, ValueError):
        vector_threshold = 0.6

    if not env_id:
        return Response({'detail': '请选择环境'}, status=400)
    if not ai_config_id:
        return Response({'detail': '请选择AI模型'}, status=400)
    if not project_id:
        return Response({'detail': '项目ID不能为空'}, status=400)
    if not AiConfig.objects.filter(id=int(ai_config_id), is_active=True, is_delete=False).exists():
        return Response({'detail': 'AI模型不可用'}, status=400)

    plant_id = request.data.get('plant')
    label = ''
    module_ids = []
    if plant_id:
        plant = Plant.objects.filter(id=int(plant_id), is_delete=False,
                                     project_id=int(project_id)).first()
        if not plant:
            return Response({'detail': '平台不存在'}, status=404)
        label = plant.name
        module_ids = list(Module.objects.filter(
            project_id=int(project_id), plant_id=plant.id, is_delete=False,
        ).values_list('id', flat=True))
        if not module_ids:
            return Response({'detail': f'平台「{plant.name}」下没有模块'}, status=400)
        env_plant = EnvPlant.objects.filter(env_id=int(env_id), plant_id=plant.id,
                                            is_delete=False, host__isnull=False).exclude(host='').first()
        if not env_plant or not env_plant.host:
            return Response({'detail': f'该环境未配置「{plant.name}」的WEB域名，请先在环境管理中配置'}, status=400)
    else:
        module_id = request.data.get('module')
        if not module_id or int(module_id) <= 0:
            return Response({'detail': '请选择具体模块'}, status=400)
        module = Module.objects.filter(id=int(module_id), is_delete=False).first()
        if not module:
            return Response({'detail': '模块不存在'}, status=404)
        label = module.name
        module_ids = [module.id]
        # 模块维度必须携带页面路径（后端直接拼接前端传入的页面地址）
        page_path = request.data.get('page_path')
        if not page_path or not str(page_path).strip():
            return Response({'detail': '请填写模块页面地址'}, status=400)
        page_path = str(page_path).strip()
        env_plant = EnvPlant.objects.filter(env_id=int(env_id), plant=module.plant,
                                            is_delete=False, host__isnull=False).exclude(host='').first()
        if not env_plant or not env_plant.host:
            plant_name = getattr(module.plant, 'name', str(module.plant_id))
            return Response({'detail': f'该环境未配置「{plant_name}」的WEB域名，请先在环境管理中配置'}, status=400)

    project = Project.objects.filter(id=int(project_id)).first()
    task_id = str(uuid.uuid4())[:8]

    if plant_id:
        page_path = None

    message = Message.objects.create(
        user=request.user,
        project=project,
        title='AI元素生成中',
        content=f'范围: {label}',
        message_type=Message.MessageType.TASK,
        task_status=Message.TaskStatus.RUNNING,
        total_count=0,
        success_count=0,
        failed_count=0,
        create_by=request.user,
        update_by=request.user,
    )

    async_task(
        'apps.elements.tasks.ai_generate_elements_task',
        task_id=task_id,
        project_id=int(project_id),
        module_ids=module_ids,
        env_id=int(env_id),
        ai_config_id=int(ai_config_id),
        need_login=bool(need_login),
        user_id=request.user.id,
        message_id=message.id,
        vector_threshold=vector_threshold,
        page_path=(page_path if not plant_id else None),
    )
    return Response({'task_id': task_id, 'message': 'AI元素生成任务已提交', 'message_id': message.id})