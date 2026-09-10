"""
LangGraph工作流 - AI从功能用例生成场景自动化脚本

节点链路: load_func_case → load_resources → generate → validate_and_fix → output

设计要点:
1. load_func_case: 从FuncCase表读功能用例(前置条件+步骤+期望)作为需求文档
2. load_resources: 按模式加载资产
   - api模式: 向量库RAG检索接口文档 + 取接口参数摘要
   - web_ui模式: 项目元素库清单
3. generate: LLM输出步骤树(api/web/control节点)
4. validate_and_fix: pydantic解析 + 业务校验(接口/元素/keyword/控制器/引用)，
   失败走LLM修复，最多MAX_RETRIES次
5. output: 输出最终结果dict
"""
import json
import time
import logging
from typing import TypedDict, Optional, List, Dict, Any

from django.conf import settings
from langgraph.graph import StateGraph, END

from apps.ai_service.llm import LLMClient
from apps.ai_service.scenario_case_schemas import (
    GeneratedScenarioCase,
)
from apps.ai_service.scenario_case_prompts import (
    build_generate_system, VALIDATE_SYSTEM,
    build_func_case_user_prompt,
)
from apps.ai_service.vectorstore import hybrid_search, SOURCE_API, build_rag_context
from apps.ai_service.api_case_saver import extract_response_field_paths
from apps.tests.models import FuncCase
from apps.interfaces.models import Api
from apps.elements.models import Element
from core.step.run_playwright import PlaywrightBaseAction

logger = logging.getLogger('ai_service')

MAX_RETRIES = getattr(settings, 'AI_MAX_RETRIES', 2)

# Playwright动作白名单
VALID_KEYWORDS = set(
    k for k in PlaywrightBaseAction.__dict__ if not k.startswith('_')
)

CONTROL_KEYWORDS = {'IF', 'FOR', 'WHILE', 'SLEEP', 'TRANSACTION', 'FOREACH'}


class GraphState(TypedDict):
    # 输入
    func_case_id: int
    project_id: int
    module_id: int
    mode: str
    generate_count: int
    ai_config_id: int
    tag_ids: list
    extra_requirement: str
    # 中间状态
    func_case_summary: Optional[dict]
    resources: Optional[list]
    rag_context: Optional[str]
    raw_llm_output: Optional[str]
    # 输出
    result: Optional[dict]
    retry_count: int
    error: Optional[str]


# ===== 节点1: 加载功能用例 =====
def load_func_case(state: GraphState) -> GraphState:
    logger.info(f"[AI-SCENE] 节点1: 加载功能用例 {state['func_case_id']}")
    try:
        fc = FuncCase.objects.get(id=state['func_case_id'], is_delete=False)
        state['func_case_summary'] = {
            'name': fc.name,
            'setup_condition': fc.setup_condition or '',
            'case_mark': fc.case_mark or '',
            'step_table': fc.step_table or [],
            'step_text': fc.step_text or '',
            'exp_text': fc.exp_text or '',
        }
    except FuncCase.DoesNotExist:
        state['error'] = f"功能用例不存在: {state['func_case_id']}"
    return state


# ===== 节点2: 加载资源 =====
def _field_names(tree: Any, depth: int = 0) -> List[str]:
    """提取参数树的字段名列表(控制token)"""
    if not tree or depth > 3:
        return []
    names = []
    for n in tree:
        if not isinstance(n, dict):
            continue
        names.append(n.get('name', ''))
        children = n.get('children') or n.get('child') or []
        if children:
            names += _field_names(children, depth + 1)
    return names


def _format_api_resource(api: Api) -> dict:
    """接口资源摘要(含真实响应字段，供LLM生成断言act_field)"""
    fields = []
    if api.params:
        fields += _field_names(api.params)
    if api.json:
        fields += _field_names(api.json)
    if api.data:
        fields += _field_names(api.data)
    # 去重保留前30个
    seen, uniq = set(), []
    for f in fields:
        if f and f not in seen:
            seen.add(f)
            uniq.append(f)

    # 响应字段: 从 response_tree/response 包装结构解包出真实响应体字段。
    # 存储结构为 [{"response_data": [<参数树>], "response_status": 200}]，
    # 真实响应体字段是 response_data 内参数树的 name 路径(如 msg/result.token_access)，
    # response_status 是HTTP状态码(对应内置 apiStatusCode)。
    # 注意: 不能把包装键 response_data 本身当字段，否则会生成
    # apiResponseBody.response_data 这种运行时不存在的引用。
    uniq_r = extract_response_field_paths(api)[:30]

    return {
        'name': api.name,
        'method': api.method,
        'url': api.url,
        'fields': ', '.join(uniq[:30]),
        'response_fields': ', '.join(uniq_r),
    }


