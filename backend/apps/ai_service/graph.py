"""
LangGraph工作流 - AI生成功能测试用例
节点: analyze → rag_retrieve → generate → validate → output
"""
import json
import time
import logging
from typing import TypedDict, Optional
from django.conf import settings
from langgraph.graph import StateGraph, END

from apps.ai_service.llm import LLMClient
from apps.ai_service.vectorstore import search_knowledge_base, build_rag_context
from apps.ai_service.schemas import GeneratedFuncCase, StepTableRow, GenerationResult
from apps.ai_service.prompts import (
    ANALYZE_SYSTEM, ANALYZE_USER,
    RAG_CONTEXT_TEMPLATE,
    GENERATE_SYSTEM, GENERATE_USER,
    VALIDATE_SYSTEM, VALIDATE_USER,
)
from apps.envs.models import Module
from apps.tests.models import Tag

logger = logging.getLogger('ai_service')

MAX_RETRIES = settings.AI_MAX_RETRIES


class GraphState(TypedDict):
    requirement: str
    project_id: int
    module_id: Optional[int]
    tag_ids: list
    generate_count: int
    include_boundary: bool
    include_exception: bool
    include_performance: bool
    ai_config_id: int
    analysis: Optional[str]
    similar_cases: Optional[str]
    raw_llm_output: Optional[str]
    result: Optional[dict]
    retry_count: int
    error: Optional[str]


def _get_module_info(module_id: Optional[int]) -> str:
    if not module_id:
        return "未指定模块"
    try:
        module = Module.objects.get(id=module_id)
        return f"模块: {module.name}"
    except Module.DoesNotExist:
        return "未指定模块"


def _get_tag_info(tag_ids: list) -> str:
    if not tag_ids:
        return "无标签"
    tags = Tag.objects.filter(id__in=tag_ids)
    return "标签: " + ", ".join([t.name for t in tags])


def _build_extra_requirements(state: GraphState) -> str:
    parts = []
    if state.get('include_boundary'):
        parts.append("- 必须包含边界值测试场景")
    if state.get('include_exception'):
        parts.append("- 必须包含异常和错误处理测试场景")
    if state.get('include_performance'):
        parts.append("- 包含性能和安全相关测试场景")
    return "\n".join(parts) if parts else ""


# ===== 节点1: 需求分析 =====
def analyze_requirement(state: GraphState) -> GraphState:
    logger.info(f"[AI] 节点1: 需求分析 - 项目{state['project_id']}")
    try:
        llm = LLMClient(state['ai_config_id'])
        extra = _build_extra_requirements(state)
        user_prompt = ANALYZE_USER.format(
            requirement=state['requirement'],
            extra_requirements=extra,
        )
        result = llm.chat_json(ANALYZE_SYSTEM, user_prompt, temperature=0.3)
        state['analysis'] = json.dumps(result, ensure_ascii=False)
        
        # 根据功能点数量动态调整生成用例数
        feature_count = len(result.get('feature_points', []))
        original_count = state.get('generate_count', 3)
        if feature_count >= 6:
            adjusted_count = min(feature_count, 8)  # 最多8条
        elif feature_count >= 3:
            adjusted_count = min(feature_count + 1, 6)  # 3-5条
        else:
            adjusted_count = original_count
        
        if adjusted_count != original_count:
            logger.info(f"[AI] 功能点{feature_count}个，调整生成数量: {original_count} → {adjusted_count}")
            state['generate_count'] = adjusted_count
        
        logger.info(f"[AI] 需求分析完成: {result.get('feature_points', [])}")
    except Exception as e:
        logger.warning(f"[AI] 需求分析失败(降级处理): {e}")
        # 降级：分析失败时用原始需求文本代替，不阻断后续流程
        state['analysis'] = json.dumps({
            'feature_points': [state['requirement']],
            'risk_points': [],
            'test_strategy': '基于原始需求文本生成',
            'raw_requirement': state['requirement'],
        }, ensure_ascii=False)
        state['error'] = f"需求分析LLM调用失败: {str(e)}"
    return state


# ===== 节点2: RAG检索 =====
def rag_retrieve(state: GraphState) -> GraphState:
    logger.info(f"[AI] 节点2: RAG知识库检索")
    try:
        # 使用混合检索：同时搜索功能用例 + 接口文档 + 已解决缺陷
        similar = search_knowledge_base(
            project_id=state['project_id'],
            query=state['requirement'],
            module_id=state.get('module_id'),
            top_k=5,
        )
        if similar:
            # 使用新的build_rag_context构建带数据源标签的上下文
            state['similar_cases'] = build_rag_context(similar, max_items=5)
            source_types = set(item['metadata'].get('source_type', '') for item in similar)
            logger.info(f"[AI] RAG检索到 {len(similar)} 条知识库内容，来源: {source_types}")
        else:
            state['similar_cases'] = "暂无相似用例参考"
            logger.info("[AI] RAG无检索结果")
    except Exception as e:
        logger.warning(f"[AI] RAG检索失败(非致命): {e}")
        state['similar_cases'] = "RAG检索失败，跳过参考"
    return state


