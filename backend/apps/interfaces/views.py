import json
import jsonpath
import requests
import copy
import time
import uuid
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from requests.sessions import Session
from django.db.models import Q
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.request import Request
from django_q.tasks import async_task

from core.com.common import api_list_to_dict
from core.com.check import CHECK_FUNC_MAP
from utils.base_view import BaseModelViewSet
from utils.base import BasePageNumberPagination

from apps.interfaces.models import Api, ApiMock
from apps.envs.models import ServiceModule, Service
from apps.users.models import User
from apps.interfaces.serializers import ApiSerializers, ApiMockSerializers
from apps.interfaces.api_guard import count_api_reference
from rest_framework.permissions import IsAuthenticated
from apps.interfaces.filters import ApiFilter, ApiMockFilter
from apps.messages.models import Message

# ★ 2026-09-22：本文件此前**没有**模块级 logger，har_analyze_ai 里直接写
#   logger.info(...) 会在运行期抛 NameError: name 'logger' is not defined ——
#   而它位于业务逻辑**之后**，会把一个本来成功的请求变成 HTTP 500，
#   且只在日志里留一条 NameError，极易被误读成「落库失败/模型问题」。
#   这里按 app 命名空间建 logger（与 apps/interfaces/tasks.py、har_ai.py 一致），
#   对应条目已在 qm_testing/settings.py 的 LOGGING 中补齐。
logger = logging.getLogger('interfaces')


class UserRequest:

    def __init__(self, headers, query_params, body, params):
        self.headers = headers
        self.query_params = query_params
        self.body = body
        self.params = params


def _batch_api_case_info(api_ids):
    """批量查询多个 API 关联的功能用例（仅 id/name），返回 {api_id: [{id, name}]}。
    列表页代替 serializer 逐行 N+1：原先每条 API 触发 3+ 次查询且嵌套全量序列化。
    """
    from apps.tests.models import Step, CaseSteps, Case
    from core.run_case import StepType
    result = {aid: [] for aid in api_ids}
    if not api_ids:
        return result
    step_ids = set(Step.objects.filter(
        Q(keyword__in=api_ids, type=StepType.Request, is_delete=False) |
        Q(keyword__in=api_ids, type=StepType.ComStep, is_delete=False, com_step_type=StepType.Request)
    ).values_list('id', flat=True))
    if not step_ids:
        return result
    case_ids = set(CaseSteps.objects.filter(is_delete=False, step_id__in=step_ids)
                   .values_list('case_id', flat=True))
    if not case_ids:
        return result
    case_id_name = dict(Case.objects.filter(id__in=case_ids, type=Case.FunctionCaseType.API)
                        .values_list('id', 'name'))
    step_to_api = dict(Step.objects.filter(id__in=step_ids).values_list('id', 'keyword'))
    api_cases = {}
    for sid, cid in CaseSteps.objects.filter(is_delete=False, step_id__in=step_ids).values_list('step_id', 'case_id'):
        aid = step_to_api.get(sid)
        if aid in api_cases:
            api_cases[aid].add(cid)
        elif aid is not None:
            api_cases[aid] = {cid}
    for aid, cids in api_cases.items():
        result[aid] = [{'id': cid, 'name': case_id_name[cid]} for cid in cids if cid in case_id_name]
    return result


class ApiViewSet(BaseModelViewSet):
    serializer_class = ApiSerializers
    queryset = Api.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ApiFilter

    def get_queryset(self):
        # select_related 预取 module/service/create_by/update_by 关联，
        # 避免列表页逐行查询 module_name/service_name/create_by_name/update_by_name 等（N+1）
        return super().get_queryset().select_related('module', 'service', 'create_by', 'update_by').filter(is_delete=False)

    def list(self, request, *args, **kwargs):
        """列表页批量预取当前页 API 的关联用例，注入 serializer context，避免逐行 N+1 查询"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            context = self.get_serializer_context()
            context['api_case_map'] = _batch_api_case_info([obj.id for obj in page])
            serializer = self.get_serializer(page, many=True, context=context)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """接口状态守卫：置为「废弃」时回传仍被引用的用例数量，提醒责任人处理存量引用"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        api_obj = serializer.save()

        payload = serializer.data
        try:
            new_status = int(request.data.get('status'))
        except (TypeError, ValueError):
            new_status = None
        if new_status is not None and new_status == Api.ApiStatus.StatusTen:
            ref_count = count_api_reference(api_obj.id)
            payload['deprecated_reference_count'] = ref_count
            if ref_count:
                payload['deprecated_warning'] = (
                    f'该接口仍被 {ref_count} 个用例引用，置为「废弃」后这些用例执行时将被直接拦截，'
                    f'请通知用例负责人及时更换接口'
                )
        return Response(payload)

    @action(methods=['post'], detail=False)
    def batch_update(self, request, *args, **kwargs):
        """批量更新接口字段

        支持批量修改: module(所属模块)、status(接口状态)
        单个修改也走此接口(ids 长度为 1)
        入参: {ids: [...], module: <id> | status: <int>}
        返回: {msg, count, fields, deprecated_reference_count?}
        """
        user = request.user
        ids = request.data.get('ids', [])
        if not ids:
            return Response(data={'error': 'ids不能为空'}, status=400)

        apis = Api.objects.filter(id__in=ids, is_delete=False)
        if not apis.exists():
            return Response(data={'error': '未找到对应接口'}, status=404)

        update_fields = []
        payload = {}

        # 所属模块：接口的 service 由模块决定，需与 serializers.validate 保持一致同步更新
        module_id = request.data.get('module')
        if module_id:
            module_obj = ServiceModule.objects.filter(id=module_id, is_delete=False).first()
            if module_obj is None:
                return Response(data={'error': '目标模块不存在'}, status=400)
            apis.update(module_id=module_obj.id, service_id=module_obj.service_id, update_by_id=user.id)
            update_fields.append('module')

        # 接口状态
        status_val = request.data.get('status')
        if status_val is not None:
            try:
                status_val = int(status_val)
            except (TypeError, ValueError):
                return Response(data={'error': 'status 必须为整数'}, status=400)
            if status_val not in [choice[0] for choice in Api.ApiStatus.choices]:
                return Response(data={'error': '无效的接口状态值'}, status=400)
            apis.update(status=status_val, update_by_id=user.id)
            update_fields.append('status')

            # 置为「废弃」时，回传这些接口上仍被引用的用例总数，供前端提示
            if status_val == Api.ApiStatus.StatusTen:
                ref_total = sum(count_api_reference(api_id) for api_id in apis.values_list('id', flat=True))
                payload['deprecated_reference_count'] = ref_total
                if ref_total:
                    payload['deprecated_warning'] = (
                        f'所选接口仍被 {ref_total} 个用例引用，置为「废弃」后这些用例执行时将被直接拦截，'
                        f'请通知用例负责人及时更换接口'
                    )

        if not update_fields:
            return Response(data={'error': '未提供任何可更新字段'}, status=400)

        payload.update({'msg': '成功', 'count': apis.count(), 'fields': update_fields})
        return Response(data=payload, status=200)


class ApiMockViewSet(BaseModelViewSet):
    serializer_class = ApiMockSerializers
    queryset = ApiMock.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = BasePageNumberPagination
    filterset_class = ApiMockFilter


@api_view(['POST'])
def json_obj_to_list(request: Request):
    """
    处置json导出过程中，json类型转化成数组
    """
    json_data = request.data.get('json_data')
    json_data = json.loads(json_data)
    base_json_params = request.data.get('json_params')
    table_data = []
    _json_to_dict(table_data, json_data, base_json_params, 0)
    return Response(data=table_data, status=200)


def _json_to_dict(table_data, json_data, base_json_params, level):
    if type(json_data) is dict:
        for key, value in json_data.items():
            base_json_params = copy.copy(base_json_params)
            base_json_params['id'] = uuid.uuid4()
            base_json_params['name'] = key
            base_json_params['level'] = level
            if type(value) is dict:
                base_json_params['children'] = []
                base_json_params['type'] = 'Dict'
                table_data.append(base_json_params)
                _json_to_dict(base_json_params['children'], value, base_json_params, level + 1)
            elif type(value) is list:
                base_json_params['children'] = []
                base_json_params['type'] = 'List'
                table_data.append(base_json_params)
                _json_to_dict(base_json_params['children'], value, base_json_params, level + 1)
            elif type(value) is str:
                base_json_params['type'] = 'Str'
                base_json_params['value'] = value
                table_data.append(base_json_params)
            elif type(value) is int:
                base_json_params['type'] = 'Int'
                base_json_params['value'] = value
                table_data.append(base_json_params)
            elif type(value) is float:
                base_json_params['type'] = 'Float'
                base_json_params['value'] = value
                table_data.append(base_json_params)
            elif type(value) is bool:
                base_json_params['type'] = 'Bool'
                base_json_params['value'] = value
                table_data.append(base_json_params)
            else:
                base_json_params['type'] = 'type error'
                base_json_params['value'] = value
                table_data.append(base_json_params)
    else:
        for index, value in enumerate(json_data):
            base_json_params = copy.copy(base_json_params)
            base_json_params['id'] = uuid.uuid4()
            base_json_params['name'] = index
            base_json_params['level'] = level
            if type(value) is dict:
                base_json_params['children'] = []
                base_json_params['type'] = 'Dict'
                table_data.append(base_json_params)
                _json_to_dict(base_json_params['children'], value, base_json_params, level + 1)
            elif type(value) is list:
                base_json_params['children'] = []
                base_json_params['type'] = 'List'
                table_data.append(base_json_params)
                _json_to_dict(base_json_params['children'], value, base_json_params, level + 1)
            elif type(value) is str:
                base_json_params['type'] = 'Str'
                base_json_params['value'] = value
                table_data.append(base_json_params)
            elif type(value) is int:
                base_json_params['type'] = 'Int'
                base_json_params['value'] = value
                table_data.append(base_json_params)
            elif type(value) is float:
                base_json_params['type'] = 'Float'
                base_json_params['value'] = value
                table_data.append(base_json_params)
            elif type(value) is bool:
                base_json_params['type'] = 'Bool'
                base_json_params['value'] = value
                table_data.append(base_json_params)
            else:
                base_json_params['type'] = 'type error'
                base_json_params['value'] = value
                table_data.append(base_json_params)


class ImportApiType:
    OpenApiJson = 'open-api-json'


def _deal_type(string_type: str):
    # ['string', 'boolean', 'array', 'object', 'number', 'null']
    if string_type is None:
        return 'object'
    if "INT" in string_type.upper():
        return 'number'
    else:
        return string_type