def load_resources(state: GraphState) -> GraphState:
    logger.info(f"[AI-SCENE] 节点2: 加载资源 mode={state['mode']}")
    try:
        if state.get('error'):
            return state

        summary = state.get('func_case_summary') or {}
        query_text = f"{summary.get('name', '')}\n{summary.get('step_text', '')}\n" \
                     f"{json.dumps(summary.get('step_table', []), ensure_ascii=False)}"

        if state['mode'] == 'api':
            # 向量库RAG检索接口文档
            hits = hybrid_search(
                state['project_id'], query_text,
                source_types=[SOURCE_API], top_k=8, min_similarity=0.25,
            )
            state['rag_context'] = build_rag_context(hits, max_items=6)

            api_ids = []
            for h in hits:
                sid = h.get('metadata', {}).get('source_id')
                if sid:
                    api_ids.append(sid)

            apis = list(Api.objects.filter(
                module__project_id=state['project_id'], id__in=api_ids, is_delete=False
            )) if api_ids else []
            if not apis:
                # 兜底: 向量库无命中时取最近更新的接口
                apis = list(Api.objects.filter(
                    module__project_id=state['project_id'], is_delete=False
                ).order_by('-update_time')[:10])

            state['resources'] = [_format_api_resource(a) for a in apis]
            logger.info(f"[AI-SCENE] 检索到接口 {len(apis)} 个")
        else:
            elems = list(Element.objects.filter(
                project_id=state['project_id'], is_delete=False
            )[:300])
            state['resources'] = [{'name': e.name, 'type': e.type} for e in elems]
            state['rag_context'] = ''
            logger.info(f"[AI-SCENE] 加载元素 {len(elems)} 个")
    except Exception as e:
        logger.error(f"[AI-SCENE] 加载资源失败: {e}")
        state['error'] = f"加载资源失败: {str(e)}"
    return state


# ===== 节点3: 用例生成 =====
def generate_cases(state: GraphState) -> GraphState:
    logger.info(f"[AI-SCENE] 节点3: 生成用例 (重试{state.get('retry_count', 0)})")
    try:
        if state.get('error'):
            return state

        llm = LLMClient(state['ai_config_id'])
        summary = state.get('func_case_summary', {})
        resources = state.get('resources') or []

        if state['mode'] == 'api':
            res_lines = [
                f"- {r['name']} | {r['method']} {r['url']} | 参数: {r.get('fields', '')} | "
                f"响应字段: {r.get('response_fields', '')}"
                for r in resources
            ]
        else:
            res_lines = [f"- {r['name']}({r['type']})" for r in resources]

        user_prompt = build_func_case_user_prompt(
            summary,
            extra_requirement=state.get('extra_requirement') or '',
            rag_context=state.get('rag_context') or '',
            resources=res_lines,
            mode=state['mode'],
        )

        result = llm.chat_json(
            build_generate_system(state.get('generate_count', 3)),
            user_prompt,
            temperature=0.7,
        )
        state['raw_llm_output'] = json.dumps(result, ensure_ascii=False)
        logger.info(f"[AI-SCENE] 生成完成，共 {len(result.get('cases', []))} 条")
    except Exception as e:
        logger.error(f"[AI-SCENE] 生成失败: {e}")
        state['error'] = f"生成失败: {str(e)}"
    return state


