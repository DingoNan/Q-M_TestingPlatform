"""
AI从功能用例生成场景脚本 - 落库模块

把LLM生成的步骤树落库为 Case + CaseSteps + Step:
- api步骤 → Step(Request)，从Api表克隆参数树并应用override
- web步骤 → Step(Playwright)，元素名匹配Element表生成func_params
- control步骤 → Step(Control)，生成逻辑控制器参数
- 变量引用 {sN.字段路径} 落库时替换为 ${stepResponse.{case_step_id}.{字段路径}}

步骤序号(step_index)按前序连续分配给所有步骤(含控制步骤)，保证执行顺序稳定；
变量引用 {sN} 只分配给api/web步骤(会产生stepResponse)，control步骤不参与计数。
"""
import re
import uuid
import logging
from typing import Any, Dict, List, Optional

from django.db import transaction

from apps.ai_service.api_case_saver import (
    _ensure_unique_case_name,
    _regenerate_tree_ids,
    _apply_override_to_tree,
    _flat_list_to_tree,
)
from apps.tests.models import Case, CaseSteps, Step, FuncCase, default_case_data
from apps.interfaces.models import Api
from apps.elements.models import Element
from apps.envs.models import Module
from core.com.common import get_function_params
from core.step.run_playwright import playwright_func_map
from core.run_case import StepType, ControlType

logger = logging.getLogger('ai_service')

# {sN.字段路径} 变量引用占位符
_REF_PATTERN = re.compile(r'\{s(\d+)(\.[^}]*)?\}')

# 运行时 stepResponse 内置字段根名(与前端 FuncAndParams.vue 变量类型一致)
_BUILTIN_REF_ROOTS = (
    'apiStatusCode', 'apiResponseBody', 'apiResponseHeaders', 'apiResponseCookies',
    'apiUrl', 'apiHost', 'apiUri', 'apiMethod',
    'apiRequestParams', 'apiRequestBody', 'apiRequestHeaders',
    'funcReturn', 'funcParams', 'stepParams', 'runTimes', 'runElement',
)
_BARE_REF_RE = re.compile(r'^(?:' + '|'.join(_BUILTIN_REF_ROOTS) + r')(?:\.|$)')
# LLM幻觉引用: 生成阶段case_step_id尚不存在，${stepResponse.<数字>.xxx}中的数字必为编造
_FAKE_STEP_RESP_RE = re.compile(r'\$\{stepResponse\.\d+\.')


def _normalize_act_field(act_field: str, own_ref: Optional[int]) -> str:
    """归一化LLM产出的断言/条件 act_field

    目标形式: {sN.<字段路径>}，落库时由 _fill_step_refs 替换为
    ${stepResponse.<case_step_id>.<字段路径>}。

    处理:
    1. 响应包装层泄漏: apiResponseBody.response_data.xxx → apiResponseBody.xxx
       (response_data 是接口文档响应树的包装键，运行时响应体里不存在该字段)
    2. LLM编造的 ${stepResponse.<数字>.xxx}(生成时ID未知，数字必为幻觉) → 引用本步骤
    3. 裸内置字段(如 apiStatusCode / apiResponseBody.msg / funcReturn) → 引用本步骤
       (断言挂在哪个步骤就引用哪个步骤的响应)
    已有 {sN.xxx} 占位符的(跨步骤引用)原样返回。
    """
    act = (act_field or '').strip()
    if not act:
        return act

    # 1. 去掉 response_data 包装层泄漏
    act = act.replace('apiResponseBody.response_data.', 'apiResponseBody.')
    if act == 'apiResponseBody.response_data':
        act = 'apiResponseBody'

    # 已有合法占位符(跨步骤引用)，交给 _fill_step_refs
    if _REF_PATTERN.search(act):
        return act

    if own_ref is not None:
        # 2. 幻觉数字ID引用 → 本步骤
        if _FAKE_STEP_RESP_RE.match(act):
            return _FAKE_STEP_RESP_RE.sub(f'{{s{own_ref}.', act)
        # 3. 裸内置字段 → 本步骤占位符
        if _BARE_REF_RE.match(act):
            return f'{{s{own_ref}.{act}}}'

    return act


