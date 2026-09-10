"""
LangGraph工作流 - AI生成接口自动化用例

节点链路: load_api_doc → analyze → generate → validate_and_fix → output
RAG阶段按需求拍板跳过。

设计要点:
1. load_api_doc: 从Api表读接口文档，把参数树压成叶子节点清单喂给LLM(避免id/parentId/uuid污染token)
2. analyze: LLM规划要生成哪些场景(只输出场景列表，不输出参数值)
3. generate: LLM为每个场景生成具体override和状态码断言
4. validate_and_fix: pydantic校验 + 业务校验，失败走LLM修复，最多重试MAX_RETRIES次
5. output: 输出最终结果dict
"""
import json
import time
import logging
from typing import TypedDict, Optional, List, Dict, Any

from django.conf import settings
from langgraph.graph import StateGraph, END

from apps.ai_service.llm import LLMClient
from apps.ai_service.api_case_schemas import (
    GeneratedApiCase, ParamOverride, AssertionCheck, ScenarioType, GenerationResult,
)
from apps.ai_service.api_case_prompts import (
    ANALYZE_SYSTEM, ANALYZE_USER,
    GENERATE_SYSTEM, GENERATE_USER,
    VALIDATE_SYSTEM, VALIDATE_USER,
)
from apps.ai_service.vectorstore import search_knowledge_base, build_rag_context
from apps.ai_service.api_case_saver import unwrap_response_data
from apps.interfaces.models import Api

logger = logging.getLogger('ai_service')

MAX_RETRIES = getattr(settings, 'AI_MAX_RETRIES', 2)


class GraphState(TypedDict):
    # 输入
    api_id: int
    project_id: int
    module_id: int
    tag_ids: list
    generate_count: int
    include_boundary: bool
    include_missing_required: bool
    include_type_error: bool
    include_exception_status: bool
    include_security: bool
    extra_requirement: str
    ai_config_id: int
    # 中间状态
    api_doc_summary: Optional[dict]
    analysis: Optional[str]
    rag_context: Optional[str]
    raw_llm_output: Optional[str]
    # 输出
    result: Optional[dict]
    retry_count: int
    error: Optional[str]


# ===== 参数树压缩工具 =====
def _flatten_param_tree(tree: Any, path_prefix: str = "") -> List[Dict[str, Any]]:
    """把参数树压成叶子节点清单

    只保留 name/type/示例值，去掉 id/parentId/uuid 等内部字段。
    用于喂给LLM，避免token爆炸 + LLM生成不可靠的结构化字段。

    输入示例(Api表里的headers/params/json/data/response_tree):
    [
        {"name": "Authorization", "value": "Bearer xxx", "type": "string", "id": "1", "parentId": ""},
        {"name": "address", "type": "object", "id": "2", "parentId": "", "children": [
            {"name": "city", "value": "北京", "type": "string", "id": "3", "parentId": "2"}
        ]}
    ]

    输出示例:
    [
        {"path": "Authorization", "type": "string", "sample_value": "Bearer xxx"},
        {"path": "address.city", "type": "string", "sample_value": "北京"}
    ]
    """
    if not tree or not isinstance(tree, list):
        return []

    result = []
    for node in tree:
        if not isinstance(node, dict):
            continue
        name = node.get("name", "")
        if not name:
            continue
        current_path = f"{path_prefix}.{name}" if path_prefix else name
        node_type = node.get("type", "string")
        children = node.get("children") or node.get("child") or []

        if children:
            # 非叶子节点，递归
            result.extend(_flatten_param_tree(children, current_path))
        else:
            # 叶子节点
            sample_value = node.get("value")
            if sample_value is None:
                sample_value = node.get("default_value", "")
            result.append({
                "path": current_path,
                "type": node_type,
                "sample_value": sample_value,
            })
    return result


def _extract_paths(leaf_list: List[Dict[str, Any]]) -> List[str]:
    """从叶子清单提取路径列表"""
    return [item["path"] for item in leaf_list]


def _flatten_all_param_nodes(nodes: list, path_prefix: str = "") -> List[Dict[str, Any]]:
    """压平参数树为节点清单(包含对象节点自身，不像_flatten_param_tree只取叶子)

    用于响应体: 对象节点(如 data/result)也需要作为断言路径(非空断言)。
    输入必须是已解包的嵌套参数树(根节点带name/children)。
    """
    result = []
    for node in nodes or []:
        if not isinstance(node, dict):
            continue
        name = node.get("name", "")
        if not name:
            continue
        current_path = f"{path_prefix}.{name}" if path_prefix else name
        sample_value = node.get("value")
        if sample_value is None:
            sample_value = node.get("default_value", "")
        result.append({
            "path": current_path,
            "type": node.get("type", "string"),
            "sample_value": sample_value,
        })
        children = node.get("children") or node.get("child") or []
        if children:
            result.extend(_flatten_all_param_nodes(children, current_path))
    return result


