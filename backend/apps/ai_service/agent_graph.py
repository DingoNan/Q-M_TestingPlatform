"""
AI助手 Agent - LangGraph ReAct 工作流
节点: agent(LLM决策) ↔ tools(执行ORM查询) → END

支持SSE流式输出:
  1. LLM决定调用工具时，向前端推送tool_status事件
  2. 工具执行完毕后回到agent继续推理
  3. 最终回答通过content事件逐字流式输出
"""
import json
import logging
from typing import TypedDict, Optional, Generator

from langgraph.graph import StateGraph, END

from apps.ai_service.llm import LLMClient
from apps.ai_service.agent_tools import ALL_TOOLS

logger = logging.getLogger('ai_service')

MAX_ITERATIONS = 6  # 最大工具调用轮次，防止死循环


# ===== 状态定义 =====
class AgentState(TypedDict):
    messages: list  # OpenAI格式的消息列表
    project_id: int
    ai_config_id: int
    iteration: int
    final_answer: Optional[str]


# ===== 工具格式转换 =====
def tools_to_openai_format(tools) -> list:
    """将LangChain Tool列表转为OpenAI function calling格式，并移除project_id参数（由系统自动注入）"""
    import copy
    result = []
    for t in tools:
        params = t.args if hasattr(t, 'args') else {}
        params = copy.deepcopy(params) if isinstance(params, dict) else {}
        # 确保type字段存在
        if isinstance(params, dict) and 'type' not in params:
            params = {'type': 'object', 'properties': params.get('properties', {}), 'required': params.get('required', [])}
        # 移除project_id：由系统自动注入，不暴露给LLM
        if isinstance(params, dict):
            props = params.get('properties', {})
            if 'project_id' in props:
                del props['project_id']
                params['properties'] = props
            req = params.get('required', [])
            if 'project_id' in req:
                params['required'] = [r for r in req if r != 'project_id']
        result.append({
            'type': 'function',
            'function': {
                'name': t.name,
                'description': t.description or '',
                'parameters': params,
            }
        })
    return result


def tools_to_map(tools) -> dict:
    """工具名→工具对象映射"""
    return {t.name: t for t in tools}


# ===== LangGraph节点定义 =====
def agent_node(state: AgentState) -> AgentState:
    """Agent节点：调用LLM（非流式），决定是否调用工具"""
    llm = LLMClient(state['ai_config_id'])
    openai_tools = tools_to_openai_format(ALL_TOOLS)

    response = llm.client.chat.completions.create(
        model=llm.model,
        messages=state['messages'],
        tools=openai_tools,
        temperature=0.7,
    )
    msg = response.choices[0].message
    # 转为dict格式存入messages
    msg_dict = {'role': 'assistant', 'content': msg.content or ''}
    if msg.tool_calls:
        msg_dict['tool_calls'] = [
            {
                'id': tc.id,
                'type': 'function',
                'function': {'name': tc.function.name, 'arguments': tc.function.arguments},
            }
            for tc in msg.tool_calls
        ]
    state['messages'].append(msg_dict)
    state['iteration'] += 1
    return state


def tools_node(state: AgentState) -> AgentState:
    """工具执行节点：执行LLM选择的工具调用"""
    tool_map = tools_to_map(ALL_TOOLS)
    last_msg = state['messages'][-1]
    tool_calls = last_msg.get('tool_calls', [])

    for tc in tool_calls:
        func_name = tc['function']['name']
        try:
            args = json.loads(tc['function']['arguments'])
        except json.JSONDecodeError:
            args = {}

        # 强制注入project_id（所有工具都需要）
        args['project_id'] = state['project_id']

        logger.info(f"[Agent] 执行工具: {func_name}({args})")
        try:
            result = tool_map[func_name].invoke(args)
            logger.info(f"[Agent] 工具结果: {result[:200]}")
        except Exception as e:
            logger.error(f"[Agent] 工具执行失败: {func_name} - {e}")
            result = f"工具执行失败: {str(e)}"

        state['messages'].append({
            'role': 'tool',
            'tool_call_id': tc['id'],
            'content': str(result),
        })

    return state


def should_continue(state: AgentState) -> str:
    """条件路由：有tool_calls则继续调用工具，否则结束"""
    last_msg = state['messages'][-1]
    if last_msg.get('role') == 'assistant' and last_msg.get('tool_calls'):
        if state['iteration'] >= MAX_ITERATIONS:
            logger.warning(f"[Agent] 达到最大轮次 {MAX_ITERATIONS}，强制结束")
            return 'end'
        return 'tools'
    return 'end'