def save_generated_scenario_cases(func_case_id: int, generated_cases: List[dict],
                                  mode: str, user_id: int, project_id: int,
                                  module_id: int, tag_ids: List[int] = None) -> List[dict]:
    """把AI生成的场景脚本用例落库

    Args:
        func_case_id: 功能用例ID
        generated_cases: GeneratedScenarioCase.model_dump() 列表
        mode: 'api' 或 'web_ui'
        user_id: 创建人
        project_id: 项目ID
        module_id: 用例模块ID(决定Step.plant)
        tag_ids: 标签ID列表

    Returns:
        [{'id': case_id, 'name': case_name}, ...]
    """
    module = Module.objects.get(id=module_id, is_delete=False)
    func_case = FuncCase.objects.get(id=func_case_id, is_delete=False)
    saved = []
    tag_ids = tag_ids or []

    for case_dict in generated_cases:
        try:
            with transaction.atomic():
                case = Case.objects.create(
                    name=_ensure_unique_case_name(case_dict.get('name') or f'AI场景_{func_case_id}'),
                    type=(Case.FunctionCaseType.API if mode == 'api' else Case.FunctionCaseType.WEB_UI),
                    project_id=project_id,
                    module_id=module_id,
                    params=[],
                    data=default_case_data(),
                    recent_test_result=Case.CaseResult.NoRUN,
                    create_by_id=user_id,
                    update_by_id=user_id,
                )
                # 关联到功能用例的"关联脚本用例"(FuncCase.case M2M)
                func_case.case.add(case)
                if tag_ids:
                    case.tag.set(tag_ids)

                step_refs: Dict[int, int] = {}  # LLM变量引用序号 -> case_step_id
                step_index = [0]   # 全局步骤序号(所有步骤含控制步骤连续占用, 保证order_by稳定)
                ref_seq = [0]      # 业务步骤序号(仅api/web, 对应LLM的{sN}引用)
                all_steps: List[Step] = []

                _create_step_tree(
                    case, case_dict.get('steps', []), module, project_id, user_id,
                    parent_id=None, step_refs=step_refs, step_index=step_index,
                    ref_seq=ref_seq, all_steps=all_steps,
                )

                # 所有步骤创建完成后统一回填变量引用
                for step in all_steps:
                    _fill_step_refs(step, step_refs)
                    step.save()

            saved.append({'id': case.id, 'name': case.name})
            logger.info(f"[AI-SAVER] 场景用例落库: case_id={case.id}, name={case.name}, 步骤数={len(all_steps)}")
        except Exception as e:
            logger.error(f"[AI-SAVER] 场景用例落库失败: {e}")
            raise

    logger.info(f"[AI-SAVER] 落库完成，共 {len(saved)} 个用例")
    return saved


def _create_step_tree(case: Case, nodes: List[dict], module: Module, project_id: int,
                      user_id: int, parent_id: Optional[int], step_refs: Dict[int, int],
                      step_index: List[int], ref_seq: List[int], all_steps: List[Step]):
    """递归创建步骤树(前序遍历)

    序号规则:
    - step_index: 所有步骤(含控制步骤)按前序连续占用, 保证执行引擎 order_by('step_index') 顺序稳定
    - 变量引用 {sN}: 仅api/web业务步骤参与计数(sN从1开始, 与LLM编号一致), 控制步骤不参与
    """
    for node in nodes:
        step_type = node.get('step_type')
        if step_type not in ('api', 'web', 'control'):
            raise ValueError(f"未知步骤类型: {step_type}")

        seq = step_index[0]        # 0-based: 首个步骤从0开始(与手工用例一致)
        step_index[0] = seq + 1

        if step_type == 'api':
            ref_seq[0] += 1
            ref = ref_seq[0]
            step = _build_api_step(node.get('api') or {}, module, project_id, user_id, ref)
        elif step_type == 'web':
            ref_seq[0] += 1
            ref = ref_seq[0]
            step = _build_web_step(node.get('web') or {}, module, project_id, user_id, ref)
        else:
            step = _build_control_step(node.get('control') or {}, module, project_id, user_id)
            ref = None

        step.save()
        all_steps.append(step)

        case_step = CaseSteps.objects.create(
            case=case,
            step=step,
            step_index=seq,
            step_params=[],
            parent_id=parent_id,
            is_run=True,
            fail_is_continue=CaseSteps.IsContinue.Stop,
        )

        # 记录LLM变量引用序号 -> case_step_id 映射(仅api/web步骤)
        if ref is not None:
            step_refs[ref] = case_step.id

        # 递归子步骤(逻辑控制器)
        if step_type == 'control':
            children = (node.get('control') or {}).get('children', [])
            if children:
                _create_step_tree(
                    case, children, module, project_id, user_id,
                    parent_id=case_step.id, step_refs=step_refs,
                    step_index=step_index, ref_seq=ref_seq, all_steps=all_steps,
                )