# ===== 节点4: 校验修复 =====
def _walk_steps(case: GeneratedScenarioCase, state: dict,
                errors: list, api_names: set, elem_names: set,
                seq_count: List[int]):
    """遍历步骤树做业务校验，统计api/web步骤数

    断言method白名单由 AssertionCheck.field_validator 在pydantic层拦截，
    此处只做接口/元素/动作/控制器的业务校验。
    """
    def _walk(nodes: list, is_child: bool = False):
        for node in nodes:
            st = node.step_type
            if st == 'api':
                seq_count[0] += 1
                if node.api.api_name not in api_names:
                    errors.append(
                        f"用例[{case.name}] 接口不存在: {node.api.api_name}")
            elif st == 'web':
                seq_count[0] += 1
                if node.web.keyword not in VALID_KEYWORDS:
                    errors.append(
                        f"用例[{case.name}] 动作不在白名单: {node.web.keyword}")
                if node.web.element_name and node.web.element_name not in elem_names:
                    errors.append(
                        f"用例[{case.name}] 元素不存在: {node.web.element_name}")
            elif st == 'control':
                ctrl = node.control
                if ctrl.keyword not in CONTROL_KEYWORDS:
                    errors.append(
                        f"用例[{case.name}] 未知控制器: {ctrl.keyword}")
                if ctrl.keyword in ('IF', 'WHILE') and not ctrl.conditions:
                    errors.append(
                        f"用例[{case.name}] {ctrl.keyword}控制器缺少条件conditions")
                if ctrl.keyword == 'FOR' and ctrl.loop_times <= 0:
                    errors.append(
                        f"用例[{case.name}] FOR控制器loop_times必须>0")
                if ctrl.keyword == 'SLEEP' and ctrl.timeout <= 0:
                    errors.append(
                        f"用例[{case.name}] SLEEP控制器timeout必须>0")
                if ctrl.keyword == 'FOREACH' and not ctrl.loop_var:
                    errors.append(
                        f"用例[{case.name}] FOREACH控制器缺少loop_var")
                # 控制器内最多一层嵌套
                if is_child:
                    errors.append(
                        f"用例[{case.name}] 控制器嵌套超过一层")
                else:
                    _walk(ctrl.children, is_child=True)

    _walk(case.steps)


def _collect_refs(obj: Any, refs: Optional[set] = None) -> set:
    """收集所有 {sN.} 引用的序号"""
    import re
    if refs is None:
        refs = set()
    pattern = re.compile(r'\{s(\d+)(\.[^}]*)?\}')
    if isinstance(obj, str):
        for m in pattern.finditer(obj):
            refs.add(int(m.group(1)))
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_refs(v, refs)
    elif isinstance(obj, list):
        for i in obj:
            _collect_refs(i, refs)
    return refs


def _validate_and_fix_cases(raw: str, state: dict) -> tuple:
    """解析 + 业务校验 + LLM修复循环，返回 (cases, error)"""
    current_raw = raw
    last_error = '未知错误'

    # 预加载项目接口名/元素名(校验依据，不依赖resources)
    api_names = set(Api.objects.filter(
        module__project_id=state['project_id'], is_delete=False
    ).values_list('name', flat=True))
    elem_names = set(Element.objects.filter(
        project_id=state['project_id'], is_delete=False
    ).values_list('name', flat=True))

    for attempt in range(MAX_RETRIES + 1):
        try:
            data = json.loads(current_raw)
            cases = [GeneratedScenarioCase(**c) for c in data.get('cases', [])]

            errors: List[str] = []
            for idx, case in enumerate(cases, 1):
                seq_count = [0]
                _walk_steps(case, state, errors, api_names, elem_names, seq_count)
                # 变量引用校验(pydantic模型需先dump成dict/list才能递归遍历)
                refs = _collect_refs(case.model_dump())
                for seq in sorted(refs):
                    if seq < 1 or seq > seq_count[0]:
                        errors.append(
                            f"用例[{case.name}] 引用不存在的步骤 s{seq}"
                            f"(有效范围1-{seq_count[0]})")

            if not errors:
                return cases, None
            last_error = '; '.join(errors)
            logger.info(f"[AI-SCENE] 校验发现 {len(errors)} 个问题: {last_error}")
        except Exception as e:
            last_error = f'结构校验失败: {e}'
            logger.warning(f"[AI-SCENE] 结构校验失败(第{attempt + 1}次): {e}")

        if attempt >= MAX_RETRIES:
            return None, last_error

        # LLM修复
        try:
            llm = LLMClient(state['ai_config_id'])
            resource_names = (
                "可用接口: " + '; '.join(f"{r['name']}|{r['method']} {r['url']}"
                                         for r in state.get('resources', []))
                if state['mode'] == 'api'
                else "可用元素: " + '; '.join(f"{r['name']}({r['type']})"
                                              for r in state.get('resources', []))
            )
            fix_prompt = (
                f"原JSON:\n{current_raw}\n\n"
                f"校验错误:\n{last_error}\n\n"
                f"{resource_names}\n\n"
                f"Playwright动作白名单: {sorted(VALID_KEYWORDS)}\n"
                f"控制器类型: {sorted(CONTROL_KEYWORDS)}"
            )
            repaired = llm.chat_json(VALIDATE_SYSTEM, fix_prompt, temperature=0.2)
            current_raw = json.dumps(repaired, ensure_ascii=False)
            logger.info(f"[AI-SCENE] LLM修复完成(第{attempt + 1}次)")
        except Exception as e:
            logger.error(f"[AI-SCENE] LLM修复失败: {e}")
            return None, f'LLM修复失败: {str(e)}'

    return None, last_error


