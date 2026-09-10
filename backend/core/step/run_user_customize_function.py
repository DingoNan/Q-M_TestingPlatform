from core.com.common import formatter_log, exec_and_return
from core.com.step_model import StepResponse
from apps.scripts.models import PythonScript
from core.com.check import loop_assert_by_check_list


def run_step_user_customize_function(manager_obj, env_id, step, case_params, case_logs_obj, run_times, run_element):
    """
    解析并执行用户项目中自定义的用户函数
    """
    step_id = step["case_step_id"]
    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    case_params.stepResponse[f'{step_id}']['runElement'] = run_element
    params_list = []
    for params_obj in step['func_params']:
        # params_obj.value = single_replace_data(params_class, case_logs_obj, params_obj.value)
        params_list.append(params_obj['value'])

    python_obj = PythonScript.objects.all().get(id=step['keyword'], is_delete=False)
    function_name = python_obj.name
    step_index = step['step_index']
    return_value = exec_and_return(python_obj)[function_name](*tuple(params_list))
    case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', f'{function_name} 函数执行成功'),
                                   'value': f'返回值 -> {return_value}'})

    step_response = StepResponse(apiUrl=None, apiMethod=None, apiRequestHeaders=None, apiRequestParams=None,
                                 apiRequestBody=None, apiStatusCode=None, apiResponseHeaders=None,
                                 apiResponseCookies=None, apiResponseBody=None, funcReturn=return_value)
    case_params.stepResponse[step_index] = step_response.__dict__

    # 执行步骤的断言参数,如果步骤中有断言数据则忽略接口的断言数据
    loop_assert_by_check_list(step['check_params'], case_params, case_logs_obj)
