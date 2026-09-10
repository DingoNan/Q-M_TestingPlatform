import ast
from core.com.common import single_replace_data, formatter_log, set_func_extract
from core.com.step_model import StepModel
from core.com.check import loop_assert_by_check_list
from core.com.faker import faker_function_map


def run_step_system_function(manager_obj, steps, step_key, env_id, one_step_data: StepModel, params_class, case_logs_obj):
    """
    解析并执行平台自带的系统函数
    """
    params_list = []
    for params_obj in one_step_data.params:
        if params_obj.type != 'Dynamic':
            params_list.append(params_obj.value)
        else:
            params_obj.value = single_replace_data(params_class, case_logs_obj, params_obj.value)
            params_list.append(params_obj.value)

    return_value = faker_function_map[step_key](*tuple(params_list))
    case_logs_obj.logs.append(formatter_log('success', '【{} 函数返回值为: {}】'.format(step_key, return_value)))
    set_func_extract(return_value, one_step_data.extract, case_logs_obj, params_class)
    # 执行步骤的断言参数,如果步骤中有断言数据则忽略接口的断言数据
    loop_assert_by_check_list(one_step_data.check, params_class, case_logs_obj)


def run_debug_system_function(function_name, params_info):
    """
    单独执行平台自带的系统中的函数
    """
    params_list = []
    for params in params_info:
        if params['type'] != 'Str':
            params['value'] = ast.literal_eval(params['value'])
        params_list.append(params['value'])
    return_value = faker_function_map[function_name](*tuple(params_list))
    return {"result": return_value}


def run_debug_user_function(python_func_obj):
    """
    单独执行用户自定义的函数
    """
    try:
        params_info = python_func_obj['params']
        exec(python_func_obj['package'])
        exec(python_func_obj['script'], locals())
        params_list = []
        for params in params_info:
            if params['type'] != 'Str':
                params['value'] = ast.literal_eval(params['value'])
            params_list.append(params['value'])
        return_value = locals()[python_func_obj['name']](*tuple(params_list))
    except Exception as e:
        return_value = '执行报错请检查函数！！！ -> ' + e.__doc__

    return {"result": return_value}