def create_api_by_open_api_json(export_obj: dict, uri: str, service: int, user_id: int, paths='paths',
                                components='components', properties='properties'):
    export_obj = json.loads(export_obj)
    paths_map: dict = export_obj[paths]
    many = True if len(paths_map.keys()) > 1 else False
    service_obj = Service.objects.get(id=service, is_delete=False)
    user_obj = User.objects.get(id=user_id, is_delete=False)

    # 处理接口基础参数
    for path_key, path_value in paths_map.items():
        for method_key, method_value in path_value.items():
            module_name = method_value.get('tags')[0]
            module_obj = ServiceModule.objects.filter(name=module_name, is_delete=False, service=service_obj)
            if module_obj.exists():
                module_obj = module_obj[0]
            else:
                module_obj = ServiceModule.objects.create(name=module_name, project=service_obj.project,
                                                          service=service_obj, parent=None, create_by=user_obj,
                                                          update_by=user_obj)
            api_model_map: dict = dict(module=module_obj, service=service_obj, headers=[], params=[], json=[],
                                       response=[], data=[], create_by=user_obj, update_by=user_obj)
            api_model_map['url'] = uri + path_key
            api_model_map['method'] = method_key.upper()
            api_model_map['name'] = method_value.get('summary', '')
            responses = method_value.get('responses', {})
            request_body = method_value.get('requestBody', {})
            parameters = method_value.get('parameters', [])

            # 处理接口查询参数
            for params_obj in parameters:

                params_map = dict(id=str(uuid.uuid4()), is_required=params_obj.get('required', ''),
                                  name=params_obj.get('name', ''), explain='',
                                  type='string', value='', parentId='')
                api_model_map['params'].append(params_map)

            # 处理接口请求体参数
            if request_body:
                content = request_body.get('content')
                if content.get('application/json'):
                    body_params = content.get('application/json').get('schema').get('$ref')
                    request_body_type = 'json'
                elif content.get('multipart/form-data'):
                    body_params = content.get('multipart/form-data').get('schema').get('$ref')
                    request_body_type = 'data'
                    api_model_map['body_type'] = Api.BodyType.Data
                else:
                    raise ValueError('需要更新代码')
                try:
                    deal_body_data(export_obj, api_model_map, body_params, many=many, body_type=request_body_type)
                except RecursionError:
                    pass

            # 处理响应体参数
            if responses:
                for response_status_code, response_value in responses.items():
                    responses_params = jsonpath.jsonpath(response_value, "$..$ref")
                    body_type = 'response'
                    api_model_map[body_type].append({'response_data': [], 'response_status': response_status_code})
                    if responses_params:
                        responses_params = responses_params[0]
                    else:
                        continue
                    try:
                        deal_body_data(export_obj, api_model_map, responses_params, body_type=body_type, many=many)
                    except RecursionError:
                        pass

            api_query = Api.objects.filter(service=service_obj, method=api_model_map['method'],
                                           url=api_model_map['url'], is_delete=False)
            if api_query:
                api_query.update(**api_model_map, update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
            else:
                Api.objects.create(**api_model_map)


def deal_body_data(export_obj, api_model_map, body_params, parent_id=None, components='components',
                   properties='properties', body_type='json', many=False, schemas='schemas'):
    if body_params:
        body_param_name = body_params.split('/')[-1]
        body_obj = export_obj[components][schemas][body_param_name] if many else export_obj[components][body_param_name]
        parent_type = body_obj.get('type')
        if body_obj.get('properties'):
            for body_name, body_map in body_obj[properties].items():
                unique_id = str(uuid.uuid4())
                params_type = 'string' if body_type == 'data' else _deal_type(body_map.get('type'))
                if body_type == 'json' or body_type == 'data':
                    value = body_map.get('example', '')
                    is_required = True if body_name in body_obj.get('required', '') else False
                    explain = body_map.get('description', '')
                    request_body_map = dict(id=unique_id, is_required=is_required, name=body_name, value=value,
                                            parentId=parent_id, explain=explain, type=params_type)
                    api_model_map[body_type].append(request_body_map)
                    body = api_model_map[body_type]
                elif body_type == 'response':
                    request_body_map = dict(id=unique_id, is_required=True, check_type=False, check_method='no_check',
                                            name=body_name, value='', parentId=parent_id,
                                            explain=body_map.get('description'),
                                            type=params_type)
                    api_model_map[body_type][-1]['response_data'].append(request_body_map)
                    body = api_model_map[body_type][-1]['response_data']

                if body_map.get('items'):
                    body_params = body_map.get('items').get('$ref')
                    children_body_param_name = body_params.split('/')[-1] if body_params else None
                    child_type = body_map.get('items').get('type', 'object')
                    if parent_type == 'array' or params_type == 'array':
                        uuid_str = str(uuid.uuid4())
                        body.append(dict(id=uuid_str, is_required=True, name='0', value='', parentId=unique_id, explain='',
                                         type=_deal_type(child_type), check_method='no_check', check_type=False))
                        if children_body_param_name != body_param_name:
                            deal_body_data(export_obj, api_model_map, body_params, parent_id=uuid_str, many=many,
                                           body_type=body_type)
                    else:
                        if children_body_param_name != body_param_name:
                            deal_body_data(export_obj, api_model_map, body_params, parent_id=unique_id, many=many,
                                           body_type=body_type)

                if body_map.get('$ref'):
                    body_params = body_map.get('$ref')
                    children_body_param_name = body_params.split('/')[-1] if body_params else None
                    if parent_type == 'array' or params_type == 'array':
                        uuid_str = str(uuid.uuid4())
                        request_body_map = dict(id=uuid_str, is_required=True, check_type=False, check_method='no_check',
                                                name='0', value='', parentId=unique_id, explain='', type='object')
                        body.append(request_body_map)
                        if children_body_param_name != body_param_name:
                            deal_body_data(export_obj, api_model_map, body_params, parent_id=uuid_str, many=many,
                                           body_type=body_type)
                    else:
                        if children_body_param_name != body_param_name:
                            deal_body_data(export_obj, api_model_map, body_params, parent_id=unique_id, many=many,
                                           body_type=body_type)


@api_view(['POST'])
def import_api(request: Request):
    """
    处置json导出过程中，json类型转化成数组
    """
    export_obj = request.data.get('value')
    export_type = request.data.get('exportType')
    uri = request.data.get('uri')
    service = request.data.get('service')
    # module = request.data.get('module')
    user_id = request.user.id
    if export_type == ImportApiType.OpenApiJson:
        create_api_by_open_api_json(export_obj, uri, service, user_id, 'paths')
    return Response(data='成功', status=200)


# ===========================================================================
# 新版导入逻辑（V2）——参考 Apifox 导入流程重构
# 保留原 create_api_by_open_api_json / deal_body_data / import_api 不删除，
# 此处另写一份实现，支持 OpenAPI 3 / Swagger 2 / Postman Collection v2.1，
# 支持文件上传 / URL 拉取 / 文本粘贴三种数据源，支持覆盖/跳过/保留三种重复处理模式。
# ===========================================================================


class ImportApiTypeV2:
    """新版导入支持的格式"""
    OpenApiSwagger = 'openapi-swagger'   # 自动识别 OpenAPI 2.0/3.x，支持 JSON & YAML
    PostmanV21 = 'postman-v2.1'
    Apifox = 'apifox'                     # Apifox 导出，自动识别为 OpenAPI/Swagger
    YApi = 'yapi'                         # YApi 导出，自动识别为 OpenAPI/Swagger
    ApiPost = 'apipost'                   # ApiPost 导出，自动识别为 OpenAPI/Swagger
    Eolink = 'eolink'                     # Eolink 导出，自动识别为 OpenAPI/Swagger
    Jmeter = 'jmeter'                     # JMeter XML 格式
    Curl = 'curl'
    Har = 'har'                           # 浏览器 HAR（HTTP Archive 1.2）

    # 需要走 OpenAPI/Swagger 解析器的格式集合
    OPENAPI_FAMILY = {OpenApiSwagger, Apifox, YApi, ApiPost, Eolink}


class ImportMatchMode:
    """重复接口（同服务+方法+URL）处理模式"""
    Overwrite = 'overwrite'      # 覆盖所有字段
    Skip = 'skip'                # 不导入重复项
    KeepBoth = 'keep_both'       # 保留两者（直接新增）


# OpenAPI 类型 → 系统内部类型
_OPENAPI_TYPE_MAP_V2 = {
    'string': 'string',
    'integer': 'number',
    'number': 'number',
    'boolean': 'bool',
    'array': 'array',
    'object': 'object',
    'file': 'file',
}


def _parse_spec_content_v2(content: str) -> dict:
    """解析 OpenAPI / Swagger / Postman 文本内容（自动识别 JSON / YAML）"""
    content = (content or '').strip()
    if not content:
        raise ValueError('导入内容不能为空')
    # 优先 JSON
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError):
        pass
    # 兜底 YAML
    try:
        import yaml
    except ImportError:
        raise ValueError('当前环境未安装 PyYAML，无法解析 YAML 内容')
    try:
        return yaml.safe_load(content)
    except Exception as e:
        raise ValueError(f'YAML 解析失败: {e}')


def _fetch_url_content_v2(url: str, timeout: int = 15) -> str:
    """从 URL 拉取接口文档文本"""
    if not url:
        raise ValueError('URL 不能为空')
    try:
        resp = requests.get(url, timeout=timeout, verify=False)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        raise ValueError(f'拉取 URL 内容失败: {e}')


def _resolve_ref_v2(ref: str, spec: dict):
    """解析 $ref（仅支持内部引用 #/...），返回 (节点, 引用名)"""
    if not ref or not isinstance(ref, str) or not ref.startswith('#'):
        return None, None
    parts = ref.lstrip('#/').split('/')
    node = spec
    for part in parts:
        if not part:
            continue
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None, None
    name = parts[-1] if parts else None
    return node, name


def _map_type_v2(openapi_type: str) -> str:
    if not openapi_type:
        return 'object'
    return _OPENAPI_TYPE_MAP_V2.get(str(openapi_type).lower(), openapi_type)


def _schema_to_params_v2(schema, spec, body_type, parent_id=None,
                         visited=None, depth=0, max_depth=10):
    """将 OpenAPI schema 转换为参数列表
    body_type: 'json' | 'data' | 'response'
    返回 list[dict]，结构兼容原 create_api_by_open_api_json 产出的字段
    """
    if visited is None:
        visited = set()
    if depth > max_depth or not schema:
        return []

    # $ref：解析后递归
    if isinstance(schema, dict) and '$ref' in schema:
        ref_key = schema['$ref']
        if ref_key in visited:
            return []
        visited.add(ref_key)
        node, _ = _resolve_ref_v2(ref_key, spec)
        if node is None:
            return []
        return _schema_to_params_v2(node, spec, body_type, parent_id, visited, depth + 1, max_depth)

    # allOf 合并 / oneOf / anyOf 取第一支
    if isinstance(schema, dict):
        if 'allOf' in schema:
            merged = {}
            for sub in schema['allOf']:
                if '$ref' in sub:
                    sub_node, _ = _resolve_ref_v2(sub['$ref'], spec)
                    if isinstance(sub_node, dict):
                        merged.update(sub_node)
                elif isinstance(sub, dict):
                    merged.update(sub)
            return _schema_to_params_v2(merged, spec, body_type, parent_id, visited, depth, max_depth)
        if schema.get('oneOf'):
            return _schema_to_params_v2(schema['oneOf'][0], spec, body_type, parent_id, visited, depth + 1, max_depth)
        if schema.get('anyOf'):
            return _schema_to_params_v2(schema['anyOf'][0], spec, body_type, parent_id, visited, depth + 1, max_depth)

    params = []
    schema_type = schema.get('type') if isinstance(schema, dict) else None

    # array
    if schema_type == 'array':
        items = schema.get('items', {}) if isinstance(schema, dict) else {}
        item_id = str(uuid.uuid4())
        item_type = _map_type_v2(items.get('type') if isinstance(items, dict) else 'object')
        if body_type == 'response':
            params.append(dict(
                id=item_id, name='0', is_required=True, check_type=False, check_method='no_check',
                value='', parentId=parent_id, explain=schema.get('description', ''),
                type='array' if item_type == 'object' else item_type,
            ))
        else:
            params.append(dict(
                id=item_id, name='0', is_required=True, value='', parentId=parent_id,
                explain=schema.get('description', ''), type='array',
            ))
        if isinstance(items, dict) and ('$ref' in items or 'properties' in items or items.get('type') == 'object'):
            params.extend(_schema_to_params_v2(items, spec, body_type, item_id, visited, depth + 1, max_depth))
        return params

    # object / properties
    properties = schema.get('properties', {}) if isinstance(schema, dict) else {}
    if not properties:
        return params
    required_fields = set(schema.get('required', []) or [])
    for name, sub_schema in properties.items():
        if not isinstance(sub_schema, dict):
            continue
        param_id = str(uuid.uuid4())
        sub_type = sub_schema.get('type')
        if '$ref' in sub_schema:
            ref_node, _ = _resolve_ref_v2(sub_schema['$ref'], spec)
            if isinstance(ref_node, dict):
                sub_type = ref_node.get('type', 'object')
        sub_type_str = _map_type_v2(sub_type)
        is_required = name in required_fields
        explain = sub_schema.get('description', '')
        value = sub_schema.get('example', '')
        if body_type == 'response':
            params.append(dict(
                id=param_id, name=name, is_required=is_required, check_type=False, check_method='no_check',
                value=value, parentId=parent_id, explain=explain, type=sub_type_str,
            ))
        else:
            params.append(dict(
                id=param_id, name=name, is_required=is_required, value=value,
                parentId=parent_id, explain=explain, type=sub_type_str,
            ))
        # 递归嵌套
        if sub_type == 'object' or sub_type == 'array' or '$ref' in sub_schema:
            params.extend(_schema_to_params_v2(sub_schema, spec, body_type, param_id, visited, depth + 1, max_depth))

    return params


def _parameters_to_params_v2(parameters, spec):
    """转换 OpenAPI 的 parameters（query / path / header）"""
    result = []
    if not parameters:
        return result
    for param in parameters:
        if not isinstance(param, dict):
            continue
        if '$ref' in param:
            param, _ = _resolve_ref_v2(param['$ref'], spec)
            if not param:
                continue
        schema = param.get('schema', {}) or {}
        result.append(dict(
            id=str(uuid.uuid4()),
            is_required=param.get('required', False),
            name=param.get('name', ''),
            explain=param.get('description', '') or schema.get('description', ''),
            type=_map_type_v2(schema.get('type', 'string')),
            value=param.get('example', '') or schema.get('example', ''),
            parentId='',
        ))
    return result


def _ensure_module_v2(tag_name, service_obj, user_obj):
    """根据 OpenAPI tag 名称确保模块存在，不存在则创建"""
    if not tag_name:
        tag_name = '未分类'
    module_qs = ServiceModule.objects.filter(name=tag_name, is_delete=False, service=service_obj)
    if module_qs.exists():
        return module_qs.first()
    return ServiceModule.objects.create(
        name=tag_name, project=service_obj.project, service=service_obj,
        parent=None, create_by=user_obj, update_by=user_obj,
    )


def _create_or_update_api_v2(api_data, match_mode):
    """根据 match_mode 创建或更新接口
    返回 (api_obj, action) where action ∈ {'created','updated','skipped'}
    """
    method = api_data['method']
    url = api_data['url']
    service_id = api_data['service'].id if hasattr(api_data['service'], 'id') else api_data['service']
    # ★ 2026-09-22 修复：
    #   去重键是 (service, method, url)。历史原因（KeepBoth 模式重复导入、
    #   或早期版本重复落库）同一组键可能存在多条记录，此时
    #     - qs.first() 取到的不一定是同组里最早的一条；
    #     - qs.update(**api_data) 会**一次性改写全部重复记录**，而调用方只把它
    #       记为 1 次 updated，导致「导入结果条数与实际落库对不上」。
    #   现改为：按 id 升序取最早的一条作为主记录，overwrite 只覆盖这一条。
    #   （不主动删除其余历史重复记录，避免导出路径之外的数据损失。）
    qs = Api.objects.filter(service_id=service_id, method=method, url=url,
                            is_delete=False).order_by('id')
    first = qs.first()
    if first is not None:
        if match_mode == ImportMatchMode.Skip:
            return first, 'skipped'
        if match_mode == ImportMatchMode.KeepBoth:
            api_obj = Api.objects.create(**api_data)
            return api_obj, 'created'
        # overwrite
        main_id = first.id
        Api.objects.filter(id=main_id).update(
            **api_data,
            update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        )
        return Api.objects.get(id=main_id), 'updated'
    api_obj = Api.objects.create(**api_data)
    return api_obj, 'created'


