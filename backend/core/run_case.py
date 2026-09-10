import time
import json
import re
import traceback
from typing import Callable
from requests import Session
from django.utils import timezone
from django.db import transaction

from core.step.run_sql import run_step_sql
import core.com.faker as sys_function
from core.com.step_model import StepResponse
from apps.projects.models import Project, ProjectMsgPush
from apps.tests.models import Step, CaseSteps
from apps.tests.serializers import RunCaseSerializer, StepSerializer
from core.com.faker import faker_function_map
from core.com.msg_push import send_dingtalk_message, send_feishu_message, send_test_report_email
from core.com.common import (
    formatter_log,
    set_user_params,
    set_case_data_params,
    get_env_params_by_env_id,
    replace_params_class_data,
    replace_all_func_value,
    single_replace_data,
    run_func_return_value,
)
from core.step.run_request import run_step_request
from core.step.run_user_customize_function import run_step_user_customize_function
from core.step.run_selenium import run_step_selenium
from core.step.run_playwright import run_step_playwright
from core.step.run_appium import run_step_appium
from core.com.step_model import CaseParams
from core.step.run_python_script import run_python_script
from core.controllers.step_controller import CONTROLLER_REGISTRY
from django_q.tasks import async_task, schedule
from django_q.models import Schedule
from functools import partial
from apps.suites.models import Suite, TestPlanFuncCase
from apps.messages.models import Message
from apps.tests.models import Case, Tag, CaseRunLog, FuncCase
from apps.envs.models import Env, EnvGlobalParams, GlobalParams, Module
from apps.reports.models import Report


class SuiteFilterMethod:
    ByCaseType = 1  # 按用例类型执行
    ByModule = 2  # 按用例所属模块执行
    ByTag = 3  # 按用例所属标签执行


class SessionDriverManage:
    def __init__(self, report_id, user_id, web_executor_id, app_executor_id, env_id):
        self.report_id = report_id
        self.user_id = user_id
        self.env_id = env_id
        self.session_manager = {}
        self.common_headers = {}
        self.driver_manager = {}
        self.web_executor_id = web_executor_id
        self.app_executor_id = app_executor_id

    def add_executor_ids(self, web_executor_id, app_executor_id):
        self.web_executor_id = web_executor_id
        self.app_executor_id = app_executor_id

    def add_session_manager(self, host):
        if host not in self.session_manager:
            self.session_manager[host] = Session()

    def add_common_headers(self, host, headers):
        self.common_headers.setdefault(host, {}).update(headers)

    def close_all(self):
        [session.close() for session in self.session_manager.values()]
        [driver_obj._quit() for driver_obj in self.driver_manager.values()]


class StepType:
    PlatformSystemFunction = -1  # 平台自带的系统函数
    UserCustomizeFunction = 1  # 用户自定义函数
    Request = 5  # request 类型的Api请求
    Selenium = 2  # selenium 类型的步骤
    Playwright = 10  # Playwright 类型的步骤
    Appium = 7  # Appium 类型的步骤
    ComStep = 3  # 用户定义的公共步骤
    UserCustomizeScript = 4  # 用户定义一次性脚本
    SQL = 8  # mysql和postgresql操作
    Control = 9  # 逻辑控制器


class ControlType:
    IF = '1'  # IF 条件控制器
    FOR = '2'  # 循环控制器
    WHILE = '3'  # While 条件控制器
    TRANSACTION = '4'  # 事务控制器
    SLEEP = '5'  # 等待时间控制器
    FOREACH = '6'  # 循环遍历对象控制器


success_case_filter = {
    'result': CaseRunLog.CaseResult.SUCCESS
}

fail_case_filter = {
    'result': CaseRunLog.CaseResult.FAIL
}

error_case_filter = {
    'result': CaseRunLog.CaseResult.ERROR
}

api_case_filter = {
    'case__type': Case.FunctionCaseType.API
}
web_ui_case_filter = {
    'case__type': Case.FunctionCaseType.WEB_UI
}

api_success_case_filter = api_case_filter | success_case_filter
api_fail_case_filter = api_case_filter | fail_case_filter
api_error_case_filter = api_case_filter | error_case_filter
ui_success_case_filter = web_ui_case_filter | success_case_filter
ui_fail_case_filter = web_ui_case_filter | fail_case_filter
ui_error_case_filter = web_ui_case_filter | error_case_filter


def get_cases_by_type(project_id, case_type):
    """
    通过用例类型获取用例ID集合
    """
    return set(
        Case.objects.all().filter(is_delete=False, project=project_id, type=case_type).values_list('id', flat=True))


def get_cases_by_module(project_id, value):
    """
    通过用例所属模块获取用例ID集合
    """
    return set(Case.objects.all().filter(project=project_id,
                                         module__in=value, is_delete=False).values_list('id', flat=True))


def get_func_cases_by_module(project_id, value):
    """
    通过用例所属模块获取用例ID集合
    """
    return set(FuncCase.objects.all().filter(project=project_id,
                                             module__in=value, is_delete=False).values_list('id', flat=True))


def get_cases_by_tag(project_id, value: list):
    """
    通过用例标签获取用例ID集合
    """
    case_dat = set()
    for tag_value in value:
        tmp_set = Tag.objects.all().get(
            project=project_id, id=tag_value).case_set.all().filter(is_delete=False).values_list('id', flat=True)
        case_dat = case_dat.union(tmp_set)
    return case_dat


def get_func_cases_by_tag(project_id, value: list):
    """
    通过用例标签获取用例ID集合
    """
    case_dat = set()
    for tag_value in value:
        tmp_set = Tag.objects.all().get(
            project=project_id, id=tag_value).funccase_set.all().filter(is_delete=False).values_list('id', flat=True)
        case_dat = case_dat.union(tmp_set)
    return case_dat