def build_graph():
    """构建LangGraph Agent工作流"""
    workflow = StateGraph(AgentState)
    workflow.add_node('agent', agent_node)
    workflow.add_node('tools', tools_node)
    workflow.set_entry_point('agent')
    workflow.add_conditional_edges('agent', should_continue, {'tools': 'tools', 'end': END})
    workflow.add_edge('tools', 'agent')
    return workflow.compile()


# ===== SSE流式执行入口 =====
def run_agent_stream(messages: list, project_id: int, ai_config_id: int) -> Generator[str, None, str]:
    """
    流式执行Agent，生成SSE事件。

    Args:
        messages: OpenAI格式消息列表（含system prompt和历史对话）
        project_id: 项目ID
        ai_config_id: AI模型配置ID

    Yields:
        SSE格式的data行，如:
          data: {"content": "你好"}    - 文本内容（逐字）
          data: {"tool_status": "正在查询: query_func_cases"}  - 工具状态
          data: {"done": true}         - 结束
          data: {"error": "..."}       - 错误

    Returns:
        完整的AI回复文本
    """
    llm = LLMClient(ai_config_id)
    openai_tools = tools_to_openai_format(ALL_TOOLS)
    tool_map = tools_to_map(ALL_TOOLS)

    # 复制一份消息，避免修改原始列表
    work_messages = list(messages)
    iteration = 0
    full_response = []

    try:
        while iteration < MAX_ITERATIONS:
            iteration += 1
            logger.info(f"[Agent] 第{iteration}轮调用LLM，消息数: {len(work_messages)}")

            # 流式调用LLM（带工具定义）
            stream = llm.client.chat.completions.create(
                model=llm.model,
                messages=work_messages,
                tools=openai_tools,
                temperature=0.7,
                stream=True,
            )

            # 累积流式响应
            content_parts = []
            tool_calls_accum = {}  # index → {id, name, arguments}

            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                # 累积文本内容
                if delta.content:
                    content_parts.append(delta.content)
                    yield f"data: {json.dumps({'content': delta.content}, ensure_ascii=False)}\n\n"

                # 累积工具调用
                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_calls_accum:
                            tool_calls_accum[idx] = {'id': '', 'name': '', 'arguments': ''}
                        if tc_delta.id:
                            tool_calls_accum[idx]['id'] = tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                tool_calls_accum[idx]['name'] = tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_calls_accum[idx]['arguments'] += tc_delta.function.arguments

            # 检查是否有工具调用
            if tool_calls_accum:
                # 构建assistant消息（含tool_calls）
                assistant_msg = {
                    'role': 'assistant',
                    'content': ''.join(content_parts) or None,
                    'tool_calls': [
                        {
                            'id': tc['id'],
                            'type': 'function',
                            'function': {'name': tc['name'], 'arguments': tc['arguments']},
                        }
                        for tc in tool_calls_accum.values()
                    ]
                }
                work_messages.append(assistant_msg)

                # 执行每个工具调用
                for tc in tool_calls_accum.values():
                    func_name = tc['name']
                    # 推送工具状态事件
                    yield f"data: {json.dumps({'tool_status': f'正在查询: {func_name}'}, ensure_ascii=False)}\n\n"

                    try:
                        args = json.loads(tc['arguments']) if tc['arguments'] else {}
                    except json.JSONDecodeError:
                        args = {}

                    # 强制注入project_id（所有工具都需要）
                    args['project_id'] = project_id

                    logger.info(f"[Agent] 执行工具: {func_name}({args})")
                    try:
                        tool_obj = tool_map.get(func_name)
                        if not tool_obj:
                            result = f"工具 {func_name} 不存在"
                        else:
                            result = tool_obj.invoke(args)
                        logger.info(f"[Agent] 工具返回: {result[:200] if isinstance(result, str) else str(result)[:200]}")
                    except Exception as e:
                        logger.error(f"[Agent] 工具执行失败: {func_name} - {e}")
                        result = f"工具执行失败: {str(e)}"

                    work_messages.append({
                        'role': 'tool',
                        'tool_call_id': tc['id'],
                        'content': str(result),
                    })

                # 继续下一轮，让LLM基于工具结果继续推理
                continue
            else:
                # 没有工具调用，说明LLM已生成最终回答（文本已流式输出）
                full_response = content_parts
                break

        if iteration >= MAX_ITERATIONS and not full_response:
            fallback = "抱歉，我在处理您的问题时超过了最大查询次数限制，请尝试缩小问题范围后重试。"
            yield f"data: {json.dumps({'content': fallback}, ensure_ascii=False)}\n\n"
            full_response = [fallback]

        return ''.join(full_response)

    except Exception as e:
        logger.error(f"[Agent] 流式执行失败: {e}", exc_info=True)
        yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        return ''