def _parse_openapi_v2(spec, service_id, user_id, uri_prefix='', match_mode=ImportMatchMode.Overwrite,
                      target_module_id=None):
    """解析 OpenAPI 3.0 / Swagger 2.0 规范到接口列表，返回统计信息"""
    service_obj = Service.objects.get(id=service_id, is_delete=False)
    user_obj = User.objects.get(id=user_id, is_delete=False)

    if not isinstance(spec, dict) or ('openapi' not in spec and 'swagger' not in spec):
        raise ValueError('无法识别的 OpenAPI/Swagger 规范（缺少 openapi 或 swagger 字段）')

    paths_map = spec.get('paths', {}) or {}
    stats = {'success': 0, 'skipped': 0, 'updated': 0, 'failed': 0, 'total': 0, 'errors': []}

    for path_key, path_value in paths_map.items():
        if not isinstance(path_value, dict):
            continue
        for method_key, method_value in path_value.items():
            method_lower = method_key.lower()
            if method_lower not in ('get', 'post', 'put', 'delete', 'patch', 'head', 'options'):
                continue
            if not isinstance(method_value, dict):
                continue
            stats['total'] += 1
            try:
                if target_module_id:
                    module_obj = ServiceModule.objects.get(id=target_module_id, is_delete=False)
                else:
                    tags = method_value.get('tags') or ['未分类']
                    module_obj = _ensure_module_v2(tags[0], service_obj, user_obj)

                api_model_map = dict(
                    module=module_obj, service=service_obj, headers=[], params=[], json=[],
                    response=[], data=[], create_by=user_obj, update_by=user_obj,
                )
                api_model_map['url'] = (uri_prefix or '') + path_key
                api_model_map['method'] = method_key.upper()
                api_model_map['name'] = method_value.get('summary') or method_value.get('operationId') or path_key

                parameters = method_value.get('parameters', []) or []
                api_model_map['params'] = _parameters_to_params_v2(parameters, spec)

                request_body = method_value.get('requestBody', {})
                if request_body:
                    content = request_body.get('content', {}) or {}
                    if 'application/json' in content:
                        schema = content['application/json'].get('schema', {}) or {}
                        api_model_map['json'] = _schema_to_params_v2(schema, spec, 'json')
                    elif 'multipart/form-data' in content:
                        schema = content['multipart/form-data'].get('schema', {}) or {}
                        api_model_map['data'] = _schema_to_params_v2(schema, spec, 'data')
                        api_model_map['body_type'] = Api.BodyType.Data
                    elif content:
                        first_key = next(iter(content))
                        schema = content[first_key].get('schema', {}) or {}
                        api_model_map['json'] = _schema_to_params_v2(schema, spec, 'json')
                else:
                    # Swagger 2.0：parameters 中 in=body / in=formData
                    for param in parameters:
                        if isinstance(param, dict) and '$ref' in param:
                            param, _ = _resolve_ref_v2(param['$ref'], spec)
                        if not isinstance(param, dict):
                            continue
                        location = param.get('in')
                        if location == 'body':
                            schema = param.get('schema', param)
                            api_model_map['json'] = _schema_to_params_v2(schema, spec, 'json')
                        elif location == 'formData':
                            schema = param.get('schema', param)
                            api_model_map['data'] = _schema_to_params_v2(schema, spec, 'data')
                            api_model_map['body_type'] = Api.BodyType.Data

                responses = method_value.get('responses', {}) or {}
                for status_code, response_value in responses.items():
                    response_entry = {'response_data': [], 'response_status': status_code}
                    api_model_map['response'].append(response_entry)
                    schema = None
                    if isinstance(response_value, dict):
                        # OpenAPI 3
                        content = response_value.get('content', {}) or {}
                        if 'application/json' in content:
                            schema = content['application/json'].get('schema')
                        elif content:
                            schema = content[next(iter(content))].get('schema')
                        # Swagger 2.0
                        if not schema and 'schema' in response_value:
                            schema = response_value.get('schema')
                    if schema:
                        try:
                            response_entry['response_data'] = _schema_to_params_v2(
                                schema, spec, 'response', max_depth=10)
                        except RecursionError:
                            pass

                _, action = _create_or_update_api_v2(api_model_map, match_mode)
                if action == 'skipped':
                    stats['skipped'] += 1
                elif action == 'updated':
                    stats['updated'] += 1
                else:
                    stats['success'] += 1
            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append(f'{method_key.upper()} {path_key}: {e}')
    return stats


def _parse_postman_v2(collection, service_id, user_id, uri_prefix='', match_mode=ImportMatchMode.Overwrite,
                      target_module_id=None):
    """解析 Postman Collection v2.1"""
    service_obj = Service.objects.get(id=service_id, is_delete=False)
    user_obj = User.objects.get(id=user_id, is_delete=False)
    stats = {'success': 0, 'skipped': 0, 'updated': 0, 'failed': 0, 'total': 0, 'errors': []}

    def _walk_items(items, parent_module=None):
        for item in items or []:
            if not isinstance(item, dict):
                continue
            # 文件夹
            if 'item' in item:
                folder_name = item.get('name', '未分类')
                if target_module_id:
                    folder_module = ServiceModule.objects.get(id=target_module_id, is_delete=False)
                else:
                    folder_module = _ensure_module_v2(folder_name, service_obj, user_obj)
                _walk_items(item['item'], folder_module)
                continue
            request = item.get('request', {})
            if not request:
                continue
            stats['total'] += 1
            try:
                method = (request.get('method', 'GET') or 'GET').upper()
                url_obj = request.get('url', {})
                if isinstance(url_obj, dict):
                    raw_url = url_obj.get('raw', '')
                    query_items = url_obj.get('query', []) or []
                else:
                    raw_url = url_obj or ''
                    query_items = []
                path = urlparse(raw_url).path or raw_url
                url = (uri_prefix or '') + path

                if target_module_id:
                    module_obj = ServiceModule.objects.get(id=target_module_id, is_delete=False)
                else:
                    module_obj = parent_module or _ensure_module_v2('未分类', service_obj, user_obj)

                api_model_map = dict(
                    module=module_obj, service=service_obj, headers=[], params=[], json=[],
                    response=[], data=[], create_by=user_obj, update_by=user_obj,
                )
                api_model_map['url'] = url
                api_model_map['method'] = method
                api_model_map['name'] = item.get('name', path)

                params_list = []
                for q in query_items:
                    if not isinstance(q, dict):
                        continue
                    params_list.append(dict(
                        id=str(uuid.uuid4()), is_required=False,
                        name=q.get('key', ''), explain=q.get('description', ''),
                        type='string', value=q.get('value', ''), parentId='',
                    ))
                api_model_map['params'] = params_list

                headers_list = []
                for h in request.get('header', []) or []:
                    if not isinstance(h, dict):
                        continue
                    headers_list.append(dict(
                        id=str(uuid.uuid4()), is_required=False,
                        name=h.get('key', ''), explain=h.get('description', ''),
                        type='string', value=h.get('value', ''), parentId='',
                    ))
                api_model_map['headers'] = headers_list

                body = request.get('body', {}) or {}
                if body.get('mode') == 'raw':
                    raw_body = body.get('raw', '')
                    try:
                        json_body = json.loads(raw_body)
                        api_model_map['json'] = [dict(
                            id=str(uuid.uuid4()), is_required=True, name='root',
                            value=raw_body, parentId='', explain='Postman raw body',
                            type='object' if isinstance(json_body, dict) else 'array',
                        )]
                    except (json.JSONDecodeError, ValueError):
                        pass

                _, action = _create_or_update_api_v2(api_model_map, match_mode)
                if action == 'skipped':
                    stats['skipped'] += 1
                elif action == 'updated':
                    stats['updated'] += 1
                else:
                    stats['success'] += 1
            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append(f'{item.get("name", "?")}: {e}')

    _walk_items(collection.get('item', []) if isinstance(collection, dict) else [])
    return stats


# ---------------------------------------------------------------------------
# cURL 解析：将一条或多条 curl 命令解析为接口定义
# ---------------------------------------------------------------------------

def _parse_curl_components_v2(text: str) -> dict:
    """解析 cURL 命令，兼容 POSIX (bash) 和 Windows cmd.exe 风格。
    核心思路：先预处理去掉 cmd.exe 的 ^ 转义，再用 shlex 标准分词。
    """
    import re
    import shlex

    result = {'method': 'GET', 'url': '', 'headers': [], 'body': '', 'body_type': ''}

    # 1. 行连接符处理：\<newline> 和 ^<newline> -> 空格
    text = re.sub(r'\\\s*\n', ' ', text)
    text = re.sub(r'\^\s*\n', ' ', text)

    # 2. 去掉开头的 curl
    text = re.sub(r'^\s*curl\b', '', text, count=1, flags=re.IGNORECASE)

    # 3. 如果是 cmd.exe 风格（含 ^" 或 ^'），去掉所有 ^ 转义
    #    ^" -> "，^{ -> {，^\ -> \，^} -> }，^% -> %，^, -> ，^` -> `
    #    re.sub 找到 ^X 的非重叠匹配，逐个替换为 X
    if re.search(r'\^[\"\'`]', text):
        text = re.sub(r'\^(.)', r'\1', text)

    # 4. 用 shlex 标准分词（自动处理 '...' "..." 和转义）
    try:
        tokens = shlex.split(text)
    except ValueError:
        # shlex 解析失败时回退到简单空格分词
        tokens = text.split()

    # 5. 解析 curl 参数
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in ('-X', '--request') and i + 1 < len(tokens):
            result['method'] = tokens[i + 1].upper()
            i += 2
            continue
        elif tok == '--url' and i + 1 < len(tokens):
            result['url'] = tokens[i + 1].strip('`')
            i += 2
            continue
        elif tok in ('-H', '--header') and i + 1 < len(tokens):
            v = tokens[i + 1]
            if ':' in v:
                k, val = v.split(':', 1)
                result['headers'].append({'name': k.strip(), 'value': val.strip()})
            i += 2
            continue
        elif tok in ('-d', '--data', '--data-raw', '--data-binary', '--data-ascii') and i + 1 < len(tokens):
            v = tokens[i + 1]
            result['body'] = v if not result['body'] else result['body'] + '&' + v
            result['body_type'] = 'json' if v.strip().startswith(('{', '[')) else 'data'
            i += 2
            continue
        elif tok in ('-F', '--form') and i + 1 < len(tokens):
            v = tokens[i + 1]
            result['body'] = v if not result['body'] else result['body'] + '&' + v
            result['body_type'] = 'data'
            i += 2
            continue
        elif tok in ('-G', '--get'):
            result['method'] = 'GET'
        elif tok in ('-b', '--cookie') and i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
            result['headers'].append({'name': 'Cookie', 'value': tokens[i + 1]})
            i += 2
            continue
        elif tok in ('-A', '--user-agent', '-e', '--referer') and i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
            i += 1  # skip value
        elif not tok.startswith('-') and not result['url']:
            # 未带 --url 的裸 URL
            result['url'] = tok.strip('`')
        i += 1

    # 有 body 但 method 仍为 GET -> 推断为 POST
    if result['body'] and result['method'] == 'GET':
        result['method'] = 'POST'

    return result


def _parse_single_curl_v2(curl_line: str) -> dict:
    """解析单条 cURL 命令，返回 {method, url, headers, body, body_type}"""
    import re

    text = curl_line.strip()
    if not text:
        return None

    components = _parse_curl_components_v2(text)

    if not components['url']:
        return None

    return {
        'method': components['method'],
        'url': components['url'],
        'headers': components['headers'],
        'body': components['body'],
        'body_type': components['body_type'],
    }


def _parse_curl_v2(curl_text: str, service_id: int, user_id: int,
                   uri_prefix: str = '', match_mode: str = ImportMatchMode.Overwrite,
                   target_module_id=None):
    """解析 cURL 文本（支持多条命令，以空行或 curl 关键字分隔），返回 stats"""
    service_obj = Service.objects.get(id=service_id, is_delete=False)
    user_obj = User.objects.get(id=user_id, is_delete=False)
    stats = {'success': 0, 'skipped': 0, 'updated': 0, 'failed': 0, 'total': 0, 'errors': []}

    import re
    # 按 "curl" 关键字分割多条命令（忽略大小写）
    raw_lines = re.split(r'(?im)^\s*(?=curl\b)', curl_text.strip())
    # 过滤空块
    blocks = [b.strip() for b in raw_lines if b.strip()]
    if not blocks:
        raise ValueError('未解析到有效的 cURL 命令')

    for block in blocks:
        try:
            parsed = _parse_single_curl_v2(block)
            if not parsed:
                stats['failed'] += 1
                stats['errors'].append(f'无法解析 cURL 命令：{block[:80]}...')
                continue
            stats['total'] += 1

            method = parsed['method']
            raw_url = parsed['url']
            # 解析 path 部分（去掉 scheme+host）
            try:
                parsed_url = urlparse(raw_url)
                path = parsed_url.path or '/'
            except Exception:
                path = raw_url
            final_url = (uri_prefix or '') + path

            if target_module_id:
                module_obj = ServiceModule.objects.get(id=target_module_id, is_delete=False)
            else:
                module_obj = _ensure_module_v2('cURL 导入', service_obj, user_obj)

            api_model_map = dict(
                module=module_obj, service=service_obj,
                headers=[], params=[], json=[], response=[], data=[],
                create_by=user_obj, update_by=user_obj,
            )
            api_model_map['url'] = final_url
            api_model_map['method'] = method
            api_model_map['name'] = f'{method} {path}'

            # Headers
            for h in parsed['headers']:
                api_model_map['headers'].append(dict(
                    id=str(uuid.uuid4()), is_required=False,
                    name=h['name'], explain='', type='string',
                    value=h['value'], parentId='',
                ))

            # Body → params
            body = parsed['body']
            body_type = parsed['body_type']
            if body:
                if body_type == 'json':
                    try:
                        json_obj = json.loads(body)
                        api_model_map['json'] = _schema_to_params_v2(
                            {'type': 'object' if isinstance(json_obj, dict) else 'array',
                             'properties': json_obj if isinstance(json_obj, dict) else {},
                             'items': json_obj if isinstance(json_obj, list) else {}},
                            {}, 'json', max_depth=5)
                    except (json.JSONDecodeError, ValueError):
                        api_model_map['json'] = [dict(
                            id=str(uuid.uuid4()), is_required=True, name='root',
                            value=body, parentId='', explain='cURL body',
                            type='object',
                        )]
                else:
                    api_model_map['body_type'] = Api.BodyType.Data
                    api_model_map['data'] = [dict(
                        id=str(uuid.uuid4()), is_required=True, name='root',
                        value=body, parentId='', explain='cURL body',
                        type='string',
                    )]

            _, action = _create_or_update_api_v2(api_model_map, match_mode)
            if action == 'skipped':
                stats['skipped'] += 1
            elif action == 'updated':
                stats['updated'] += 1
            else:
                stats['success'] += 1
        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append(f'{block[:60]}: {e}')

    return stats