def _flatten_response_tree(wrapper: Any) -> List[Dict[str, Any]]:
    """把响应包装结构压成字段清单

    Api.response_tree/response 结构为 [{"response_data": [<参数树>], "response_status": 200}]，
    包装层dict没有name键，直接走_flatten_param_tree会整体跳过导致响应字段清单为空。
    需先解包 response_data(扁平parentId结构也会被转为嵌套)，多状态码条目按path去重。
    """
    result: List[Dict[str, Any]] = []
    seen = set()
    for nodes in unwrap_response_data(wrapper):
        for item in _flatten_all_param_nodes(nodes):
            if item["path"] not in seen:
                seen.add(item["path"])
                result.append(item)
    return result


def _build_scenario_switches(state: GraphState) -> str:
    """构建场景开关文本，明确标注包含/不包含，防止LLM自行发挥"""
    parts = []
    parts.append("- 正向场景(normal): 必须包含")
    parts.append(f"- 边界场景(boundary): {'包含' if state.get('include_boundary') else '不包含'}")
    parts.append(f"- 缺必填字段场景(missing_required): {'包含' if state.get('include_missing_required') else '不包含'}")
    parts.append(f"- 类型错误场景(type_error): {'包含' if state.get('include_type_error') else '不包含'}")
    parts.append(f"- 异常状态码场景(exception_status): {'包含' if state.get('include_exception_status') else '不包含'}")
    parts.append(f"- 安全性场景(security): {'包含' if state.get('include_security') else '不包含'}")
    return "\n".join(parts)


# ===== 节点1: 加载接口文档 =====
def load_api_doc(state: GraphState) -> GraphState:
    """从Api表读接口文档，压缩参数树喂给LLM"""
    logger.info(f"[AI-API] 节点1: 加载接口文档 - api_id={state['api_id']}")
    try:
        api = Api.objects.get(id=state['api_id'])

        headers_leaves = _flatten_param_tree(api.headers)
        params_leaves = _flatten_param_tree(api.params)
        json_leaves = _flatten_param_tree(api.json)
        data_leaves = _flatten_param_tree(api.data)
        # 响应树是 [{"response_data": [...], "response_status": 200}] 包装结构，
        # 需先解包再压平(否则包装层无name会整体跳过，LLM拿不到响应字段只能瞎猜)
        response_leaves = _flatten_response_tree(api.response_tree)
        if not response_leaves:
            response_leaves = _flatten_response_tree(api.response)

        body_type_name = "JSON" if api.body_type == Api.BodyType.Json else "Form-data"
        body_leaves = json_leaves if api.body_type == Api.BodyType.Json else data_leaves

        state['api_doc_summary'] = {
            "name": api.name,
            "method": api.method,
            "url": api.url,
            "body_type": body_type_name,
            "headers": [{"path": l["path"], "type": l["type"], "sample": l["sample_value"]} for l in headers_leaves],
            "params": [{"path": l["path"], "type": l["type"], "sample": l["sample_value"]} for l in params_leaves],
            "body": [{"path": l["path"], "type": l["type"], "sample": l["sample_value"]} for l in body_leaves],
            "response": [{"path": l["path"], "type": l["type"], "sample": l["sample_value"]} for l in response_leaves],
        }

        # 路径清单单独存一份，校验节点用
        state['api_doc_summary']['_paths'] = {
            "headers": _extract_paths(headers_leaves),
            "params": _extract_paths(params_leaves),
            "body": _extract_paths(body_leaves),
            "response": _extract_paths(response_leaves),
        }

        logger.info(
            f"[AI-API] 接口文档加载完成: {api.method} {api.url}, "
            f"headers={len(headers_leaves)} params={len(params_leaves)} "
            f"body={len(body_leaves)} response={len(response_leaves)}"
        )
    except Api.DoesNotExist:
        state['error'] = f"接口不存在: api_id={state['api_id']}"
        logger.error(f"[AI-API] {state['error']}")
    except Exception as e:
        state['error'] = f"加载接口文档失败: {str(e)}"
        logger.error(f"[AI-API] {state['error']}")
    return state


