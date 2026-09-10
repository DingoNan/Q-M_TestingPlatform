import copy
import json
import core.com.faker as sys_function
from functools import partial
import requests.exceptions
from requests import Response
from apps.envs.models import EnvService, Headers, Service, EnvPlant
from core.com.common import (
    formatter_log,
    extract_by_jsonpath,
    replace_params_class_data,
    list_to_dict,
    lis2dict,
    replace_all_func_value,
)
from utils.user_exception import EnvServiceNotExistException, EnvPlantNotExistException
from core.com.check import loop_assert_by_check_list, CHECK_FUNC_MAP, CHECK_TEXT
from apps.tests.models import CaseRunLog, Step
from apps.interfaces.api_guard import assert_api_runnable
from core.com.step_model import CaseParams
from core.com.faker import faker_function_map
from core.step.run_python_script import exec_and_return


class ApiModel:

    @staticmethod
    def push_log_info(title: str, log_info: str, case_logs_obj: object):
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO',
                                                                      f'{title}'), 'value': f'{log_info}'})

    @staticmethod
    def get_api_host(uri, host_rules):
        """
        根据接口请求路径匹配对应的规则
        """
        for rules_index in range(len(host_rules) - 1, -1, -1):
            method = host_rules[rules_index]['method']
            rule = host_rules[rules_index]['rule']
            host = host_rules[rules_index]['host']
            if method == '任意匹配':
                return host
            elif method == '前缀匹配' and uri.startswith(rule):
                return host
            elif method == '精准匹配' and uri == rule:
                return host
        return '127.0.0.1'

    def __init__(self, host, url, method, step, case_params, case_logs_obj, env_headers, manager_obj):
        step_id = step["case_step_id"]
        replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)

        # 处理域名和请求地址
        self.url = replace_request_data(url)
        self.url = replace_all_func_value(faker_function_map, self.url)
        self.host = host
        case_params.stepResponse[f'{step_id}']['apiHost'] = self.host
        # 处理请求地址
        case_params.stepResponse[f'{step_id}']['apiUri'] = self.url
        case_params.stepResponse[f'{step_id}']['apiUrl'] = self.host + self.url
        self.push_log_info('Request Url', self.host + self.url, case_logs_obj)

        # 处理请求方法
        self.method = method
        case_params.stepResponse[f'{step_id}']['apiMethod'] = self.method
        self.push_log_info('Request Method', self.method, case_logs_obj)

        # 处理拼接参数
        self.params, _ = lis2dict(step['api_params'], case_params, case_logs_obj, step_id, 'apiRequestParams')
        case_params.stepResponse[f'{step_id}']['apiRequestParams'] = self.params
        self.push_log_info('Request Params', json.dumps(self.params, indent=4, ensure_ascii=False), case_logs_obj)

        # 处理请求体
        if step['body_type'] == Step.BodyType.Json:
            self.json = list_to_dict(step['api_json_tree'], {} if step['api_json_type'] == 'object' else [],
                                     case_params, case_logs_obj, step_id, 'apiRequestBody')

            case_params.stepResponse[f'{step_id}']['apiRequestBody'] = self.json
            self.push_log_info('Request Body', json.dumps(self.json, indent=4, ensure_ascii=False), case_logs_obj)

        else:
            self.data, self.file = lis2dict(step['api_data'], case_params, case_logs_obj, step_id, 'apiRequestBody')
            case_params.stepResponse[f'{step_id}']['apiRequestBody'] = self.data
            self.push_log_info('Request Body', json.dumps(self.data, indent=4, ensure_ascii=False), case_logs_obj)

        # 处理请求头
        self.headers = step['api_headers']
        self.headers, _ = lis2dict(self.headers, case_params, case_logs_obj, step_id, 'apiRequestHeaders')
        self.final_headers = {}
        if env_headers is not None:
            self.com_headers = env_headers.value
            self.com_headers, _ = lis2dict(self.com_headers, case_params, case_logs_obj, step_id, 'apiRequestHeaders')
            self.final_headers.update(self.headers)

        if manager_obj.common_headers and self.host in manager_obj.common_headers:
            tmp_headers = copy.deepcopy(manager_obj.common_headers[self.host])
            self.final_headers.update(tmp_headers)
        self.final_headers.update(self.headers)
        self.headers = copy.deepcopy(self.final_headers)
        case_params.stepResponse[f'{step_id}']['apiRequestHeaders'] = self.headers

        # 处理断言
        self.check = step['check_params']