GetCasesFilterMap = {
    SuiteFilterMethod.ByCaseType: get_cases_by_type,
    SuiteFilterMethod.ByModule: get_cases_by_module,
    SuiteFilterMethod.ByTag: get_cases_by_tag
}

GetFuncCasesFilterMap = {
    SuiteFilterMethod.ByModule: get_func_cases_by_module,
    SuiteFilterMethod.ByTag: get_func_cases_by_tag
}


def get_plan_cases(plan_obj):
    """
    获取测试计划下所有的功能用例ID和数量
    """
    all_case_number = plan_obj.func_cases.filter(is_delete=False).count()
    all_func_cases = plan_obj.func_cases.filter(is_delete=False).values_list('id', flat=True)
    return all_case_number, all_func_cases


def get_suite_cases(suite_obj):
    """
    获取套件下所有的用例ID
    """
    project_id = suite_obj.project

    # 按脚本用例,动态模式收集用例
    if suite_obj.plant_type == Suite.PlanType.AUTO and suite_obj.plant_model == Suite.PlanModel.Dynamic:
        all_cases = GetCasesFilterMap.get(SuiteFilterMethod.ByCaseType)(project_id, suite_obj.auto_type)
        if suite_obj.dynamic_conditions:
            cases = set()
            for index, suite_condition_obj in enumerate(suite_obj.dynamic_conditions):
                method, value = suite_condition_obj['method'], suite_condition_obj['value']
                sub_cases = GetCasesFilterMap.get(method)(project_id, value)
                if index == 0:
                    cases = cases.union(sub_cases)
                else:
                    cases = cases.intersection(sub_cases) if suite_obj.conditions[index - 1][
                                                                 'andOr'] == 'And' else cases.union(sub_cases)

            return list(all_cases.intersection(cases))

        else:
            return list(all_cases)

    # 按脚本用例,静态模式收集用例
    elif suite_obj.plant_type == Suite.PlanType.AUTO and suite_obj.plant_model == Suite.PlanModel.STATIC:
        return suite_obj.auto_cases.values_list('id', flat=True)

    # 按功能用例,动态模式收集用例
    elif suite_obj.plant_type == Suite.PlanType.FUNCTION and suite_obj.plant_model == Suite.PlanModel.Dynamic:
        all_cases = set()
        if suite_obj.dynamic_conditions:
            cases = set()
            for index, suite_condition_obj in enumerate(suite_obj.dynamic_conditions):
                method, value = suite_condition_obj['method'], suite_condition_obj['value']
                sub_cases = GetFuncCasesFilterMap.get(method)(project_id, value)
                if index == 0:
                    cases = cases.union(sub_cases)
                else:
                    cases = cases.intersection(sub_cases) if suite_obj.conditions[index - 1][
                                                                 'andOr'] == 'And' else cases.union(sub_cases)
            all_func_cases = list(cases)
            return len(all_func_cases), all_func_cases

        else:
            return len(list(all_cases)), list(all_cases)

    # 按功能用例,静态模式收集用例
    else:
        all_case_number = suite_obj.func_cases.count()
        all_func_cases = suite_obj.func_cases.values_list('id', flat=True)
        return all_case_number, all_func_cases


def get_case_number(report_obj, **kwargs):
    # CaseRunLog.objects.filter(report=report_obj, **kwargs).values_list('case', 'case_name').distinct().count()
    return CaseRunLog.objects.filter(report=report_obj, **kwargs).values_list('case_id', 'case_name').distinct().count()


def get_module_case_number(report_obj, module_id, **kwargs):
    # CaseRunLog.objects.filter(report=report_obj,
    #                           case__module=module_id, **kwargs).values_list('case', 'case_name').distinct().count()
    return CaseRunLog.objects.filter(report=report_obj, case__module=module_id, **kwargs).values_list('case_id',
                                                                                                      'case_name').distinct().count()


def get_tag_case_number(report_obj, tag_id, **kwargs):
    """统计指定标签的用例数量（先获取关联该标签的所有case_id，再统计）"""
    from apps.tests.models import Case
    case_ids = list(Case.objects.filter(tag=tag_id).values_list('id', flat=True))
    return CaseRunLog.objects.filter(report=report_obj, case_id__in=case_ids, **kwargs).values_list('case_id',
                                                                                                    'case_name').distinct().count()


step_type_map = {
    StepType.Request: run_step_request,
    StepType.UserCustomizeFunction: run_step_user_customize_function,
    StepType.Selenium: run_step_selenium,
    StepType.Playwright: run_step_playwright,
    StepType.Appium: run_step_appium,
    StepType.UserCustomizeScript: run_python_script,
    StepType.ComStep: False,
    StepType.SQL: run_step_sql,
}


def step_type_function(step_type, com_step_type):
    if step_type == StepType.ComStep:
        return step_type_map.get(com_step_type)
    else:
        return step_type_map.get(step_type)


def run_one_step(manager_obj, env_id, case_params, case_logs_obj, step, run_times=0, run_element=None):
    """
    执行一个测试步骤
    """
    step_response = StepResponse(apiUrl=None, apiHost=None, apiUri=None, apiMethod=None, stepParams={},
                                 apiRequestHeaders={}, apiRequestParams={}, apiRequestBody={},
                                 apiStatusCode=None, apiResponseHeaders={}, apiResponseCookies={},
                                 apiResponseBody={}, funcReturn=None, funcParams=None, runTimes=0, runElement=None)
    case_params.stepResponse[f'{step["case_step_id"]}'] = step_response.__dict__
    case_logs_obj.logs.append({'step_desc': f'Step{step["step_index"] + 1} -> ' + step['desc'], 'logs': [],
                               'case_step_id': step['case_step_id'], 'step_index': step['step_index']})
    set_step_params(case_params, case_logs_obj, step, faker_function_map)

    # 判断是否执行该步骤
    if not step['is_run']:
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '该步骤已跳过'), 'value': '该步骤已设置为不执行'})
        return None
    # 判断该步骤是否是逻辑控制器
    if step['type'] == StepType.Control or step['com_step_type'] == StepType.Control:
        controller_obj = CONTROLLER_REGISTRY.get(step['keyword'])()
        controller_obj.execute(manager_obj, env_id, case_params, case_logs_obj, step, run_times, run_element, run_one_step)

    else:
        # 获取步骤类型
        step_run_func: Callable = partial(step_type_function(step['type'], step['com_step_type']), manager_obj, env_id,
                                          step, case_params, case_logs_obj)
        step_run_func(run_times, run_element)


