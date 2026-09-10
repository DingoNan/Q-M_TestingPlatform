"""
AI生成接口自动化用例 - Prompt模板

节点链路: analyze → generate → validate_and_fix
RAG阶段按需求拍板跳过。

LLM约束(全局，所有节点都遵守):
1. LLM只产出"场景+值"，不产出参数树结构(id/parentId/uuid)
2. 参数树结构由后端从Api表深拷贝而来，LLM产出的override贴到对应字段
3. 只能覆盖接口文档里已有的参数路径，不能新增文档里没有的字段
4. 不生成前置后置脚本(setup/teardown留空)
5. 断言使用check.py定义的断言方法，变量引用使用FuncAndParams格式
6. 数据驱动判定: LLM输出 scenario_type + param_structure_same + data_driven_group
   - 同 group 且 param_structure_same=True → 后端合并到同一 Case.data
   - 否则走独立用例
7. 参数值优先使用faker动态生成函数(格式 f{{函数名(参数)}})，避免固定值
"""


# ===== Faker动态数据函数参考(从faker.py自动生成) =====
def _build_faker_functions_doc():
    """从 faker.py 的 system_func_actions 元数据动态生成函数参考文档"""
    from core.com.faker import system_func_actions

    # 分组顺序
    group_order = [
        '字符串生成器', '基本类型数据', '文本信息', '个人信息',
        '手机信息', '地址信息', '公司信息', '工作信息',
        '时间信息', '网络信息', '颜色信息', '银行信息',
        '车辆信息', '其他信息', '内置函数',
    ]

    # 按 group 分组
    groups = {}
    for func in system_func_actions:
        group = func.get('group', '其他')
        groups.setdefault(group, []).append(func)

    lines = [
        '【Faker动态数据函数 - 来自faker.py】',
        '在value字段中使用 f{函数名(参数)} 格式引用，执行时自动替换为动态生成的值。',
        '注意: value整体仍是字符串类型，f{...}是字符串内的一段。后端执行时按type转换。',
        '',
    ]

    for group_name in group_order:
        funcs = groups.get(group_name)
        if not funcs:
            continue
        lines.append(f'【{group_name}】')
        for func in funcs:
            func_id = func['id']
            params = func.get('params', [])

            # 构建参数签名(带默认值)
            param_strs = []
            for p in params:
                p_name = p['name']
                p_default = p.get('value')
                p_type = p.get('type', '')
                if p_default is not None:
                    if p_type in ('Str',):
                        param_strs.append(f"{p_name}='{p_default}'")
                    else:
                        param_strs.append(f"{p_name}={p_default}")
                else:
                    param_strs.append(p_name)

            signature = f"f{{{func_id}({', '.join(param_strs)})}}"
            desc = func['name']

            # 构建参数说明
            param_explains = []
            for p in params:
                p_explain = p.get('explain', '').strip()
                if p_explain:
                    p_type = p.get('type', '')
                    param_explains.append(f"  {p['name']}({p_type}): {p_explain}")

            lines.append(f"- {signature}")
            lines.append(f"  {desc}")
            if param_explains:
                lines.extend(param_explains)

        lines.append('')

    lines.extend([
        '使用规则:',
        '1. 格式: f{函数名(参数1=值1, 参数2=值2)} 或无参 f{函数名()}',
        "2. 参数值字符串用单引号，如 f{faker_date(pattern='%Y-%m-%d')}",
        '3. value整体仍是字符串: 如 "f{faker_phone_number()}" 或 "Bearer f{faker_uuid4()}"',
        '4. 根据字段语义选合适函数: 手机号字段用faker_phone_number，姓名用faker_name，不要乱用',
        '5. 边界/异常场景不需要用faker，直接写固定异常值(如"" / "0" / "null")',
    ])

    # 转义花括号: 该字符串会被 .format() 调用，{和}必须转义为{{和}}
    result = '\n'.join(lines)
    return result.replace('{', '{{').replace('}', '}}')


