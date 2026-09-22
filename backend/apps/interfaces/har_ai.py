# -*- coding: utf-8 -*-
"""
HAR 轨迹 → 规则式分析 → LLM 归因 → 用例草稿
============================================================
「阶段一：轨迹 → AI 归因 → 用例草稿」最小闭环的最后一环。

此前两条链各自独立、并不相连：

  A. 规则式分析  `_har_analyze()`（apps/interfaces/views.py）
     —— 确定性地给出：真实时序、认证补齐、动态参数、跨请求依赖、路径族分组。
        零成本、零幻觉，但它**不理解业务**，只会说「序号 7 的请求用了序号 3 返回的 token」。

  B. AI 归因     `ai_service.LLMClient`
     —— 只能从「用户手写的需求文本」出发生成用例。它**看不到**浏览器里真实发生了什么。

缺的正是中间那一段：把 A 的结构化产物压成一份 LLM 读得懂的「轨迹摘要」，
让 B 直接基于真实录制到的调用序列做归因，而不是靠人复述需求。
本模块就是这座桥。

设计取舍（三条，都踩过坑才定下来）
------------------------------------------------------------
1. **规则式分析是事实来源，LLM 只做语义层归因。**
   「谁调用了谁 / 哪个变量来自哪次响应 / 一共几个接口」这类客观事实一律由
   `_har_analyze` 给出，LLM 只负责业务场景划分、断言设计、风险与缺口。
   这样即使模型产生幻觉，也污染不到接口清单与依赖关系这些可核对的事实。

2. **摘要必须短。**
   HAR 动辄上百条接口，整包丢给 LLM 既贵又容易失焦。故按时序截断到 MAX_APIS 条，
   并在摘要首行显式写出「共 N 条，以下为前 M 条」，让模型知道自己看到的是片段。

3. **同步调用。**
   归因一般 20~60 秒，同步返回才能让「导入 HAR → 看归因 → 入库草稿」在一屏内闭环。
   不做成异步 task + 站内信，是因为这条链的价值恰恰在于「立刻看到结果」。
"""
import json
import logging

from apps.ai_service.llm import LLMClient

logger = logging.getLogger('interfaces')

#: 轨迹摘要最多喂给 LLM 的接口条数（超出部分只统计不展开）
MAX_APIS = 80
# ★ 输出上界。原先把「尽可能全面」写进提示词，实测模型吐了 5 场景 + 12 覆盖缺口 +
#   7 风险 + 长断言，直接撞上 max_tokens 被**从字符串中间截断**，整份 JSON 失效
#   （表现为 502「Unterminated string」）。归因质量靠「挑重点」而不是「堆条数」，
#   所以这里把上界写死并同步进提示词。
MAX_SCENARIOS = 6
MAX_DATA_FLOW = 8
MAX_RISKS = 6
MAX_GAPS = 6
MAX_CASES = 4
MAX_OUTPUT_TOKENS = 8000
#: 判定「写操作」的方法集合
WRITE_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}
#: 单条用例步骤数的上限提示（超出时在 prompt 里提醒模型收敛）
MAX_STEPS_HINT = 8


