from pydantic import BaseModel
from typing import List, Any, Union


class StepResponse(BaseModel):
    stepParams: Any
    apiHost: Any
    apiUri: Any
    apiUrl: Any
    apiMethod: Any
    apiRequestHeaders: Any
    apiRequestParams: Any
    apiRequestBody: Any
    apiStatusCode: Any
    apiResponseHeaders: Any
    apiResponseCookies: Any
    apiResponseBody: Any
    funcParams: Any
    funcReturn: Any
    runTimes: Any
    runElement: Any


class CaseParams(BaseModel):
    # 用例执行过程中用来存储环境变量
    globalParams: dict
    # 用例执行过程中用来存储环境变量
    envParams: dict
    # 用例执行过程中用来存储用例变量
    caseParams: dict
    caseData: dict
    # 用来存续步骤执行过程中步骤的结果值
    stepResponse: dict


class SuiteCondition(BaseModel):
    method: int
    value: Any
    andOr: str


class ApiHeadersModel(BaseModel):
    key: str
    value: str


class CheckModel(BaseModel):
    method: str
    exp: Any
    act: Any
    type: str


class RunModel(BaseModel):
    method: str
    exp: Any
    act: Any
    type: str
    andOr: str


class LoopModel(BaseModel):
    exp: Any
    type: str


class ApiExtractModel(BaseModel):
    key: str
    value: str


class FuncExtractModel(BaseModel):
    key: str


class ParamsModel(BaseModel):
    value: Any
    type: str


class StepModel(BaseModel):
    desc: str  # 步骤描述
    key: list  # 步骤类型和对应的key
    api_headers: Union[List[ApiHeadersModel], List]  # 接口请求头
    api_body: str  # 接口请求体
    step_after: bool  # 退出while循环的条件判断是在执行步骤前还是执行步骤后
    body_type: str  # 接口请求类型
    body_type: str  # 接口请求类型
    api_params: list  # 接口查询参数
    extract: Union[List[ApiExtractModel], List[FuncExtractModel], List]  # 步骤数据提取
    check: Union[List[CheckModel], List]  # 步骤断言
    params: Union[List[ParamsModel], List]  # 函数入参
    run: Union[List[RunModel], List]  # 是否执行该步骤
    loop: Union[List[LoopModel], List]  # 循环执行该步骤
    until: Union[List[RunModel], List]  # while条件判断语句


class SeleniumStepType:
    All = 0  # 全部操作
    DriverAction = 1  # 浏览器操作
    ElementAction = 2  # 元素操作
    MouseAction = 3  # 鼠标操作
    KeyboardAction = 4  # 键盘操作
    WaitAction = 5  # 等待机制
    AlertHandling = 6  # 弹窗处理
    WindowSwitching = 7  # 窗口切换
    CookiesManagement = 8  # Cookies Management
    JavaScriptExecution = 9  # js脚本执行
    Screenshots = 10  # 屏幕截图
    SelectClass = 11  # 下拉框处理


class SeleniumStepTypeName:
    All = '全部操作'
    DriverAction = '浏览器操作'
    ElementAction = '元素操作'
    MouseAction = '鼠标操作'
    KeyboardAction = '键盘操作'
    WaitAction = '等待机制'
    AlertHandling = '弹窗处理'
    WindowSwitching = '窗口切换'
    CookiesManagement = 'Cookies 管理'
    JavaScriptExecution = '执行js脚本'
    Screenshots = '屏幕截图'
    SelectClass = '下拉框处理'


class AppiumStepType:
    All = 0  # 全部操作
    ElementAction = 1  # 元素操作
    PhoneAction = 2  # 手机操作
    AlertHandling = 3  # 弹窗操作
    KeyboardAction = 4  # 键盘操作
    WaitAction = 5  # 等待机制
    Content = 6  # 上下文切换
    Screenshots = 10  # 屏幕截图


class AppiumStepTypeName:
    All = '全部操作'
    ElementAction = '元素操作'
    PhoneAction = '手机操作'
    AlertHandling = '弹窗操作'
    KeyboardAction = '键盘操作'
    WaitAction = '等待机制'
    Content = '上下文切换'
    Screenshots = '屏幕截图'


class PlaywrightStepType:
    All = 0  # 全部操作
    DriverAction = 1  # 浏览器操作
    ElementAction = 2  # 元素操作
    MouseAction = 3  # 鼠标操作
    KeyboardAction = 4  # 键盘操作
    AlertHandling = 5  # 弹窗处理
    WindowSwitching = 6  # 窗口切换
    CookiesManagement = 7  # Cookies Management
    JavaScriptExecution = 8  # js脚本执行
    Screenshots = 9  # 屏幕截图


class PlaywrightStepTypeName:
    All = '全部操作'
    DriverAction = '浏览器操作'
    ElementAction = '元素操作'
    MouseAction = '鼠标操作'
    KeyboardAction = '键盘操作'
    AlertHandling = '弹窗处理'
    WindowSwitching = '窗口切换'
    CookiesManagement = 'Cookies 管理'
    JavaScriptExecution = '执行js脚本'
    Screenshots = '屏幕截图'


class SystemFuncType:
    StringGenerate = '字符串生成器'
    BuildFunc = '内置函数'
    OtherInfo = '其他信息'
    TextInfo = '文本信息'
    PersonInfo = '个人信息'
    CarInfo = '车辆信息'
    BankInfo = '银行信息'
    PhoneInfo = '手机信息'
    PythonBaseData = '基本类型数据'
    AddressInfo = '地址信息'
    ColorInfo = '颜色信息'
    CompanyInfo = '公司信息'
    JobInfo = '工作信息'
    TimeInfo = '时间信息'
    InternetInfo = '网络信息'


def action_group(group_id, group_name=None):
    """
    为函数添加分组
    """
    def decorator(func):
        func.group_id = group_id
        func.group_name = group_name
        return func
    return decorator

