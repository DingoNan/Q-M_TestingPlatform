import core.com.faker as sys_function
from urllib.parse import urlparse
from functools import partial
import requests.exceptions
from core.locust.locust_com import (
    replace_params_class_data,
    list_to_dict,
    lis2dict,
    CaseParams
)
from core.locust.check import loop_assert_by_check_list


def exec_and_return(manager_obj, script_code, case_params, sys_function):
    if script_code:
        python_func_objs, script_code = parse_user_function(script_code)
        session = manager_obj.session_manager
        selenium = manager_obj.driver_manager
        if parse_user_function(script_code):
            for python_func_obj in python_func_objs:
                exec(python_func_obj.package)
                exec(python_func_obj.script, locals())
        exec(script_code, locals())


def run_python_script(manager_obj, env_id, step, case_params, run_times):
    step_id = step["case_step_id"]
    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    step_script = step['script']
    setup_script = step['setup']
    teardown_script = step['teardown']
    exec_and_return(manager_obj, setup_script, case_params, sys_function)
    exec_and_return(manager_obj, step_script, case_params, sys_function)
    exec_and_return(manager_obj, teardown_script, case_params, sys_function)


class ApiModel:

    def __init__(self, url, method, step, case_params):
        step_id = step["case_step_id"]
        replace_request_data = partial(replace_params_class_data, case_params)

        # 处理域名和请求地址
        self.url = replace_request_data(url)
        parsed = urlparse(self.url)
        self.host = f"{parsed.scheme}://{parsed.netloc}"
        case_params.stepResponse[f'{step_id}']['apiHost'] = self.host
        # 处理请求地址
        case_params.stepResponse[f'{step_id}']['apiUri'] = parsed.path
        case_params.stepResponse[f'{step_id}']['apiUrl'] = self.url

        # 处理请求方法
        self.method = method
        case_params.stepResponse[f'{step_id}']['apiMethod'] = self.method

        # 处理拼接参数
        self.params, _ = lis2dict(step['api_params'], case_params, step_id, 'apiRequestParams')
        case_params.stepResponse[f'{step_id}']['apiRequestParams'] = self.params

        # 处理请求体
        if step['body_type'] == 1:
            self.json = list_to_dict(step['api_json_tree'], {} if step['api_json_type'] == 'object' else [],
                                     case_params, step_id, 'apiRequestBody')

            case_params.stepResponse[f'{step_id}']['apiRequestBody'] = self.json

        else:
            self.data, self.file = lis2dict(step['api_data'], case_params, step_id, 'apiRequestBody')
            case_params.stepResponse[f'{step_id}']['apiRequestBody'] = self.data

        # 处理请求头
        self.headers = step['api_headers']
        self.headers, _ = lis2dict(self.headers, case_params, step_id, 'apiRequestHeaders')
        case_params.stepResponse[f'{step_id}']['apiRequestHeaders'] = self.headers
        self.plant_headers = step['plant_headers']
        self.plant_headers, _ = lis2dict(self.plant_headers, case_params, step_id, 'apiRequestHeaders')
        self.plant_headers.update(self.headers)
        case_params.stepResponse[f'{step_id}']['apiRequestHeaders'] = self.plant_headers

        # 处理断言
        self.check = step['check_params']


def run_step_request(locust_client_mng, step, case_params, run_times, run_element, res_size=0):
    step_id = step["case_step_id"]
    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    case_params.stepResponse[f'{step_id}']['runElement'] = run_element

    api_request: ApiModel = ApiModel(url=step['api_uri'], method=step['api_method'], step=step, case_params=case_params)

    if step['common_headers']:
        locust_client_mng.add_common_headers(api_request.host, api_request.headers)

    if locust_client_mng.common_headers and api_request.host in locust_client_mng.common_headers:
        api_request.headers.update(locust_client_mng.common_headers[api_request.host])

    # 执行前置脚本
    exec_and_return(locust_client_mng, step['setup'], case_params, sys_function)

    url = case_params.stepResponse[f'{step_id}']['apiUri']
    method = case_params.stepResponse[f'{step_id}']['apiMethod']
    body = case_params.stepResponse[f'{step_id}']['apiRequestBody']
    params = case_params.stepResponse[f'{step_id}']['apiRequestParams']
    headers = case_params.stepResponse[f'{step_id}']['apiRequestHeaders']

    def _tear_down(_api_response):
        try:
            response_body = api_response.json()
        except requests.exceptions.JSONDecodeError:
            response_body = api_response.text

        # 检查Response中的参数类型和预期结果
        if not isinstance(response_body, str) and step['api_response_tree']:
            # 提取接口的响应参数
            extract_response_set_params(response_body, api_response, case_params, step)
            # 执行后置脚本
            exec_and_return(locust_client_mng, step['teardown'], case_params, sys_function)

        else:
            # 执行后置脚本
            extract_response_set_params(response_body, api_response, case_params, step)
            exec_and_return(locust_client_mng, step['teardown'], case_params, sys_function)

        # 执行步骤的断言参数,如果步骤中有断言数据则忽略接口的断言数据
        loop_assert_by_check_list(api_response, api_request.check, case_params)
        return len(_api_response.content or b'')

    if step['body_type'] == 1:
        with locust_client_mng.session_manager[api_request.host].\
                request(url=url, method=method, json=body, params=params, headers=headers, verify=step['verify'],
                        allow_redirects=step['allow_redirects'],
                        timeout=step['timeout'], catch_response=True) as api_response:
            res_size = _tear_down(api_response)

    elif api_request.file:
        with locust_client_mng.session_manager[api_request.host].\
                request(url=url, method=method, data=body, params=params, headers=headers, files=api_request.file,
                        verify=step['verify'],
                        allow_redirects=step['allow_redirects'], timeout=step['timeout'], catch_response=True) as api_response:
            res_size = _tear_down(api_response)
    else:
        with locust_client_mng.session_manager[api_request.host].\
                request(url=url, method=method, data=body, params=params, headers=headers, verify=step['verify'],
                        allow_redirects=step['allow_redirects'],
                        timeout=step['timeout'], catch_response=True) as api_response:
            res_size = _tear_down(api_response)
    return res_size


def extract_response_set_params(response_body, api_response, case_params: CaseParams, step):
    """
    根据json响应体提取值并设置变量
    """
    step_id = step["case_step_id"]
    case_params.stepResponse[f'{step_id}']['apiStatusCode'] = api_response.status_code
    case_params.stepResponse[f'{step_id}']['apiResponseHeaders'] = dict(api_response.headers)
    case_params.stepResponse[f'{step_id}']['apiResponseCookies'] = dict(api_response.cookies)
    case_params.stepResponse[f'{step_id}']['apiResponseBody'] = response_body

    return response_body







