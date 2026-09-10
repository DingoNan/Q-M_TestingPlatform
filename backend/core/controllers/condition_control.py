import ast
from functools import partial
from core.com.faker import faker_function_map
from core.com.common import formatter_log, replace_params_class_data,\
    replace_all_func_value, list_to_dict
from core.com.check import loop_assert_by_check_list


def is_run_step(run_params, case_params, case_logs_obj, result=True, is_if=True) -> bool:
    """
    判断是否执行该测试步骤，True执行步骤，False不执行该步骤
    """
    if not run_params:
        return result

    result = loop_assert_by_check_list(run_params, case_params, case_logs_obj, raise_assert_error=False)
    if is_if:
        value = '执行该步骤' if result else '跳过该步骤'
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', f'条件表达式的结果为： {result}'), 'value':  value})
    else:
        value = '退出一直循环' if result else '条件不满足继续循环执行'
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', f'条件表达式的结果为： {result}'), 'value': value})
    return result


def get_loop_number(step, case_params, case_logs_obj):
    """
    获取循环执行的次数，返回一个数字
    """
    if not step['loop']:
        return 0

    row_loop_times = step['loop'][0]['loop_times']
    replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)
    loop_times = replace_request_data(row_loop_times)
    loop_times = replace_all_func_value(faker_function_map, loop_times)
    try:
        loop_times = int(loop_times)
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', f"循环执行次数为： {loop_times}"),
                                       'value': f'{row_loop_times} -> {loop_times}'})
    except ValueError as e:
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('ERROR', f"循环执行次数非正整数"),
                                       'value': f'{row_loop_times} -> {loop_times}'})
        raise e

    return loop_times


def get_loop_element(step, case_params, case_logs_obj):
    """
    获取循环执行的对象body_type=json 为自定义数据， 否则为动态变量引用，api_json_type判断是列表还是字典
    返回值可以是字符串，列表和字典
    """
    # 这种为自定义数据类型
    if step['body_type'] == 1:
        loop_value = list_to_dict(step['loop'], {} if step['api_json_type'] == 'object' else [], case_params,
                                  case_logs_obj, step['case_step_id'], 'tmp_loop')

    else:
        row_loop_var = step['loop'][0]['loop_times']
        replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)
        loop_var = replace_request_data(row_loop_var)
        loop_value = replace_all_func_value(faker_function_map, loop_var)
        try:
            loop_value = ast.literal_eval(loop_value)
            if type(loop_value) not in [list, dict, str]:
                case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('ERROR', f"变量引用值不可迭代"),
                                                           'value': f'{row_loop_var} -> {str(loop_value)}'})
                raise TypeError('变量引用值不可迭代')
        except Exception as e:
            case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('ERROR', f"变量引用值转换成Python对象报错"),
                                                   'value': f'{row_loop_var} -> {e}'})
            raise e

    case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', f"循环执行次数为： {len(loop_value)}"),
                                           'value': f'迭代对象 -> {str(loop_value)}'})

    return loop_value