def run_one_case(env_id: int, case_id: int, user_id: int, web_executor_id, app_executor_id, report_id=0, rerun_times=0,
                 func_case_id=None, fail_is_continue=0, case_data=None, is_retry=False, plan_id=0, step_index=None, return_user_params=False):
    """
    执行一条测试用例
    env_id: 执行测试用例的环境
    case_id: 执行测试用例用例ID
    user_id: 触发执行用例的用户
    report_id: 单个用例执行不会生成report_id=0
    """
    case = Case.objects.all().get(id=case_id)
    case_logs_obj = None
    project_id = case.project
    results = []
    if case_data is None:
        if case.data and 'value' in case.data and case.data['value']:
            case_data = case.data['value']
        else:
            case_data = [{}]
    for index, one_case_data in enumerate(case_data):
        run_start_time = time.time()
        # 管理不同微服务的接口Session和浏览器Driver对象
        manager_obj = SessionDriverManage(report_id, user_id, web_executor_id, app_executor_id, env_id)
        # manager_obj.add_executor_ids(web_executor_id, app_executor_id)

        # 用例执行情况和日志记录
        result = CaseRunLog.CaseResult.SUCCESS
        report_obj = Report.objects.get(id=report_id) if report_id else None
        case_name = one_case_data.get("_name_") if one_case_data else case.name
        case_log_info = []
        case_logs_obj = CaseRunLog(case_id=case_id, env=Env.objects.get(id=env_id), logs=case_log_info, result=result,
                                   time=0, create_by_id=user_id, update_by_id=user_id, report=report_obj,
                                   func_case_id=func_case_id, case_name=case_name, plan_id=plan_id if plan_id else None)
        save_test_log(run_start_time, case_logs_obj)

        # 生成用例变量类用来存储环境变量,用例变量,测试步骤变量
        case_params = CaseParams(globalParams={}, envParams={}, caseParams={}, stepResponse={}, caseData=one_case_data)

        # 为用例变量添加环境全局变量
        case_logs_obj.logs.append({'step_desc': 'Setup -> 加载全局变量', 'logs': []})
        global_params_set = GlobalParams.objects.all().filter(project=project_id, is_delete=False)
        if global_params_set:
            for global_params_obj in global_params_set:
                case_params.globalParams[global_params_obj.name] = global_params_obj.value
            global_params = json.dumps(case_params.globalParams, indent=4, ensure_ascii=False)
            case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '加载全局变量'), 'value': global_params})
        else:
            case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '加载全局变量'), 'value': None})
        env_query_set = get_env_params_by_env_id(env_id, project_id)
        if env_query_set:
            for env_params_obj in env_query_set:
                case_params.envParams[env_params_obj.name] = env_params_obj.value
            env_params = json.dumps(case_params.envParams, indent=4, ensure_ascii=False)
            case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '加载环境变量'), 'value': env_params})
        else:
            case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '加载环境变量'), 'value': None})

        # 设置用例全局变量
        try:
            set_user_params(case_params, case_logs_obj, case.params, faker_function_map)
        except Exception as e:
            _e = traceback.format_exc()
            case_logs_obj.result = CaseRunLog.CaseResult.ERROR
            case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('ERROR', e.__doc__), 'value': _e})
            save_test_log(run_start_time, case_logs_obj)
            manager_obj.close_all()
            return case, case_logs_obj

        set_case_data_params(case_params, case_logs_obj, faker_function_map)
        case_data = json.dumps(case_params.caseData, indent=4, ensure_ascii=False)
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '加载测试数据集'), 'value': case_data})

        # 根据用例ID获取用例步骤
        steps = get_run_step_data(case)
        steps = build_tree(steps)

        for step in steps:
            try:
                # 用例中单个步骤调试的时候只执行步骤ID一样的
                if step_index is None:
                    run_one_step(manager_obj, env_id, case_params, case_logs_obj, step)
                elif step_index == step['step_index']:
                    run_one_step(manager_obj, env_id, case_params, case_logs_obj, step)
                else:
                    continue
            except Exception as e:
                _e = traceback.format_exc()
                if type(e) == AssertionError:
                    case_logs_obj.result = CaseRunLog.CaseResult.FAIL
                else:
                    case_logs_obj.result = CaseRunLog.CaseResult.ERROR
                case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('ERROR', e.__doc__), 'value': _e})
            finally:
                # 判断步骤是否继续执行还是停止
                if case_logs_obj.result != CaseRunLog.CaseResult.SUCCESS:
                    _fail_is_continue = step['fail_is_continue'] if report_id else fail_is_continue
                    if _fail_is_continue == CaseSteps.IsContinue.Stop:
                        break
                    elif _fail_is_continue == CaseSteps.IsContinue.Continue:
                        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '不忽略失败并继续执行'),
                                                               'value': '步骤执行失败不忽略失败继续执行'})
                    else:
                        case_logs_obj.result = CaseRunLog.CaseResult.SUCCESS
                        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '忽略失败并继续执行'),
                                                               'value': '步骤执行失败忽略失败继续执行'})
        manager_obj.close_all()
        case.recent_test_result = case_logs_obj.result
        save_test_log(run_start_time, case_logs_obj)
        case.save()
        results.append(case_logs_obj.result)
        if report_id:
            # 脚本用例失败时进行重试
            if case_logs_obj.result != CaseRunLog.CaseResult.SUCCESS:
                for i in range(rerun_times):
                    result = run_one_case(env_id, case_id, user_id, web_executor_id, app_executor_id,
                                          case_data=[one_case_data], report_id=report_id, rerun_times=0,
                                          func_case_id=func_case_id, fail_is_continue=0, is_retry=True,
                                          plan_id=plan_id)
                    results[-1] = result[0]
                    if result[0] == CaseRunLog.CaseResult.SUCCESS:
                        break

            # 按脚本用例执行时，每个脚本用例执行完后更新进度（包括重试后的结果）
            if not func_case_id and not is_retry:
                with transaction.atomic():
                    report_obj = Report.objects.filter(id=report_id).select_for_update().first()
                    if case_logs_obj.result == CaseRunLog.CaseResult.SUCCESS:
                        report_obj.success_case_number += 1
                    elif case_logs_obj.result == CaseRunLog.CaseResult.FAIL:
                        report_obj.fail_case_number += 1
                    else:
                        report_obj.error_case_number += 1
                    report_obj.save(update_fields=['success_case_number', 'fail_case_number', 'error_case_number', 'update_time'])
    if return_user_params:
        return case_params.caseParams
    else:
        return results if report_id else case_logs_obj.id