# ---------------------------------------------------------------- 摘要构造
def build_trace_digest(api_list, dependencies, stats, max_apis=MAX_APIS):
    """把 _har_analyze 的产物压成一段 LLM 可读的紧凑文本

    :param api_list: _har_analyze 返回的接口列表（已按真实发起顺序升序）
    :param dependencies: 动态参数依赖字典
    :param stats: 统计字典
    :param max_apis: 最多展开多少条接口
    :return: str
    """
    total = len(api_list)
    shown = api_list[:max_apis]
    lines = []

    hosts = ', '.join(stats.get('hosts') or []) or '-'
    lines.append(
        '【轨迹概览】共 %d 个 XHR/Fetch 调用（按真实发起时间升序），'
        '原始 entries %s 条，跳过静态资源 %s 条。主机: %s'
        % (total, stats.get('total_entries'), stats.get('skipped_static'), hosts)
    )
    if stats.get('auth_injected'):
        lines.append('【认证】已自动补齐认证头（HAR 导出时通常会剥离 Authorization）。')
    elif stats.get('auth_header_present_in_har'):
        lines.append('【认证】HAR 里本身就带着认证头。')
    if stats.get('auth_error'):
        lines.append('【认证】补齐失败: %s' % stats['auth_error'])
    methods = stats.get('methods') or {}
    if methods:
        lines.append('【方法分布】' + ', '.join('%s=%d' % (k, v) for k, v in sorted(methods.items())))

    lines.append('')
    lines.append('【调用时序】序号 | 方法 | 路径 | 状态码 | 请求体 | 读写 | 本请求携带的动态参数')
    for a in shown:
        dyn = ','.join((a.get('dynamic') or {}).keys())
        kind = (a.get('body_kind') or '-')
        rw = '写' if (a.get('method') or '').upper() in WRITE_METHODS else '读'
        st = a.get('status')
        lines.append('%s | %s | %s | %s | %s | %s | %s' % (
            a.get('seq'), a.get('method'), a.get('path'),
            st if st not in (None, '') else '-',
            kind, rw, dyn or '-',
        ))
    if total > len(shown):
        lines.append('…（其余 %d 条已省略，仅参与统计不展开）' % (total - len(shown)))

    if dependencies:
        lines.append('')
        lines.append('【跨请求数据依赖】（规则引擎识别，可直接采信）')
        for var, d in dependencies.items():
            used_by = d.get('used_by') or []
            used_seq = ', '.join(str(u.get('seq')) for u in used_by if u.get('seq') is not None)
            where = d.get('where')
            lines.append('- %s：来自序号 %s 的响应（字段 %s），被序号 [%s] 使用；依据: %s%s' % (
                var,
                where if where not in (None, '') else '?',
                d.get('key') or '?',
                used_seq or '-',
                d.get('reason') or '-',
                '（可能为空）' if d.get('nullable') else '',
            ))

    groups = stats.get('groups') or {}
    if groups:
        lines.append('')
        lines.append('【路径族分组】（同一资源的不同操作，可辅助场景划分）')
        for key, seqs in list(groups.items())[:25]:
            lines.append('- %s → 序号 %s' % (key, seqs))

    return '\n'.join(lines)


# ---------------------------------------------------------------- Prompt
SYSTEM_PROMPT = """你是资深测试架构师。用户会给你一段「浏览器真实录制的接口调用轨迹」，
它已经由规则引擎按时序排好、并标注了跨请求的数据依赖。

你的任务是把这段轨迹**归因**为可评审的业务场景，并产出可直接入库的功能测试用例草稿。

硬性要求：
1. 只依据轨迹里**真实出现过**的接口做归因，不要虚构未出现的接口、字段或业务规则。
2. 「登录 / 鉴权 / 取 token / 获取用户信息」属于前置条件，不要单独算作业务场景；
   把它们写进相关场景的 preconditions 里。
3. 场景划分要贴合业务动作：同一次业务操作引发的连续接口算一个场景；
   被多处复用的公共查询（字典、菜单、权限树、列表字典）归入「公共数据准备」。
4. 数据依赖：轨迹里已给出候选，你要点明「哪个字段来自哪次响应、被下游哪个请求用掉」，
   并说明这一依赖对用例步骤顺序的影响（顺序错了用例就是假的）。
5. 断言必须**具体可验证**：写清 HTTP 状态码、关键响应字段名、数量或业务含义。
   禁止出现「返回正确」「数据正常」这类无法判定的表述。
6. 用例草稿的每个步骤要写出「方法 + 路径 + 关键入参」，预期写明判据；
   一条用例控制在 3~%d 步，超出请拆成多条用例。
7. 必须给出**覆盖缺口**：这段轨迹没有覆盖、但按业务应有覆盖的点
   （异常分支、边界值、越权访问、并发、幂等、状态机的非法跃迁）。
8. 只输出一个 JSON 对象。不要输出解释性文字，不要包 markdown 代码块。
9. ★ 数量必须受控（这是硬约束，不是建议）：
   scenarios ≤ %d 条、每个场景 assertions ≤ 3 条、data_flow ≤ %d 项、
   risks ≤ 6 条、coverage_gaps ≤ 6 条、cases ≤ 4 条。
   宁缺毋滥：优先保留最能代表业务价值的条目，每条一句话说清即可。
   超出上界的一律丢弃 —— 输出被截断会导致整份 JSON 失效，比少写两条严重得多。""" % (
    MAX_STEPS_HINT, MAX_SCENARIOS, MAX_DATA_FLOW)

