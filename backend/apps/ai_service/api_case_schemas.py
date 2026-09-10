"""
AI生成接口自动化用例 - 数据结构定义
与 FuncCase 的 schema 分离，目标结构是 Case + CaseSteps + Step(type=Request)
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any
from enum import Enum


# check.py中可用的断言方法白名单(与core.com.check.CHECK_FUNC_MAP一致)
CHECK_METHODS = (
    'check_equal', 'check_not_equal',
    'check_number_equal', 'check_number_not_equal',
    'check_number_gt', 'check_number_ge', 'check_number_lt', 'check_number_le',
    'check_bool_equal', 'check_bool_not_equal',
    'check_object_is_empty', 'check_object_is_not_empty',
    'no_check',
)


class ScenarioType(str, Enum):
    """场景类型，用于落库时判定走数据驱动还是独立用例"""
    NORMAL = "normal"                       # 正向场景，参数合法
    BOUNDARY = "boundary"                   # 边界值，参数结构不变，值变
    MISSING_REQUIRED = "missing_required"   # 缺必填字段，参数结构变化
    TYPE_ERROR = "type_error"               # 类型错误，参数结构不变，值类型错
    EXCEPTION_STATUS = "exception_status"   # 异常状态码处理，参数结构不变


class ParamOverride(BaseModel):
    """单个参数的覆盖值

    path: 参数路径，叶子节点名或嵌套路径(用点号连接，如 'address.city')
    value: 覆盖值，始终用字符串表示(如 "123" / "true" / "")，后端按type转换
    type: 值类型(仅body_overrides需要填)，可选: string/boolean/array/object/number/null
          非string类型时必填，string类型可省略
    is_null: 是否显式置空(用于测试空值场景)
    remove: 是否移除该字段(用于缺必填字段场景)
    """
    path: str = Field(..., description="参数路径，如 'userId' 或 'address.city'")
    value: Any = Field(None, description="覆盖值，用字符串表示，后端按type转换")
    type: Optional[str] = Field(
        None,
        description="值类型，可选: string/boolean/array/object/number/null "
                    "(仅body_overrides非string类型时必填)"
    )
    is_null: bool = Field(False, description="是否置空")
    remove: bool = Field(False, description="是否移除该字段")


class AssertionCheck(BaseModel):
    """完整断言

    method: check.py中的断言方法名(如 check_equal/check_number_equal等)
    exp_value: 预期值(字面量，如 200 / "success" / true)
    act_field: 实际值引用字段路径(如 apiStatusCode / apiResponseBody.code)
    desc: 断言说明

    后端落库时把 act_field 转成 ${stepResponse.{case_step_id}.{act_field}}，
    method 直接作为 check_params 的 method 字段。
    """
    method: str = Field(
        ...,
        description="断言方法名，可选值: " + '/'.join(CHECK_METHODS)
    )
    exp_value: Any = Field(..., description="预期值(字面量)")
    act_field: str = Field(
        ...,
        description="实际值引用字段路径，如 apiStatusCode / apiResponseBody.code / apiResponseBody.data.id"
    )
    desc: str = Field("", description="断言说明")

    @field_validator('method')
    @classmethod
    def _validate_method(cls, v: str) -> str:
        """拦截白名单外的断言方法(如 check_text_equal)，避免落库后执行时报KeyError"""
        if v not in CHECK_METHODS:
            raise ValueError(
                f"断言方法 {v!r} 不在白名单中，必须为: {', '.join(CHECK_METHODS)}")
        return v


class GeneratedApiCase(BaseModel):
    """AI生成的单条接口用例

    设计原则: LLM只产出"场景+值"，不产出参数树结构。
    参数树结构由后端落库时从Api表深拷贝而来，再把override贴上去。
    """
    name: str = Field(..., max_length=50, description="用例名称(<=50字符)")
    desc: str = Field("", description="步骤描述")
    scenario_type: ScenarioType = Field(..., description="场景类型")
    scenario_desc: str = Field("", description="场景说明，给用户看的自然语言")

    # 参数结构是否与接口文档完全一致(决定能否合并到数据驱动)
    # True: 同 data_driven_group 的多条用例会合并到同一 Case.data
    # False: 即使 group 相同也走独立用例
    param_structure_same: bool = Field(
        True, description="参数结构是否与文档一致(影响数据驱动判定)"
    )

    # 数据驱动分组标记
    # 同group且param_structure_same=True的多条用例合并到一个Case.data
    # None或空表示独立用例
    data_driven_group: Optional[str] = Field(
        None, description="数据驱动分组key，相同则合并到同一Case"
    )

    # 请求参数覆盖(只覆盖部分字段，其余用文档示例值)
    header_overrides: List[ParamOverride] = Field(
        default_factory=list, description="请求头覆盖"
    )
    param_overrides: List[ParamOverride] = Field(
        default_factory=list, description="查询参数覆盖"
    )
    body_overrides: List[ParamOverride] = Field(
        default_factory=list, description="请求体覆盖(headers/params/body按body_type选其一)"
    )

    # 完整断言列表(状态码+响应体字段等)
    assertions: List[AssertionCheck] = Field(
        default_factory=list, description="断言列表，每条包含method/exp_value/act_field"
    )


class GenerationResult(BaseModel):
    """生成结果"""
    success: bool = Field(..., description="是否成功")
    cases: List[GeneratedApiCase] = Field(
        default_factory=list, description="生成的用例列表"
    )
    error: Optional[str] = Field(None, description="错误信息")
    duration: float = Field(default=0, description="耗时(秒)")


# ===== LangGraph State =====

class GraphState(BaseModel):
    """接口用例生成的LangGraph工作流状态

    与 graph.py 里的 FuncCase GraphState 分离，避免字段语义混淆。
    """
    # 输入
    api_id: int = Field(..., description="接口文档ID(Api表)")
    project_id: int = Field(..., description="项目ID")
    module_id: int = Field(..., description="用例模块ID(Module表, 决定Step.plant)")
    tag_ids: List[int] = Field(default_factory=list, description="标签ID列表")
    generate_count: int = Field(default=3, description="生成条数")
    include_boundary: bool = Field(default=False, description="包含边界场景")
    include_missing_required: bool = Field(
        default=False, description="包含缺必填字段场景"
    )
    include_type_error: bool = Field(default=False, description="包含类型错误场景")
    include_exception_status: bool = Field(
        default=False, description="包含异常状态码场景"
    )
    include_security: bool = Field(
        default=False, description="包含安全性场景(SQL注入/XSS/命令注入等)"
    )
    extra_requirement: str = Field(default="", description="补充需求文本")

    # LLM配置
    ai_config_id: int = Field(..., description="AiConfig表记录ID")

    # 中间状态
    api_doc_summary: Optional[dict] = Field(
        None, description="load_api_doc节点产出的接口文档摘要"
    )
    analysis: Optional[str] = Field(None, description="analyze节点产出的场景分析JSON")
    raw_llm_output: Optional[str] = Field(
        None, description="generate节点产出的LLM原始输出JSON"
    )

    # 输出
    result: Optional[dict] = Field(None, description="最终结果dict(GenerationResult序列化)")
    retry_count: int = Field(default=0, description="校验重试次数")
    error: Optional[str] = Field(None, description="错误信息")