# ===== 节点1.5: RAG知识库检索 =====
def rag_retrieve_for_api(state: GraphState) -> GraphState:
    """从知识库检索相关的接口文档、缺陷和用例，辅助用例生成"""
    logger.info(f"[AI-API] 节点1.5: RAG知识库检索")
    try:
        if state.get('error'):
            return state

        api_summary = state.get('api_doc_summary', {})
        # 用接口名称和URL作为检索query
        query_text = f"{api_summary.get('name', '')} {api_summary.get('method', '')} {api_summary.get('url', '')}"

        similar = search_knowledge_base(
            project_id=state['project_id'],
            query=query_text,
            module_id=state.get('module_id'),
            top_k=5,
        )
        if similar:
            state['rag_context'] = build_rag_context(similar, max_items=5)
            source_types = set(item['metadata'].get('source_type', '') for item in similar)
            logger.info(f"[AI-API] RAG检索到 {len(similar)} 条知识库内容，来源: {source_types}")
        else:
            state['rag_context'] = None
            logger.info("[AI-API] RAG无检索结果")
    except Exception as e:
        logger.warning(f"[AI-API] RAG检索失败(非致命): {e}")
        state['rag_context'] = None
    return state


# ===== 节点2: 场景分析 =====
def analyze_scenarios(state: GraphState) -> GraphState:
    """LLM分析要生成哪些场景，只输出场景列表"""
    logger.info(f"[AI-API] 节点2: 场景分析")
    try:
        if state.get('error'):
            return state

        llm = LLMClient(state['ai_config_id'])
        api_summary = state.get('api_doc_summary', {})
        switches = _build_scenario_switches(state)
        rag_context = state.get('rag_context') or ''

        user_prompt = ANALYZE_USER.format(
            api_doc_summary=json.dumps(api_summary, ensure_ascii=False, indent=2),
            extra_requirement=state.get('extra_requirement') or "无",
            scenario_switches=switches,
        )
        # 在用户prompt中追加RAG上下文
        if rag_context:
            user_prompt += f"\n\n{rag_context}"

        result = llm.chat_json(
            ANALYZE_SYSTEM.format(generate_count=state.get('generate_count', 3)),
            user_prompt,
            temperature=0.3,
        )
        # 硬过滤：按前端选择的开关剔除LLM自行发挥的未选场景类型
        switch_map = {
            'normal': True,  # 正向永远包含
            'boundary': state.get('include_boundary', True),
            'missing_required': state.get('include_missing_required', True),
            'type_error': state.get('include_type_error', False),
            'exception_status': state.get('include_exception_status', True),
            'security': state.get('include_security', False),
        }
        raw_scenarios = result.get('scenarios', [])
        filtered = [s for s in raw_scenarios if switch_map.get(s.get('scenario_type', ''), True)]
        removed = len(raw_scenarios) - len(filtered)
        if removed > 0:
            logger.info(f"[AI-API] 场景硬过滤: 剔除 {removed} 个未选场景类型")
        result['scenarios'] = filtered
        state['analysis'] = json.dumps(result, ensure_ascii=False)
        logger.info(f"[AI-API] 场景分析完成，规划 {len(filtered)} 个场景")
    except Exception as e:
        logger.error(f"[AI-API] 场景分析失败: {e}")
        state['error'] = f"场景分析失败: {str(e)}"
    return state


# ===== 节点3: 用例生成 =====
def generate_cases(state: GraphState) -> GraphState:
    """LLM为每个场景生成具体override和状态码断言"""
    logger.info(f"[AI-API] 节点3: 用例生成 (重试{state.get('retry_count', 0)})")
    try:
        if state.get('error'):
            return state

        llm = LLMClient(state['ai_config_id'])
        api_summary = state.get('api_doc_summary', {})
        paths = api_summary.get('_paths', {"headers": [], "params": [], "body": []})

        user_prompt = GENERATE_USER.format(
            api_doc_summary=json.dumps(api_summary, ensure_ascii=False, indent=2),
            extra_requirement=state.get('extra_requirement') or "无",
            analysis=state.get('analysis', ''),
            header_paths=paths.get('headers', []),
            param_paths=paths.get('params', []),
            body_paths=paths.get('body', []),
            response_paths=paths.get('response', []),
        )

        result = llm.chat_json(
            GENERATE_SYSTEM.format(generate_count=state.get('generate_count', 3)),
            user_prompt,
            temperature=0.7,
        )

        state['raw_llm_output'] = json.dumps(result, ensure_ascii=False)
        cases = result.get('cases', [])
        logger.info(f"[AI-API] 用例生成完成，共 {len(cases)} 条")
    except Exception as e:
        logger.error(f"[AI-API] 用例生成失败: {e}")
        state['error'] = f"用例生成失败: {str(e)}"
    return state