# ---------------------------------------------------------------------------
# JMeter XML 解析：将 JMeter .jmx 测试计划解析为接口定义
# ---------------------------------------------------------------------------

def _parse_jmeter_v2(content: str, service_id: int, user_id: int,
                     uri_prefix: str = '', match_mode: str = ImportMatchMode.Overwrite,
                     target_module_id=None):
    """解析 JMeter XML (.jmx) 文件，提取 HTTP 请求"""
    import xml.etree.ElementTree as ET

    service_obj = Service.objects.get(id=service_id, is_delete=False)
    user_obj = User.objects.get(id=user_id, is_delete=False)
    stats = {'success': 0, 'skipped': 0, 'updated': 0, 'failed': 0, 'total': 0, 'errors': []}

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ValueError(f'JMeter XML 解析失败: {e}')

    # JMeter 的 HTTP 请求采样器标签
    http_sampler_tags = ('HTTPSampler', 'HTTPSamplerProxy', 'HTTPSamplerSC')

    # 收集所有 HTTP 采样器
    samplers = []
    for tag in http_sampler_tags:
        samplers.extend(root.findall(f'.//{tag}'))
        samplers.extend(root.findall(f'.//{{{http://jakarta.apache.org/jmeter}}}{tag}'))

    if not samplers:
        raise ValueError('未在 JMeter 文件中找到 HTTP 请求采样器')

    for sampler in samplers:
        try:
            # 获取 HTTP 元素
            http_elem = sampler.find('.//HTTPsampler')
            if http_elem is None:
                http_elem = sampler

            # 方法
            method_elem = http_elem.find('.//stringProp[@name="HTTPSampler.method"]')
            method = method_elem.text.strip().upper() if method_elem is not None and method_elem.text else 'GET'

            # URL / path
            path_elem = http_elem.find('.//stringProp[@name="HTTPSampler.path"]')
            path = path_elem.text.strip() if path_elem is not None and path_elem.text else '/'
            domain_elem = http_elem.find('.//stringProp[@name="HTTPSampler.domain"]')
            domain = domain_elem.text.strip() if domain_elem is not None and domain_elem.text else ''
            if domain:
                raw_url = f'{domain}{path}'
            else:
                raw_url = path

            # 解析 URL
            try:
                parsed_url = urlparse(raw_url if raw_url.startswith('http') else f'http://{raw_url}')
                final_url = (uri_prefix or '') + (parsed_url.path or '/')
            except Exception:
                final_url = (uri_prefix or '') + path

            # 名称
            name_elem = sampler.find('.//stringProp[@name="TestElement.name"]')
            name = name_elem.text.strip() if name_elem is not None and name_elem.text else f'{method} {path}'

            # Headers
            headers_elem = http_elem.find('.//elementProp[@name="HTTPsampler.Arguments"]//collectionProp')
            headers = []
            if headers_elem is not None:
                for header in headers_elem.findall('.//elementProp'):
                    h_name = header.find('.//stringProp[@name="Header.name"]')
                    h_value = header.find('.//stringProp[@name="Header.value"]')
                    if h_name is not None and h_value is not None:
                        headers.append({
                            'name': h_name.text.strip(),
                            'value': h_value.text.strip(),
                        })

            # Body / arguments
            body = ''
            body_type = ''
            args_elem = http_elem.find('.//elementProp[@name="HTTPsampler.Arguments"]')
            if args_elem is not None:
                for arg in args_elem.findall('.//elementProp[@elementType="HTTPArgument"]'):
                    arg_val = arg.find('.//stringProp[@name="Argument.value"]')
                    arg_name = arg.find('.//stringProp[@name="Argument.name"]')
                    if arg_val is not None and arg_val.text:
                        val = arg_val.text.strip()
                        if arg_name is not None and arg_name.text:
                            body += f'{arg_name.text}={val}&'
                        else:
                            body = val
                            if val.strip().startswith('{') or val.strip().startswith('['):
                                body_type = 'json'
                            else:
                                body_type = 'data'
                            break
                if body.endswith('&'):
                    body = body[:-1]

            # Module
            if target_module_id:
                module_obj = ServiceModule.objects.get(id=target_module_id, is_delete=False)
            else:
                module_obj = _ensure_module_v2('JMeter 导入', service_obj, user_obj)

            api_model_map = dict(
                module=module_obj, service=service_obj,
                headers=[], params=[], json=[], response=[], data=[],
                create_by=user_obj, update_by=user_obj,
            )
            api_model_map['url'] = final_url
            api_model_map['method'] = method
            api_model_map['name'] = name

            # Headers
            for h in headers:
                api_model_map['headers'].append(dict(
                    id=str(uuid.uuid4()), is_required=False,
                    name=h['name'], explain='', type='string',
                    value=h['value'], parentId='',
                ))

            # Body
            if body:
                if body_type == 'json':
                    try:
                        json_obj = json.loads(body)
                        api_model_map['json'] = _schema_to_params_v2(
                            {'type': 'object' if isinstance(json_obj, dict) else 'array',
                             'properties': json_obj if isinstance(json_obj, dict) else {},
                             'items': json_obj if isinstance(json_obj, list) else {}},
                            {}, 'json', max_depth=5)
                    except (json.JSONDecodeError, ValueError):
                        api_model_map['json'] = [dict(
                            id=str(uuid.uuid4()), is_required=True, name='root',
                            value=body, parentId='', explain='JMeter body',
                            type='object',
                        )]
                else:
                    api_model_map['body_type'] = Api.BodyType.Data
                    api_model_map['data'] = [dict(
                        id=str(uuid.uuid4()), is_required=True, name='root',
                        value=body, parentId='', explain='JMeter body',
                        type='string',
                    )]

            stats['total'] += 1
            _, action = _create_or_update_api_v2(api_model_map, match_mode)
            if action == 'skipped':
                stats['skipped'] += 1
            elif action == 'updated':
                stats['updated'] += 1
            else:
                stats['success'] += 1
        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append(f'{sampler.get("testname", "unknown")}: {e}')

    return stats


# ===========================================================================
# HAR（HTTP Archive 1.2）导入
# ---------------------------------------------------------------------------
# 设计说明：
#   1. HAR 与其它格式最大的差别 —— 浏览器导出时会剥离 Authorization / Cookie
#      等安全敏感请求头，直接入库的接口无法回放。因此本模块支持 authConfig
#      传入「登录接口 + token 提取路径 + 注入模板」，导入前先换取真实凭据再
#      注入到所有步骤的请求头。
#   2. HAR 记录的是「带真实值的流水」，其中一部分值随环境/账号变化
#      （如行政区划码、监控对象类型）。这些值硬编码会导致换环境后取到
#      错误数据且不报错 —— 比报错更危险。因此本模块用显式规则表识别
#      这类参数，标记为动态变量而非明文。
#   3. 一切依赖识别都走规则表 + 同值匹配双确认，不做纯值级猜测（噪音极大）。
# ===========================================================================

# ---------------------------------------------------------------------------
# HAR 请求头黑名单：这些头由客户端/浏览器自身产生，入库无意义且回放会出错
# ---------------------------------------------------------------------------
_HAR_HEADER_BLACKLIST = {
    'host', 'connection', 'content-length', 'accept-encoding',
    'sec-fetch-dest', 'sec-fetch-mode', 'sec-fetch-site', 'sec-fetch-user',
    'sec-ch-ua', 'sec-ch-ua-mobile', 'sec-ch-ua-platform',
    'upgrade-insecure-requests', 'pragma', 'cache-control',
    'if-none-match', 'if-modified-since', 'origin',
}

# 需要脱敏保存的头（值替换为占位符，避免凭据泄漏到接口库）
_HAR_SENSITIVE_HEADERS = {
    'authorization', 'cookie', 'x-token', 'x-auth-token', 'x-access-token',
    'token', 'x-session-id', 'x-xsrf-token', 'x-csrf-token',
}

# 默认去掉的查询参数（分页/缓存穿透类，入库会造成误导）
_HAR_QUERY_NOISE = {'_t', '_', 'timestamp', 'cachebuster', 'rnd'}

# ---------------------------------------------------------------------------
# 动态参数识别规则表（显式规则，避免值级匹配噪音）
#   key      : 参数名
#   match    : 可选，URL 路径需包含该片段才生效
#   var      : 建议的变量名（PascalCase）
#   scope    : 参数出现位置，'any' 表示查询串与请求体都扫（默认 any）
#   nullable : 该参数允许为 null（表示「不限定」语义）。这类参数被硬编码后
#              会把「全国范围」静默收窄成「某一个省」，比报错更危险
#   reason   : 说明，会写入参数的 explain 字段
# ---------------------------------------------------------------------------
_HAR_DYNAMIC_RULES = [
    {
        'key': 'parentAdmDivCode',
        'var': 'AdmDivCode',
        'nullable': True,
        'reason': '行政区划编码随登录用户所属机构变化；本参数可为 null 表示不限定范围，'
                  '硬编码成固定省份会把「全国统计」静默收窄为「单省统计」',
    },
    {
        'key': 'admDivCode',
        'var': 'AdmDivCode',
        'scope': 'query',
        'reason': '行政区划编码随登录用户所属机构变化',
    },
    {
        'key': 'moType',
        'var': 'MoType',
        'reason': '监控对象类型来自上游查询结果，需动态提取',
    },
    {
        'key': 'moId',
        'var': 'MoId',
        'reason': '监控对象 ID 随环境变化',
    },
    {
        'key': 'orgId',
        'var': 'OrgId',
        'reason': '组织机构 ID 随环境变化',
    },
    {
        'key': 'tenantId',
        'var': 'TenantId',
        'reason': '租户 ID 随环境变化',
    },
    {
        'key': 'deptId',
        'var': 'DeptId',
        'reason': '部门 ID 随环境变化',
    },
    {
        'key': 'projectId',
        'var': 'ProjectId',
        'reason': '项目 ID 随环境变化',
    },
]


def _har_json_scalars(obj, prefix=''):
    """递归收集 JSON 里的标量键值对，返回 {点号路径: 值}

    只收标量（str/int/float/bool/None），容器继续下钻。
    """
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f'{prefix}.{k}' if prefix else str(k)
            if isinstance(v, (dict, list)):
                out.update(_har_json_scalars(v, path))
            else:
                out[path] = v
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            path = f'{prefix}[{i}]'
            if isinstance(v, (dict, list)):
                out.update(_har_json_scalars(v, path))
            else:
                out[path] = v
    return out


def _har_query_to_dict(query_string: str) -> dict:
    """HAR 查询串 → 扁平 dict

    注意：parse_qs 返回 {k: [v1, v2]}，直接拼 URL 会得到
    'moType=[%27server%27]' 这类非法值。必须压平为标量。
    """
    if not query_string:
        return {}
    out = {}
    for k, v in parse_qsl(query_string, keep_blank_values=True):
        if k in _HAR_QUERY_NOISE:
            continue
        out[k] = v
    return out


def _har_dict_to_query(query_dict: dict) -> str:
    """扁平 dict → 查询串（保持键顺序）"""
    if not query_dict:
        return ''
    return urlencode([(k, v) for k, v in query_dict.items()])


def _har_extract_headers(entry: dict) -> tuple:
    """从 HAR entry 提取请求头，返回 (headers_list, auth_header_name)

    - 过滤客户端自动头
    - 敏感头即使存在也标记出来（浏览器通常已剥离，存在则说明来源不是 DevTools）
    """
    headers = []
    auth_name = ''
    for h in (entry.get('request', {}).get('headers') or []):
        name = (h.get('name') or '').strip()
        value = h.get('value') or ''
        if not name:
            continue
        low = name.lower()
        if low in _HAR_HEADER_BLACKLIST:
            continue
        if low in _HAR_SENSITIVE_HEADERS:
            auth_name = name
            # 不落明文凭据，占位待后续注入
            value = '__AUTH_PLACEHOLDER__'
        headers.append({
            'name': name,
            'value': value,
            'is_sensitive': low in _HAR_SENSITIVE_HEADERS,
        })
    return headers, auth_name


def _har_extract_post_data(entry: dict) -> tuple:
    """从 HAR entry 提取请求体，返回 (body_text, body_kind)

    body_kind ∈ {'json', 'form', 'text', ''}
    """
    post = (entry.get('request', {}) or {}).get('postData')
    if not post:
        return '', ''
    mime = (post.get('mimeType') or '').lower()
    text = post.get('text') or ''

    # form 类：优先用 params 结构还原，比 text 可靠
    params = post.get('params')
    if params and 'json' not in mime:
        pairs = [(p.get('name', ''), p.get('value', '')) for p in params if p.get('name')]
        if 'urlencoded' in mime or not mime:
            return urlencode(pairs), 'form'
        # multipart 等场景保留原始文本
        return text, 'text'

    if 'json' in mime:
        return text, 'json'
    if text.strip().startswith('{') or text.strip().startswith('['):
        return text, 'json'
    return text, 'text' if text else ''


