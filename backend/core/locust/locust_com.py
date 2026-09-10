import json
import base64
import jsonpath
import time
import re
import importlib
import ast
import inspect
from functools import partial
from typing import Any
from pydantic import BaseModel
from utils.user_exception import UserFuncNotExistException, ParseParamsException
from core.com.faker import faker_function_map


class StepType:
    PlatformSystemFunction = -1  # 平台自带的系统函数
    Request = 5  # request 类型的Api请求
    ComStep = 3  # 用户定义的公共步骤
    UserCustomizeScript = 4  # 用户定义一次性脚本
    Control = 9  # 逻辑控制器


class StepResponse(BaseModel):
    stepParams: Any
    apiHost: Any
    apiUri: Any
    apiUrl: Any
    apiMethod: Any
    apiRequestHeaders: Any
    apiRequestParams: Any
    apiRequestBody: Any
    apiStatusCode: Any
    apiResponseHeaders: Any
    apiResponseCookies: Any
    apiResponseBody: Any
    funcReturn: Any
    runTimes: Any
    runElement: Any



class ParamsType:
    STRING = "Str"
    INT = 'Int'
    FLOAT = 'Float'
    BOOL = 'Bool'
    DICT = 'Dict'
    LIST = "List"
    TUPLE = 'Tuple'


ParamsTypeMap = {
    int: ParamsType.INT,
    float: ParamsType.FLOAT,
    str: ParamsType.STRING,
    bool: ParamsType.BOOL,
    dict: ParamsType.DICT,
    list: ParamsType.LIST,
    tuple: ParamsType.TUPLE,
}


class CaseParams(BaseModel):
    globalParams: dict
    # 用例执行过程中用来存储环境变量
    envParams: dict
    # 用例执行过程中用来存储用例变量
    caseParams: dict
    # 用来存续步骤执行过程中步骤的结果值
    stepResponse: dict


def is_run_step(run_params, case_params, case_logs_obj, result=True) -> bool:
    """
    判断是否执行该测试步骤，True执行步骤，False不执行该步骤
    """
    if not run_params:
        return result

    return loop_assert_by_check_list(run_params, case_params, case_logs_obj, raise_assert_error=False)


def get_loop_number(step, case_params) -> int:
    """
    获取循环执行的次数，返回一个数字
    """
    if not step['loop']:
        return 0

    row_loop_times = step['loop'][0]['loop_times']
    replace_request_data = partial(replace_params_class_data, case_params)
    loop_times = replace_request_data(row_loop_times)
    loop_times = replace_all_func_value(faker_function_map, loop_times)
    try:
        loop_times = int(loop_times)
    except ValueError as e:
        raise e

    return loop_times


def get_loop_element(step, case_params):
    """
    获取循环执行的对象body_type=json 为自定义数据， 否则为动态变量引用，api_json_type判断是列表还是字典
    返回值可以是字符串，列表和字典
    """
    # 这种为自定义数据类型
    if step['body_type'] == 1:
        loop_value = list_to_dict(step['loop'], {} if step['api_json_type'] == 'object' else [], case_params,
                                  step['case_step_id'], 'tmp_loop')

    else:
        row_loop_var = step['loop'][0]['loop_times']
        replace_request_data = partial(replace_params_class_data, case_params)
        loop_var = replace_request_data(row_loop_var)
        loop_value = replace_all_func_value(faker_function_map, loop_var)
        try:
            loop_value = ast.literal_eval(loop_value)
            if type(loop_value) not in [list, dict, str]:
                raise TypeError('变量引用值不可迭代')
        except Exception as e:

            raise e

    return loop_value


def get_module_functions(module_path):
    return dict(inspect.getmembers(importlib.import_module(module_path), inspect.isfunction))


