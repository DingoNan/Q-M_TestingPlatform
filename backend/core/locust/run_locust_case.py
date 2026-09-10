import time
from functools import partial
from typing import Callable
from core.locust.locust_com import (
    replace_params_class_data,
    replace_all_func_value,
    CaseParams,
    StepType,
    StepResponse
)
from core.locust.locust_com import get_loop_number, is_run_step, set_user_params, set_step_params, get_loop_element
from core.locust.run_locust_request import run_step_request, run_python_script
from core.com.faker import faker_function_map

step_type_map = {
    StepType.Request: run_step_request,
    StepType.UserCustomizeScript: run_python_script,
    StepType.ComStep: False,
}


class ControlType:
    IF = '1'     # IF 条件控制器
    FOR = '2'     # 循环控制器
    WHILE = '3'   # While 条件控制器
    TRANSACTION = '4'  # 事务控制器


def step_type_function(step_type, com_step_type):
    if step_type == StepType.ComStep:
        return step_type_map.get(com_step_type)
    else:
        return step_type_map.get(step_type)


def run_locust_one_step(self, locust_client_mng, case_params, step, run_times=0, run_element=None):
    """
    执行一个测试步骤
    """
    step_response = StepResponse(apiUrl=None, apiHost=None, apiUri=None, apiMethod=None, stepParams={},
                                 apiRequestHeaders={}, apiRequestParams={}, apiRequestBody={},
                                 apiStatusCode=None, apiResponseHeaders={}, apiResponseCookies={},
                                 apiResponseBody={}, funcReturn=None, runTimes=0, runElement=None)
    case_params.stepResponse[f'{step["case_step_id"]}'] = step_response.__dict__
    set_step_params(case_params, step, faker_function_map)

    # 替换步骤描述
    replace_request_data = partial(replace_params_class_data, case_params)
    desc = replace_request_data(step['desc'])
    step['desc'] = replace_all_func_value(faker_function_map, desc)

    # 判断是否执行该步骤
    if not step['is_run']:
        return None
    # 判断该步骤是否是逻辑控制器
    if step['type'] == StepType.Control:
        # 执行IF控制器
        if step['keyword'] == ControlType.IF and is_run_step(step['run_params'], case_params, False):
            for children_step in step['children']:
                run_locust_one_step(self, locust_client_mng, case_params, children_step, run_times, run_element)
        # 执行FOR控制器
        elif step['keyword'] == ControlType.FOR:
            for_run_times = get_loop_number(step, case_params)
            for run_index in range(for_run_times):
                case_params.stepResponse[f'{step["case_step_id"]}']['runTimes'] = run_index
                case_params.stepResponse[f'{step["case_step_id"]}']['runElement'] = run_element
                for children_step in step['children']:
                    run_locust_one_step(self, locust_client_mng, case_params, children_step, run_index, run_element)
                # 执行FOREACH控制器
        elif step['keyword'] == ControlType.FOREACH:
            loop_value = get_loop_element(step, case_params)
            if isinstance(loop_value, dict):
                for run_key, run_value in loop_value.items():
                    case_params.stepResponse[f'{step["case_step_id"]}']['runTimes'] = run_key
                    case_params.stepResponse[f'{step["case_step_id"]}']['runElement'] = run_value
                    for children_step in step['children']:
                        run_locust_one_step(self, locust_client_mng, case_params, children_step, run_key, run_value)

            else:
                for run_index, run_value in enumerate(loop_value):
                    case_params.stepResponse[f'{step["case_step_id"]}']['runTimes'] = run_index
                    case_params.stepResponse[f'{step["case_step_id"]}']['runElement'] = run_value
                    for children_step in step['children']:
                        run_locust_one_step(self, locust_client_mng, case_params, children_step, run_index, run_value)

            # 执行等待时间控制器
        elif step['keyword'] == ControlType.SLEEP:
            time.sleep(step['timeout'])
        # 执行WHILE控制器
        elif step['keyword'] == ControlType.WHILE:
            times = 0
            max_loop_times = int(step['until'][0]['max_loop_times'])
            while is_run_step(step['until'], case_params, False):
                for children_step in step['children']:
                    run_locust_one_step(self, locust_client_mng, case_params, children_step, times)
                times = times + 1
                if times == max_loop_times:
                    break
        elif step['keyword'] == ControlType.TRANSACTION:
            start_time = time.time()
            total_response_length = 0
            try:
                for children_step in step['children']:
                    total_response_length += run_locust_one_step(self, locust_client_mng, case_params, children_step,
                                                                 run_times)
                total_time = int((time.time() - start_time) * 1000)
                # 记录事务成功
                self.environment.events.request.fire(
                    request_type="TRANSACTION",
                    name=step['desc'],
                    response_time=total_time,
                    response_length=total_response_length,  # 使用实际响应大小
                    exception=None,
                    context={}
                )
            except Exception as e:
                total_time = int((time.time() - start_time) * 1000)
                self.environment.events.request.fire(
                    request_type="TRANSACTION",
                    name=step['desc'],
                    response_time=total_time,
                    response_length=total_response_length,  # 使用实际响应大小
                    exception=e,
                    context={}
                )

    else:
        # 获取步骤类型

        step_run_func: Callable = partial(step_type_function(step['type'], step['com_step_type']), locust_client_mng,
                                          step, case_params)
        return step_run_func(run_times, run_element)


def run_locust_case(self, steps, locust_client_mng, global_params_map, env_params_map):

    # 生成用例变量类用来存储环境变量,用例变量,测试步骤变量
    case_params = CaseParams(globalParams=global_params_map, envParams=env_params_map, caseParams={}, stepResponse={})

    set_user_params(case_params, [], faker_function_map)

    for step in steps:
        run_locust_one_step(self, locust_client_mng, case_params, step)