def _har_value_to_schema(value, depth=0, max_depth=6):
    """把「真实值」递归转成 _schema_to_params_v2 认识的「schema」形态。

    背景（★ 这是一个真实踩过的坑）：
      _har_body_to_params 早期直接把 HAR 里的值对象当成 schema.properties 传给
      _schema_to_params_v2，而后者要求 properties 的每个 value 必须是 dict（即 schema），
      遇到字符串/数字/bool/null 这类标量会走 `continue` 全部丢弃，
      最终产出空 list —— 表现为「导入进来的接口请求体参数整块丢失」。

    注意类型判断顺序：bool 必须早于 int（Python 里 isinstance(True, int) 为 True，
    顺序写反会把 true/false 变成 number）。
    """
    if depth > max_depth:
        return {'type': 'string', 'example': str(value)}
    # ★ bool 先判，否则会被 int 吃掉
    if isinstance(value, bool):
        return {'type': 'boolean', 'example': value}
    if value is None:
        # null 保留下来：对应「本参数可为 null 表示不限定范围」的语义
        return {'type': 'null', 'example': None}
    if isinstance(value, (int, float)):
        return {'type': 'number', 'example': value}
    if isinstance(value, str):
        return {'type': 'string', 'example': value}
    if isinstance(value, dict):
        return {
            'type': 'object',
            'properties': {k: _har_value_to_schema(v, depth + 1, max_depth)
                           for k, v in value.items()},
        }
    if isinstance(value, list):
        if not value:
            return {'type': 'array', 'items': {}}
        return {
            'type': 'array',
            'items': _har_value_to_schema(value[0], depth + 1, max_depth),
        }
    return {'type': 'string', 'example': str(value)}


def _har_obj_to_schema(obj, max_depth=6):
    """JSON 对象/数组 → 顶层 schema（供 _schema_to_params_v2 消费）"""
    if isinstance(obj, dict):
        return {
            'type': 'object',
            'properties': {k: _har_value_to_schema(v, 1, max_depth)
                           for k, v in obj.items()},
        }
    if isinstance(obj, list):
        if not obj:
            return {'type': 'array', 'items': {}}
        return {
            'type': 'array',
            'items': _har_value_to_schema(obj[0], 1, max_depth),
        }
    return {'type': 'string', 'example': obj}


def _har_body_to_params(body_text: str, body_kind: str, explain_prefix: str = 'HAR body') -> list:
    """请求体文本 → 平台参数项列表（兼容 _schema_to_params_v2 的产物结构）"""
    if not body_text:
        return []
    if body_kind == 'json':
        try:
            obj = json.loads(body_text)
        except (json.JSONDecodeError, ValueError):
            obj = None
        if obj is not None:
            # ★ 必须把「值」转成「schema」再交出去：直接传值会让
            #   _schema_to_params_v2 因属性不是 dict 而全部丢弃（见 _har_value_to_schema 注释）
            schema = _har_obj_to_schema(obj)
            try:
                out = _schema_to_params_v2(schema, {}, 'json', max_depth=6)
                if out:
                    return out
            except Exception:
                pass
    # 兜底：整块作为 root 参数
    return [dict(
        id=str(uuid.uuid4()), is_required=True, name='root',
        value=body_text, parentId='', explain=explain_prefix, type='string',
    )]


def _har_response_to_params(entry: dict) -> list:
    """HAR 响应体 → 参数项列表（用于生成接口的 response 字段）"""
    content = (entry.get('response', {}) or {}).get('content') or {}
    text = content.get('text') or ''
    mime = (content.get('mimeType') or '').lower()
    if not text:
        return []
    if 'json' in mime or text.strip().startswith('{') or text.strip().startswith('['):
        try:
            obj = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return []
        if not isinstance(obj, (dict, list)):
            return []
        # ★ 同 _har_body_to_params：值必须转 schema，否则响应参数也会整块丢失
        schema = _har_obj_to_schema(obj)
        try:
            return _schema_to_params_v2(schema, {}, 'response', max_depth=6)
        except Exception:
            return []
    return []


def _har_entry_to_api(entry: dict, index: int) -> dict:
    """HAR entry → 中间结构（尚未绑定 service/module）"""
    req = entry.get('request', {}) or {}
    url = req.get('url') or ''
    parsed = urlparse(url)

    # 路径 + 查询参数
    path = parsed.path or '/'
    query_dict = _har_query_to_dict(parsed.query)

    headers, auth_name = _har_extract_headers(entry)
    body_text, body_kind = _har_extract_post_data(entry)

    # 接口名：优先 HAR 里的 _name 注释，其次方法+路径
    method = (req.get('method') or 'GET').upper()
    name = ''
    for h in headers:
        if h['name'].lower() == 'x-har-name':
            name = h['value']
    if not name:
        comment = entry.get('comment') or ''
        name = comment.strip() or f'{method} {path}'
    name = name[:50]

    # 识别动态参数：查询串 + 请求体都要扫
    # （★ 首版只扫了 query，漏掉了 body —— 实测本 HAR 的 parentAdmDivCode
    #   全在请求体里，导致核心依赖被漏判。这是本轮修正的关键点。）
    dynamic = {}

    def _hit(key, value, where):
        for rule in _HAR_DYNAMIC_RULES:
            if rule['key'] != key:
                continue
            scope = rule.get('scope', 'any')
            if scope != 'any' and scope != where:
                continue
            if rule.get('match') and rule['match'] not in path:
                continue
            dynamic[key] = {
                'var': rule['var'],
                'reason': rule['reason'],
                'value': value,
                'where': where,
                'nullable': bool(rule.get('nullable')),
                'is_null': value is None,
            }
            return

    for k, v in query_dict.items():
        _hit(k, v, 'query')

    body_scalars = {}
    if body_text and body_kind == 'json':
        try:
            body_scalars = _har_json_scalars(json.loads(body_text))
        except (json.JSONDecodeError, ValueError):
            body_scalars = {}
    for path_key, v in body_scalars.items():
        leaf = path_key.split('.')[-1].split('[')[0]
        _hit(leaf, v, 'body')

    return {
        'seq': index,
        'name': name,
        'method': method,
        'host': f'{parsed.scheme}://{parsed.netloc}' if parsed.scheme else '',
        'path': path,
        'query': query_dict,
        'query_string': _har_dict_to_query(query_dict),
        'headers': headers,
        'auth_header_name': auth_name,
        'body': body_text,
        'body_kind': body_kind,
        'body_scalars': body_scalars,
        'status': (entry.get('response', {}) or {}).get('status'),
        'started': entry.get('startedDateTime') or '',
        'dynamic': dynamic,
        'referer': next((h['value'] for h in headers if h['name'].lower() == 'referer'), ''),
        '_raw_response': entry.get('response') or {},
    }


def _har_group_key(api: dict) -> str:
    """按业务动作给接口分组（用于生成用例）

    分组依据优先级：请求的 Referer 路由 → 接口路径前缀
    """
    ref = api.get('referer') or ''
    if ref:
        try:
            ref_path = urlparse(ref).path or ''
        except Exception:
            ref_path = ''
        if ref_path and ref_path != api.get('path'):
            low = ref_path.lower()
            if 'login' in low:
                return '登录'
            # 取最后一段作为动作名
            seg = [s for s in ref_path.split('/') if s]
            if seg:
                return seg[-1]
    seg = [s for s in (api.get('path') or '').split('/') if s]
    return seg[-1] if seg else '未分组'


def _har_apply_auth(headers: list, auth_config: dict) -> list:
    """按 authConfig 注入认证头

    auth_config: {
        'token': 'xxx',                 # 已获取到的 token（优先）
        'headerName': 'Authorization',  # 注入的头名
        'template': 'Bearer {token}',   # 值模板，{token} 会被替换
    }
    """
    if not auth_config:
        return headers
    token = auth_config.get('token')
    if not token:
        return headers
    header_name = auth_config.get('headerName') or 'Authorization'
    template = auth_config.get('template') or '{token}'
    value = template.replace('{token}', str(token))

    out = []
    replaced = False
    for h in headers:
        if h['name'].lower() == header_name.lower() or h.get('is_sensitive'):
            out.append({'name': h['name'] if h['name'].lower() == header_name.lower() else header_name,
                        'value': value, 'is_sensitive': False})
            replaced = True
        else:
            out.append(h)
    if not replaced:
        out.insert(0, {'name': header_name, 'value': value, 'is_sensitive': False})
    return out


def _har_fetch_token(auth_config: dict) -> str:
    """按 authConfig 里的 login 定义实际发一次登录请求，取回 token

    auth_config['login'] = {
        'url': 'http://host/api/v1/auth/login',
        'method': 'POST',
        'json': {...},
        'tokenPath': 'data.token',      # 支持 a.b.c 与 data[0].token
        'tokenPrefix': 'Bearer ',
    }
    """
    login = (auth_config or {}).get('login')
    if not login:
        return ''
    url = login.get('url')
    if not url:
        return ''
    method = (login.get('method') or 'POST').upper()
    try:
        resp = requests.request(
            method=method,
            url=url,
            json=login.get('json') if login.get('json') is not None else None,
            data=login.get('data'),
            headers=login.get('headers') or {},
            timeout=login.get('timeout', 20),
            verify=False,
        )
    except requests.RequestException as e:
        raise ValueError(f'认证登录请求失败: {e}')
    if resp.status_code >= 400:
        raise ValueError(f'认证登录失败 HTTP {resp.status_code}: {resp.text[:200]}')
    try:
        payload = resp.json()
    except ValueError:
        raise ValueError('认证登录响应不是合法 JSON，无法提取 token')

    token_path = login.get('tokenPath') or 'data.token'
    node = payload
    for seg in str(token_path).replace('[', '.').replace(']', '').split('.'):
        if not seg:
            continue
        if isinstance(node, list):
            try:
                node = node[int(seg)]
            except (ValueError, IndexError):
                return ''
        elif isinstance(node, dict):
            if seg not in node:
                return ''
            node = node[seg]
        else:
            return ''
    return str(node) if node else ''


def _har_sort_entries_by_time(entries):
    """按 HAR entry 的 startedDateTime 升序排序（还原真实请求发起顺序）。

    ★ 2026-09-17 新增，修复「导入的接口顺序是反的」。

    背景
    ----
    HAR 的 `log.entries` 数组在 Chrome / Edge 导出时基本按 **请求完成时刻** 排列，
    而不是按用户操作顺序。因此一个响应较慢的功能接口会把先发出的登录接口
    挤到数组后面，导入后平台里看到的就是「功能接口 … login」，
    与用户「登录 → 点击某功能」的实际操作顺序正好相反。

    实现
    ----
    按 `entry['startedDateTime']`（HAR 1.2 规范必填，形如
    `2026-09-17T10:23:45.123Z`）升序排列。

    兼容性
    ------
    - 缺失 / 无法解析的时间戳统一排在末尾（用哨兵值），保持其相对原顺序；
    - 全程使用 Python 稳定排序（sorted 自带），原始顺序相同的项不会被打乱；
    - 任何异常都不向上抛，最坏情况退化为「保持原顺序」，
      绝不因为排序问题让整个导入失败。
    """
    import datetime as _dt

    def _parse(ts):
        if not ts or not isinstance(ts, str):
            return None
        s = ts.strip()
        # 兼容末尾 Z（UTC）与 +08:00 偏移
        if s.endswith('Z') or s.endswith('z'):
            s = s[:-1] + '+00:00'
        for parser in (
            lambda x: _dt.datetime.fromisoformat(x),
            lambda x: _dt.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%f%z'),
            lambda x: _dt.datetime.strptime(x, '%Y-%m-%dT%H:%M:%S%z'),
            lambda x: _dt.datetime.strptime(x.replace('T', ' ')[:19], '%Y-%m-%d %H:%M:%S'),
        ):
            try:
                v = parser(s)
                # 统一成 aware，避免与 naive 比较时抛 TypeError
                if v.tzinfo is None:
                    v = v.replace(tzinfo=_dt.timezone.utc)
                return v
            except (ValueError, TypeError):
                continue
        return None

    try:
        # 哨兵：解析不到的用 datetime.max，稳定排序后仍在末尾且保持原相对顺序
        far_future = _dt.datetime.max.replace(tzinfo=_dt.timezone.utc)
        decorated = []
        for i, e in enumerate(entries):
            if not isinstance(e, dict):
                decorated.append((far_future, i, e))
                continue
            t = _parse(e.get('startedDateTime'))
            decorated.append((t if t is not None else far_future, i, e))
        decorated.sort(key=lambda x: (x[0], x[1]))
        return [e for _, _, e in decorated]
    except Exception:
        # 兜底：任何意外都退回原顺序，不让导入失败
        return list(entries)


def _har_analyze(content: str, auth_config: dict = None):
    """HAR 文本 → (api_list, dict 依赖关系, dict 统计)"""
    try:
        har = json.loads(content)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f'HAR 不是合法 JSON: {e}')

    log = (har.get('log') or {}) if isinstance(har, dict) else {}
    entries = log.get('entries') or []
    if not entries:
        raise ValueError('HAR 文件中没有 entries，可能导出时未勾选内容')

    # ★ 2026-09-17 修复「导入的接口顺序是反的」：
    #   HAR 的 entries 数组并不保证是「用户操作顺序」。
    #   Chrome / Edge 导出时 entries 基本按 **请求完成时刻** 排列，
    #   一个响应慢的功能接口会把先发出的登录接口挤到后面，
    #   于是导入后列表呈现为「功能接口 … login」，与用户「登录 → 点击某功能」的
    #   实际操作顺序相反，后续做接口串联（依赖提取）时上下文也就错了。
    #   正解：HAR 每个 entry 都有 startedDateTime（HAR 1.2 规范的必填项，
    #   形如 2026-09-17T10:23:45.123Z），按它升序排才是真实发起顺序。
    #   注意：解析失败/缺失时保持原顺序（稳定排序），不抛异常。
    entries = _har_sort_entries_by_time(entries)

    api_list = []
    skipped_static = 0
    for idx, entry in enumerate(entries):
        req = entry.get('request', {}) or {}
        url = req.get('url') or ''
        if not url.lower().startswith('http'):
            skipped_static += 1
            continue
        # 只保留 XHR / Fetch（静态资源不是接口）
        rt = (entry.get('_resourceType') or '').lower()
        mime = ((entry.get('response', {}) or {}).get('content') or {}).get('mimeType') or ''
        path = urlparse(url).path
        if rt and rt not in ('xhr', 'fetch'):
            skipped_static += 1
            continue
        if not rt and ('json' not in mime.lower() and not path.startswith('/api')):
            skipped_static += 1
            continue
        api_list.append(_har_entry_to_api(entry, len(api_list) + 1))

    if not api_list:
        raise ValueError('HAR 中未识别到任何 XHR/Fetch 接口，请确认录制时页面有实际接口调用')

    # ---- 认证注入（可选） ----
    token = ''
    auth_error = ''
    if auth_config:
        if auth_config.get('token'):
            token = auth_config['token']
        elif auth_config.get('login'):
            try:
                token = _har_fetch_token(auth_config)
            except ValueError as e:
                auth_error = str(e)
        if token:
            for api in api_list:
                api['headers'] = _har_apply_auth(api['headers'], {
                    'token': token,
                    'headerName': auth_config.get('headerName') or 'Authorization',
                    'template': auth_config.get('template') or 'Bearer {token}',
                })
                api['auth_injected'] = True

    # ---- 依赖识别：显式规则命中 ----
    dependencies = {}
    for api in api_list:
        for key, meta in (api.get('dynamic') or {}).items():
            dependencies.setdefault(meta['var'], {
                'var': meta['var'],
                'key': key,
                'reason': meta['reason'],
                'where': meta.get('where'),
                'nullable': meta.get('nullable', False),
                'used_by': [],
                'source_hint': '',
            })
            dependencies[meta['var']]['used_by'].append({
                'seq': api['seq'], 'name': api['name'], 'path': api['path'],
                'where': meta.get('where'), 'is_null': meta.get('is_null', False),
            })

    groups = {}
    for api in api_list:
        groups.setdefault(_har_group_key(api), []).append(api['seq'])

    stats = {
        'total_entries': len(entries),
        'xhr_count': len(api_list),
        'skipped_static': skipped_static,
        'hosts': sorted({a['host'] for a in api_list if a['host']}),
        'auth_injected': bool(token),
        'auth_header_present_in_har': any(a['auth_header_name'] for a in api_list),
        'auth_error': auth_error,
        'dynamic_params': list(dependencies.keys()),
        'groups': groups,
        'methods': {m: sum(1 for a in api_list if a['method'] == m)
                    for m in sorted({a['method'] for a in api_list})},
    }
    return api_list, dependencies, stats