USER_TMPL = """项目：{project}

===== 录制的接口轨迹（按真实发起顺序）=====
{digest}
===== 轨迹结束 =====

请基于上面的轨迹输出如下 JSON 结构：

{{
  "scenarios": [
    {{
      "name": "场景名，不超过 20 字",
      "intent": "这个场景在业务上想验证什么",
      "api_seqs": [1, 2, 3],
      "preconditions": "前置条件（含登录/数据准备）",
      "assertions": ["可验证的断言，写清状态码/字段名/数量", "第二条断言"]
    }}
  ],
  "data_flow": [
    {{"var": "变量名", "from_seq": 1, "to_seqs": [3, 5], "note": "取哪个字段、为什么、对步骤顺序的影响"}}
  ],
  "risks": ["这段轨迹暴露出的风险点"],
  "coverage_gaps": ["应该补测但轨迹里没有覆盖的点"],
  "cases": [
    {{
      "name": "用例名，不超过 50 字",
      "setup_condition": "前置条件",
      "case_mark": "备注",
      "step_table": [
        {{"step": 1, "desc": "操作（写清 方法 + 路径 + 关键入参）", "exp": "预期（写清判据）"}}
      ]
    }}
  ]
}}"""


def _chat_json_resilient(llm, system_prompt, user_prompt, temperature, max_tokens):
    """自己发起 LLM 调用 + 稳健的 JSON 收敛（**不用** llm.chat_json）

    为什么不用 LLMClient.chat_json：
      它在解析失败后最终只 re-raise 一个 json.JSONDecodeError —— **不回传原始
      文本**，外部既无法补救也无法定位；而且它内置的「截断修复」用的是
      `raw.rfind('}')` + 补右括号，当截断点落在**字符串内部**时（实测就是这种：
      `Unterminated string starting at: ... char 3799`）必然失手。

    这里的策略：
      ① max_tokens 给足，并把 finish_reason 记下来（'length' 即被截断，可观测）；
      ② 直解失败 → json_repair（它能处理截断 JSON 与未闭合字符串）；
      ③ 仍失败 → 抛出含 finish_reason / 长度 / 尾部片段的 ValueError，
         让调用方和日志能一眼看出是「被截断」还是「格式乱」。
    :return: (dict, raw_text, finish_reason)
    """
    resp = llm.client.chat.completions.create(
        model=llm.model,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        temperature=temperature,
        response_format={'type': 'json_object'},
        max_tokens=max_tokens,
    )
    choice = resp.choices[0]
    raw = choice.message.content or ''
    finish = getattr(choice, 'finish_reason', None) or 'unknown'
    logger.info('[HAR归因] LLM 返回 %d 字，finish_reason=%s', len(raw), finish)
    try:
        return json.loads(raw), raw, finish
    except json.JSONDecodeError as e:
        logger.warning('[HAR归因] JSON 直解失败(%s)，改用 json_repair；finish_reason=%s 长度=%d',
                       e, finish, len(raw))
    try:
        from json_repair import repair_json
        obj = repair_json(raw, return_objects=True)
        if isinstance(obj, dict):
            logger.info('[HAR归因] json_repair 修复成功（finish_reason=%s）', finish)
            return obj, raw, finish
        logger.warning('[HAR归因] json_repair 结果不是对象：%r', type(obj))
    except Exception as e2:
        logger.warning('[HAR归因] json_repair 也失败：%s', e2)
    raise ValueError(
        '模型输出无法解析为 JSON（finish_reason=%s，长度 %d 字%s；尾部 160 字：%s）'
        % (finish, len(raw),
           '，疑似被 max_tokens 截断' if finish == 'length' else '',
           raw[-160:].replace('\n', ' '))
    )


