"""
接口状态守卫
================
背景：接口状态（Api.ApiStatus）之前只是一个展示用的标记，接口置为「废弃」后
依然可以被用例新增引用、也可以在测试计划/用例执行时照常发起请求，状态形同虚设。

本模块把状态变成真正的约束，统一收口三处校验：

1. 新增/编辑步骤（引用接口）时拦截 —— StepSerializer.validate
2. 用例/计划执行到该步骤时拦截 —— core/step/run_request.run_step_request
3. 把接口置为「废弃」时给出引用告警 —— ApiViewSet.update

约定：
- Step 通过 keyword（字符型，存 Api.id）+ type=5(Request) 引用接口文档，
  公共步骤为 type=3(ComStep) 且 com_step_type=5。
- 目前只有「废弃(10)」是强约束状态；「维护(9)」「异常(8)」仅提示不阻断，
  后续如需收紧，直接往 BLOCKED_STATUS / WARN_STATUS 里加即可。
"""

from rest_framework.exceptions import ValidationError

from apps.interfaces.models import Api
from apps.tests.models import Step, CaseSteps
from django.db.models import Q

# 强约束：不允许被用例引用、不允许执行
BLOCKED_STATUS = {
    Api.ApiStatus.StatusTen: '废弃',
}

# 弱约束：允许引用与执行，但保存/执行时给出提示
WARN_STATUS = {
    Api.ApiStatus.StatusEight: '异常',
    Api.ApiStatus.StatusNine: '维护',
}


class ApiDeprecatedException(Exception):
    """执行时遇到已废弃接口，直接中断该步骤"""

    def __init__(self, api_name, status_name):
        error_msg = (
            f'接口「{api_name}」当前状态为「{status_name}」，已禁止执行。'
            f'请更换为有效接口，或由接口负责人将状态改回后再执行。'
        )
        super().__init__(error_msg)
        self.__doc__ = f'接口已{status_name}，禁止执行'


def _to_int(value):
    """keyword 可能是 str / int / None，统一转换，非法值返回 None"""
    if value is None or value == '':
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def get_api_status_conflict(api_id, keyword_type=None, com_step_type=None):
    """检查接口是否处于被约束状态。

    :return: (level, api, message)
             level: 'block' | 'warn' | None
    """
    api_pk = _to_int(api_id)
    if not api_pk:
        return None, None, ''
    api = Api.objects.filter(id=api_pk, is_delete=False).first()
    if api is None:
        return None, None, ''

    if api.status in BLOCKED_STATUS:
        return 'block', api, (
            f'接口「{api.name}」当前状态为「{api.get_status_display()}」，'
            f'不允许被用例引用，请更换为有效接口'
        )
    if api.status in WARN_STATUS:
        return 'warn', api, (
            f'接口「{api.name}」当前状态为「{api.get_status_display()}」，'
            f'请确认是否仍可用于自动化执行'
        )
    return None, api, ''


def assert_api_reference_allowed(api_id, keyword_type=None, com_step_type=None):
    """新增/编辑步骤时调用：引用了废弃接口直接抛 400。"""
    level, api, message = get_api_status_conflict(api_id, keyword_type, com_step_type)
    if level == 'block':
        raise ValidationError(message)
    return message


def assert_api_runnable(api_id):
    """执行时调用：引用了废弃接口直接抛异常，由用例执行器捕获为 ERROR。"""
    level, api, message = get_api_status_conflict(api_id)
    if level == 'block':
        raise ApiDeprecatedException(api.name, api.get_status_display())


def count_api_reference(api_id):
    """统计某个接口被多少个未删除的自动化用例引用（用于置为废弃时的提示）。"""
    api_pk = _to_int(api_id)
    if not api_pk:
        return 0
    step_ids = Step.objects.filter(
        Q(keyword=api_pk, type=5, is_delete=False) |
        Q(keyword=api_pk, type=3, com_step_type=5, is_delete=False)
    ).values_list('id', flat=True)
    return CaseSteps.objects.filter(
        is_delete=False, step_id__in=step_ids
    ).values('case_id').distinct().count()