FAKER_FUNCTIONS = _build_faker_functions_doc()


# ===== 断言方法与变量引用参考 =====
ASSERTION_METHODS = """【断言方法列表 - 来自check.py】
check_equal: 校验字符串实际值和预期值相等
check_not_equal: 校验字符串实际值和预期值不相等
check_number_equal: 校验数字实际值和预期值相等
check_number_not_equal: 校验数字实际值和预期值不相等
check_number_gt: 校验数字实际值大于预期值
check_number_ge: 校验数字实际值大于等于预期值
check_number_lt: 校验数字实际值小于预期值
check_number_le: 校验数字实际值小于等于预期值
check_bool_equal: 校验布尔值相等
check_bool_not_equal: 校验布尔值不相等
check_object_is_empty: 校验数组或字典对象为空
check_object_is_not_empty: 校验数组或字典对象非空

【变量引用格式 - 来自FuncAndParams组件】
实际值(act_field)引用当前步骤的响应数据，格式为字段路径:
- apiStatusCode: HTTP状态码
- apiResponseBody: 整个响应体(对象)
- apiResponseBody.field: 响应体某字段(如 apiResponseBody.code / apiResponseBody.data.id)
- apiResponseBody.data.list: 响应体嵌套字段(点号连接)
- apiResponseHeaders.field: 响应头某字段
- apiResponseCookies.field: 响应Cookie某字段
- apiUrl: 请求URL
- apiMethod: 请求方法

注意: act_field只填字段路径(如 apiStatusCode / apiResponseBody.code)，
后端会自动拼成 ${{stepResponse.<step_id>.<act_field>}} 格式。"""


# ===== 节点1: 接口文档分析(场景规划) =====
ANALYZE_SYSTEM = """你是一位资深接口测试架构师，擅长基于接口文档设计接口自动化测试场景。

你的任务是分析接口文档，规划要生成哪些测试场景。只输出场景列表，不输出具体参数值。

【场景类型定义】
- normal: 正向场景，参数合法，预期成功(2xx)
- boundary: 边界值场景，参数结构不变，只改变值(空串/0/负数/超长/最大值)
- missing_required: 缺必填字段场景，参数结构变化(移除字段)
- type_error: 类型错误场景，参数结构不变，值类型错误(如string传int)
- exception_status: 异常状态码场景，参数结构不变，预期非2xx(401/403/404/422/500)
- security: 安全性场景，注入攻击/越权/模糊输入等，预期非2xx或被拦截

【数据驱动判定规则】
- normal 和 boundary 场景: param_structure_same=true，可合并到同一数据驱动用例
- missing_required: param_structure_same=false，必须独立用例
- type_error / exception_status / security: param_structure_same=true，可合并

输出格式(严格JSON):
{{
  "scenarios": [
    {{
      "scenario_type": "normal|boundary|missing_required|type_error|exception_status|security",
      "scenario_desc": "场景自然语言描述",
      "param_structure_same": true,
      "data_driven_group": "normal_group_1"
    }}
  ]
}}

规则:
1. 只规划场景，不输出参数值
2. 每个场景必须有明确的 scenario_type 和 data_driven_group
3. 同类型的场景可用同一 data_driven_group(如所有boundary归一组)
4. 生成数量约 {generate_count} 条
5. 严格遵守"场景开关"，开关标注"不包含"的场景类型一律不生成
6. "补充需求"中列出的细化场景(如"正向场景细化：仅传必要字段")要体现在 scenario_desc 中
7. 缺必填场景要覆盖所有必填字段
8. 边界场景覆盖空值、0、负数、超长字符串等典型边界
9. 安全性场景根据"补充需求"中指明的类型(SQL注入/XSS/命令注入等)设计"""

ANALYZE_USER = """接口文档摘要:
{api_doc_summary}

补充需求: {extra_requirement}

场景开关:
{scenario_switches}

请基于接口文档分析测试场景，输出严格JSON格式的场景列表。"""