def get_function_params(function_name):
    """
    获取函数名,函数参数类型,函数参数默认值
    """
    a = inspect.signature(function_name).parameters
    params_list = []
    for name, param in a.items():
        if name == 'self':
            continue
        params_info = dict()
        params_info['function_name'] = function_name.__name__
        params_info['params_name'] = name
        params_info['type'] = ParamsTypeMap[param.annotation]
        # 判断参数是否有默认值
        if param.default != param.empty:
            params_info['value'] = str(param.default)
        else:
            params_info['value'] = None
        params_list.append(params_info)
        # # 判断参数是否是可变位置参数
        # if param.kind == inspect.Parameter.VAR_POSITIONAL:
        #     print('可变位置参数')
        # # 判断参数是否是可变关键字参数
        # if param.kind == inspect.Parameter.VAR_KEYWORD:
        #     print('可变关键字参数')
    return params_list


def exec_and_return(python_obj):
    exec(python_obj.package)
    exec(python_obj.script, locals())
    return locals()


def extract_by_jsonpath(input_data, json_path, is_contains=False):
    extract_data = jsonpath.jsonpath(input_data, json_path)
    if extract_data:
        return True, extract_data[0]

    if is_contains:
        return False, None
    else:
        raise ParseParamsException(json_path)


def formatter_log(log_type, log_title):
    local_time = time.strftime('%Y-%m-%d %H:%M:%S')
    return '【{}】【{}】【{}】'.format(local_time, log_type, log_title)


def list_to_dict(list_obj: list, json_data, case_params, step_id, data_type, root_data=None):
    """
    将列表嵌套字典转换成dict
    """
    if root_data is None:  # 第一次调用时初始化root_data
        root_data = json_data

    replace_request_data = partial(replace_params_class_data, case_params)
    for obj in list_obj:
        name, value, obj_type, children = obj['name'], str(obj['value']), obj['type'], obj.get('children', [])
        if obj_type == 'object':
            if isinstance(json_data, dict):
                json_data[name] = dict()
                list_to_dict(children, json_data[name], case_params, step_id, data_type, root_data)
            else:
                json_data.append(dict())
                list_to_dict(children, json_data[-1], case_params, step_id, data_type, root_data)
            continue
        elif obj_type == 'array':
            if isinstance(json_data, dict):
                json_data[name] = list()
                list_to_dict(children, json_data[name], case_params, step_id, data_type, root_data)
            else:
                json_data.append(list())
                list_to_dict(children, json_data[-1], case_params, step_id, data_type, root_data)
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
        case_params.stepResponse[f'{step_id}'][data_type] = root_data
    return json_data


def lis2dict(list_obj: list, case_params, step_id, data_type):
    """
    将列表嵌套字典转换成dict，不带子级的数据结构
    """
    json_data = {}
    file_data = {}
    replace_request_data = partial(replace_params_class_data, case_params)
    for obj in list_obj:
        name, obj_type, children = obj['name'], obj['type'], obj.get('children', [])
        if obj_type == 'string':
            value = replace_all_func_value(faker_function_map, replace_request_data(str(obj['value'])))
            json_data[name] = value
        elif obj_type == 'file':
            value = obj['value']
            file_data[name] = (value.get('name'), base64.b64decode(value.get('raw')), value.get('type'))
        else:
            value = None
            json_data[name] = value
        case_params.stepResponse[f'{step_id}'][data_type] = json_data
    return json_data, file_data


def json_to_dict(json_str):
    if json_str:
        return json.loads(json_str)
    return dict()


def run_func_return_value(match_value, inner_funcs):
    func = match_value[2:-1]
    match_func_name = func[:func.find('(')]
    # 函数执行匹配到内部函数
    if inner_funcs.get(match_func_name):
        params_value = eval(match_value[2:-1], inner_funcs)
    # 函数执行匹配到用户自定义函数
    elif PythonScript.objects.all().filter(name=match_func_name, is_delete=False):
        python_obj = PythonScript.objects.all().get(name=match_func_name)
        params_value = eval(match_value[2:-1], exec_and_return(python_obj))
    # 没有配置到函数,用户脚本错误
    else:
        raise UserFuncNotExistException(func)
    return params_value


def replace_all_func_value(inner_funcs, params_value, f_pattern=r'f{.*}'):
    def inner_replace(match):
        return str(run_func_return_value(match.group(0), inner_funcs))

    return re.sub(f_pattern, inner_replace, params_value)