def get_run_step_data(case):
    """
    获取平级的执行步骤数据
    """
    case_data = RunCaseSerializer(case).data
    case_data['step'] = []
    case_step_set = CaseSteps.objects.filter(case_id=case_data['id'], is_delete=False).order_by('step_index')
    for case_step_obj in case_step_set:
        step_map = {'step_index': case_step_obj.step_index, 'step_params': case_step_obj.step_params,
                    'case_step_id': case_step_obj.id, 'parent_id': case_step_obj.parent_id, 'children': [],
                    'is_run': case_step_obj.is_run, 'fail_is_continue': case_step_obj.fail_is_continue}
        step_set = Step.objects.filter(id=case_step_obj.step_id, is_delete=False)
        if not step_set.exists():
            continue
        step_map.update(StepSerializer(step_set[0]).data)
        case_data['step'].append(step_map)
    return case_data['step']


def build_tree(data, id_key='case_step_id', parent_key='parent_id', children_key='children'):
    """
    将平级数据结构转换为多层树形结构

    参数:
        data: 列表，包含字典元素
        id_key: 节点ID的键名 (默认为 'id')
        parent_key: 父节点ID的键名 (默认为 'parent_id')
        children_key: 子节点列表的键名 (默认为 'children')

    返回:
        树形结构列表（森林），只包含根节点
    """
    # 创建节点字典和根节点列表
    nodes = {item[id_key]: item.copy() for item in data}
    roots = []

    # 构建树结构
    for item_id, node in nodes.items():
        parent_id = node.get(parent_key)

        # 根节点直接添加到结果
        if parent_id is None:
            roots.append(node)
        else:
            # 找到父节点并添加当前节点到其子节点列表
            parent = nodes.get(parent_id)
            if parent:
                # 初始化父节点的children列表（如果不存在）
                if children_key not in parent:
                    parent[children_key] = []
                parent[children_key].append(node)

    return roots


def save_test_log(run_start_time, case_logs_obj):
    """
    保存一条测试记录
    """
    cost_time = time.time() - run_start_time
    case_logs_obj.time = cost_time
    case_logs_obj.save()


def set_step_params(case_params: CaseParams, case_logs_obj, step, inner_funcs, f_pattern=r'f{.*?}'):
    """
    设置步骤变量
    """
    step_index = step['step_index']
    if step['step_params']:
        for params_obj in step['step_params']:
            params_key = params_obj['name']
            params_value = params_obj['value']
            params_value = single_replace_data(case_params, case_logs_obj, params_value)
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
        step_params = json.dumps(case_params.stepResponse[f'{step["case_step_id"]}']["stepParams"], indent=4, ensure_ascii=False)
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '设置步骤变量'), 'value': step_params})
    else:
        case_logs_obj.logs[-1]['logs'].append({'title': formatter_log('INFO', '设置步骤变量'), 'value': None})

    # 替换步骤描述
    replace_request_data = partial(replace_params_class_data, case_params, case_logs_obj)
    desc = replace_request_data(step['desc'])
    step['desc'] = replace_all_func_value(faker_function_map, desc)
    case_logs_obj.logs[-1]['step_desc'] = f'step{step["step_index"] + 1} -> {step["desc"]}'


def update_env_params_info(env_id, params_name, params_value):
    params_obj = EnvGlobalParams.objects.get(env=env_id, name=params_name, is_delete=False)
    params_obj.value = params_value
    params_obj.save()


def run_env_script(script, update_env_params_info, sys_function):
    if script:
        exec(script, locals())


def run_task_suite_async(env_id, user_id, suite_id):

    suite_obj = Suite.objects.get(id=suite_id)
    env_obj = Env.objects.get(id=env_id)

    web_executor_id = suite_obj.web_executor.id if suite_obj.web_executor else 0
    app_executor_id = suite_obj.app_executor.id if suite_obj.app_executor else 0
    rerun_times = suite_obj.rerun_times

    if suite_obj.plant_type == Suite.PlanType.AUTO:
        cases = get_suite_cases(suite_obj)
        all_case_num = get_all_case_num(cases)

    else:
        all_case_num, cases = get_suite_cases(suite_obj)

    if env_obj.setup:
        run_env_script(env_obj.setup, partial(update_env_params_info, env_id), sys_function)

    report_obj = Report.objects.create(
        name=suite_obj.name,
        project=suite_obj.project,
        create_by_id=user_id,
        update_by_id=user_id,
        env=env_obj,
        suite=suite_obj,
        detail={
            'plant_filter': [],
            'tag_filter': [],
            'module_filter': [],
            'module': {},
            'tag': {}
        },
        all_case_number=all_case_num
    )

    async_task(
        'core.run_case.run_suite_async',
        env_id=env_id, user_id=user_id,
        report_id=report_obj.id,
        web_executor_id=web_executor_id, app_executor_id=app_executor_id,
        rerun_times=rerun_times,
        cases=list(cases),
        plant_type=suite_obj.plant_type
    )


