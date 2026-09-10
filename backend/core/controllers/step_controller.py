import time
from abc import ABC, abstractmethod
from core.com.common import formatter_log
from core.controllers.condition_control import is_run_step, get_loop_number, get_loop_element

class ControlType:
    IF = '1'  # IF 条件控制器
    FOR = '2'  # 循环控制器
    WHILE = '3'  # While 条件控制器
    TRANSACTION = '4'  # 事务控制器
    SLEEP = '5'  # 等待时间控制器
    FOREACH = '6'  # 循环遍历对象控制器


class BaseStepController(ABC):
    """
    步骤运行的逻辑控制器基类
    """
    @abstractmethod
    def execute(self, manager_obj, env_id, case_params, case_logs_obj, step, run_times, run_element, run_one_step):
        pass


class IfController(BaseStepController):

    def execute(self, manager_obj, env_id, case_params, case_logs_obj, step, run_times, run_element, run_one_step):
        if is_run_step(step['run_params'], case_params, case_logs_obj):
            for children_step in step['children']:
                run_one_step(manager_obj, env_id, case_params, case_logs_obj, children_step, run_times, run_element)


class ForLoopController(BaseStepController):
    def execute(self, manager_obj, env_id, case_params, case_logs_obj, step, run_times, run_element, run_one_step):
        for_run_times = get_loop_number(step, case_params, case_logs_obj)
        for run_index in range(for_run_times):
            case_params.stepResponse[f'{step["case_step_id"]}']['runTimes'] = run_times
            case_params.stepResponse[f'{step["case_step_id"]}']['runElement'] = run_element
            for children_step in step['children']:
                run_one_step(manager_obj, env_id, case_params, case_logs_obj, children_step, run_index, run_element)


class ForEachController(BaseStepController):
    def execute(self, manager_obj, env_id, case_params, case_logs_obj, step, run_times, run_element, run_one_step):
        loop_value = get_loop_element(step, case_params, case_logs_obj)
        if isinstance(loop_value, dict):
            for run_key, run_value in loop_value.items():
                case_params.stepResponse[f'{step["case_step_id"]}']['runTimes'] = run_key
                case_params.stepResponse[f'{step["case_step_id"]}']['runElement'] = run_value
                for children_step in step['children']:
                    run_one_step(manager_obj, env_id, case_params, case_logs_obj, children_step, run_key, run_value)

        else:
            for run_index, run_value in enumerate(loop_value):
                case_params.stepResponse[f'{step["case_step_id"]}']['runTimes'] = run_index
                case_params.stepResponse[f'{step["case_step_id"]}']['runElement'] = run_value
                for children_step in step['children']:
                    run_one_step(manager_obj, env_id, case_params, case_logs_obj, children_step, run_index,
                                 run_value)

class SleepController(BaseStepController):
    def execute(self, manager_obj, env_id, case_params, case_logs_obj, step, run_times, run_element, run_one_step):
        time.sleep(step['timeout'])
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '执行强制等待'),
                                               'value': f'等待时间-> {step["timeout"]}秒'})


class WhileController(BaseStepController):
    def execute(self, manager_obj, env_id, case_params, case_logs_obj, step, run_times, run_element, run_one_step):
        times = 0
        max_loop_times = int(step['until'][0]['max_loop_times'])
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '开始一直循环执行'),
                                               'value': f'最大循环次数->{max_loop_times}'})
        while is_run_step(step['until'], case_params, case_logs_obj, is_if=False):
            for children_step in step['children']:
                run_one_step(manager_obj, env_id, case_params, case_logs_obj, children_step, times, run_element)
            times = times + 1
            if times == max_loop_times:
                case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '退出一直循环执行'),
                                                       'value': '超过最大循环次数'})
                break

class TransactionController(BaseStepController):
    def execute(self, manager_obj, env_id, case_params, case_logs_obj, step, run_times, run_element, run_one_step):
        for children_step in step['children']:
            run_one_step(manager_obj, env_id, case_params, case_logs_obj, children_step, run_times, run_element)



# 注册所有控制器
CONTROLLER_REGISTRY = {
    ControlType.IF: IfController,
    ControlType.SLEEP: SleepController,
    ControlType.FOR: ForLoopController,
    ControlType.FOREACH: ForEachController,
    ControlType.WHILE: WhileController,
    ControlType.TRANSACTION: TransactionController

}