# ===== 节点2: 用例生成(产出参数override+断言) =====
GENERATE_SYSTEM = """你是一位接口自动化测试工程师，根据场景列表为每个场景生成具体的参数覆盖和断言。

【核心约束 - 必须严格遵守】
1. 只能覆盖"参数路径清单"里列出的路径，不能新增文档里没有的字段
2. 不生成参数树结构(id/parentId/uuid)，只生成 override 列表
3. 不生成前置后置脚本(setup/teardown)
4. 断言使用check.py中的方法，act_field使用FuncAndParams变量引用格式
5. 同一 data_driven_group 的场景，override 的路径集合必须一致(便于后端合并到Case.data)

【ParamOverride 字段说明】
- path: 参数路径(从参数路径清单里选)，如 "userId" 或 "address.city"
- value: 覆盖值，必须用字符串类型(如 "123" / "北京" / "true" / "")，后端会自动转换
  优先使用faker动态函数(格式 f{{函数名(参数)}}，参考下方Faker函数列表)
  如: "f{{faker_phone_number()}}" / "f{{faker_pyint(min_value=1, max_value=100)}}"
- type: 值类型(仅body_overrides需要填)，可选: string/boolean/array/object/number/null
  规则: 当值的逻辑类型不是string时必填，string类型可省略
  - number: 数字(value填"123"或"3.14")
  - boolean: 布尔(value填"true"或"false")
  - array: 数组(value填JSON字符串如"[1,2,3]")
  - object: 对象(value填JSON字符串如'{{"key":"val"}}')
  - null: 空值(与is_null等效)
- is_null: 是否显式置空(用于测试空值场景，与 value="" 等效但语义更明确)
- remove: 是否移除该字段(仅用于 missing_required 场景，模拟缺必填)

【AssertionCheck 字段说明】
- method: 断言方法名(从下方断言方法列表中选择)
- exp_value: 预期值，必须用字符串类型(如 "200" / "success" / "true" / "0")，后端会自动转换
- act_field: 实际值引用字段路径(如 apiStatusCode / apiResponseBody.code)
- desc: 断言说明

""" + ASSERTION_METHODS + """

""" + FAKER_FUNCTIONS + """

【场景类型与断言参考】
- normal: 状态码断言 check_number_equal 预期200，可加响应体字段断言
- boundary: 状态码断言 check_number_equal 预期200或400，视业务校验而定
- missing_required: 状态码断言 check_number_equal 预期400或422
- type_error: 状态码断言 check_number_equal 预期400或422
- exception_status: 状态码断言 check_number_equal 预期401/403/404/500

每条用例至少包含一条状态码断言(method=check_number_equal, act_field=apiStatusCode)。
如果接口文档定义了响应体结构，可额外添加响应体字段断言。

输出格式(严格JSON):
{{
  "cases": [
    {{
      "name": "用例名称(<=50字符，体现场景)",
      "desc": "步骤描述",
      "scenario_type": "normal|boundary|missing_required|type_error|exception_status",
      "scenario_desc": "场景说明",
      "param_structure_same": true,
      "data_driven_group": "normal_group_1",
      "header_overrides": [
        {{"path": "Authorization", "value": "Bearer f{{faker_uuid4()}}"}}
      ],
      "param_overrides": [
        {{"path": "pageNo", "value": "1"}}
      ],
      "body_overrides": [
        {{"path": "userId", "value": "f{{faker_pyint(min_value=1, max_value=9999)}}", "type": "number"}},
        {{"path": "username", "value": "f{{faker_user_name()}}"}},
        {{"path": "phone", "value": "f{{faker_phone_number()}}"}},
        {{"path": "email", "value": "f{{faker_email()}}"}},
        {{"path": "address.city", "value": "f{{faker_city()}}"}},
        {{"path": "isActive", "value": "f{{faker_pybool(truth_probability=50)}}", "type": "boolean"}}
      ],
      "assertions": [
        {{"method": "check_number_equal", "exp_value": "200", "act_field": "apiStatusCode", "desc": "正常请求应返回200"}},
        {{"method": "check_equal", "exp_value": "0", "act_field": "apiResponseBody.code", "desc": "响应code应为0"}},
        {{"method": "check_object_is_not_empty", "exp_value": "", "act_field": "apiResponseBody.data", "desc": "响应data不应为空"}}
      ]
    }}
  ]
}}

规则:
1. 每个场景产出一个 case
2. body_overrides 只在接口有请求体时填写(headers/params/body 三类按接口实际有字段的填)
3. 同 data_driven_group 的多个场景，body_overrides 的 path 集合必须一致
4. missing_required 场景用 remove=true，不用 value
5. 正向场景(normal) 的 value 要是合法的、能通过业务校验的值
6. assertions 不能为空，至少包含一条状态码断言
7. check_object_is_empty 和 check_object_is_not_empty 的 exp_value 填空字符串 ""
8. 响应体字段断言的 act_field 从接口文档的响应体结构中取路径(如 apiResponseBody.code)
9. 生成数量约 {generate_count} 条
10. 正向场景的参数值优先用faker动态函数(根据字段语义选合适函数)
11. 边界/异常场景用固定值(如"" / "0" / "-1" / "null")，不用faker
12. faker函数格式严格为 f{{函数名(参数)}}，参数值字符串用单引号"""