def run_suite_async(env_id, user_id, report_id, web_executor_id, app_executor_id, rerun_times, cases, plant_type, run_msg_id=0):

    if plant_type == Suite.PlanType.AUTO:
        for case_id in cases:
            task_id = async_task(
                'core.run_case.run_one_case',
                env_id=env_id, case_id=case_id, user_id=user_id,
                web_executor_id=web_executor_id, app_executor_id=app_executor_id,
                report_id=report_id, rerun_times=rerun_times, func_case_id=None,
                fail_is_continue=0,
            )

        schedule(
            'core.run_case.check_suite_completion',
            report_id, True, run_msg_id,
            schedule_type=Schedule.ONCE,
            next_run=timezone.now() + timezone.timedelta(seconds=2)
        )
    else:
        for func_case_id in cases:
            task_id = async_task(
                'core.run_case.func_group_run',
                env_id=env_id, user_id=user_id,
                web_executor_id=web_executor_id, app_executor_id=app_executor_id,
                report_id=report_id, func_case_id=func_case_id,
                rerun_times=rerun_times, set_result=False, plan_id=0,
            )

        schedule(
            'core.run_case.check_suite_completion',
            report_id, False, run_msg_id,
            schedule_type=Schedule.ONCE,
            next_run=timezone.now() + timezone.timedelta(seconds=2)
        )


def check_suite_completion(report_id, is_auto, run_msg_id=0):
    print(f'[check_suite_completion] 开始检查报告 {report_id}')
    
    report_obj = Report.objects.filter(id=report_id).first()
    
    completed_count = report_obj.success_case_number + report_obj.error_case_number + report_obj.fail_case_number
    
    print(f'[check_suite_completion] 报告 {report_id}: 已完成={completed_count}, 总数={report_obj.all_case_number}')

    if completed_count >= report_obj.all_case_number:
        print(f'[check_suite_completion] 所有用例已完成，开始执行 finalize_suite')
        finalize_suite(report_id, is_auto, run_msg_id)
    else:
        print(f'[check_suite_completion] 用例未完成，2秒后继续检查')
        schedule(
            'core.run_case.check_suite_completion',
            report_id, is_auto, run_msg_id,
            schedule_type=Schedule.ONCE,
            next_run=timezone.now() + timezone.timedelta(seconds=2)
        )


def finalize_suite(report_id, is_auto=True, run_msg_id=0):

    report_obj = Report.objects.get(id=report_id)
    env_obj = report_obj.env
    suite_obj = report_obj.suite
    
    if env_obj.teardown:
        print(f'[finalize_suite] 执行环境 teardown 脚本')
        run_env_script(env_obj.teardown, partial(update_env_params_info, env_obj.id), sys_function)
    else:
        print(f'[finalize_suite] 无 teardown 脚本，跳过')

    if is_auto:
        print(f'[finalize_suite] 执行脚本用例统计')
        calculate_case_statistics(report_id)
    else:
        print(f'[finalize_suite] 执行功能用例统计')
        calculate_func_case_statistics(report_id)

    # 站内信 + WebSocket：更新"执行中"消息为完成状态，没有就新建
    try:
        _update_run_completion_message(env_obj, report_obj, run_msg_id)
    except Exception as exc:
        print(f'[finalize_suite] 站内信更新/创建失败: {exc}')

    # 外部推送（飞书/钉钉）仅在 Suite 且启用时推送
    if suite_obj and suite_obj.push_msg:
        print(f'[finalize_suite] 发送外部消息推送')
        _push_external_msg(env_obj, report_obj)
    else:
        print(f'[finalize_suite] 无需发送外部消息推送')


def _update_run_completion_message(env_obj, report_obj, run_msg_id=0):
    """更新"执行中"消息为完成状态；若没有则新建"""
    from apps.messages.models import Message
    from apps.messages.push import push_message_to_user, build_message_payload
    from apps.projects.models import Project

    project_obj = Project.objects.get(id=env_obj.project.id)

    case_all = report_obj.all_case_number
    case_pass = report_obj.success_case_number
    case_fail = report_obj.fail_case_number + report_obj.error_case_number
    success = case_fail == 0

    duration = (report_obj.update_time - report_obj.create_time).total_seconds()
    related_url = f'/report/listView?id={report_obj.id}'

    if report_obj.plan_id:
        title = '测试计划执行完成'
    elif report_obj.suite_id:
        title = '套件执行完成'
    else:
        title = '脚本用例批跑执行完成'
    content = f'{report_obj.name} | 成功 {case_pass}，失败 {case_fail}'

    if run_msg_id and run_msg_id > 0:
        updated = Message.objects.filter(id=run_msg_id).update(
            title=title, content=content,
            task_status=Message.TaskStatus.SUCCESS if success else Message.TaskStatus.FAILED,
            total_count=case_all, success_count=case_pass, failed_count=case_fail,
            duration=duration, related_url=related_url,
            is_read=False, read_time=None, update_time=timezone.now(),
        )
        if updated:
            # update() 不触发 post_save 信号，手动推送 WebSocket
            msg = Message.objects.get(id=run_msg_id)
            push_message_to_user(msg.user_id, build_message_payload(msg))
            print(f'[finalize_suite] 已更新并推送站内信 id={run_msg_id}')
            return

    # 没有 run_msg_id 或更新失败，新建（create 会触发 post_save 信号自动推送）
    msg_obj = Message.objects.create(
        user=report_obj.create_by, project=project_obj,
        title=title, content=content,
        message_type=Message.MessageType.TASK,
        task_status=Message.TaskStatus.SUCCESS if success else Message.TaskStatus.FAILED,
        total_count=case_all, success_count=case_pass, failed_count=case_fail,
        duration=duration, related_url=related_url,
        create_by=report_obj.create_by, update_by=report_obj.create_by,
    )
    print(f'[finalize_suite] 新建站内信 id={msg_obj.id}')


