import json
import base64

import jsonpath
import time
import re
import importlib
import ast
import inspect
from functools import partial
from core.com.enum_obj import ParamsTypeMap
from utils.user_exception import UserFuncNotExistException, StrToObjectException, ParseParamsException
from apps.scripts.models import PythonScript, EnumScript
from apps.envs.models import Env
from apps.tests.models import CaseRunLog
from apps.elements.models import Element
from apps.elements.serializers import ElementSerializers
from apps.envs.models import EnvGlobalParams
from core.com.step_model import CaseParams
from core.com.faker import faker_function_map


def get_module_functions(module_path):
    return dict(inspect.getmembers(importlib.import_module(module_path), inspect.isfunction))


def get_enum_map(env_id):
    project_id = Env.objects.get(env=env_id, is_delete=False).project
    enum_query_set = EnumScript.objects.filter(is_delete=False, project=project_id)
    enum_map = {}
    for enum_obj in enum_query_set:
        enum_map[enum_obj.name] = {}
        for enum_params in enum_obj.value:
            enum_map[enum_obj.name][enum_params.get('name')] = enum_params.get('value')
    return enum_map


def get_function_params(function_name):
    """
    获取函数名,函数参数类型,函数参数默认值
    """
    a = inspect.signature(function_name).parameters
    func_desc = [new_str.strip() for new_str in function_name.__doc__.strip().split('\n')] if function_name.__doc__ else None

    params_list = []
    index = 0
    for name, param in a.items():
        if name == 'self':
            continue
        params_info = dict()
        params_info['function_name'] = function_name.__name__
        params_info['explain'] = func_desc[index + 1][len(name) + 1:] if func_desc else ''
        params_info['name'] = name
        params_info['type'] = ParamsTypeMap[param.annotation]
        # 判断参数是否有默认值
        if param.default != param.empty:
            params_info['value'] = str(param.default)
        else:
            params_info['value'] = None
        index = index + 1
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


def get_env_params_by_env_id(env_id, project_id):
    """
    通过项目ID和环境ID获取环境下所有变量
    """
    return EnvGlobalParams.objects.all().filter(env=env_id, is_delete=False, project=project_id)


def loop_for_iterator(item):
    """
    循环执行迭代器中的内容
    """
    while True:
        try:
            next(item)
        except StopIteration:
            break


def extract_by_jsonpath(input_data, json_path, case_logs_obj, is_contains=False):
    extract_data = jsonpath.jsonpath(input_data, json_path)
    if extract_data:
        return True, extract_data[0]

    if is_contains:
        return False, None
    else:
        case_logs_obj.result = CaseRunLog.CaseResult.ERROR
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('ERROR', '变量引用失败'), 'value': f'请检查变量引用->{json_path}'})
        raise ValueError(f'请检查变量引用->{json_path}')


def formatter_log(log_type, log_title):
    local_time = time.strftime('%Y-%m-%d %H:%M:%S')
    return '【{}】【{}】【{}】'.format(local_time, log_type, log_title)


def func_list_to_dict(list_obj: list, json_data, case_params, case_logs_obj):
    """
    将列表嵌套字典转换成dict,适用于函数调用
    """
    replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)
    for obj in list_obj:
        if obj.get('parentId'):
            continue
        name, value, obj_type, children = obj['name'], str(obj['value']), obj['type'], obj.get('children', [])
        if obj_type == 'Dict':
            json_data[name] = dict()
            func_list_to_dict(children, json_data[name], case_params, case_logs_obj)
            continue
        elif obj_type == 'List':
            json_data[name] = list()
            func_list_to_dict(children, json_data[name], case_params, case_logs_obj)
            continue
        elif obj_type == 'EleObject':
            value = ElementSerializers(Element.objects.all().get(id=value, is_delete=False)).data
        elif obj_type == 'Str':
            value = replace_all_func_value(faker_function_map, replace_request_data(value))
        elif obj_type == 'Int':
            value = replace_all_func_value(faker_function_map, replace_request_data(value))
            try:
                value = int(value)
            except ValueError:
                value = value
        elif obj_type == 'Float':
            value = replace_all_func_value(faker_function_map, replace_request_data(value))
            try:
                value = float(value)
            except ValueError:
                value = value
        elif obj_type == 'Bool':
            value = replace_all_func_value(faker_function_map, replace_request_data(value))
            if value.upper() == "TRUE":
                value = True
            else:
                value = False
        else:
            value = None
        json_data[name] = value
    return json_data


