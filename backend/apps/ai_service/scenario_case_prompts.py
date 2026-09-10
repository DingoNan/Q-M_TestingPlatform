"""
AI从功能用例生成场景自动化脚本 - Prompt模板

节点链路: load_func_case → load_resources → generate → validate

LLM约束(全局):
1. LLM只产出"步骤树+值"，不产出参数树结构(id/parentId/uuid)
2. 接口调用必须引用项目接口库中真实存在的接口名称，参数结构由后端从Api表克隆
3. WebUI动作必须使用下发的动作白名单，元素必须引用项目元素库中真实存在的元素名称
4. 变量引用使用 {sN.字段路径} 占位符(sN=步骤序号, 从1计数)，
   如 {s1.apiResponseBody.data.id} / {s2.funcReturn}，后端落库时自动替换为真实引用
5. 逻辑控制器(IF/FOR/WHILE/SLEEP/TRANSACTION/FOREACH)必须按规则生成，
   最多嵌套一层子控制器
6. 不生成前置后置python脚本(setup/teardown留空)
7. 断言使用check.py定义的断言方法: check_equal/check_not_equal/check_number_equal/
   check_number_not_equal/check_number_gt/check_number_ge/check_number_lt/check_number_le/
   check_bool_equal/check_bool_not_equal/check_object_is_empty/check_object_is_not_empty
8. 参数值优先使用faker动态生成函数(格式 f{{函数名(参数)}})，避免固定值
"""


# ===== Playwright动作白名单(从run_playwright.py动态生成) =====
def _build_playwright_action_doc():
    """从 PlaywrightBaseAction 的方法签名动态生成动作参考文档"""
    try:
        from core.step.run_playwright import PlaywrightBaseAction
        from core.com.step_model import PlaywrightStepTypeName, PlaywrightStepType

        lines = []
        for name, func in sorted(PlaywrightBaseAction.__dict__.items()):
            if name.startswith('_'):
                continue
            doc = (func.__doc__ or '').strip().split('\n')[0]
            if not doc:
                continue
            lines.append(f"- {name}: {doc}")
        return lines
    except Exception:
        # 兜底动作列表，防止导入异常导致生成失败
        return [
            "- goto: 打开指定URL",
            "- click: 点击元素",
            "- fill: 在输入框输入文本",
            "- clear: 清空输入框",
            "- select_option: 下拉框选择",
            "- upload_file: 上传文件",
            "- is_visible: 判断元素可见",
            "- text_content: 获取元素文本",
            "- url: 获取当前页面URL",
            "- title: 获取页面标题",
            "- reload: 刷新页面",
            "- press_key: 键盘按键",
        ]


PLAYWRIGHT_ACTION_DOC = _build_playwright_action_doc()


# ===== 控制器规则 =====
CONTROL_RULES = """
【逻辑控制器规则】(步骤树中最多嵌套一层子控制器)
- IF: 当"如果...则..."或条件分支时使用。条件写在 conditions 数组中，每项格式同断言:
  {"method": "check_number_equal", "exp_value": 200, "act_field": "{s1.apiStatusCode}", "desc": "状态码为200"}
- FOR: 当"循环N次"时使用，loop_times填写次数
- WHILE: 当"直到...才结束"时使用，条件同样写在 conditions 数组中，必须填max_loop_times(建议3-5)防止死循环
- SLEEP: 当"等待N秒"时使用，timeout填秒数
- TRANSACTION: 包裹一组步骤标记为事务(不计入具体耗时统计)，children填步骤
- FOREACH: 当"遍历列表/数组"时使用，loop_var引用列表变量，如 {s1.apiResponseBody.data.list}
子步骤只能使用api/web类型，不能再嵌套控制器。
"""


# ===== 功能用例摘要 =====
def build_func_case_user_prompt(func_case_summary: dict, extra_requirement: str = "",
                                rag_context: str = "", resources: list = None,
                                mode: str = "api") -> str:
    """构建generate节点的用户提示词"""
    parts = [
        "【功能用例】请根据以下功能用例生成自动化脚本用例：",
        "```",
        __import__('json').dumps(func_case_summary, ensure_ascii=False, indent=2),
        "```",
        "",
        f"【生成模式】{ '接口自动化(HTTP接口步骤)' if mode == 'api' else 'WebUI自动化(Playwright浏览器步骤, 前置可插入接口步骤造数据)' }",
    ]

    if resources:
        parts.append(f"【可用的{mode == 'api' and '接口' or '元素'}清单】")
        for r in resources:
            parts.append(f"- {r}")

    if rag_context:
        parts.append(rag_context)

    if extra_requirement:
        parts.append(f"【补充需求】{extra_requirement}")

    return "\n".join(parts)