def _push_external_msg(env_obj, report_obj):
    """飞书/钉钉外部推送"""
    from apps.messages.models import ProjectMsgPush
    from core.com.msg_push import send_dingtalk_message, send_feishu_message
    from apps.projects.models import Project

    project_obj = Project.objects.get(id=env_obj.project.id)
    report_url = f"http://127.0.0.1:8080/#/report/listView?id={report_obj.id}"

    case_all = report_obj.all_case_number
    case_pass = report_obj.success_case_number
    case_fail = report_obj.fail_case_number + report_obj.error_case_number
    case_rate = case_pass / case_all if case_all > 0 else 0

    for config in ProjectMsgPush.objects.filter(project=project_obj, is_active=True):
        try:
            if config.push_type == ProjectMsgPush.PushType.FeiShu:
                send_feishu_message(
                    webhook_url=config.webhook_url,
                    report_url=report_url,
                    project_name=project_obj.name,
                    env_name=env_obj.name,
                    case_rate=case_rate,
                    case_all=case_all,
                    case_pass=case_pass,
                    case_fail=case_fail,
                    report_title=report_obj.name,
                    start_time=report_obj.create_time,
                    end_time=report_obj.update_time,
                    secret=config.email_password if config.email_password else None
                )
            elif config.push_type == ProjectMsgPush.PushType.DingDing:
                send_dingtalk_message(
                    webhook_url=config.webhook_url,
                    report_url=report_url,
                    project_name=project_obj.name,
                    env_name=env_obj.name,
                    case_rate=case_rate,
                    case_all=case_all,
                    case_pass=case_pass,
                    case_fail=case_fail,
                    report_title=report_obj.name,
                    start_time=report_obj.create_time,
                    end_time=report_obj.update_time,
                    secret=config.email_password if config.email_password else None
                )
        except Exception as exc:
            print(f'[finalize_suite] 外部推送失败: {exc}')

def get_module_func_case_number(report_obj, module_id, **kwargs):
    """统计指定模块的功能用例数量（按func_case去重）"""
    queryset = CaseRunLog.objects.filter(report=report_obj, func_case__isnull=False, func_case__module=module_id, **kwargs)
    result = queryset.values_list('func_case_id').distinct().count()
    return result


def get_tag_func_case_number(report_obj, tag_id, **kwargs):
    """统计指定标签的功能用例数量（先获取关联该标签的所有func_case_id，再统计）"""
    from apps.tests.models import FuncCase
    func_case_ids = list(FuncCase.objects.filter(tag=tag_id).values_list('id', flat=True))
    return CaseRunLog.objects.filter(report=report_obj, func_case__isnull=False, func_case_id__in=func_case_ids,
                                     **kwargs).values_list('func_case_id').distinct().count()


def calculate_case_statistics(report_id):
    """
    基于CaseRunLog实时统计脚本用例的模块和标签计数
    """
    report_obj = Report.objects.filter(id=report_id).first()

    detail = report_obj.detail
    detail.setdefault('module_filter', [])
    detail.setdefault('plant_filter', [])
    detail.setdefault('tag_filter', [])
    detail.setdefault('module', {})
    detail.setdefault('tag', {})

    # 从CaseRunLog中获取所有执行过的case_id
    case_ids = list(set(CaseRunLog.objects.filter(report=report_obj).values_list('case_id', flat=True)))

    module_ids = list(set(Case.objects.filter(id__in=case_ids).values_list('module_id', flat=True)))

    # 统计每个模块的计数
    for module_id in module_ids:
        module_obj = Module.objects.filter(id=module_id).first()
        if module_obj:
            case_plant_name = module_obj.plant.name
            case_module_name = module_obj.name
            plant_module = case_plant_name + '_' + case_module_name
            module_filter_obj = {'text': plant_module, 'value': module_id}
            plant_filter_obj = {'text': case_plant_name, 'value': module_obj.plant.id}

            if module_filter_obj not in detail['module_filter']:
                detail['module_filter'].append(module_filter_obj)
            if plant_filter_obj not in detail['plant_filter']:
                detail['plant_filter'].append(plant_filter_obj)

            detail['module'][module_id] = {
                'plant_name': case_plant_name,
                'module_name': case_module_name,
                'all_case_number': get_module_case_number(report_obj, module_id),
                'success_number': get_module_case_number(report_obj, module_id, **success_case_filter),
                'fail_number': get_module_case_number(report_obj, module_id, **fail_case_filter),
                'error_number': get_module_case_number(report_obj, module_id, **error_case_filter)
            }
    
    # 获取这些用例关联的所有标签
    tag_ids = list(set(Case.objects.filter(id__in=case_ids).values_list('tag', flat=True)))
    tag_ids = [tid for tid in tag_ids if tid is not None]

    # 统计每个标签的计数
    for tag_id in tag_ids:
        tag_obj = Tag.objects.filter(id=tag_id).first()
        if tag_obj:
            tag_filter_obj = {'text': tag_obj.name, 'value': tag_id}
            if tag_filter_obj not in detail['tag_filter']:
                detail['tag_filter'].append(tag_filter_obj)

            detail['tag'][tag_id] = {
                'name': tag_obj.name,
                'all_case_number': get_tag_case_number(report_obj, tag_id),
                'success_number': get_tag_case_number(report_obj, tag_id, **success_case_filter),
                'fail_number': get_tag_case_number(report_obj, tag_id, **fail_case_filter),
                'error_number': get_tag_case_number(report_obj, tag_id, **error_case_filter)
            }

    report_obj.detail = detail
    report_obj.success_case_number = get_case_number(report_obj, **success_case_filter)
    report_obj.fail_case_number = get_case_number(report_obj, **fail_case_filter)
    report_obj.error_case_number = get_case_number(report_obj, **error_case_filter)
    report_obj.save()


