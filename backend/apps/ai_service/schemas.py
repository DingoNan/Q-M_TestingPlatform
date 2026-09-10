from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class StepTableRow(BaseModel):
    """表格步骤行"""
    step_desc: str = Field(..., description="步骤描述")
    step_exp: str = Field(..., description="预期结果")


class GeneratedFuncCase(BaseModel):
    """AI生成的功能用例结构 - 与FuncCase模型对齐"""
    name: str = Field(..., max_length=50, description="用例名称")
    module_id: Optional[int] = Field(None, description="所属模块ID")
    tag_ids: List[int] = Field(default_factory=list, description="标签ID列表")
    setup_condition: str = Field(default="", description="前置条件")
    case_mark: str = Field(default="AI生成，待人工审核", description="用例备注")
    step_type: int = Field(default=2, description="步骤类型: 1=文本, 2=表格")
    step_text: Optional[str] = Field(None, description="文本步骤描述")
    exp_text: Optional[str] = Field(None, description="文本期望结果")
    step_table: List[StepTableRow] = Field(default_factory=list, description="表格步骤")
    can_autoed: int = Field(default=3, description="是否可自动化: 1=全自动, 2=半自动, 3=手工")
    auto_status: int = Field(default=4, description="自动化状态: 4=手工测试")


class GenerationResult(BaseModel):
    """生成结果"""
    success: bool = Field(..., description="是否成功")
    cases: List[GeneratedFuncCase] = Field(default_factory=list, description="生成的用例列表")
    error: Optional[str] = Field(None, description="错误信息")
    duration: float = Field(default=0, description="耗时(秒)")


# ===== LangGraph State =====

class GraphState(BaseModel):
    """LangGraph工作流状态"""
    # 输入
    requirement: str = Field(..., description="用户需求描述")
    project_id: int = Field(..., description="项目ID")
    module_id: Optional[int] = Field(None, description="模块ID")
    tag_ids: List[int] = Field(default_factory=list, description="标签ID列表")
    generate_count: int = Field(default=3, description="生成条数")
    include_boundary: bool = Field(default=True, description="包含边界场景")
    include_exception: bool = Field(default=True, description="包含异常场景")
    include_performance: bool = Field(default=False, description="包含性能安全场景")

    # LLM配置
    ai_config_id: int = Field(..., description="AiConfig表记录ID")

    # 中间状态
    analysis: Optional[str] = Field(None, description="测试范围分析结果")
    similar_cases: Optional[str] = Field(None, description="RAG召回的相似用例")
    raw_llm_output: Optional[str] = Field(None, description="LLM原始输出")

    # 输出
    result: Optional[GenerationResult] = Field(None, description="生成结果")
    retry_count: int = Field(default=0, description="校验重试次数")
    error: Optional[str] = Field(None, description="错误信息")