def get_api_data(env_id, step, case_params, case_logs_obj, manager_obj):
    server_obj = Service.objects.all().get(id=step['api_service'])

    # 接口请求域名跟随服务域名走
    if server_obj.is_server_host:
        env_service_query = EnvService.objects.all().filter(env=env_id, service=step['api_service'], is_delete=False)
        if not env_service_query.exists():
            raise EnvServiceNotExistException()
        host = env_service_query[0].host
    # 接口请求域名跟随产品域名配置
    else:
        env_plant_query = EnvPlant.objects.all().filter(env=env_id, plant=step['plant'], is_delete=False)
        if not env_plant_query.exists():
            raise EnvPlantNotExistException()
        host = env_plant_query[0].host

    if manager_obj.report_id:
        env_headers_query = Headers.objects.filter(plant=step['plant'], is_delete=False, is_all_run=True, env=env_id)
    else:
        env_headers_query = Headers.objects.filter(plant=step['plant'], is_delete=False, is_all_run=False, env=env_id,
                                                   create_by=manager_obj.user_id)
    env_headers_obj = env_headers_query[0] if env_headers_query else None

    return ApiModel(host=host, url=step['api_uri'], method=step['api_method'], step=step, case_params=case_params,
                    case_logs_obj=case_logs_obj, env_headers=env_headers_obj, manager_obj=manager_obj)


def run_step_request(manager_obj, env_id, step, case_params, case_logs_obj, run_times, run_element):
    step_id = step["case_step_id"]
    # 接口状态守卫：引用了「废弃」接口直接中断，不再发起真实请求
    assert_api_runnable(step.get('keyword'))
    # 执行前置脚本
    exec_and_return(manager_obj, step['setup'], case_logs_obj, formatter_log, case_params, sys_function)
    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    case_params.stepResponse[f'{step_id}']['runElement'] = run_element
    api_request: ApiModel = get_api_data(env_id, step, case_params, case_logs_obj, manager_obj)

    # 根据接口的域名判断需要几个Session
    manager_obj.add_session_manager(api_request.host)
    if step['common_headers']:
        manager_obj.add_common_headers(api_request.host, api_request.headers)

    api_request.push_log_info('Request Headers', json.dumps(api_request.headers, indent=4, ensure_ascii=False), case_logs_obj)

    url = case_params.stepResponse[f'{step_id}']['apiUrl']
    method = case_params.stepResponse[f'{step_id}']['apiMethod']
    body = case_params.stepResponse[f'{step_id}']['apiRequestBody']
    params = case_params.stepResponse[f'{step_id}']['apiRequestParams']
    headers = case_params.stepResponse[f'{step_id}']['apiRequestHeaders']
    if step['body_type'] == Step.BodyType.Json:
        api_response = manager_obj.session_manager[api_request.host].request(url=url, method=method, json=body,
                                                                             params=params,
                                                                             headers=headers,
                                                                             allow_redirects=step['allow_redirects'],
                                                                             verify=step['verify'],
                                                                             timeout=step['timeout'])
    elif api_request.file:
        api_response = manager_obj.session_manager[api_request.host].request(url=url, method=method, data=body,
                                                                             params=params, headers=headers,
                                                                             files=api_request.file,
                                                                             allow_redirects=step['allow_redirects'],
                                                                             verify=step['verify'],
                                                                             timeout=step['timeout'])
    else:
        api_response = manager_obj.session_manager[api_request.host].request(url=url, method=method, data=body,
                                                                             params=params, headers=headers,
                                                                             allow_redirects=step['allow_redirects'],
                                                                             verify=step['verify'],
                                                                             timeout=step['timeout'])
    try:
        response_body = api_response.json()
    except requests.exceptions.JSONDecodeError:
        response_body = api_response.text

    # 检查Response中的参数类型和预期结果
    if not isinstance(response_body, str) and step['api_response_tree']:
        # 提取接口的响应参数
        extract_response_set_params(response_body, api_response, case_params, step)
        # 执行后置脚本
        exec_and_return(manager_obj, step['teardown'], case_logs_obj, formatter_log, case_params, sys_function)
        push_api_request_logs(case_logs_obj, api_response, api_request, response_body)
        # 校验JSON文档结构
        if step['is_check']:
            json_data = {} if step['api_response_type'] == 'object' else []
            request_response, check_required_list, check_type_list,\
                check_value_list = response_list_to_dict(step['api_response_tree'], json_data, [], [],
                                                         [], case_params, case_logs_obj, response_body)
            check_value(request_response, response_body, check_value_list, case_logs_obj)
            check_type(request_response, response_body, check_type_list, case_logs_obj)
            check_required(request_response, response_body, check_required_list, case_logs_obj)
    else:
        # 执行后置脚本
        extract_response_set_params(response_body, api_response, case_params, step)
        exec_and_return(manager_obj, step['teardown'], case_logs_obj, formatter_log, case_params, sys_function)
        push_api_request_logs(case_logs_obj, api_response, api_request, response_body)

    # 执行步骤的断言参数,如果步骤中有断言数据则忽略接口的断言数据
    loop_assert_by_check_list(api_request.check, case_params, case_logs_obj)