# ===== 各类Step构建 =====

def _build_check_params(assertions: List[Any], own_ref: Optional[int] = None) -> list:
    """把AssertionCheck列表转为执行引擎的check_params格式

    结构对齐手工用例(如"登录用例一"的IF控制器run_params):
        {
            "id": "<uuid>",              # 前端条件表格行标识
            "method": "check_number_equal",   # check.py中的函数名
            "exp_value": 200,                 # 预期值
            "act_value": "{s1.apiStatusCode}",# 实际值引用(落库时由_fill_step_refs替换为${stepResponse...})
            "andOr": "And"                    # 多条件组合逻辑, 默认And
        }

    own_ref: 当前步骤自身的{sN}序号(api/web步骤)，用于把LLM漏写占位符的
             裸字段/幻觉数字ID引用归一化到本步骤；控制步骤(条件引用前序步骤)传None。
    """
    check_params = []
    for a in assertions or []:
        a_dict = a if isinstance(a, dict) else (a.model_dump() if hasattr(a, 'model_dump') else {})
        raw_exp = a_dict.get('exp_value')
        if raw_exp is None:
            exp_value = ''
        elif isinstance(raw_exp, str):
            exp_value = raw_exp
        else:
            exp_value = str(raw_exp)
        check_params.append({
            'id': str(uuid.uuid4()),
            'method': a_dict.get('method', 'check_equal'),
            'exp_value': exp_value,
            'act_value': _normalize_act_field(a_dict.get('act_field', ''), own_ref),
            'andOr': 'And',
        })
    return check_params

def _build_api_step(api_step_dict: dict, module: Module, project_id: int, user_id: int,
                    own_ref: Optional[int] = None) -> Step:
    """构建接口步骤(Request)，从Api表克隆参数树并应用override"""
    api_name = api_step_dict.get('api_name', '')
    api = Api.objects.filter(module__project_id=project_id, name=api_name, is_delete=False).first()
    if not api:
        raise ValueError(f"接口不存在: {api_name}")

    headers = _regenerate_tree_ids(api.headers)
    params = _regenerate_tree_ids(api.params)
    json_body = _regenerate_tree_ids(api.json) if api.body_type == Api.BodyType.Json else []
    data_body = _regenerate_tree_ids(api.data) if api.body_type == Api.BodyType.Data else []
    response_tree = _regenerate_tree_ids(api.response_tree)

    _apply_override_to_tree(headers, api_step_dict.get('headers_override', []))
    _apply_override_to_tree(params, api_step_dict.get('params_override', []))
    if api.body_type == Api.BodyType.Json:
        _apply_override_to_tree(json_body, api_step_dict.get('body_override', []))
    else:
        _apply_override_to_tree(data_body, api_step_dict.get('body_override', []))

    return Step(
        desc=(api_step_dict.get('desc') or api.name)[:100],
        project_id=project_id,
        database_name=None,
        step_active_tab='body',
        is_check=False,
        type=StepType.Request,
        com_step_type=StepType.Request,
        timeout=7,
        allow_redirects=True,
        verify=False,
        keyword=str(api.id),
        plant=module.plant,
        api_service=api.service,
        api_method=api.method,
        api_uri=api.url,
        api_headers=headers,
        common_headers=False,
        api_json_type=api.api_json_type,
        json_body_deal=None,
        api_json=json_body,
        body_type=api.body_type,
        api_json_tree=_flat_list_to_tree(json_body),
        api_data=data_body,
        data_body_deal=None,
        api_response=[],
        api_response_tree=response_tree,
        api_response_type=api.api_response_type,
        response_body_deal=None,
        api_params=params,
        check_params=_build_check_params(api_step_dict.get('assertions', []), own_ref),
        run_params=[],
        loop=[],
        until=[],
        setup='',
        script='',
        teardown='',
        func_params=[],
        create_by_id=user_id,
        update_by_id=user_id,
    )