# ===== 节点3: 用例生成 =====
def generate_cases(state: GraphState) -> GraphState:
    logger.info(f"[AI] 节点3: 生成用例 (重试{state.get('retry_count', 0)})")
    try:
        if state.get('error') and 'LLM调用失败' in state.get('error', ''):
            logger.warning("[AI] LLM不可用，跳过生成")
            state['result'] = {
                'success': False,
                'cases': [],
                'error': state.get('error', 'LLM调用失败'),
            }
            return state

        llm = LLMClient(state['ai_config_id'])
        module_info = _get_module_info(state.get('module_id'))
        tag_info = _get_tag_info(state.get('tag_ids', []))

        user_prompt = GENERATE_USER.format(
            analysis=state.get('analysis', ''),
            module_info=module_info,
            tag_info=tag_info,
            rag_context=state.get('similar_cases', ''),
            generate_count=state.get('generate_count', 3),
        )

        result = llm.chat_json(GENERATE_SYSTEM.format(
            generate_count=state.get('generate_count', 3)
        ), user_prompt, temperature=0.7)

        state['raw_llm_output'] = json.dumps(result, ensure_ascii=False)
        logger.info(f"[AI] 用例生成完成，共 {len(result.get('cases', []))} 条")
    except Exception as e:
        logger.error(f"[AI] 用例生成失败: {e}")
        state['error'] = f"用例生成失败: {str(e)}"
    return state


# ===== 节点4: 校验修复 =====
def validate_and_fix(state: GraphState) -> GraphState:
    logger.info(f"[AI] 节点4: 校验用例 (重试{state.get('retry_count', 0)})")
    try:
        # 如果已经有result了（如LLM不可用的降级结果），直接跳过
        if state.get('result'):
            return state

        if state.get('error'):
            return state

        raw = state.get('raw_llm_output', '{}')
        data = json.loads(raw) if isinstance(raw, str) else raw
        cases = data.get('cases', [])

        valid_cases = []
        has_error = False

        for case_data in cases:
            try:
                case = GeneratedFuncCase(**case_data)
                # 校验step_table非空
                if case.step_type == 2 and not case.step_table:
                    has_error = True
                    continue
                valid_cases.append(case.model_dump())
            except Exception as e:
                logger.warning(f"[AI] 用例校验失败: {case_data.get('name', '未知')} - {e}")
                has_error = True

        # 如果有错误且未超过重试次数，走修复
        if has_error and state.get('retry_count', 0) < MAX_RETRIES:
            state['retry_count'] = state.get('retry_count', 0) + 1
            logger.info(f"[AI] 校验发现问题，尝试LLM修复 (第{state['retry_count']}次)")
            try:
                llm = LLMClient(state['ai_config_id'])
                fixed = llm.chat_json(VALIDATE_SYSTEM, VALIDATE_USER.format(raw_json=raw), temperature=0.3)
                state['raw_llm_output'] = json.dumps(fixed, ensure_ascii=False)
                # 递归再校验一次
                fixed_cases = fixed.get('cases', [])
                valid_cases = []
                for case_data in fixed_cases:
                    try:
                        case = GeneratedFuncCase(**case_data)
                        if case.step_type == 2 and not case.step_table:
                            continue
                        valid_cases.append(case.model_dump())
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"[AI] LLM修复失败: {e}")

        state['result'] = {
            'success': len(valid_cases) > 0,
            'cases': valid_cases,
            'error': None if valid_cases else "生成用例校验失败",
        }
        logger.info(f"[AI] 校验完成，有效用例 {len(valid_cases)} 条")
    except Exception as e:
        logger.error(f"[AI] 校验失败: {e}")
        state['result'] = {'success': False, 'cases': [], 'error': str(e)}
    return state


# ===== 节点5: 输出 =====
def final_output(state: GraphState) -> GraphState:
    logger.info("[AI] 节点5: 输出结果")
    result = state.get('result')
    if not result:
        result = {
            'success': False,
            'cases': [],
            'error': state.get('error') or '未知错误',
        }
    state['result'] = result
    return state


# ===== 构建工作流 =====
def build_graph():
    """构建LangGraph工作流"""
    workflow = StateGraph(GraphState)

    workflow.add_node("analyze", analyze_requirement)
    workflow.add_node("rag_retrieve", rag_retrieve)
    workflow.add_node("generate", generate_cases)
    workflow.add_node("validate", validate_and_fix)
    workflow.add_node("output", final_output)

    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "rag_retrieve")
    workflow.add_edge("rag_retrieve", "generate")
    workflow.add_edge("generate", "validate")

    # 条件路由：校验失败且未超重试次数 → 重新生成
    def should_retry(state: GraphState) -> str:
        result = state.get('result') or {}
        if (not result.get('success', False) and
                state.get('retry_count', 0) < MAX_RETRIES and
                not state.get('error')):
            return "generate"
        return "output"

    workflow.add_conditional_edges("validate", should_retry)
    workflow.add_edge("output", END)

    return workflow.compile()


# ===== 执行入口 =====
def run_generation(requirement: str, project_id: int, ai_config_id: int,
                   module_id: Optional[int] = None, tag_ids: list = None,
                   generate_count: int = 3, include_boundary: bool = True,
                   include_exception: bool = True, include_performance: bool = False) -> dict:
    """执行AI生成工作流"""
    start_time = time.time()
    graph = build_graph()

    initial_state = {
        'requirement': requirement,
        'project_id': project_id,
        'module_id': module_id,
        'tag_ids': tag_ids or [],
        'generate_count': generate_count,
        'include_boundary': include_boundary,
        'include_exception': include_exception,
        'include_performance': include_performance,
        'ai_config_id': ai_config_id,
        'analysis': None,
        'similar_cases': None,
        'raw_llm_output': None,
        'result': None,
        'retry_count': 0,
        'error': None,
    }

    final_state = graph.invoke(initial_state)
    duration = round(time.time() - start_time, 2)

    result = final_state.get('result', {})
    result['duration'] = duration

    logger.info(f"[AI] 生成完成，耗时 {duration}s，成功 {len(result.get('cases', []))} 条")
    return result
