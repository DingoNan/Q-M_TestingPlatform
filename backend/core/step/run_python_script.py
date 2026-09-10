import re
from core.com.common import formatter_log
from apps.scripts.models import PythonScript
import core.com.faker as sys_function


def exec_and_return(manager_obj, script_code, case, formatter_log, case_params, sys_function):
    if script_code:
        python_func_objs, script_code = parse_user_function(script_code)
        session = manager_obj.session_manager
        selenium = manager_obj.driver_manager
        # 替换引用用例函数
        script_code = replace_run_one_case(script_code, manager_obj.env_id, manager_obj.user_id)
        # 延迟导入避免循环依赖，并注入 exec 命名空间供脚本调用 run_one_case
        from core.run_case import run_one_case
        if parse_user_function(script_code):
            for python_func_obj in python_func_objs:
                case_log = case.logs[-1]['logs']
                exec(python_func_obj.package)
                exec(python_func_obj.script, locals())
        case_log = case.logs[-1]['logs']
        exec(script_code, locals())


def run_python_script(manager_obj, env_id, step, case_params, case_logs_obj, run_times, run_element):
    step_id = step["case_step_id"]
    case_params.stepResponse[f'{step_id}']['runTimes'] = run_times
    case_params.stepResponse[f'{step_id}']['runElement'] = run_element
    step_script = step['script']
    setup_script = step['setup']
    teardown_script = step['teardown']
    exec_and_return(manager_obj, setup_script, case_logs_obj, formatter_log, case_params, sys_function)
    exec_and_return(manager_obj, step_script, case_logs_obj, formatter_log, case_params, sys_function)
    exec_and_return(manager_obj, teardown_script, case_logs_obj, formatter_log, case_params, sys_function)


def parse_user_function(python_script, pattern = r"user_function\.(\w+)\("):
    """
    解析用户自定义函数
    """
    matches = re.findall(pattern, python_script)
    python_func_obj = []
    if matches:
        python_script = python_script.replace('user_function.', '')
        for func in matches:
            python_func_obj.append(PythonScript.objects.all().get(name=func, is_delete=False))
    return python_func_obj, python_script


def replace_run_one_case(python_script, env_id, user_id):
    """
    将文本中的 run_one_case(数字) 替换为 run_one_case(env_id, 数字, user_id, 0, 0)

    Args:
        python_script: 要替换的原始python代码
        env_id: 环境ID（作为第一个参数）
        user_id: 用户ID（作为第三个参数）

    Returns:
        替换后的文本
    """
    # 正则模式：匹配 run_one_case(数字)
    pattern = r'run_one_case\s*\(\s*(\d+)\s*\)'

    # 替换函数
    def replacement(match):
        # 提取原始数字
        case_id = match.group(1)
        # 构建新格式
        return f'run_one_case({env_id}, {case_id}, {user_id}, 0, 0, return_user_params=True)'

    # 执行替换
    return re.sub(pattern, replacement, python_script)