# 标量参数类型(其余如Dict/List保留LLM声明的类型，避免破坏JSON结构)
_SCALAR_PARAM_TYPES = {'Str', 'Int', 'Float', 'Bool'}


def _build_web_step(web_step_dict: dict, module: Module, project_id: int, user_id: int,
                    own_ref: Optional[int] = None) -> Step:
    """构建WebUI步骤(Playwright)，按动作签名生成func_params(与"WEB UI登录用例一"结构一致)

    生成的每个参数项结构:
        {"id", "name", "value", "type", "explain", "children", "_X_ROW_CHILD", "function_name"}
    - obj 参数: 来自element_name匹配Element表的元素ID(EleObject)
    - 其余参数: 按动作签名顺序填充，LLM已给值的用其值，未给的用签名默认值
      (如 fill 自动补全 element_index=0、timeout=5; goto 自动补全 need_add_cookie=False)
    - 缺失必填参数时明确报错，避免生成无法执行的步骤
    """
    keyword = web_step_dict.get('keyword', '')
    element_name = web_step_dict.get('element_name') or ''

    func = playwright_func_map.get(keyword)
    if not func:
        raise ValueError(f"未知Playwright动作: {keyword}")

    signature = get_function_params(func)
    llm_params = {p.get('name'): p for p in web_step_dict.get('params', [])}

    func_params = []
    for sp in signature:
        name = sp['name']
        if sp['type'] == 'EleObject':
            # 元素参数: 仅支持单个 obj, 多元素动作(如drag_and_drop)暂不支持
            if name != 'obj':
                raise ValueError(f"动作 {keyword} 暂不支持多元素参数 {name}")
            if not element_name:
                if sp['value'] is None:
                    raise ValueError(f"动作 {keyword} 缺少必填参数 {name}(需提供element_name)")
                continue
            elem = Element.objects.filter(project_id=project_id, name=element_name, is_delete=False).first()
            if not elem:
                raise ValueError(f"元素不存在: {element_name}")
            fvalue = int(elem.id)
            ftype = 'EleObject'
        else:
            llm_p = llm_params.get(name)
            if llm_p is not None:
                fvalue = str(llm_p.get('value', ''))
                # 标量参数以签名类型为准(保证执行时类型正确), Dict/List等保留LLM声明类型
                ftype = sp['type'] if sp['type'] in _SCALAR_PARAM_TYPES else (llm_p.get('value_type') or 'Str')
            elif sp['value'] is not None:
                fvalue = sp['value']   # 签名默认值(如 element_index=0, timeout=5)
                ftype = sp['type']
            else:
                raise ValueError(f"动作 {keyword} 缺少必填参数 {name}")
        func_params.append({
            'id': f"row_{uuid.uuid4().hex[:8]}",
            'name': name,
            'value': fvalue,
            'type': ftype,
            'explain': sp['explain'],
            'children': [],
            '_X_ROW_CHILD': [],
            'function_name': keyword,
        })

    assertion = web_step_dict.get('assertion')
    check_params = _build_check_params([assertion] if assertion else [], own_ref)

    return Step(
        desc=(web_step_dict.get('desc') or keyword)[:100],
        project_id=project_id,
        database_name=None,
        step_active_tab='params',
        is_check=False,
        type=StepType.Playwright,
        com_step_type=StepType.Playwright,
        timeout=7,
        allow_redirects=True,
        verify=False,
        keyword=keyword,
        plant=module.plant,
        api_service=None,
        api_method=None,
        api_uri=None,
        api_headers=[],
        common_headers=False,
        api_json_type='object',
        json_body_deal=None,
        api_json=[],
        body_type=1,
        api_json_tree=[],
        api_data=[],
        data_body_deal=None,
        api_response=[],
        api_response_tree=[],
        api_response_type='object',
        response_body_deal=None,
        api_params=[],
        check_params=check_params,
        run_params=[],
        loop=[],
        until=[],
        setup='',
        script='',
        teardown='',
        func_params=func_params,
        create_by_id=user_id,
        update_by_id=user_id,
    )