# ===== 节点4: 校验修复 =====
def validate_and_fix(state: GraphState) -> GraphState:
    """pydantic校验 + 业务校验，失败走LLM修复"""
    logger.info(f"[AI-API] 节点4: 校验用例 (重试{state.get('retry_count', 0)})")
    try:
        if state.get('error'):
            state['result'] = {'success': False, 'cases': [], 'error': state['error']}
            return state

        api_summary = state.get('api_doc_summary', {})
        paths = api_summary.get('_paths', {"headers": [], "params": [], "body": []})

        valid_cases = _validate_cases(state.get('raw_llm_output', '{}'), paths)

        # 如果校验失败且未超过重试次数，走LLM修复
        if not valid_cases and state.get('retry_count', 0) < MAX_RETRIES:
            state['retry_count'] = state.get('retry_count', 0) + 1
            logger.info(f"[AI-API] 校验失败，尝试LLM修复 (第{state['retry_count']}次)")
            try:
                llm = LLMClient(state['ai_config_id'])
                fixed = llm.chat_json(
                    VALIDATE_SYSTEM,
                    VALIDATE_USER.format(
                        header_paths=paths.get('headers', []),
                        param_paths=paths.get('params', []),
                        body_paths=paths.get('body', []),
                        response_paths=paths.get('response', []),
                        extra_requirement=state.get('extra_requirement') or "无",
                        raw_json=state.get('raw_llm_output', '{}'),
                    ),
                    temperature=0.3,
                )
                state['raw_llm_output'] = json.dumps(fixed, ensure_ascii=False)
                valid_cases = _validate_cases(state.get('raw_llm_output', '{}'), paths)
            except Exception as e:
                logger.error(f"[AI-API] LLM修复失败: {e}")

        state['result'] = {
            'success': len(valid_cases) > 0,
            'cases': valid_cases,
            'error': None if valid_cases else "生成用例校验失败",
        }
        logger.info(f"[AI-API] 校验完成，有效用例 {len(valid_cases)} 条")
    except Exception as e:
        logger.error(f"[AI-API] 校验失败: {e}")
        state['retry_count'] = state.get('retry_count', 0) + 1
        state['result'] = {'success': False, 'cases': [], 'error': str(e)}
    return state


def _validate_cases(raw_json: str, paths: dict) -> List[dict]:
    """校验LLM输出，返回valid_cases(list of dict)

    校验项:
    1. pydantic模型校验
    2. override的path必须在参数路径清单内
    3. 同data_driven_group的用例param_structure_same必须全true
    4. 同data_driven_group的用例override的path集合必须一致
    5. missing_required场景的override必须有remove=true
    """
    data = json.loads(raw_json) if isinstance(raw_json, str) else raw_json
    cases_raw = data.get('cases', [])

    header_paths = set(paths.get('headers', []))
    param_paths = set(paths.get('params', []))
    body_paths = set(paths.get('body', []))

    valid_cases = []
    for case_data in cases_raw:
        try:
            case = GeneratedApiCase(**case_data)
        except Exception as e:
            logger.warning(f"[AI-API] 用例校验失败: {case_data.get('name', '未知')} - {e}")
            continue

        # 业务校验: override的path必须在路径清单内
        if not _check_override_paths(case, header_paths, param_paths, body_paths):
            logger.warning(f"[AI-API] 用例override路径越界: {case.name}")
            continue

        # 业务校验: missing_required场景必须有remove=true
        if case.scenario_type == ScenarioType.MISSING_REQUIRED:
            has_remove = any(
                ov.remove for overrides in [
                    case.header_overrides, case.param_overrides, case.body_overrides
                ] for ov in overrides
            )
            if not has_remove:
                logger.warning(f"[AI-API] missing_required场景缺remove=true: {case.name}")
                continue

        # 业务校验: assertions非空
        if not case.assertions:
            logger.warning(f"[AI-API] assertions为空: {case.name}")
            continue

        valid_cases.append(case.model_dump())

    # 校验同data_driven_group一致性
    valid_cases = _check_group_consistency(valid_cases)

    return valid_cases


def _check_override_paths(case: GeneratedApiCase,
                           header_paths: set, param_paths: set, body_paths: set) -> bool:
    """检查override的path是否都在接口参数路径清单内"""
    for ov in case.header_overrides:
        if ov.path not in header_paths:
            return False
    for ov in case.param_overrides:
        if ov.path not in param_paths:
            return False
    for ov in case.body_overrides:
        if ov.path not in body_paths:
            return False
    return True