def run_llm_attribution(ai_config_id, digest, project_name=''):
    """调用 LLM 做轨迹归因，返回归一化后的 dict

    失败处理：第一次解析失败（多为输出被截断）时**自动重试一次**，
    第二次在系统提示里追加「务必精简、严格控制条数」——因为同一条轨迹
    重试一次通常就能收敛，比直接把 502 甩给用户有价值得多。

    :param ai_config_id: AiConfig 主键
    :param digest: build_trace_digest() 的产物
    :param project_name: 项目名（仅作为上下文提示，可为空）
    :return: {scenarios, data_flow, risks, coverage_gaps, cases}
    """
    llm = LLMClient(int(ai_config_id))
    user_prompt = USER_TMPL.format(project=project_name or '-', digest=digest)
    logger.info('[HAR归因] 开始，摘要 %d 字，模型 %s，max_tokens=%d',
                len(digest), llm.model, MAX_OUTPUT_TOKENS)

    last_err = None
    for attempt in (1, 2):
        sys_prompt = SYSTEM_PROMPT
        if attempt == 2:
            sys_prompt = SYSTEM_PROMPT + (
                '\n\n★ 上一次输出被截断导致 JSON 失效。这次务必**大幅精简**：'
                'scenarios 只留最核心的 3 条，assertions 每条不超过 40 字，'
                'risks / coverage_gaps 各不超过 4 条，cases 只留 2 条、每步不超过 60 字。'
            )
        try:
            raw_dict, raw_text, finish = _chat_json_resilient(
                llm, sys_prompt, user_prompt, 0.3, MAX_OUTPUT_TOKENS)
            data = normalize_attribution(raw_dict)
            logger.info(
                '[HAR归因] 完成(attempt=%d, finish=%s)：场景 %d 个，用例草稿 %d 条，依赖 %d 项，缺口 %d 项',
                attempt, finish, len(data['scenarios']), len(data['cases']),
                len(data['data_flow']), len(data['coverage_gaps']),
            )
            return data
        except Exception as e:
            last_err = e
            logger.warning('[HAR归因] 第 %d 次归因失败：%s', attempt, e)

    raise ValueError(str(last_err))


# ---------------------------------------------------------------- 归一化
def _as_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _str_list(v):
    if not isinstance(v, (list, tuple)):
        return []
    return [str(x).strip() for x in v if str(x).strip()]