def _har_detect_auth_endpoint(api_list) -> dict:
    """从 HAR 里自动找登录接口，生成 authConfig 骨架

    命中特征：路径含 login/signin/auth 且方法为 POST
    """
    for api in api_list:
        low = (api['path'] or '').lower()
        if api['method'] == 'POST' and any(k in low for k in ('login', 'signin', 'sign-in', 'token')):
            body = {}
            if api['body'] and api['body_kind'] == 'json':
                try:
                    body = json.loads(api['body'])
                except (json.JSONDecodeError, ValueError):
                    body = {}
            return {
                'url': (api['host'] or '') + (api['path'] or ''),
                'method': 'POST',
                'json': body,
                'tokenPath': 'data.token',
                'headerName': 'Authorization',
                'template': 'Bearer {token}',
                '_seq': api['seq'],
            }
    return {}


def _parse_har_v2(content: str, service_id: int, user_id: int,
                  uri_prefix: str = '', match_mode: str = ImportMatchMode.Overwrite,
                  target_module_id=None, auth_config: dict = None,
                  dry_run: bool = False, api_ids_out: list = None):
    """解析 HAR 文件，提取 XHR/Fetch 接口并入库

    auth_config: 见 _har_apply_auth / _har_fetch_token
    dry_run: True 时只解析不落库，stats 里回传完整解析结果供前端预览
    api_ids_out: 传入 list 时，会把本次落库的接口 id 按 HAR 真实发起顺序
                 追加进去（供「用例内 HAR 导入」接着批量建步骤用）。
                 2026-09-22 新增。
    """
    service_obj = Service.objects.get(id=service_id, is_delete=False)
    user_obj = User.objects.get(id=user_id, is_delete=False)
    stats = {'success': 0, 'skipped': 0, 'updated': 0, 'failed': 0, 'total': 0, 'errors': []}

    api_list, dependencies, har_stats = _har_analyze(content, auth_config)
    stats.update({
        'har': har_stats,
        'dependencies': dependencies,
        'preview': [],
    })
    stats['total'] = len(api_list)
    if har_stats.get('auth_error'):
        stats['errors'].append(f"认证补齐失败: {har_stats['auth_error']}")

    # ★ 2026-09-22 修复「HAR 导入后接口列表顺序整体反了」：
    #   解析层 _har_sort_entries_by_time() 已按 startedDateTime 把 api_list 排成
    #   真实发起顺序（升序），但 Api.Meta.ordering = ['-update_time', '-id']，
    #   而 update_time 是 auto_now ⇒ 同批导入单调递增 ⇒ 列表倒序展示时会把
    #   刚排好的顺序整体翻回去（161 线上实测：列表 id 序列严格递减）。
    #   这里改为「逆序落库」：最先发起的接口最后入库、拿到最大的 id，
    #   再配合 '-id' 倒序，列表即可还原成 HAR 里的真实发起顺序。
    #   注意：dry_run 预览需保持正序，见下方 stats['preview'].reverse()。
    for api in reversed(api_list):
        try:
            # 目标 URL：优先按 uriPrefix 重写前缀，否则沿用 HAR 里的路径
            final_url = (uri_prefix or '') + api['path']
            if api['query_string']:
                final_url = f"{final_url}?{api['query_string']}"

            if target_module_id:
                module_obj = ServiceModule.objects.get(id=target_module_id, is_delete=False)
            else:
                module_obj = _ensure_module_v2(_har_group_key(api)[:50] or 'HAR 导入',
                                               service_obj, user_obj)

            api_model_map = dict(
                module=module_obj, service=service_obj,
                headers=[], params=[], json=[], response=[], data=[],
                create_by=user_obj, update_by=user_obj,
            )
            api_model_map['url'] = final_url[:200]
            api_model_map['method'] = api['method'][:10]
            api_model_map['name'] = api['name'][:50]

            # 请求头
            for h in api['headers']:
                if h['name'].lower() == 'x-har-name':
                    continue
                api_model_map['headers'].append(dict(
                    id=str(uuid.uuid4()), is_required=False,
                    name=h['name'], explain='', type='string',
                    value=h['value'], parentId='',
                ))

            # 查询参数：命中动态规则的标记为变量
            for k, v in (api.get('query') or {}).items():
                meta = (api.get('dynamic') or {}).get(k)
                api_model_map['params'].append(dict(
                    id=str(uuid.uuid4()), is_required=False, name=k,
                    explain=(meta['reason'] if meta else ''),
                    type='string',
                    value=('${' + meta['var'] + '}') if meta else v,
                    parentId='',
                ))

            # 请求体
            if api['body']:
                if api['body_kind'] == 'json':
                    body_text = api['body']
                    # 命中动态规则的字段替换成变量占位，避免换环境后静默取错数据
                    dyn = api.get('dynamic') or {}
                    body_dyn = {k: m for k, m in dyn.items() if m.get('where') == 'body'}
                    if body_dyn:
                        try:
                            body_obj = json.loads(body_text)
                            for k, m in body_dyn.items():
                                if k in body_obj:
                                    body_obj[k] = '${' + m['var'] + '}'
                            body_text = json.dumps(body_obj, ensure_ascii=False)
                        except (json.JSONDecodeError, ValueError):
                            pass
                    api_model_map['json'] = _har_body_to_params(body_text, 'json')
                    api_model_map['api_json_type'] = (
                        'array' if body_text.strip().startswith('[') else 'object'
                    )
                    if body_dyn:
                        api_model_map.setdefault('_dynamic_params', [])
                        for k, m in body_dyn.items():
                            api_model_map['_dynamic_params'].append(dict(
                                name=k, var=m['var'], reason=m['reason'],
                                nullable=m.get('nullable', False),
                            ))
                else:
                    api_model_map['body_type'] = Api.BodyType.Data
                    api_model_map['data'] = [dict(
                        id=str(uuid.uuid4()), is_required=True, name='root',
                        value=api['body'], parentId='', explain='HAR 请求体', type='string',
                    )]

            # _dynamic_params 是给调用方/预览用的附加信息，不是模型字段，落库前必须摘掉
            dyn_meta = api_model_map.pop('_dynamic_params', None)

            # 响应体
            entry_resp = _har_response_to_params({'response': api.get('_raw_response') or {}})
            if entry_resp:
                api_model_map['response'] = entry_resp

            if dry_run:
                stats['preview'].append({
                    'seq': api['seq'], 'name': api['name'], 'method': api['method'],
                    'url': final_url, 'group': _har_group_key(api),
                    'dynamic': {k: m['var'] for k, m in (api.get('dynamic') or {}).items()},
                    'dynamic_detail': [
                        {'name': k, 'var': m['var'], 'where': m.get('where'),
                         'reason': m['reason'], 'nullable': m.get('nullable', False),
                         'is_null': m.get('is_null', False)}
                        for k, m in (api.get('dynamic') or {}).items()
                    ],
                    'body_dynamic': dyn_meta or [],
                    'auth_injected': bool(api.get('auth_injected')),
                    'body_kind': api['body_kind'],
                    'status': api.get('status'),
                })
                stats['success'] += 1
                continue

            api_obj, action = _create_or_update_api_v2(api_model_map, match_mode)
            if action == 'skipped':
                stats['skipped'] += 1
            elif action == 'updated':
                stats['updated'] += 1
            else:
                stats['success'] += 1
            # ★ 2026-09-22：回传落库接口 id，供「用例内 HAR 导入」接着批量建步骤。
            #   循环是逆序的，这里先按落库顺序收集，函数末尾统一翻回发起顺序。
            if api_ids_out is not None and api_obj is not None:
                api_ids_out.append(api_obj.id)
        except Exception as e:
            stats['failed'] += 1
            stats['errors'].append(f"[{api['seq']}] {api['name']}: {e}")

    # ★ 逆序落库后 dry_run 的预览列表也变成倒序了，这里翻回真实发起顺序，
    #   保证前端「导入预览」表格与 HAR 抓包时间线一致。
    if dry_run and len(stats['preview']) > 1:
        stats['preview'].reverse()

    # ★ 同理，回传的接口 id 列表也翻回真实发起顺序
    if api_ids_out is not None and len(api_ids_out) > 1:
        api_ids_out.reverse()

    return stats


@api_view(['POST'])
def import_api_v2(request: Request):
    """
    新版导入接口（V2）— 异步执行
    参数:
      - format: 导入格式（openapi-swagger/postman-v2.1/jmeter/curl）
      - source: 数据来源 ('url' | 'file')
      - url: 数据文件 URL（source=url 时必填）
      - file: 上传文件（source=file 时必填）
      - service: 目标服务 ID（必填）
      - module: 目标模块 ID（可选）
      - uriPrefix: URL 前缀
      - matchMode: 重复处理模式（overwrite/skip/keep_both）
    返回: {task_id, message_id}，导入在后台执行，完成后发送站内信通知
    """
    fmt = request.data.get('format')
    source = (request.data.get('source') or 'url').lower()
    service_id = request.data.get('service')
    target_module_id = request.data.get('module') or request.data.get('moduleId')
    uri_prefix = request.data.get('uriPrefix') or request.data.get('uri') or ''
    match_mode = request.data.get('matchMode') or ImportMatchMode.Overwrite

    if not fmt:
        return Response({'detail': '请选择导入格式'}, status=400)
    if not service_id:
        return Response({'detail': '请选择所属服务'}, status=400)
    if match_mode not in (ImportMatchMode.Overwrite, ImportMatchMode.Skip, ImportMatchMode.KeepBoth):
        return Response({'detail': '不支持的匹配模式'}, status=400)

    # HAR 的认证配置（可选）：token 直接给，或给 login 配置由任务内换取
    auth_config = request.data.get('authConfig')
    if isinstance(auth_config, str) and auth_config.strip():
        try:
            auth_config = json.loads(auth_config)
        except (json.JSONDecodeError, ValueError):
            return Response({'detail': 'authConfig 不是合法 JSON'}, status=400)
    if auth_config is not None and not isinstance(auth_config, dict):
        return Response({'detail': 'authConfig 必须是对象'}, status=400)

    # 请求期内读取上传文件内容（request.FILES 无法在异步任务中访问），URL 交由任务内拉取
    content = ''
    url = ''
    if fmt == ImportApiTypeV2.Curl:
        content = request.data.get('curlText', '') or ''
        if not content.strip():
            return Response({'detail': '请粘贴 cURL 命令'}, status=400)
    elif source == 'url':
        url = request.data.get('url')
        if not url:
            return Response({'detail': '请输入 URL'}, status=400)
    elif source == 'file':
        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': '请上传文件'}, status=400)
        try:
            content = uploaded.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return Response({'detail': f'文件读取失败: {e}'}, status=400)
        if not content or not content.strip():
            return Response({'detail': '导入内容不能为空'}, status=400)
    else:
        return Response({'detail': '不支持的数据来源'}, status=400)

    user_id = request.user.id
    service_obj = Service.objects.filter(id=service_id, is_delete=False).first()
    task_id = str(uuid.uuid4())[:8]

    message = Message.objects.create(
        user=request.user,
        project=service_obj.project if service_obj else None,
        title='接口文档导入中',
        content=f'服务: {service_obj.name if service_obj else service_id}\n格式: {fmt}',
        message_type=Message.MessageType.TASK,
        task_status=Message.TaskStatus.RUNNING,
        total_count=0,
        success_count=0,
        failed_count=0,
        create_by=request.user,
        update_by=request.user,
    )

    async_task(
        'apps.interfaces.tasks.import_api_doc_task',
        task_id=task_id,
        format=fmt,
        source=source,
        service_id=int(service_id),
        user_id=user_id,
        message_id=message.id,
        url=url,
        content=content,
        uri_prefix=uri_prefix,
        match_mode=match_mode,
        target_module_id=int(target_module_id) if target_module_id else None,
        auth_config=auth_config,
    )
    return Response({'task_id': task_id, 'message': '导入任务已提交，完成后将发送站内信通知',
                     'message_id': message.id}, status=200)


