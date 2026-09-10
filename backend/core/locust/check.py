import ast
from functools import partial
from core.com.faker import faker_function_map
from core.locust.locust_com import replace_params_class_data, \
    replace_all_func_value, get_module_functions

CHECK_LOG_INFO = '预期结果: {} -> {}\n实际结果: {} -> {}'


CHECK_TEXT = {
    'check_equal': "校验字符串实际值和预期值相等",
    'check_not_equal': "校验字符串实际值和预期值不相等",
    'check_number_equal': "校验数字实际值和预期值相等",
    'check_number_gt': '校验数字实际值大于预期值',
    'check_number_ge': '校验数字实际值大于等于预期值',
    'check_number_lt': '校验数字实际值小于于预期值',
    'check_number_le': '校验数字实际值小于等于预期值',
    'check_number_not_equal': "校验数字实际值和预期值不相等",
    'check_bool_equal': "校验布尔值相等",
    'check_bool_not_equal': "校验布尔值不相等",
    'check_object_is_empty': '校验数组或字典对象为空',
    'check_object_is_not_empty': '校验数组或字典对象非空',

}


def no_check():
    pass


def check_equal(check_exp_value, check_act_value):
    """
    校验字符串是否相等
    """
    if check_exp_value == check_act_value:
        return True
    else:
        return False


def check_not_equal(check_exp_value, check_act_value):
    """
    校验字符串是否不相等
    """
    if check_exp_value != check_act_value:
        return True
    else:
        return False


def check_number_equal(check_exp_value, check_act_value):
    """
    校验数字是否相等
    """
    try:
        check_exp_value = int(check_exp_value)
        check_act_value = int(check_act_value)
    except ValueError:
        try:
            check_exp_value = float(check_exp_value)
            check_act_value = float(check_act_value)
        except ValueError:
            check_exp_value = check_exp_value
            check_act_value = check_act_value
    if check_exp_value == check_act_value:
        return True
    else:
        return False


def check_number_not_equal(check_exp_value, check_act_value):
    """
    校验数字是否不相等
    """
    try:
        check_exp_value = int(check_exp_value)
        check_act_value = int(check_act_value)
    except ValueError:
        try:
            check_exp_value = float(check_exp_value)
            check_act_value = float(check_act_value)
        except ValueError:
            check_exp_value = check_exp_value
            check_act_value = check_act_value
    if check_exp_value != check_act_value:
        return True
    else:
        return False


def check_number_gt(check_exp_value, check_act_value):
    """
    校验实际值是否大于预期值
    """
    try:
        check_exp_value = int(check_exp_value)
        check_act_value = int(check_act_value)
    except ValueError:
        try:
            check_exp_value = float(check_exp_value)
            check_act_value = float(check_act_value)
        except ValueError:
            raise ValueError('字符串转换成数字类型失败')
    if check_act_value > check_exp_value:
        return True
    else:
        return False


def check_number_ge(check_exp_value, check_act_value):
    """
    校验实际值是否大于等于预期值
    """
    try:
        check_exp_value = int(check_exp_value)
        check_act_value = int(check_act_value)
    except ValueError:
        try:
            check_exp_value = float(check_exp_value)
            check_act_value = float(check_act_value)
        except ValueError:
            raise ValueError('字符串转换成数字类型失败')
    if check_act_value >= check_exp_value:
        return True
    else:
        return False


def check_number_lt(check_exp_value, check_act_value):
    """
    校验实际值是否小于预期值
    """
    try:
        check_exp_value = int(check_exp_value)
        check_act_value = int(check_act_value)
    except ValueError:
        try:
            check_exp_value = float(check_exp_value)
            check_act_value = float(check_act_value)
        except ValueError:
            raise ValueError('字符串转换成数字类型失败')
    if check_act_value < check_exp_value:
        return True
    else:
        return False


def check_number_le(check_exp_value, check_act_value):
    """
    校验实际值是否小于等于预期值
    """
    try:
        check_exp_value = int(check_exp_value)
        check_act_value = int(check_act_value)
    except ValueError:
        try:
            check_exp_value = float(check_exp_value)
            check_act_value = float(check_act_value)
        except ValueError:
            raise ValueError('字符串转换成数字类型失败')
    if check_act_value <= check_exp_value:
        return True
    else:
        return False


def check_bool_equal(check_exp_value, check_act_value):
    """
    校验布尔值是否相等
    """
    if check_exp_value.upper() == check_act_value.upper():
        return True
    else:
        return False


def check_bool_not_equal(check_exp_value, check_act_value):
    """
    校验布尔值是否不相等
    """
    if check_exp_value.upper() != check_act_value.upper():
        return True
    else:
        return False


def check_object_is_empty(check_exp_value, check_act_value):
    """
    校验数组或字典对象是否为空
    """
    if isinstance(check_act_value, str):
        try:
            check_act_value = ast.literal_eval(check_act_value)
        except SyntaxError:
            raise SyntaxError('实际值不是数组对象或字典对象')

    if not check_act_value:
        return True
    else:
        return False


def check_object_is_not_empty(check_exp_value, check_act_value):
    """
    校验数组或字典对象是否不为空
    """
    if isinstance(check_act_value, str):
        try:
            check_act_value = ast.literal_eval(check_act_value)
        except SyntaxError:
            raise SyntaxError('实际值不是数组对象或字典对象')

    if check_act_value:
        return True
    else:
        return False


CHECK_FUNC_MAP = get_module_functions('core.locust.check')


def loop_assert_by_check_list(api_response, check_list, case_params, result=True, exp_key='exp_value',
                              act_key='act_value', check_key='method', is_condition=False):
    """
    循环校验列表返回校验结果
    """
    replace_request_data = partial(replace_params_class_data, case_params)

    for index, check_obj in enumerate(check_list):
        # 动态替换实际值和预期值
        raw_act_value = check_obj[act_key]
        check_act_value = replace_request_data(raw_act_value)
        check_act_value = replace_all_func_value(faker_function_map, check_act_value)
        raw_exp_value = check_obj[exp_key]
        check_exp_value = replace_request_data(raw_exp_value)
        check_exp_value = replace_all_func_value(faker_function_map, check_exp_value)

        # 实际校验
        check_str = check_obj[check_key]
        check_func = CHECK_FUNC_MAP[check_str]
        check_result = check_func(check_exp_value, check_act_value)

        if not check_result:
            check_title = CHECK_TEXT[check_str]
            check_info = CHECK_LOG_INFO.format(raw_exp_value, check_exp_value, raw_act_value, check_act_value)
            api_response.failure(check_title + '->' + check_info)

        if is_condition:
            if index:
                result = check_result
            else:
                condition = check_list[index - 1]['andOr']
                result = result and check_result if condition == 'And' else result or check_result

    return result