def validate_and_fix(state: GraphState) -> GraphState:
    logger.info(f"[AI-SCENE] 节点4: 校验用例")
    try:
        if state.get('error'):
            state['result'] = {'success': False, 'cases': [], 'error': state['error']}
            return state

        raw = state.get('raw_llm_output') or '{}'
        cases, error = _validate_and_fix_cases(raw, state)
        if error is None:
            state['result'] = {
                'success': True,
                'cases': [c.model_dump() for c in cases],
            }
        else:
            state['error'] = error
            state['result'] = {'success': False, 'cases': [], 'error': error}
    except Exception as e:
        logger.error(f"[AI-SCENE] 校验异常: {e}")
        state['error'] = f"校验异常: {str(e)}"
        state['result'] = {'success': False, 'cases': [], 'error': str(e)}
    return state


# ===== 节点5: 输出 =====
def final_output(state: GraphState) -> GraphState:
    if not state.get('result'):
        state['result'] = {
            'success': False,
            'cases': [],
            'error': state.get('error', '未知错误'),
        }
    return state


# ===== 构建工作流 =====
def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("load_func_case", load_func_case)
    workflow.add_node("load_resources", load_resources)
    workflow.add_node("generate", generate_cases)
    workflow.add_node("validate", validate_and_fix)
    workflow.add_node("output", final_output)

    workflow.set_entry_point("load_func_case")
    workflow.add_edge("load_func_case", "load_resources")
    workflow.add_edge("load_resources", "generate")
    workflow.add_edge("generate", "validate")
    workflow.add_edge("validate", "output")
    workflow.add_edge("output", END)

    return workflow.compile()


# ===== 执行入口 =====
def run_generation(func_case_id: int, project_id: int, ai_config_id: int,
                   module_id: int, mode: str, tag_ids: list = None,
                   generate_count: int = 3,
                   extra_requirement: str = "") -> dict:
    """执行AI生成工作流，返回dict格式结果

    返回:
        {
            'success': bool,
            'cases': [GeneratedScenarioCase.model_dump()],
            'error': str|None,
            'duration': float
        }
    """
    start_time = time.time()
    graph = build_graph()

    initial_state = {
        'func_case_id': func_case_id,
        'project_id': project_id,
        'module_id': module_id,
        'mode': mode,
        'generate_count': generate_count,
        'ai_config_id': ai_config_id,
        'tag_ids': tag_ids or [],
        'extra_requirement': extra_requirement,
        'func_case_summary': None,
        'resources': None,
        'rag_context': None,
        'raw_llm_output': None,
        'result': None,
        'retry_count': 0,
        'error': None,
    }

    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"[AI-SCENE] LangGraph工作流执行异常: {e}")
        return {
            'success': False,
            'cases': [],
            'error': f"工作流执行异常: {str(e)}",
            'duration': round(time.time() - start_time, 2),
        }

    duration = round(time.time() - start_time, 2)
    if not final_state or not isinstance(final_state, dict):
        return {
            'success': False,
            'cases': [],
            'error': '工作流返回空状态',
            'duration': duration,
        }

    result = final_state.get('result') or {}
    result['duration'] = duration
    logger.info(
        f"[AI-SCENE] 生成完成，耗时 {duration}s，"
        f"成功 {len(result.get('cases', []))} 条"
    )
    return result