def calculate_func_case_statistics(report_id):
    """
    基于CaseRunLog实时统计功能用例的模块和标签计数
    """
    report_obj = Report.objects.filter(id=report_id).first()

    detail = report_obj.detail
    detail.setdefault('module_filter', [])
    detail.setdefault('plant_filter', [])
    detail.setdefault('tag_filter', [])
    detail.setdefault('module', {})
    detail.setdefault('tag', {})
    
    # 先查看CaseRunLog的原始数据
    all_logs = CaseRunLog.objects.filter(report=report_obj, func_case__isnull=False)
    
    # 使用set去重，确保func_case_id唯一
    func_case_ids = list(set(all_logs.values_list('func_case_id', flat=True)))

    module_ids = list(set(FuncCase.objects.filter(id__in=func_case_ids).values_list('module_id', flat=True)))

    # 统计每个模块的功能用例计数
    for module_id in module_ids:
        module_obj = Module.objects.filter(id=module_id).first()
        if module_obj:
            case_plant_name = module_obj.plant.name
            case_module_name = module_obj.name
            plant_module = case_plant_name + '_' + case_module_name
            module_filter_obj = {'text': plant_module, 'value': module_id}
            plant_filter_obj = {'text': case_plant_name, 'value': module_obj.plant.id}

            if module_filter_obj not in detail['module_filter']:
                detail['module_filter'].append(module_filter_obj)
            if plant_filter_obj not in detail['plant_filter']:
                detail['plant_filter'].append(plant_filter_obj)

            detail['module'][module_id] = {
                'plant_name': case_plant_name,
                'module_name': case_module_name,
                'all_case_number': get_module_func_case_number(report_obj, module_id),
                'success_number': get_module_func_case_number(report_obj, module_id, **success_case_filter),
                'fail_number': get_module_func_case_number(report_obj, module_id, **fail_case_filter),
                'error_number': get_module_func_case_number(report_obj, module_id, **error_case_filter)
            }

    # 获取这些功能用例关联的所有标签
    tag_ids = list(set(FuncCase.objects.filter(id__in=func_case_ids).values_list('tag__id', flat=True)))
    tag_ids = [tid for tid in tag_ids if tid is not None]

    # 统计每个标签的功能用例计数
    for tag_id in tag_ids:
        tag_obj = Tag.objects.filter(id=tag_id).first()
        if tag_obj:
            tag_filter_obj = {'text': tag_obj.name, 'value': tag_id}
            if tag_filter_obj not in detail['tag_filter']:
                detail['tag_filter'].append(tag_filter_obj)

            detail['tag'][tag_id] = {
                'name': tag_obj.name,
                'all_case_number': get_tag_func_case_number(report_obj, tag_id),
                'success_number': get_tag_func_case_number(report_obj, tag_id, **success_case_filter),
                'fail_number': get_tag_func_case_number(report_obj, tag_id, **fail_case_filter),
                'error_number': get_tag_func_case_number(report_obj, tag_id, **error_case_filter)
            }

    report_obj.detail = detail
    report_obj.save()


def run_test_plan(env_id, test_plan_id, user_id, func_case_ids, report_id, web_executor_id=0, app_executor_id=0, run_msg_id=0):
    for func_case_id in func_case_ids:
        task_id = async_task(
            'core.run_case.func_group_run',
            env_id=env_id, user_id=user_id,
            web_executor_id=web_executor_id, app_executor_id=app_executor_id,
            report_id=report_id, func_case_id=func_case_id,
            rerun_times=0, set_result=True, plan_id=test_plan_id,
        )
    # 有报告ID 说明是执行整个测试计划
    if report_id:
        schedule(
            'core.run_case.check_suite_completion',
            report_id, False, run_msg_id,
            schedule_type=Schedule.ONCE,
            next_run=timezone.now() + timezone.timedelta(seconds=2)
        )


def get_all_case_num(cases):
    all_case_num = 0
    for case_id in cases:
        case_obj = Case.objects.get(id=case_id)
        if case_obj.data and case_obj.data.get('value'):
            all_case_num = all_case_num + len(case_obj.data.get('value'))
        else:
            all_case_num = all_case_num + 1
    return all_case_num


def split_list_by_groups_itertools(lst, n):
    """使用轮询方式分配元素到各组"""
    groups = [[] for _ in range(n)]

    for i, item in enumerate(lst):
        groups[i % n].append(item)

    return groups


def update_func_case_statistics(report_id, module_id, tag_ids, case_plant_name, case_module_name,
                                module_filter_obj, plant_filter_obj, is_success):
    """
    更新功能用例的过滤器信息（不更新计数，计数基于CaseRunLog实时统计）
    """
    with transaction.atomic():
        report_obj = Report.objects.filter(id=report_id).select_for_update().first()
        if not report_obj:
            return

        detail = report_obj.detail

        # 只更新过滤器信息，不更新计数
        detail.setdefault('module_filter', [])
        detail.setdefault('plant_filter', [])
        detail.setdefault('tag_filter', [])
        detail.setdefault('module', {})
        detail.setdefault('tag', {})

        # 更新模块过滤器
        if module_filter_obj not in detail['module_filter']:
            detail['module_filter'].append(module_filter_obj)

        if plant_filter_obj not in detail['plant_filter']:
            detail['plant_filter'].append(plant_filter_obj)

        # 更新模块基本信息（不更新计数）
        detail['module'].setdefault(module_id, {})
        detail['module'][module_id]['plant_name'] = case_plant_name
        detail['module'][module_id]['module_name'] = case_module_name

        # 更新标签过滤器和标签基本信息
        for tag_id in tag_ids:
            try:
                tag_obj = Tag.objects.get(id=tag_id)
                tag_name = tag_obj.name
            except:
                tag_name = f"tag_{tag_id}"

            tag_filter_obj = {'text': tag_name, 'value': tag_id}
            if tag_filter_obj not in detail['tag_filter']:
                detail['tag_filter'].append(tag_filter_obj)

            detail['tag'].setdefault(tag_id, {})
            detail['tag'][tag_id]['name'] = tag_name

        # 保存过滤器信息
        report_obj.detail = detail
        report_obj.save(update_fields=['detail'])