@api_view(['POST'])
def har_preview(request: Request):
    """HAR 解析预览（不落库）

    上传 HAR 文件后先解析并返回结构预览，前端据此展示分组、动态参数与
    认证探测结果，用户确认后再调用 import_api_v2 真正入库。

    参数:
      - file: HAR 文件（source=file）
      - url:  HAR 文件 URL（source=url）
      - authConfig: 可选，认证补齐配置
      - probeAuth: 是否从 HAR 中自动探测登录接口（默认 true）
    返回: {stats, apis, dependencies, authSuggestion}
    """
    source = (request.data.get('source') or 'file').lower()
    content = ''
    if source == 'url':
        url = request.data.get('url')
        if not url:
            return Response({'detail': '请输入 URL'}, status=400)
        try:
            content = _fetch_url_content_v2(url)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
    else:
        uploaded = request.FILES.get('file')
        if not uploaded:
            return Response({'detail': '请上传 HAR 文件'}, status=400)
        try:
            content = uploaded.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return Response({'detail': f'文件读取失败: {e}'}, status=400)
        if not content or not content.strip():
            return Response({'detail': '导入内容不能为空'}, status=400)

    auth_config = request.data.get('authConfig')
    if isinstance(auth_config, str) and auth_config.strip():
        try:
            auth_config = json.loads(auth_config)
        except (json.JSONDecodeError, ValueError):
            return Response({'detail': 'authConfig 不是合法 JSON'}, status=400)
    if auth_config is not None and not isinstance(auth_config, dict):
        return Response({'detail': 'authConfig 必须是对象'}, status=400)

    try:
        api_list, dependencies, har_stats = _har_analyze(content or '', auth_config)
    except ValueError as e:
        return Response({'detail': str(e)}, status=400)

    # 认证探测：HAR 里通常没有 Authorization，帮用户把登录接口找出来
    auth_suggestion = _har_detect_auth_endpoint(api_list)
    if auth_suggestion:
        auth_suggestion.pop('_seq', None)

    apis = [{
        'seq': a['seq'],
        'name': a['name'],
        'method': a['method'],
        'path': a['path'],
        'query': a.get('query') or {},
        'group': _har_group_key(a),
        'status': a.get('status'),
        'headers_count': len(a.get('headers') or []),
        'body_kind': a.get('body_kind') or '',
        'body_dynamic': {k: v['var'] for k, v in (a.get('dynamic') or {}).items()
                         if v.get('where') == 'body'},
        'query_dynamic': {k: v['var'] for k, v in (a.get('dynamic') or {}).items()
                          if v.get('where') == 'query'},
        'dynamic_nullable': [k for k, v in (a.get('dynamic') or {}).items()
                             if v.get('nullable')],
        'has_null_dynamic': any(v.get('is_null') for v in (a.get('dynamic') or {}).values()),
        'auth_injected': bool(a.get('auth_injected')),
        'sensitive_header_stripped': not bool(a.get('auth_header_name')),
    } for a in api_list]

    return Response({
        'stats': har_stats,
        'apis': apis,
        'dependencies': dependencies,
        'authSuggestion': auth_suggestion,
    }, status=200)


@api_view(['POST'])
def import_har_sync(request: Request):
    """同步导入 HAR（解析 → 落库 → 回传接口 id，按 HAR 真实发起顺序）

    ★ 2026-09-22 新增，服务于「用例内 HAR 导入」。

    与 import_api_v2 的区别：那个是**异步**的（返回 task_id、完成后发站内信），
    调用方拿不到落库结果，也就无法接着做后续动作；而「用例里导入一段 HAR
    并直接把接口挂成步骤」必须知道刚导入了哪些接口。本接口同步执行并回传
    api_ids，调用方拿到后再调 POST /test/add_many_api_step/ 建步骤即可。

    参数:
      - file / url : HAR 内容来源（二选一；也支持直接传 content）
      - service    : 目标服务 ID（必填）
      - module     : 目标模块 ID（可选；不传则按 HAR 分组自动建模块）
      - uriPrefix  : URL 前缀（可选）
      - matchMode  : overwrite / skip / keep_both（默认 overwrite）
      - authConfig : 认证补齐配置（可选）

    返回:
      {"stats": {...}, "api_ids": [...], "apis": [{id,name,method,url,status}]}

    注意：api_ids 的顺序是 HAR 里的**真实发起顺序**（已由
    _parse_har_v2 的逆序落库 + 末尾 reverse 还原），可直接按序建步骤。
    """
    source = (request.data.get('source') or 'file').lower()
    content = ''
    if source == 'url':
        url = request.data.get('url')
        if not url:
            return Response({'detail': '请输入 URL'}, status=400)
        try:
            content = _fetch_url_content_v2(url)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
    else:
        uploaded = request.FILES.get('file')
        if uploaded is not None:
            try:
                content = uploaded.read().decode('utf-8', errors='ignore')
            except Exception as e:
                return Response({'detail': f'文件读取失败: {e}'}, status=400)
        else:
            raw = request.data.get('content') or ''
            content = raw.decode('utf-8', errors='ignore') if isinstance(raw, bytes) else raw
        if not content or not str(content).strip():
            return Response({'detail': '请上传 HAR 文件或提供 content'}, status=400)

    service_id = request.data.get('service') or request.data.get('service_id')
    if not service_id:
        return Response({'detail': '缺少参数 service（目标服务 ID）'}, status=400)
    service_obj = Service.objects.filter(id=service_id, is_delete=False).first()
    if service_obj is None:
        return Response({'detail': f'服务 {service_id} 不存在或已删除'}, status=400)

    module_id = request.data.get('module') or None
    uri_prefix = request.data.get('uriPrefix') or ''
    match_mode = request.data.get('matchMode') or ImportMatchMode.Overwrite
    if match_mode not in (ImportMatchMode.Overwrite, ImportMatchMode.Skip,
                          ImportMatchMode.KeepBoth):
        match_mode = ImportMatchMode.Overwrite

    auth_config = request.data.get('authConfig')
    if isinstance(auth_config, str) and auth_config.strip():
        try:
            auth_config = json.loads(auth_config)
        except (json.JSONDecodeError, ValueError):
            return Response({'detail': 'authConfig 不是合法 JSON'}, status=400)
    if auth_config is not None and not isinstance(auth_config, dict):
        return Response({'detail': 'authConfig 必须是对象'}, status=400)

    user = getattr(request, 'user', None)
    if user is None or not getattr(user, 'is_authenticated', False):
        return Response({'detail': '未认证，请先登录'}, status=401)

    api_ids = []
    try:
        stats = _parse_har_v2(str(content), service_obj.id, user.id,
                              uri_prefix=uri_prefix, match_mode=match_mode,
                              target_module_id=module_id, auth_config=auth_config,
                              api_ids_out=api_ids)
    except (Service.DoesNotExist, ServiceModule.DoesNotExist):
        return Response({'detail': '目标服务或模块不存在'}, status=400)
    except User.DoesNotExist:
        return Response({'detail': '当前用户不存在'}, status=401)
    except ValueError as e:
        return Response({'detail': str(e)}, status=400)

    apis = []
    for api_obj in Api.objects.filter(id__in=api_ids):
        apis.append({
            'id': api_obj.id,
            'name': api_obj.name,
            'method': api_obj.method,
            'url': api_obj.url,
            'status': api_obj.status,
        })

    return Response({'stats': stats, 'api_ids': api_ids, 'apis': apis}, status=200)