_CONTROL_TYPE_MAP = {
    'IF': ControlType.IF,
    'FOR': ControlType.FOR,
    'WHILE': ControlType.WHILE,
    'SLEEP': ControlType.SLEEP,
    'TRANSACTION': ControlType.TRANSACTION,
    'FOREACH': ControlType.FOREACH,
}


def _build_control_step(ctrl_dict: dict, module: Module, project_id: int, user_id: int) -> Step:
    """构建逻辑控制器步骤(Control)"""
    keyword = ctrl_dict.get('keyword', '')
    ctype = _CONTROL_TYPE_MAP.get(keyword)
    if not ctype:
        raise ValueError(f"未知控制器类型: {keyword}")

    run_params = []
    loop = []
    until = []
    body_type = 1
    api_json_type = 'object'
    timeout = 7

    if keyword == 'IF':
        # IF条件 → run_params(loop_assert_by_check_list格式)
        run_params = _build_check_params(ctrl_dict.get('conditions', []))
    elif keyword == 'WHILE':
        # WHILE条件 → until(条件字段+max_loop_times，WhileController读取until[0])
        until = _build_check_params(ctrl_dict.get('conditions', []))
        for u in until:
            u['max_loop_times'] = str(ctrl_dict.get('max_loop_times', 5))
    elif keyword == 'FOR':
        loop = [{'loop_times': str(ctrl_dict.get('loop_times', 0))}]
    elif keyword == 'FOREACH':
        loop = [{'loop_times': ctrl_dict.get('loop_var', '')}]
        body_type = 2  # 变量引用模式
        api_json_type = 'array'
    elif keyword == 'SLEEP':
        timeout = int(ctrl_dict.get('timeout') or 0)

    return Step(
        desc=(ctrl_dict.get('desc') or keyword)[:100],
        project_id=project_id,
        database_name=None,
        step_active_tab='params',
        is_check=False,
        type=StepType.Control,
        com_step_type=StepType.Control,
        timeout=timeout,
        allow_redirects=True,
        verify=False,
        keyword=ctype,
        plant=module.plant,
        api_service=None,
        api_method=None,
        api_uri=None,
        api_headers=[],
        common_headers=False,
        api_json_type=api_json_type,
        json_body_deal=None,
        api_json=[],
        body_type=body_type,
        api_json_tree=[],
        api_data=[],
        data_body_deal=None,
        api_response=[],
        api_response_tree=[],
        api_response_type='object',
        response_body_deal=None,
        api_params=[],
        check_params=[],
        run_params=run_params,
        loop=loop,
        until=until,
        setup='',
        script='',
        teardown='',
        func_params=[],
        create_by_id=user_id,
        update_by_id=user_id,
    )


# ===== 变量引用回填 =====

def _fill_step_refs(step: Step, step_refs: Dict[int, int]):
    """把步骤JSON字段中的 {sN.xxx} 占位符替换为 ${stepResponse.{id}.xxx}"""
    fields = [
        'check_params', 'func_params', 'run_params', 'loop', 'until',
        'api_headers', 'api_params', 'api_json', 'api_data',
    ]
    for f in fields:
        val = getattr(step, f, None)
        if val:
            setattr(step, f, _replace_refs(val, step_refs))


def _replace_refs(obj: Any, step_refs: Dict[int, int]) -> Any:
    """递归替换 {sN.xxx} 占位符"""
    if isinstance(obj, str):
        def _repl(m):
            seq = int(m.group(1))
            path = m.group(2) or ''
            cid = step_refs.get(seq)
            if cid is None:
                # 引用不存在的步骤，保留原文(validate阶段应已拦截)
                return m.group(0)
            return f'${{stepResponse.{cid}{path}}}'
        return _REF_PATTERN.sub(_repl, obj)
    if isinstance(obj, dict):
        return {k: _replace_refs(v, step_refs) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_replace_refs(i, step_refs) for i in obj]
    return obj