def check_required(exp_data, act_data, check_list, case_logs_obj):
    for json_path in check_list:
        act_result, act_value = extract_by_jsonpath(act_data, json_path, case_logs_obj, is_contains=True)
        if not act_result:
            case_logs_obj.result = CaseRunLog.CaseResult.FAIL
            case_logs_obj.logs[-1]['logs'].append(
                {'title': formatter_log('INFO', 'ResponseBody 校验必含失败'), f'value': f'实际值不存在 -> {json_path}'})
            raise AssertionError


def check_type(exp_data, act_data, check_list, case_logs_obj):
    for json_path in check_list:
        exp_result, exp_value = extract_by_jsonpath(exp_data, json_path, case_logs_obj, is_contains=True)
        act_result, act_value = extract_by_jsonpath(act_data, json_path, case_logs_obj, is_contains=True)
        if act_result:
            exp_type = type(exp_value)
            act_type = type(act_value)
            if exp_type != act_type:
                case_logs_obj.result = CaseRunLog.CaseResult.FAIL
                case_logs_obj.logs[-1]['logs'].append(
                    {'title': formatter_log('INFO', 'Response Body 校验类型失败'),
                     f'value': f'校验字段 -> {json_path}\n预期类型 -> {exp_type}\n实际类型 -> {act_type}'})
                raise AssertionError
        else:
            case_logs_obj.result = CaseRunLog.CaseResult.FAIL
            case_logs_obj.logs[-1]['logs'].append(
                {'title': formatter_log('INFO', 'ResponseBody 校验类型失败'), f'value': f'实际值不存在 -> {json_path}'})
            raise AssertionError


def check_value(exp_data, act_data, check_list, case_logs_obj):
    for check_obj in check_list:
        json_path, check_method = check_obj['path'], check_obj['method']
        exp_result, exp_value = extract_by_jsonpath(exp_data, json_path, case_logs_obj, is_contains=True)
        act_result, act_value = extract_by_jsonpath(act_data, json_path, case_logs_obj, is_contains=True)
        if act_result:
            check_func = CHECK_FUNC_MAP[check_method]
            check_title = CHECK_TEXT[check_method]
            check_result = check_func(exp_value, act_value, raise_assert_error=False)
            if not check_result:
                case_logs_obj.logs[-1]['logs'].append(
                    {'title': formatter_log('INFO', 'ResponseBody ' + check_title),
                     f'value': f'校验字段 -> {json_path}\n预期值 -> {exp_value}\n实际值 -> {act_value}'})
                raise AssertionError
        else:
            case_logs_obj.result = CaseRunLog.CaseResult.FAIL
            case_logs_obj.logs[-1]['logs'].append(
                {'title': formatter_log('INFO', 'ResponseBody 校验相等失败'), f'value': f'实际值不存在 -> {json_path}'})
            raise AssertionError