@api_view(['POST'])
def har_analyze_ai(request: Request):
    """HAR 轨迹 → 规则式分析 → LLM 归因 → 用例草稿（阶段一最小闭环）

    ★ 2026-09-22 新增。把此前两条**互不相连**的链串起来：

      _har_analyze（时序 / 认证补齐 / 动态参数 / 跨请求依赖 / 路径族分组，确定性、零幻觉）
        → build_trace_digest 压成一份 LLM 读得懂的轨迹摘要
        → LLM 归因（业务场景划分 / 数据流解释 / 可验证断言 / 风险与覆盖缺口 / 用例草稿）

    在此之前，「规则式分析」只服务于「把接口导进资产库」，而「AI 生成用例」只能从
    用户手写的需求文本出发 —— 浏览器里真实发生过什么，AI 是看不到的。本接口补上这一段。

    参数:
      - source      : file / url / content（默认 file）
      - file / url / content : HAR 内容来源
      - ai_config_id: AI 模型配置 ID（必填）
      - project     : 项目 ID（必填）
      - uriPrefix   : URL 前缀（可选，进入轨迹摘要用）
      - authConfig  : 认证补齐配置（可选，JSON 字符串或对象）
      - module      : 落库目标模块 ID（可选，缺省用项目第一个模块）
      - apply       : 是否把用例草稿落库为功能用例（默认 false，只归因不入库）
      - draft       : 可选。把上一次 apply=false 返回的 ai 对象原样回传，
                      则**跳过 LLM 调用**直接用它落库 —— 保证「你审阅的那份」和
                      「入库的那份」是同一份数据（LLM 有随机性，重跑结果会变），
                      同时省掉一次 30s+ 的模型调用。与 apply=true 搭配使用。

    返回（裸 payload，由全局渲染器 CustomRender 统一套 {code,msg,result}）:
      {
          "digest": 喂给 LLM 的轨迹摘要（原文回传，便于人工复核归因依据）,
          "rule_stats": _har_analyze 统计,
          "apis": 精简接口清单,
          "ai": {scenarios, data_flow, risks, coverage_gaps, cases},
          "ai_error": LLM 失败时的原因（空串=成功）。失败时 ai 为空结构，
                     但 digest/rule_stats/apis 仍然有效 —— 规则层不会因模型故障而丢,
          "saved": [{"id":..,"name":..}],           # apply=true 时
          "apply_requested": bool,
          "apply_note": not_requested | saved | no_case_saved | llm_produced_no_case
      }
      ⚠ 不要再手写一层 {code,msg,result} —— 那会产生 result.result 双层嵌套。

    说明：本接口**同步**执行（归因一般 20~60 秒）。做成异步 task + 站内信会切断
    「导入后立刻看到归因」这个闭环，而这正是本链路的全部价值所在。
    """
    from apps.interfaces.har_ai import (
        build_trace_digest, run_llm_attribution, save_cases_as_func_case,
        normalize_attribution,
    )
    from apps.projects.models import Project

    # ---- 0. 先鉴权，再干活 ----
    #   顺序很重要：若先解析内容，未带凭据的请求会先撞上「请上传 HAR 文件」的 400，
    #   把「没登录」这个真正的失败原因盖掉，排查时极易误判为参数问题。
    user = getattr(request, 'user', None)
    if user is None or not getattr(user, 'is_authenticated', False):
        return Response({'detail': '未认证，请先登录'}, status=401)

    # ---- 0.5 先读 draft（透传模式：跳过 LLM，也就不需要模型配置） ----
    #   放在 ai_config_id 校验**之前**，否则「只把审阅过的草稿入库」这条路径
    #   会被「请选择 AI 模型」这个无关的 400 拦下。
    draft = request.data.get('draft')
    if draft:
        if isinstance(draft, str):
            try:
                draft = json.loads(draft)
            except (json.JSONDecodeError, ValueError):
                return Response({'detail': 'draft 不是合法 JSON'}, status=400)
        if not isinstance(draft, dict):
            return Response({'detail': 'draft 必须是对象'}, status=400)

    # ---- 1. 解析 HAR 内容来源（与 import_har_sync 同一套口径） ----
    #   ⚠ 走 content(JSON body) 时受 Django DATA_UPLOAD_MAX_MEMORY_SIZE（默认 2.5MB）限制，
    #     超出会由框架直接返回 400 HTML（连本函数都进不来）。前端请用 file(multipart)
    #     上传 —— FILES 走 FILE_UPLOAD_MAX_MEMORY_SIZE，超大文件自动落临时文件，不受该限制。
    source = (request.data.get('source') or 'file').lower()
    content = ''
    if source == 'url':
        url = request.data.get('url')
        if not url:
            return Response({'detail': '请输入 URL'}, status=400)
        try:
            content = _fetch_url_content_v2(url)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
    else:
        uploaded = request.FILES.get('file')
        if uploaded is not None:
            try:
                content = uploaded.read().decode('utf-8', errors='ignore')
            except Exception as e:
                return Response({'detail': f'文件读取失败: {e}'}, status=400)
        else:
            raw = request.data.get('content') or ''
            content = raw.decode('utf-8', errors='ignore') if isinstance(raw, bytes) else raw
        if not content or not str(content).strip():
            return Response({'detail': '请上传 HAR 文件或提供 content'}, status=400)

    ai_config_id = request.data.get('ai_config_id')
    if not ai_config_id and not draft:
        # 透传 draft 时不走 LLM，模型 ID 无意义，不强行要求
        return Response({'detail': '请选择 AI 模型'}, status=400)

    project_id = request.data.get('project') or request.data.get('project_id')
    if not project_id:
        return Response({'detail': '项目 ID 不能为空'}, status=400)

    auth_config = request.data.get('authConfig')
    if isinstance(auth_config, str) and auth_config.strip():
        try:
            auth_config = json.loads(auth_config)
        except (json.JSONDecodeError, ValueError):
            return Response({'detail': 'authConfig 不是合法 JSON'}, status=400)
    if auth_config is not None and not isinstance(auth_config, dict):
        return Response({'detail': 'authConfig 必须是对象'}, status=400)

    # ---- 2. 规则式分析（事实来源，LLM 不得改写） ----
    try:
        api_list, dependencies, stats = _har_analyze(str(content), auth_config)
    except ValueError as e:
        return Response({'detail': str(e)}, status=400)

    # ---- 3. 轨迹摘要 ----
    digest = build_trace_digest(api_list, dependencies, stats)

    project_obj = Project.objects.filter(id=project_id).first()
    project_name = project_obj.name if project_obj is not None else ''

    # ---- 4. LLM 归因 ----
    #   ★ 支持 draft 透传：调用方可以先把 apply=false 拿到的 ai 结果给用户审阅，
    #     再把**同一份** JSON 通过 draft 回传落库。否则 apply=true 会重跑一次 LLM，
    #     用户看到的草稿和实际入库的草稿就不是同一份（LLM 有随机性），
    #     既不可审计，也白花一次 30s+ 的模型调用。
    ai_result = None
    ai_error = ''
    if draft:
        # draft 已在 ---- 0.5 段解析完毕
        ai_result = normalize_attribution(draft)
        logger.info('[HAR归因] 使用调用方透传的 draft（跳过 LLM 调用）')
    else:
        try:
            ai_result = run_llm_attribution(int(ai_config_id), digest, project_name)
        except Exception as e:
            # ★ 优雅降级：规则式分析（时序/认证/动态参数/跨依赖/分组）是确定性的、
            #   已经成功，那部分价值不该被 LLM 的失败一笔勾销；而 LLM 失败最常见的原因
            #   是「输出被 max_tokens 截断」，重试一次往往就好。
            #   因此这里**不返 4xx/5xx**（前端拦截器会把非 200 弹成一个不说明原因的通用错误），
            #   改为 200 + ai_error 字段，与本平台 /test/system_function_doc/ 的既有约定一致。
            logger.exception('[HAR归因] LLM 调用失败，降级为仅返回规则层结果')
            ai_error = str(e)
            ai_result = {'scenarios': [], 'data_flow': [], 'risks': [],
                         'coverage_gaps': [], 'cases': []}

    # ---- 5. 可选落库（默认不入库，避免未评审的草稿污染用例库） ----
    saved = []
    apply_requested = str(request.data.get('apply')).lower() in ('1', 'true', 'yes', 'on')
    if apply_requested:
        module_id = request.data.get('module') or None
        try:
            saved = save_cases_as_func_case(
                ai_result.get('cases') or [], project_id, user, module_id,
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
        logger.info('[HAR归因] 已落库功能用例 %d 条', len(saved))

    # 落库结果要能被机器判定：调用方靠 apply_requested + case_drafts 才能区分
    # 「没要求落库」/「要求了但 LLM 这次没产出用例」/「落库失败」三种情况。
    # 否则 saved=[] 有歧义，很容易被当成「功能坏了」（实测就误判过一轮）。
    if not apply_requested:
        apply_note = 'not_requested'
    elif saved:
        apply_note = 'saved'
    elif ai_result.get('cases'):
        apply_note = 'no_case_saved'      # 有草稿但一条都没落进去 —— 需要查
    else:
        apply_note = 'llm_produced_no_case'  # LLM 本次未产出有效用例（重试即可）

    apis = [{
        'seq': a.get('seq'),
        'method': a.get('method'),
        'path': a.get('path'),
        'name': a.get('name'),
        'status': a.get('status'),
        'host': a.get('host'),
        'dynamic': sorted((a.get('dynamic') or {}).keys()),
    } for a in api_list[:200]]

    # ⚠ 返回契约：这里必须交**裸 payload**。
    #   全局渲染器 utils/base.py:90 CustomRender 会无条件把视图返回的 dict
    #   塞进 result（data 为 dict 且无 'results' 键 → response['result'] = data）。
    #   若此处再手写一层 {code,msg,result}，响应体就变成
    #   {"code":200,"msg":"ok","result":{"code":0,"msg":"ok","result":{...}}}
    #   —— 前端按 result.digest 取值会全部拿到 undefined，而且 HTTP 仍是 200，
    #   排查时极易误判为「LLM 没产出内容」。同类端点 import_har_sync(L2412)
    #   同样是裸 payload，保持一致。
    return Response({
        'digest': digest,
        'rule_stats': stats,
        'apis': apis,
        'ai': ai_result,
        'ai_error': ai_error,
        'saved': saved,
        'apply_requested': apply_requested,
        'apply_note': apply_note,
    }, status=200)


@api_view(['POST'])
def api_run(request: Request):
    # 对应接口文档中的接口调试
    host = request.data.get('host')
    headers = request.data.get('headers')
    body_type = request.data.get('body_type')
    params = request.data.get('params')
    json_body = request.data.get('json_tree')
    data_body = request.data.get('data')
    api_json_type = request.data.get('api_json_type')
    uri = request.data.get('url')
    method = request.data.get('method')
    response = run_api_request(host, headers, params, json_body, data_body, uri, method, api_json_type,
                               body_type, False)
    return Response(data=response, status=200)


@api_view(['POST'])
def mock_api_run(request: Request):
    user_request = UserRequest(headers={}, query_params={}, body={}, params={})
    user_request.headers = api_list_to_dict(request.data.get('headers'), {})
    user_request.params = api_list_to_dict(request.data.get('params'), {})
    if request.data.get('body_type') == ApiMock.BodyType.Json:
        json_body = api_list_to_dict(request.data.get('json_tree'), {} if request.data.get('api_json_type') == 'object' else [])
        user_request.body = json_body
    else:
        data_body = api_list_to_dict(request.data.get('data'), {})
        user_request.body = data_body

    data, status_code = _api_mock_view(user_request, '/'.join(urlparse(request.data.get('url')).path.split('/')[2:]))
    # if isinstance(data, dict):
    #     data = json.dumps(data, indent=4, ensure_ascii=False)
    return Response(data=data, status=status_code)


def run_api_request(host, headers, params, json_body, data_body, uri, method, api_json_type, body_type, env_header):

    _api_response = {'request_body': None, 'request_header': None, 'response_body': None, 'response_header': None,
                     'response_status': None, 'request_url': None}
    # 处理请求头和查询参数
    headers = api_list_to_dict(headers, {})
    params = api_list_to_dict(params, {})

    if env_header:
        env_header = api_list_to_dict(env_header, {})
        env_header.update(headers)
    else:
        env_header = headers

    if body_type == ApiMock.BodyType.Json:
        # 处理请求体
        json_body = api_list_to_dict(json_body, {} if api_json_type == 'object' else [])
        body = json_body
        api_response = Session().request(method=method, url=host + uri, json=json_body, headers=env_header,
                                         params=params, verify=False)
    else:
        data_body = api_list_to_dict(data_body, {})
        body = data_body
        api_response = Session().request(method=method, url=host + uri, data=data_body, headers=env_header,
                                         params=params, verify=False)

    _api_response['response_status'] = str(api_response.status_code)
    _api_response['request_body'] = body
    _api_response['request_header'] = api_response.request.headers
    _api_response['request_url'] = api_response.request.url
    _api_response['response_header'] = api_response.headers
    try:
        _api_response['response_body'] = api_response.json()
    except requests.exceptions.JSONDecodeError:
        _api_response['response_body'] = api_response.text

    return _api_response


def _api_mock_view(request, sub_path):
    # 获取mock请求的api的接口ID
    api_id = sub_path.strip('/').split('/')[0]
    api_mock_queryset = ApiMock.objects.filter(is_delete=False, api=api_id, is_enable=True)
    if not api_mock_queryset.exists():
        return '该接口没有创建Mock规则或者没有启用', 200

    match_mock_obj = None
    for api_mock_obj in api_mock_queryset:
        if not check_headers_condition(request.headers, api_mock_obj.headers):
            continue
        if not check_body_condition(request, api_mock_obj):
            continue
        if not check_params_condition(request.query_params, api_mock_obj.params):
            continue
        match_mock_obj = api_mock_obj
        break

    if match_mock_obj is None:
        return '该接口请求没有满足Mock触发条件', 200
    # 设置响应延长时间
    time.sleep(match_mock_obj.timeout / 1000)
    data_type = {} if match_mock_obj.api_response_type == 'object' else []
    response_header = api_list_to_dict(match_mock_obj.response_headers, {})
    mock_response = {'request_body': request.body, 'request_header': request.headers, 'response_body': {},
                     'response_header': response_header,
                     'response_status': str(match_mock_obj.status_code),
                     'request_params': request.params}
    if match_mock_obj.response_type == ApiMock.ResBodyType.Json:
        mock_response['response_body'] = api_list_to_dict(match_mock_obj.response_tree, data_type)
        return mock_response, match_mock_obj.status_code
    else:
        api_obj = Api.objects.get(is_delete=False, id=api_id)
        for obj in api_obj.response_tree:
            if int(obj['response_status']) == match_mock_obj.status_code:
                mock_response['response_body'] = api_list_to_dict(obj['response_data'], data_type)
                return mock_response, match_mock_obj.status_code

        return '该接口文档响应体没有对应的响应状态码', match_mock_obj.status_code


@api_view(['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS'])
def api_mock_view(request: Request, sub_path=None):
    # 获取mock请求的api的接口ID
    api_id = sub_path.strip('/').split('/')[0]
    api_mock_queryset = ApiMock.objects.filter(is_delete=False, api=api_id, is_enable=True)
    if not api_mock_queryset.exists():
        return Response(data='该接口没有创建Mock规则或者没有启用', status=200)

    match_mock_obj = None
    for api_mock_obj in api_mock_queryset:
        if not check_headers_condition(request.headers, api_mock_obj.headers):
            continue
        if not check_body_condition(request, api_mock_obj):
            continue
        if not check_params_condition(request.query_params, api_mock_obj.params):
            continue
        match_mock_obj = api_mock_obj
        break

    if match_mock_obj is None:
        return Response(data='该接口请求没有满足Mock触发条件', status=200)
    # 设置响应延长时间
    time.sleep(match_mock_obj.timeout / 1000)
    data_type = {} if match_mock_obj.api_response_type == 'object' else []
    if match_mock_obj.response_type == ApiMock.ResBodyType.Json:
        data = api_list_to_dict(match_mock_obj.response_tree, data_type)
        headers = api_list_to_dict(match_mock_obj.response_headers, {})
        return Response(data=data, status=match_mock_obj.status_code, headers=headers)
    else:
        api_obj = Api.objects.get(is_delete=False, id=api_id)
        for obj in api_obj.response_tree:
            if int(obj['response_status']) == match_mock_obj.status_code:
                data = api_list_to_dict(obj['response_data'], data_type)
                return Response(data=data, status=match_mock_obj.status_code)
        return Response(data='该接口文档响应体没有对应的响应状态码', status=200)


def check_headers_condition(act_headers, exp_headers, result=True):
    """
    检查请求头的参数是否满足Mock条件
    """
    for check_obj in exp_headers:
        check_str = check_obj['check_method']
        check_func = CHECK_FUNC_MAP[check_str]
        check_exp_value = check_obj['value']
        check_act_value = act_headers.get(check_obj['name'])
        check_result = check_func(check_exp_value, check_act_value, raise_assert_error=False)
        result = result and check_result
        if not result:
            break
    return result


def check_body_condition(request, api_mock_obj, content_type='application/json'):
    """
    检查请求体的参数是否满足Mock条件
    """
    if api_mock_obj.body_type == ApiMock.BodyType.Json:
        if isinstance(request, UserRequest):
            data = request.body
        else:
            data = request.data if content_type in request.content_type else {}
        json_data = {} if api_mock_obj.api_json_type == 'object' else []
        _, check_list = get_json_check_condition(api_mock_obj.json_tree, json_data, [])
        return check_json_condition(check_list, data)
    else:
        if isinstance(request, UserRequest):
            data = request.body
        else:
            data = {} if content_type in request.content_type else request.data
        return check_data_condition(data, api_mock_obj.data)


def check_data_condition(act_data, exp_data, result=True):
    """
    检查Form-data参数是否满足Mock条件
    """

    for check_obj in exp_data:
        check_str = check_obj['check_method']
        check_func = CHECK_FUNC_MAP[check_str]
        check_exp_value = check_obj['value']
        check_act_value = act_data.get(check_obj['name'])
        check_result = check_func(check_exp_value, check_act_value, raise_assert_error=False)
        result = result and check_result
        if not result:
            break
    return result


def check_params_condition(act_params, exp_params, result=True):
    """
    检查查询参数是否满足Mock条件
    """

    for check_obj in exp_params:
        check_str = check_obj['check_method']
        check_func = CHECK_FUNC_MAP[check_str]
        check_exp_value = check_obj['value']
        check_act_value = act_params.get(check_obj['name'])
        check_result = check_func(check_exp_value, check_act_value, raise_assert_error=False)
        result = result and check_result
        if not result:
            break
    return result


def get_json_check_condition(list_obj: list, json_data, check_list, json_path='$'):
    """
    检查json参数是否满足Mock条件
    """
    for obj in list_obj:
        name, value, obj_type, children = obj['name'], str(obj['value']), obj['type'], obj.get('children', [])
        is_required, check_method = obj['is_required'], obj['check_method']
        check_list.append({'json_path': json_path + f'.{name}', 'check_method': check_method,
                           'is_required': is_required, 'exp_value': value})
        if obj_type == 'object':
            if isinstance(json_data, dict):
                json_data[name] = dict()
                get_json_check_condition(children, json_data[name],  check_list, json_path + f'.{name}')
            else:
                json_data.append(dict())
                get_json_check_condition(children, json_data[-1],  check_list, json_path + f'.{name}')
            continue
        elif obj_type == 'array':
            if isinstance(json_data, dict):
                json_data[name] = list()
                get_json_check_condition(children, json_data[name], check_list,  json_path + f'.{name}')
            else:
                json_data.append(list())
                get_json_check_condition(children, json_data[-1],  check_list, json_path + f'.{name}')
            continue
        elif obj_type == 'string':
            value = value
        elif obj_type == 'number':
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    value = value
        elif obj_type == 'boolean':
            if value.upper() == "TRUE":
                value = True
            else:
                value = False
        else:
            value = None
        if isinstance(json_data, dict):
            json_data[name] = value
        else:
            json_data.append(value)

    return json_data, check_list


def check_json_condition(check_list, act_body):
    """
    检查json请求参数
    """
    for check_obj in check_list:
        check_method = check_obj['check_method']
        path = check_obj['json_path']
        is_required = check_obj['is_required']
        exp_value = check_obj['exp_value']

        get_data = jsonpath.jsonpath(act_body, path)
        if not get_data:
            if check_method != 'no_check' or is_required:
                return False
        if get_data and check_method != 'no_check':
            result = CHECK_FUNC_MAP[check_method](exp_value, get_data[0], raise_assert_error=False)
            if not result:
                return False
    else:
        return True