def func_group_run(env_id, user_id, report_id, func_case_id, web_executor_id, app_executor_id, rerun_times,
                   set_result=False, plan_id=0):
    func_case_obj = FuncCase.objects.all().get(id=func_case_id)
    auto_cases = list(func_case_obj.case.values_list('id', flat=True))
    results = []
    for auto_case_id in auto_cases:
        result = run_one_case(env_id=env_id, case_id=auto_case_id, user_id=user_id, web_executor_id=web_executor_id,
                              app_executor_id=app_executor_id, report_id=report_id, rerun_times=rerun_times,
                              func_case_id=func_case_id, fail_is_continue=0, plan_id=plan_id)
        results = results + result

    # 判断测试结果

    is_success = set(results) == {1}

    print(f"测试结果:{is_success}", results)

    if set_result:
        if is_success and func_case_obj.can_autoed == FuncCase.IsAutoed.CAN and func_case_obj.auto_status == FuncCase.AutoStatus.Done:
            TestPlanFuncCase.objects.filter(test_plan_id=plan_id, is_delete=False, func_case_id=func_case_id).update(
                exec_status=TestPlanFuncCase.ExecStatus.PASSED, executed_by_id=user_id, executed_time=timezone.now())
        else:
            TestPlanFuncCase.objects.filter(test_plan_id=plan_id, is_delete=False, func_case_id=func_case_id).update(
                exec_status=TestPlanFuncCase.ExecStatus.TESTING, executed_by_id=user_id, executed_time=timezone.now())

    if report_id:
        # 按功能用例执行时，执行完所有关联脚本用例后根据is_success累加更新进度
        with transaction.atomic():
            report_obj = Report.objects.filter(id=report_id).select_for_update().first()
            if report_obj:
                if is_success:
                    report_obj.success_case_number += 1
                else:
                    report_obj.fail_case_number += 1
                report_obj.save(update_fields=['success_case_number', 'fail_case_number', 'update_time'])


def end_run_push_msg(env_obj, report_id):
    project_obj = Project.objects.get(id=env_obj.project.id)
    report_obj = Report.objects.get(id=report_id)

    case_all = report_obj.all_case_number
    case_pass = report_obj.success_case_number
    case_fail = report_obj.fail_case_number + report_obj.error_case_number

    case_rate = case_pass / case_all if case_all > 0 else 0

    report_url = f"http://127.0.0.1:8080/#/report/listView?id={report_id}"

    start_time = report_obj.create_time
    end_time = report_obj.update_time
    duration = end_time - start_time

    msg_obj = Message.objects.create(
        task_status=Message.TaskStatus.SUCCESS,
        total_count=case_all,
        success_count=case_pass,
        failed_count=case_fail,
        is_read=False,
        read_time=None,
        duration=duration.total_seconds(),
        user=report_obj.create_by,
        create_by=report_obj.create_by,
        update_by=report_obj.create_by,
        project=project_obj,
        title='脚本用例批跑执行完成',
        content=f'脚本用例批跑执行完成，成功 {case_pass} 条，失败 {case_fail} 条',
        message_type=Message.MessageType.TASK,
        related_url=f'/report/listView?id={report_id}'
    )

    # 通过 WebSocket 实时推送给该用户的所有在线连接
    try:
        from apps.messages.push import build_message_payload, push_message_to_user
        push_message_to_user(report_obj.create_by_id, build_message_payload(msg_obj))
    except Exception as exc:
        print(f"WS 实时推送失败: {str(exc)}")

    report_title = f"{report_obj.name}"

    msg_push_configs = ProjectMsgPush.objects.filter(project=project_obj, is_active=True)

    for config in msg_push_configs:
        try:
            if config.push_type == ProjectMsgPush.PushType.FeiShu:
                send_feishu_message(
                    webhook_url=config.webhook_url,
                    report_url=report_url,
                    project_name=project_obj.name,
                    env_name=env_obj.name,
                    case_rate=case_rate,
                    case_all=case_all,
                    case_pass=case_pass,
                    case_fail=case_fail,
                    report_title=report_title,
                    start_time=start_time,
                    end_time=end_time,
                    secret=config.email_password if config.email_password else None
                )

            elif config.push_type == ProjectMsgPush.PushType.DingDing:
                send_dingtalk_message(
                    webhook_url=config.webhook_url,
                    report_url=report_url,
                    project_name=project_obj.name,
                    env_name=env_obj.name,
                    case_rate=case_rate,
                    case_all=case_all,
                    case_pass=case_pass,
                    case_fail=case_fail,
                    report_title=report_title,
                    start_time=start_time,
                    end_time=end_time,
                    secret=config.email_password if config.email_password else None
                )

            elif config.push_type == ProjectMsgPush.PushType.Email:
                send_test_report_email(
                    smtp_host=config.email_host,
                    smtp_port=config.email_port,
                    smtp_user=config.email_user,
                    smtp_password=config.email_password,
                    from_addr=config.email_user,
                    to_addrs=[email.strip() for email in config.email_to.split(',') if email.strip()],
                    report_url=report_url,
                    project_name=project_obj.name,
                    env_name=env_obj.name,
                    case_rate=case_rate,
                    case_all=case_all,
                    case_pass=case_pass,
                    case_fail=case_fail,
                    report_title=report_title,
                    start_time=start_time,
                    end_time=end_time,
                    subject_prefix='测试报告'
                )
        except Exception as e:
            print(f"推送消息失败: {str(e)}")
            continue