def extract_response_set_params(response_body, api_response: Response, case_params: CaseParams, step):
    """
    根据json响应体提取值并设置变量
    """
    step_id = step["case_step_id"]
    case_params.stepResponse[f'{step_id}']['apiStatusCode'] = api_response.status_code
    case_params.stepResponse[f'{step_id}']['apiResponseHeaders'] = dict(api_response.headers)
    case_params.stepResponse[f'{step_id}']['apiResponseCookies'] = dict(api_response.cookies)
    case_params.stepResponse[f'{step_id}']['apiResponseBody'] = response_body

    return response_body


def response_list_to_dict(list_obj: list, json_data, check_required_list, check_type_list, check_value_list,
                          case_params, case_logs_obj, response_body, json_path='$'):
    """
    将列表嵌套字典转换成dict
    """
    replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)
    for obj in list_obj:
        name, value, obj_type, children = obj['name'], str(obj['value']), obj['type'], obj.get('children', [])
        is_required, check_value_type, check_method = obj['is_required'], obj['check_type'], obj['check_method']
        if check_method != 'no_check':
            check_value_list.append({'path': json_path + f'.{name}', 'method': check_method})
        elif check_value_type:
            check_type_list.append(json_path + f'.{name}')
        elif is_required:
            check_required_list.append(json_path + f'.{name}')
        if obj_type == 'object':
            if isinstance(json_data, dict):
                json_data[name] = dict()
                # 暂时注释掉通过表格方式去动态替换响应体
                # if value:
                #     res_body = json.dumps(response_body, indent=4, ensure_ascii=False)
                #     case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', 'Response Body'), 'value': res_body})
                #     value = replace_request_data(value)
                #     replace_data = replace_all_func_value(faker_function_map, value)
                #     replace_data = ast.literal_eval(replace_data)
                #     parse(json_path + f'.{name}').update(response_body, replace_data)
                response_list_to_dict(children, json_data[name], check_required_list, check_type_list, check_value_list,
                                      case_params, case_logs_obj, response_body, json_path + f'.{name}')
            else:
                json_data.append(dict())
                response_list_to_dict(children, json_data[-1], check_required_list, check_type_list, check_value_list,
                                      case_params, case_logs_obj, response_body, json_path + f'.{name}')
            continue
        elif obj_type == 'array':
            if isinstance(json_data, dict):
                json_data[name] = list()
                response_list_to_dict(children, json_data[name], check_required_list, check_type_list, check_value_list,
                                      case_params, case_logs_obj, response_body, json_path + f'.{name}')
            else:
                json_data.append(list())
                response_list_to_dict(children, json_data[-1], check_required_list, check_type_list, check_value_list,
                                      case_params, case_logs_obj, response_body, json_path + f'.{name}')
            continue
        elif obj_type == 'string':
            value = replace_all_func_value(faker_function_map, replace_request_data(value))
        elif obj_type == 'number':
            value = replace_all_func_value(faker_function_map, replace_request_data(value))
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    value = value
        elif obj_type == 'boolean':
            value = replace_all_func_value(faker_function_map, replace_request_data(value))
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
    return json_data, check_required_list, check_type_list, check_value_list


def push_api_request_logs(case_logs_obj, api_response: Response, api_request: ApiModel, response_body):
    response_headers = json.dumps(dict(api_response.headers), indent=4, ensure_ascii=False)
    response_cookies = json.dumps(dict(api_response.cookies), indent=4, ensure_ascii=False)
    status_code = f'{api_response.status_code}'
    try:
        response_body = json.dumps(response_body, indent=4, ensure_ascii=False)
    except requests.exceptions.JSONDecodeError:
        response_body = api_response.text
    case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', 'Response Body'), 'value': response_body})
    case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', 'Response Status Code'), 'value': status_code})
    case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', 'Response Headers'), 'value': response_headers})
    case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', 'Response Cookies'), 'value': response_cookies})