def normalize_attribution(data):
    """把 LLM 输出规整成稳定 schema —— 缺字段补空、类型不对丢弃、超量硬截断，绝不抛异常

    LLM 输出的结构漂移是最常见的故障（少字段 / 给成字符串 / seqs 混进 null），
    这里做一次严格收敛，让调用方可以无条件信任返回结构。

    ★ 同时兜底「数量上界」：提示词里的上界是软约束（模型可能不遵守），
      归一化层再硬截一次。条数越多 → prompt 输出越长 → 越容易撞 max_tokens
      被从字符串中间截断，整份 JSON 失效。宁可少几条，也不要整批丢掉。
    """
    if not isinstance(data, dict):
        data = {}
    out = {'scenarios': [], 'data_flow': [], 'risks': [], 'coverage_gaps': [], 'cases': []}

    for s in (data.get('scenarios') or [])[:MAX_SCENARIOS]:
        if not isinstance(s, dict):
            continue
        seqs = [_as_int(x) for x in (s.get('api_seqs') or [])]
        out['scenarios'].append({
            'name': str(s.get('name') or '').strip()[:40],
            'intent': str(s.get('intent') or '').strip(),
            'api_seqs': [x for x in seqs if x is not None],
            'preconditions': str(s.get('preconditions') or '').strip(),
            'assertions': _str_list(s.get('assertions'))[:3],
        })

    for d in (data.get('data_flow') or [])[:MAX_DATA_FLOW]:
        if not isinstance(d, dict):
            continue
        to_seqs = [_as_int(x) for x in (d.get('to_seqs') or [])]
        out['data_flow'].append({
            'var': str(d.get('var') or '').strip(),
            'from_seq': _as_int(d.get('from_seq')),
            'to_seqs': [x for x in to_seqs if x is not None],
            'note': str(d.get('note') or '').strip(),
        })

    out['risks'] = _str_list(data.get('risks'))[:MAX_RISKS]
    out['coverage_gaps'] = _str_list(data.get('coverage_gaps'))[:MAX_GAPS]

    _dropped = 0
    for c in (data.get('cases') or []):
        if len(out['cases']) >= MAX_CASES:
            break
        if not isinstance(c, dict):
            _dropped += 1
            continue
        # ★ LLM 的键名最不稳定：step_table / steps / step_list / test_steps 都见过。
        #   只认 step_table 的话，键名一漂移就会把**整批用例静默丢光**，调用方只看到
        #   cases=[] 而完全不知道发生了什么（实测就踩过一次：两次调用一次 1 条、一次 0 条）。
        raw_steps = c.get('step_table')
        if not isinstance(raw_steps, (list, tuple)) or not raw_steps:
            for _alias in ('steps', 'step_list', 'test_steps', 'case_steps'):
                _v = c.get(_alias)
                if isinstance(_v, (list, tuple)) and _v:
                    raw_steps = _v
                    logger.info('[HAR归因] 用例步骤键名使用了别称 %s', _alias)
                    break
        steps = []
        for st in (raw_steps or []):
            if isinstance(st, str):
                st = {'desc': st, 'exp': ''}
            if not isinstance(st, dict):
                continue
            desc = str(st.get('desc') or st.get('step_desc') or st.get('action') or '').strip()
            exp = str(st.get('exp') or st.get('expected') or st.get('expect') or '').strip()
            if not desc and not exp:
                continue
            steps.append({'step': 0, 'desc': desc, 'exp': exp})
            if len(steps) >= MAX_STEPS_HINT:
                break
        if not steps:
            # 没有步骤的「用例」不是用例，直接丢弃（否则入库后是空壳）
            _dropped += 1
            continue
        # 统一重排序号：中途跳过无效步骤时，原 enumerate 的下标会留下断号
        for n, _st in enumerate(steps, 1):
            _st['step'] = n
        name = str(c.get('name') or '').strip() or 'HAR归因用例'
        out['cases'].append({
            'name': name[:50],
            'setup_condition': str(c.get('setup_condition') or '').strip(),
            'case_mark': (str(c.get('case_mark') or '').strip() or 'HAR归因生成，待人工审核'),
            'step_table': steps,
        })

    # 丢弃必须留痕。静默丢弃会让「LLM 没产出」与「产出但被规整掉」看起来一模一样。
    if _dropped:
        logger.warning(
            '[HAR归因] 有 %d 条用例因缺少可解析的步骤被丢弃（原始 cases 共 %d 条）',
            _dropped, len(data.get('cases') or []),
        )

    return out


# ---------------------------------------------------------------- 落库
def save_cases_as_func_case(cases, project_id, user, module_id=None):
    """把归因出的用例草稿落为 FuncCase（功能用例）

    与 ai_service 的 AI 生成保持同一落库口径：
      can_autoed=3(手工) / auto_status=4(手工测试) / case_status=1(待修改)
    —— 明确标记为「草稿待人工评审」，不会被误当成可执行用例。

    :return: [{'id':.., 'name':..}, ...]
    """
    from apps.projects.models import Project
    from apps.tests.models import FuncCase

    project = Project.objects.filter(id=project_id).first()
    if project is None:
        raise ValueError('项目不存在')

    resolved_module = module_id
    if not resolved_module:
        from apps.ai_service.tasks import _get_default_module
        resolved_module = _get_default_module(project_id)

    saved = []
    for c in (cases or []):
        if not c.get('step_table'):
            continue
        obj = FuncCase.objects.create(
            name=(c.get('name') or 'HAR归因用例')[:50],
            project=project,
            owner=user,
            module_id=resolved_module,
            setup_condition=c.get('setup_condition') or '',
            case_mark=c.get('case_mark') or 'HAR归因生成，待人工审核',
            step_type=FuncCase.StepType.STEP,
            step_table=c['step_table'],
            can_autoed=FuncCase.IsAutoed.NoCan,
            auto_status=FuncCase.AutoStatus.NoAuto,
            case_status=FuncCase.CaseStatus.DESIGNING,
            create_by=user,
            update_by=user,
        )
        saved.append({'id': obj.id, 'name': obj.name})
    return saved
