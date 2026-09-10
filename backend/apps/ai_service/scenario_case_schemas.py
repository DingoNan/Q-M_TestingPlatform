"""
AI从功能用例生成场景自动化脚本 - 数据结构定义

与 api_case_schemas 的差异:
- 输入是 FuncCase(功能用例) 而非 Api(接口文档)
- 产物是步骤树(含逻辑控制器) + 可选前置接口造数据
- 支持两种模式: api(接口自动化) / web_ui(WebUI自动化)
- 变量引用使用占位符 {sN.字段路径}, 落库时由 saver 替换为 ${stepResponse.{case_step_id}.{字段路径}}

步骤树示例:
{
  "steps": [
    {"step_type": "api", "desc": "创建会议室", "api_name": "创建会议室接口", ...},
    {"step_type": "control", "keyword": "IF", "desc": "创建成功则预订",
     "condition": "{s1.apiResponseBody.code} 等于 200",
     "children": [{"step_type": "web", "desc": "点击预订按钮", "keyword": "click", "element_name": "预订按钮"}]},
    {"step_type": "control", "keyword": "SLEEP", "desc": "等待弹窗", "timeout": 2}
  ]
}
"""
from typing import List, Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field

from apps.ai_service.api_case_schemas import ParamOverride, AssertionCheck


class ScenarioType(str, Enum):
    """场景类型"""
    NORMAL = "normal"        # 正向场景
    BOUNDARY = "boundary"    # 边界场景
    ABNORMAL = "abnormal"    # 异常/反例场景


class ApiStep(BaseModel):
    """接口调用步骤"""
    desc: str = Field("", description="步骤描述")
    api_name: str = Field(..., description="接口名称，必须在项目接口库中存在")
    headers_override: List[ParamOverride] = Field(
        default_factory=list, description="请求头覆盖")
    params_override: List[ParamOverride] = Field(
        default_factory=list, description="查询参数覆盖")
    body_override: List[ParamOverride] = Field(
        default_factory=list, description="请求体覆盖(按body_type选其一)")
    assertions: List[AssertionCheck] = Field(
        default_factory=list, description="接口断言，act_field用{sN.}占位符引用")


class WebParam(BaseModel):
    """WebUI动作参数(映射到func_params)"""
    name: str = Field(..., description="参数名，与Playwright动作签名一致，如 value/uri/text/keys")
    value: str = Field(..., description="参数值，支持${变量}和{sN.}引用以及f{函数}动态生成")
    value_type: Literal['Str', 'Int', 'Bool', 'Float'] = Field(
        'Str', description="参数值类型，默认Str")


class WebStep(BaseModel):
    """WebUI操作步骤"""
    desc: str = Field("", description="步骤描述")
    keyword: str = Field(..., description="Playwright动作名，必须在下发的动作白名单中")
    element_name: str = Field("", description="元素名称，必须在项目元素库中存在(浏览器动作可不填)")
    params: List[WebParam] = Field(
        default_factory=list, description="动作参数列表(不含元素)，如 fill 的 value、goto 的 uri")
    element_index: int = Field(0, description="元素索引，默认0")
    assertion: Optional[AssertionCheck] = Field(
        None, description="页面断言，act_field用{sN.}占位符引用，仅对取值类动作生效")


class ControlStep(BaseModel):
    """逻辑控制器节点"""
    keyword: Literal['IF', 'FOR', 'WHILE', 'SLEEP', 'TRANSACTION', 'FOREACH'] = Field(
        ..., description="控制器类型")
    desc: str = Field("", description="控制器说明")
    conditions: List[AssertionCheck] = Field(
        default_factory=list, description="IF/WHILE条件(act_field用{sN.}占位符)，仅IF/WHILE必填")
    loop_times: int = Field(0, description="FOR循环次数")
    max_loop_times: int = Field(0, description="WHILE最大循环次数，防止死循环")
    timeout: float = Field(0, description="SLEEP等待秒数")
    loop_var: str = Field("", description="FOREACH遍历的变量引用，如 {s1.apiResponseBody.data.list}")
    children: List["StepNode"] = Field(default_factory=list, description="子步骤，仅IF/FOR/WHILE/TRANSACTION/FOREACH使用")


class StepNode(BaseModel):
    """递归步骤节点"""
    step_type: Literal['api', 'web', 'control'] = Field(..., description="步骤类型")
    api: Optional[ApiStep] = Field(None, description="api类型时必填")
    web: Optional[WebStep] = Field(None, description="web类型时必填")
    control: Optional[ControlStep] = Field(None, description="control类型时必填")


ControlStep.model_rebuild()


class GeneratedScenarioCase(BaseModel):
    """AI生成的单条场景脚本用例"""
    name: str = Field(..., max_length=50, description="用例名称(<=50字符)")
    desc: str = Field("", description="用例说明")
    scenario_type: ScenarioType = Field(..., description="场景类型")
    steps: List[StepNode] = Field(
        default_factory=list, description="步骤树，最多支持两层控制器嵌套")


class GenerationResult(BaseModel):
    """生成结果"""
    success: bool = Field(..., description="是否成功")
    cases: List[GeneratedScenarioCase] = Field(
        default_factory=list, description="生成的用例列表")
    error: Optional[str] = Field(None, description="错误信息")
    duration: float = Field(default=0, description="耗时(秒)")


# ===== LangGraph State =====

class GraphState(BaseModel):
    """场景脚本生成的LangGraph工作流状态"""
    # 输入
    func_case_id: int = Field(..., description="功能用例ID")
    project_id: int = Field(..., description="项目ID")
    module_id: int = Field(..., description="用例模块ID(Module表, 决定Step.plant)")
    mode: Literal['api', 'web_ui'] = Field(..., description="生成模式")
    generate_count: int = Field(default=3, description="生成条数")
    ai_config_id: int = Field(..., description="AiConfig表记录ID")
    tag_ids: List[int] = Field(default_factory=list, description="标签ID列表")
    extra_requirement: str = Field(default="", description="补充需求文本")

    # 中间状态
    func_case_summary: Optional[dict] = Field(
        None, description="load_func_case节点产出的功能用例摘要")
    resources: Optional[list] = Field(
        None, description="load_resources节点产出的资产清单(接口或元素)")
    raw_llm_output: Optional[str] = Field(
        None, description="generate节点产出的LLM原始输出JSON")

    # 输出
    result: Optional[dict] = Field(None, description="最终结果dict(GenerationResult序列化)")
    retry_count: int = Field(default=0, description="校验重试次数")
    error: Optional[str] = Field(None, description="错误信息")