def set_user_params(case_params: CaseParams, params: list, inner_funcs, f_pattern=r'f{.*}'):
    """
    设置用户全局变量
    """
    if params:
        for params_obj in params:
            params_key = params_obj['name']
            params_value = params_obj['value']
            params_value = single_replace_data(case_params, params_value)
            # 返回的非字符串类型,不用在进行函数执行匹配
            if not isinstance(params_value, str):
                case_params.caseParams[params_key] = params_value
                continue

            match_all = re.findall(f_pattern, params_value)
            # 只匹配到了一个执行函数并且匹配函数的字符串长度和原字符串长度相等
            if match_all and len(match_all) == 1 and len(params_value) == len(match_all[0]):
                params_value = run_func_return_value(match_all[0], inner_funcs)
            # 匹配到执行函数
            elif match_all:
                params_value = replace_all_func_value(inner_funcs, params_value)
            # 用户参数为固定值
            else:
                params_value = params_value
            case_params.caseParams[params_key] = params_value


def set_step_params(case_params: CaseParams, step, inner_funcs, f_pattern=r'f{.*?}'):
    """
    设置步骤变量
    """
    if step['step_params']:
        for params_obj in step['step_params']:
            params_key = params_obj['name']
            params_value = params_obj['value']
            params_value = single_replace_data(case_params, params_value)
            # 返回的非字符串类型,不用在进行函数执行匹配
            if not isinstance(params_value, str):
                case_params.stepResponse[f'{step["case_step_id"]}']["stepParams"][params_key] = params_value
                continue

            match_all = re.findall(f_pattern, params_value)
            # 只匹配到了一个执行函数并且匹配函数的字符串长度和原字符串长度相等
            if match_all and len(match_all) == 1 and len(params_value) == len(match_all[0]):
                params_value = run_func_return_value(match_all[0], inner_funcs)
            # 匹配到执行函数
            elif match_all:
                params_value = replace_all_func_value(inner_funcs, params_value)
            # 用户参数为固定值
            else:
                params_value = params_value
            case_params.stepResponse[f'{step["case_step_id"]}']["stepParams"][params_key] = params_value


def single_replace_data(case_params: CaseParams, original_data, pattern=r'\${.*?}'):
    match_all = re.findall(pattern, original_data)
    if match_all and len(match_all) == 1 and len(original_data) == len(match_all[0]):
        return get_attr(case_params, match_all[0][2: -1])
    else:
        return replace_params_class_data(case_params, original_data)


def get_attr(case_params: CaseParams, attr_name):
    try:
        extra_json_path = '$.' + attr_name
        extra_result, extra_data = extract_by_jsonpath(case_params.__dict__, extra_json_path)
        return extra_data
    except AttributeError as e:
        raise e


def replace_params_class_data(case_params: CaseParams, original_data, pattern=r'\${.*?}'):
    """
    替换用例中URL， Method， Headers， Data， Params，Json， 断言中的数据，通过正则， 默认的替换规规是${}
    """

    def inner_replace(match):
        end_position = -1
        match_group = match.group(0)
        start_position = 3 if '$1' in match_group else 2
        match_value = match_group[start_position: end_position]
        extra_json_path = '$.' + match_value
        extra_result, extra_data = extract_by_jsonpath(case_params.__dict__, extra_json_path, is_contains=True)
        if extra_result:
            return str(extra_data)
        # 匹配枚举值
        else:
            raise ParseParamsException(extra_json_path)

    return re.sub(r'\S1{.*?}', inner_replace, re.sub(pattern, inner_replace, original_data))


def set_func_extract(return_value, extract, case_logs_obj, params_class):
    if isinstance(return_value, tuple):
        {setattr(params_class, extract_obj.key, return_value[index]):
             case_logs_obj.logs.append(formatter_log('success', '【{} 被设置为: {}】'.format(extract_obj.key,
                                                                                       return_value[index])))
         for index, extract_obj in enumerate(extract)}
    elif extract:
        setattr(params_class, extract[0].key, return_value)
        case_logs_obj.logs.append(formatter_log('success', '【{} 被设置为: {}】'.format(extract[0].key, return_value)))