def _check_group_consistency(cases: List[dict]) -> List[dict]:
    """校验同data_driven_group的用例一致性

    规则:
    1. 同组的 param_structure_same 必须全为 true
    2. 同组的 override path集合必须一致
    不一致的从组里剔除(改data_driven_group=None，降级为独立用例)
    """
    groups: Dict[str, List[dict]] = {}
    for c in cases:
        group = c.get('data_driven_group')
        if not group:
            continue
        groups.setdefault(group, []).append(c)

    result = []
    for c in cases:
        group = c.get('data_driven_group')
        if not group:
            result.append(c)
            continue

        group_members = groups.get(group, [c])
        # 检查param_structure_same全true
        if not all(m.get('param_structure_same') for m in group_members):
            c['data_driven_group'] = None
            result.append(c)
            continue

        # 检查override path集合一致
        ref_paths = _get_override_paths(group_members[0])
        if not all(_get_override_paths(m) == ref_paths for m in group_members[1:]):
            c['data_driven_group'] = None
            result.append(c)
            continue

        result.append(c)

    return result


def _get_override_paths(case_dict: dict) -> frozenset:
    """提取用例所有override的path集合"""
    paths = set()
    for key in ('header_overrides', 'param_overrides', 'body_overrides'):
        for ov in case_dict.get(key, []):
            paths.add(ov.get('path'))
    return frozenset(paths)


# ===== 节点5: 输出 =====
def final_output(state: GraphState) -> GraphState:
    logger.info("[AI-API] 节点5: 输出结果")
    if not state.get('result'):
        state['result'] = {
            'success': False,
            'cases': [],
            'error': state.get('error', '未知错误'),
        }
    return state


# ===== 构建工作流 =====
def build_graph():
    """构建LangGraph工作流"""
    workflow = StateGraph(GraphState)

    workflow.add_node("load_api_doc", load_api_doc)
    workflow.add_node("rag_retrieve", rag_retrieve_for_api)
    workflow.add_node("analyze", analyze_scenarios)
    workflow.add_node("generate", generate_cases)
    workflow.add_node("validate", validate_and_fix)
    workflow.add_node("output", final_output)

    workflow.set_entry_point("load_api_doc")
    workflow.add_edge("load_api_doc", "rag_retrieve")
    workflow.add_edge("rag_retrieve", "analyze")
    workflow.add_edge("analyze", "generate")
    workflow.add_edge("generate", "validate")

    # 条件路由: 校验失败且未超重试次数 → 重新生成
    def should_retry(state: GraphState) -> str:
        if not state or not isinstance(state, dict):
            return "output"
        result = state.get('result') or {}
        if (not result.get('success') and
                state.get('retry_count', 0) < MAX_RETRIES and
                not state.get('error')):
            return "generate"
        return "output"

    workflow.add_conditional_edges("validate", should_retry)
    workflow.add_edge("output", END)

    return workflow.compile()


# ===== 执行入口 =====
def run_generation(api_id: int, project_id: int, ai_config_id: int,
                   module_id: int, tag_ids: list = None,
                   generate_count: int = 3, include_boundary: bool = False,
                   include_missing_required: bool = False, include_type_error: bool = False,
                   include_exception_status: bool = False,
                   include_security: bool = False,
                   extra_requirement: str = "") -> dict:
    """执行AI生成工作流，返回dict格式结果

    返回:
        {
            'success': bool,
            'cases': [GeneratedApiCase.model_dump()],
            'error': str|None,
            'duration': float
        }
    """
    start_time = time.time()
    graph = build_graph()

    initial_state = {
        'api_id': api_id,
        'project_id': project_id,
        'module_id': module_id,
        'tag_ids': tag_ids or [],
        'generate_count': generate_count,
        'include_boundary': include_boundary,
        'include_missing_required': include_missing_required,
        'include_type_error': include_type_error,
        'include_exception_status': include_exception_status,
        'include_security': include_security,
        'extra_requirement': extra_requirement,
        'ai_config_id': ai_config_id,
        'api_doc_summary': None,
        'analysis': None,
        'rag_context': None,
        'raw_llm_output': None,
        'result': None,
        'retry_count': 0,
        'error': None,
    }

    try:
        final_state = graph.invoke(initial_state)
    except Exception as e:
        logger.error(f"[AI-API] LangGraph工作流执行异常: {e}")
        return {
            'success': False,
            'cases': [],
            'error': f"工作流执行异常: {str(e)}",
            'duration': round(time.time() - start_time, 2),
        }

    duration = round(time.time() - start_time, 2)

    # final_state 可能为 None（LangGraph 内部异常时）
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
        f"[AI-API] 生成完成，耗时 {duration}s，"
        f"成功 {len(result.get('cases', []))} 条"
    )
    return result