def build_generate_system(generate_count: int = 3) -> str:
    """构建generate节点的系统提示词(拼接CONTROL_RULES，避免.format与占位符冲突)"""
    return (
        "你是资深自动化测试工程师，负责把功能用例转换为可直接执行的自动化脚本用例。\n\n"
        f"{CONTROL_RULES}\n\n"
        "【变量引用规则】\n"
        "- 步骤按生成顺序从1开始编号，所有引用前序步骤返回值的地方(断言act_field、IF/WHILE条件、\n"
        "  请求参数值)都必须写成 {sN.字段路径} 占位符，N是被引用步骤的序号\n"
        "- 接口步骤返回字段: sN.apiStatusCode(状态码) / sN.apiResponseBody.字段路径(响应体) / sN.apiResponseHeaders\n"
        "- WebUI取值动作返回字段: sN.funcReturn\n"
        "- 断言本步骤自己的响应时，N就是当前步骤的序号(如第1步的状态码断言写 {s1.apiStatusCode})\n"
        "- 禁止裸写字段路径(如 apiStatusCode / apiResponseBody.msg)，禁止编造 ${stepResponse.数字.xxx} 形式的引用\n"
        "  (真实数字ID由后端落库时自动填充)\n"
        "- 例: 第1步是创建会议室的接口，第2步WebUI点击时引用 {s1.apiResponseBody.data.id}\n\n"
        "【接口步骤规则】\n"
        "- api_name 必须严格使用接口清单中存在的名称，用于后端匹配参数结构\n"
        "- 只覆盖必要的参数，其余用接口文档默认值\n"
        "- 每个接口步骤应附带断言(状态码+关键字段)，断言act_field写法:\n"
        "  状态码: {sN.apiStatusCode}；响应体: {sN.apiResponseBody.字段路径}(N为当前步骤序号)\n"
        "- 断言method必须使用白名单: check_equal/check_not_equal/check_number_equal/\n"
        "  check_number_not_equal/check_number_gt/check_number_ge/check_number_lt/check_number_le/\n"
        "  check_bool_equal/check_bool_not_equal/check_object_is_empty/check_object_is_not_empty\n"
        "- 断言act_field中 apiResponseBody. 后面的字段路径必须来自接口清单中“响应字段”列出的真实字段，\n"
        "  禁止凭空猜测字段名(如响应是msg就不要写message)，也不要带 response_data 等包装层前缀\n\n"
        "【WebUI步骤规则】\n"
        "- keyword 必须使用动作白名单中的名称\n"
        "- element_name 必须使用元素清单中存在的名称\n"
        "- params 为动作参数数组，参数名必须与动作签名一致(如 goto 用 uri、fill 用 value、\n"
        "  press_other 用 key_name、alert_send_keys 用 value、get_attribute 用 name)\n"
        "- 只填必要参数，未填的可选参数会自动补默认值(如 element_index=0、timeout=5、need_add_cookie=False)\n"
        "- 取值类动作(is_visible/text_content/url/title/get_attribute)适合做页面断言\n\n"
        "【输出格式】\n"
        '只输出JSON对象: {"cases": [{"name": "用例名", "desc": "说明", "scenario_type": "normal|boundary|abnormal", "steps": [...]}]}\n'
        "steps数组每个元素为:\n"
        '{"step_type": "api", "api": {"desc": "...", "api_name": "接口名", "assertions": [{"method": "check_number_equal", "exp_value": 200, "act_field": "{s1.apiStatusCode}", "desc": "..."}]}}\n'
        '{"step_type": "web", "web": {"desc": "...", "keyword": "goto", "element_name": "", "params": [{"name": "uri", "value": "/#/user/login", "value_type": "Str"}]}}\n'
        '{"step_type": "web", "web": {"desc": "...", "keyword": "fill", "element_name": "用户名输入框", "params": [{"name": "value", "value": "admin", "value_type": "Str"}]}}\n'
        '{"step_type": "control", "control": {"keyword": "IF", "desc": "...", "conditions": [{"method": "check_number_equal", "exp_value": 200, "act_field": "{s1.apiStatusCode}", "desc": "创建成功才继续"}], "children": [...]}}\n\n'
        "要求:\n"
        f"1. 生成{generate_count}条用例，覆盖正常流程，若功能用例描述中存在边界/异常条件则生成对应场景\n"
        "2. 步骤数3-15步，优先复用功能用例步骤\n"
        "3. WebUI模式若前置需要测试数据(如创建订单/预约会议室)，第一步先生成对应的接口调用步骤造数据\n"
        "4. 不要编造接口或元素名称\n"
    )


VALIDATE_SYSTEM = """
你是自动化脚本校验专家。用户会给你一个JSON格式的自动化脚本用例和校验错误信息，
请根据错误信息修正JSON并原样返回。只输出修正后的JSON，不要输出其他内容。
要求:
1. api_name必须来自给定的接口清单
2. element_name必须来自给定的元素清单
3. keyword必须来自动作白名单
4. 断言act_field和IF/WHILE条件act_field必须写成 {sN.字段路径} 形式:
   - N是被引用步骤的序号(断言本步骤响应时N为当前步骤序号)
   - 接口状态码用 {sN.apiStatusCode}，响应体用 {sN.apiResponseBody.字段路径}
   - WebUI取值动作用 {sN.funcReturn}
   - 不允许裸写字段路径，不允许出现 ${stepResponse.数字.xxx}(数字ID由后端生成)
   - apiResponseBody.后的字段路径必须来自接口清单的"响应字段"，且不能带 response_data 前缀
5. IF/WHILE控制器的条件必须写在 conditions 数组中(每项含method/exp_value/act_field)，不要写condition字符串
6. 控制器条件中的 {sN.} 引用必须指向真实存在的步骤序号
7. 保持原有JSON结构不变，只修正错误字段
"""