def list_to_dict(list_obj: list, json_data, case_params, case_logs_obj, step_id, data_type, root_data=None):
    """
    将列表嵌套字典转换成dict
    """
    if root_data is None:  # 第一次调用时初始化root_data
        root_data = json_data

    replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)
    for obj in list_obj:
        name, value, obj_type, children = obj['name'], str(obj['value']), obj['type'], obj.get('children', [])
        if obj_type == 'object':
            if isinstance(json_data, dict):
                json_data[name] = dict()
                list_to_dict(children, json_data[name], case_params, case_logs_obj, step_id, data_type, root_data)
            else:
                json_data.append(dict())
                list_to_dict(children, json_data[-1], case_params, case_logs_obj, step_id, data_type, root_data)
            continue
        elif obj_type == 'array':
            if isinstance(json_data, dict):
                json_data[name] = list()
                list_to_dict(children, json_data[name], case_params, case_logs_obj, step_id, data_type, root_data)
            else:
                json_data.append(list())
                list_to_dict(children, json_data[-1], case_params, case_logs_obj, step_id, data_type, root_data)
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


def lis2dict(list_obj: list, case_params, case_logs_obj, step_id, data_type):
    """
    将列表嵌套字典转换成dict，不带子级的数据结构
    """
    json_data = {}
    file_data = {}
    replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)
    for obj in list_obj:
        name, obj_type, children = obj['name'], obj['type'], obj.get('children', [])
        if name:
            if obj_type == 'string':
                value = replace_all_func_value(faker_function_map, replace_request_data(str(obj['value'])))
                json_data[name] = value
            elif obj_type == 'file':
                value = obj['value']
                file_data[name] = (value.get('name'), base64.b64decode(value.get('raw')), value.get('type'))
            elif obj_type == 'null':
                value = None
                json_data[name] = value
            else:
                value = replace_all_func_value(faker_function_map, replace_request_data(str(obj['value'])))
                json_data[name] = value
            case_params.stepResponse[f'{step_id}'][data_type] = json_data
    return json_data, file_data


def api_list_to_dict(list_obj: list, json_data):
    """
    将列表嵌套字典转换成dict
    """
    # 请求头/请求体为空时上层会传 None，这里兜底，避免 TypeError: 'NoneType' is not iterable
    if not list_obj:
        return json_data
    for obj in list_obj:
        name, value, obj_type, children = obj['name'], str(obj['value']), obj['type'], obj.get('children', [])
        if obj_type == 'object':
            if isinstance(json_data, dict):
                json_data[name] = dict()
                api_list_to_dict(children, json_data[name])
            else:
                json_data.append(dict())
                api_list_to_dict(children, json_data[-1])
            continue
        elif obj_type == 'array':
            if isinstance(json_data, dict):
                json_data[name] = list()
                api_list_to_dict(children, json_data[name])
            else:
                json_data.append(list())
                api_list_to_dict(children, json_data[-1])
            continue
        elif obj_type == 'string':
            value = replace_all_func_value(faker_function_map, value)
            value = value
        elif obj_type == 'number':
            value = replace_all_func_value(faker_function_map, value)
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    value = value
        elif obj_type == 'boolean':
            value = replace_all_func_value(faker_function_map, value)
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
    return json_data


def json_to_dict(json_str):
    if json_str:
        return json.loads(json_str)
    return dict()


