import json
import jsonpath
import requests
import copy
import time
import uuid
from datetime import datetime
from urllib.parse import urlparse
from requests.sessions import Session
from django.db.models import Q
from rest_framework.decorators import api_view
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
from rest_framework.permissions import IsAuthenticated
from apps.interfaces.filters import ApiFilter, ApiMockFilter
from apps.messages.models import Message


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
    qs = Api.objects.filter(service_id=service_id, method=method, url=url, is_delete=False)
    if qs.exists():
        if match_mode == ImportMatchMode.Skip:
            return qs.first(), 'skipped'
        if match_mode == ImportMatchMode.KeepBoth:
            api_obj = Api.objects.create(**api_data)
            return api_obj, 'created'
        # overwrite
        qs.update(**api_data, update_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
        return qs.first(), 'updated'
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
    )
    return Response({'task_id': task_id, 'message': '导入任务已提交，完成后将发送站内信通知',
                     'message_id': message.id}, status=200)


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