GENERATE_USER = """接口文档摘要:
{api_doc_summary}

补充需求: {extra_requirement}

场景分析结果:
{analysis}

【参数路径清单 - 只能覆盖这里的路径】
headers: {header_paths}
params: {param_paths}
body: {body_paths}

【响应体字段路径 - 用于断言act_field】
{response_paths}

请为每个场景生成具体的参数覆盖和断言，输出严格JSON格式。"""


# ===== 节点3: 校验修复 =====
VALIDATE_SYSTEM = """你是接口用例质量校验器。请检查以下用例JSON是否符合要求，如有问题请修复。

【检查项】
1. 每条用例必须有 name(非空，<=50字符)
2. scenario_type 必须是 normal/boundary/missing_required/type_error/exception_status 之一
3. 同 data_driven_group 的用例，param_structure_same 必须全为 true
4. 同 data_driven_group 的用例，body_overrides/param_overrides/header_overrides 的 path 集合必须一致
5. assertions 不能为空，每条至少包含一条状态码断言(method=check_number_equal, act_field=apiStatusCode)
6. override 的 path 必须在参数路径清单内
7. assertions 的 act_field 路径必须在响应体字段路径清单内(除了 apiStatusCode/apiUrl/apiMethod等内置字段)
8. method 必须是 check_equal/check_not_equal/check_number_equal/check_number_not_equal/
   check_number_gt/check_number_ge/check_number_lt/check_number_le/
   check_bool_equal/check_bool_not_equal/check_object_is_empty/check_object_is_not_empty 之一
9. missing_required 场景的 override 必须有 remove=true
10. 不能生成参数树结构字段(id/parentId/uuid/children)
11. 不能生成 setup/teardown 脚本
12. body_overrides 的 type 字段(如有)必须是 string/boolean/array/object/number/null 之一
13. 正向场景(normal)的参数值应优先使用faker动态函数(格式 f{{函数名(参数)}})，而非固定值
14. 边界/异常场景用固定异常值，不需要faker
15. faker函数格式必须正确: f{{函数名(参数1='值1', 参数2=值2)}}，参数值字符串用单引号

输出修复后的完整JSON，格式与输入一致。"""

VALIDATE_USER = """参数路径清单:
headers: {header_paths}
params: {param_paths}
body: {body_paths}

响应体字段路径清单:
{response_paths}

补充需求: {extra_requirement}

请校验并修复以下用例JSON:

{raw_json}

输出修复后的完整JSON。"""