def str_to_number_and_bool(params_list, int_pattern='int[(].*?[)]', float_pattern='float[(].*?[)]',
                           bool_pattern='bool[(].*?[)]', list_pattern='list[(].*[)]',
                           dict_pattern='dict[(].*[)]', tuple_pattern='tuple[(].*[)]'):
    """
    解析函数中传入的参数并返回解析后参数的元组
    """
    for index, var in enumerate(params_list):
        bool_match = re.findall(bool_pattern, var)
        float_match = re.findall(float_pattern, var)
        int_match = re.findall(int_pattern, var)
        list_match = re.findall(list_pattern, var)
        dict_match = re.findall(dict_pattern, var)
        tuple_match = re.findall(tuple_pattern, var)
        try:
            if int_match:
                params_list[index] = ast.literal_eval(int_match[0][4:-1])
            if float_match:
                params_list[index] = ast.literal_eval(float_match[0][6:-1])
            if bool_match:
                params_list[index] = ast.literal_eval(bool_match[0][5:-1])
            if list_match:
                params_list[index] = ast.literal_eval(list_match[0][5:-1])
            if dict_match:
                params_list[index] = ast.literal_eval(dict_match[0][5:-1])
            if tuple_match:
                params_list[index] = ast.literal_eval(tuple_match[0][6:-1])
        except Exception as e:
            raise StrToObjectException()

    return params_list


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


def set_user_params(case_params: CaseParams, case_logs_obj, params: list, inner_funcs, f_pattern=r'f{.*}'):
    """
    设置用户全局变量
    """
    if params:
        for params_obj in params:
            params_key = params_obj['name']
            params_value = params_obj['value']
            params_value = single_replace_data(case_params, case_logs_obj, params_value)
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
        case_params = json.dumps(case_params.caseParams, indent=4, ensure_ascii=False)
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '加载用例变量'), 'value': case_params})
    else:
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '加载用例变量'), 'value': None})


def set_case_data_params(case_params: CaseParams, case_logs_obj, inner_funcs, f_pattern=r'f{.*}'):
    """
    设置用户全局变量
    """
    for params_key, params_value in case_params.caseData.items():
        params_value = single_replace_data(case_params, case_logs_obj, params_value)
        # 返回的非字符串类型,不用在进行函数执行匹配
        if not isinstance(params_value, str):
            case_params.caseData[params_key] = params_value
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
        case_params.caseData[params_key] = params_value


def single_replace_data(case_params: CaseParams, case_logs_obj, original_data, pattern=r'\${.*?}'):
    match_all = re.findall(pattern, original_data)
    if match_all and len(match_all) == 1 and len(original_data) == len(match_all[0]):
        return get_attr(case_params, case_logs_obj, match_all[0][2: -1])
    else:
        return replace_params_class_data(case_params, case_logs_obj, original_data)


def get_attr(case_params: CaseParams, case_logs_obj, attr_name):
    try:
        extra_json_path = '$.' + attr_name
        extra_result, extra_data = extract_by_jsonpath(case_params.__dict__, extra_json_path, case_logs_obj)
        return extra_data
    except AttributeError as e:
        case_logs_obj.result = CaseRunLog.CaseResult.ERROR
        raise e


def replace_params_class_data(case_params: CaseParams, case_logs_obj, original_data, pattern=r'\${.*?}'):
    """
    替换用例中URL， Method， Headers， Data， Params，Json， 断言中的数据，通过正则， 默认的替换规规是${}
    """
    def inner_replace(match):
        end_position = -1
        match_group = match.group(0)
        start_position = 3 if '$1' in match_group else 2
        match_value = match_group[start_position: end_position]
        extra_json_path = '$.' + match_value
        extra_result, extra_data = extract_by_jsonpath(case_params.__dict__, extra_json_path, case_logs_obj, is_contains=True)
        if extra_result:
            return str(extra_data)
        # 匹配枚举值
        else:
            try:
                extra_json_list = extra_json_path.split('.')
                enum_obj = EnumScript.objects.get(is_delete=False, name=extra_json_list[1])
                for params in enum_obj.value:
                    if params.get('name') == extra_json_list[2]:
                        return params.get('value')
                raise  ParseParamsException(extra_json_path)
            except Exception:
                raise  ParseParamsException(extra_json_path)

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