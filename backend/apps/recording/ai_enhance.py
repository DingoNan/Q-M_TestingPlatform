# -*- coding: utf-8 -*-
"""录制 IR 的 AI 增强（P2）—— A1 定位器优化 / A2 断言补全 / A3 用例命名。

定位（对齐 `QM平台_Web自动化录制功能_P0-P4实施计划.html` §05）
--------------------------------------------------------------------------
这里做的**不是**「让 AI 写用例」，而是补上录制方案天然缺失的三块拼图。
A3（NL → 步骤补充）本轮不做 —— 它的关键缺口（element_name 必须来自元素库）
需要与 A1 合流，按投入产出比排在 A1/A2 之后。

三条不可妥协的硬约束（都来自本项目实战教训）
--------------------------------------------------------------------------
① **数量上界**：实测过 —— 提示词不给上界时模型会产出超量内容 ⇒ 撞
   `max_tokens` 被**从字符串中间截断** ⇒ 整份 JSON 失效
   （曾现 `502 Unterminated string starting at line 1 column 3800`）。
   所以每个 prompt 都写死条数上限，**且代码侧再截一次**（不信模型自觉）。
② **可修复 + 可降级**：`json_repair` 兜底（已在 LLMClient 内）→ 失败按
   「追加『大幅精简』重试一次」→ 最终降级为 **规则产物 + `ai_error`**，
   HTTP **仍返 200**。录制 IR 本身已是有效产物；AI 失败绝不能丢录制数据，
   更不能让前端拿到 4xx 而以为「录制坏了」。
③ **只建议不落库**：所有产出带 `confidence` / `reason` 回到审阅台，
   由人勾选后走 `patch/` 写进 `ir_payload`。
   ★ 本模块**不 import `views.patch`，也绝不写 `session.ir_payload`** ——
     唯一的写路径就是审阅台的 patch，这条纪律靠「模块无写库能力」来保证。

成本控制（对应设计文档「成本控制五招」）
--------------------------------------------------------------------------
  · **规则优先**：断言先由 `core/recorder/assert_rules.py` 推导，
    **只有 `report()['ai_target_seqs']` 里的步骤**才进 prompt；
  · 定位器只对**低分元素**调模型（`low_confidence_seqs`），不在全量元素上花钱；
  · 只传精简 DOM 片段（≤4KB），绝不整页 HTML；
  · 用直连 SDK（`LLMClient` 即 openai SDK），**不走 MCP**
    —— 业界实测 MCP 约 114K tokens/交互 vs 直连 27K（−76%）；
  · 三个 scope 都不自动跑；单会话调用次数有上限（`MAX_AI_CALLS_PER_SESSION`）。
"""
import logging
import time

from core.recorder import assert_rules as AR

logger = logging.getLogger('recording')

# ===== 数量上界（prompt 里写死在文案中，代码侧再截一次） =====
MAX_LOCATOR_CANDS = 5            # 每个元素最多几个定位器候选
MAX_ASSERTS_PER_STEP = 3         # 每步最多几条断言
MAX_NAME_CANDS = 3               # 用例名最多几个候选
LOCATOR_BATCH = 8                # 单次请求最多处理几个低分元素
ASSERT_BATCH = 12                # 单次请求最多处理几个未覆盖步骤
MAX_AI_CALLS_PER_SESSION = 20    # 单会话 AI 调用上限（超限需显式确认）

LOW_CONFIDENCE = 0.6             # 低于此分的元素才值得交给 A1

SCOPE_LOCATOR = 'locator'
SCOPE_ASSERTION = 'assertion'
SCOPE_NAMING = 'naming'
SCOPES = (SCOPE_LOCATOR, SCOPE_ASSERTION, SCOPE_NAMING)

SCOPE_LABEL = {
    SCOPE_LOCATOR: '定位器优化',
    SCOPE_ASSERTION: '断言补全',
    SCOPE_NAMING: '用例命名',
}

# ★ 合法取值的唯一真源。不要在这里另抄一份 ——
#   抄一份的后果是「AI 产出的 by 落库时被静默降级成 css」，症状极难定位。
from apps.recording.importer import ELEMENT_BY_CHOICES, _VERIFY_DESC  # noqa: E402
from core.com.check import CHECK_TEXT  # noqa: E402

METHODS = tuple(CHECK_TEXT.keys())
EXTRACT_KEYWORDS = tuple(_VERIFY_DESC.keys())

# 断言里「期望值」必须能落到 check_params 的 exp_value（字符串）。
_EXPECT_MAX = 300
_VALUE_MAX = 240


class AiError(Exception):
    """AI 不可用 / 调用失败。

    ★ 消息会进 `ai_meta` 与响应体的 `ai_error`，但**不改变 HTTP 状态** ——
      调用方（视图）必须捕获它并降级成 200，见 constraints ②。
    """


# ---------------------------------------------------------------------------
# 提示词
# ---------------------------------------------------------------------------
_SHRINK_HINT = (
    '\n\n上一轮输出未能解析。请**大幅精简**：只保留最关键的几条，'
    '不要解释、不要注释、不要 markdown 代码块，直接输出合法 JSON。'
)

_A1_SYSTEM = """你是 Web 自动化测试的定位器专家。
给你目标元素的精简 DOM 描述，你要给出**更稳定**的候选定位器。

评判优先级（从高到低）：
1. 语义化属性：data-testid / data-test / name / id（且非机器随机串）
2. 无障碍：role + 可访问名、label、aria-label、placeholder
3. 可视文本：text（仅当文案稳定、不随语言/数据变化）
4. css / xpath：最后手段，且必须**避免**用 :nth-child 之类的结构索引

硬性要求：
- 最多输出 **5** 个候选，按推荐度从高到低；
- `by` 只能取以下之一：%s；
- `value` 不能为空，且必须是**可直接用于该 by 的字面量**；
- 不要输出任何解释性文字，只输出 JSON。
""" % '、'.join(ELEMENT_BY_CHOICES)

_A1_USER_TMPL = """目标元素（精简 DOM）：
%s

已录到的候选定位器（供参考，可能都不够稳）：
%s

请输出 JSON，结构严格如下（candidates 最多 5 条）：
{"candidates":[{"by":"role","value":"button","opts":{"name":"登 录"},
"reason":"用可访问名定位，改版不影响","confidence":0.9}]}
"""

_A2_SYSTEM = """你是 Web 自动化测试的断言设计专家。
给你一段浏览器录制的动作序列（部分步骤还没有任何断言），
你要为**这些步骤**各给出**最多 3 条**最有价值的断言。

设计原则：
- 优先断言「用户能观察到的结果」：提示文案、列表行数变化、URL、页面标题；
- 不要断言与业务无关的东西（元素坐标、随机 id、时间戳、动态生成的 token）；
- 期望值必须是**确定的字面量**；如果你推不出确定值，就把 expect 设为 null，
  并在 reason 里说明「需人工补期望值」——不要编造；
- 不要为「输入类」动作之外的步骤重复添加「元素存在」这类无信息量断言。

硬性要求：
- 每条断言必须带 `seq`（步骤号）与 `method`；
- `method` 只能取以下之一：%s；
- `extract_keyword` 只能取以下之一：%s；
- ★ `expect` 一律输出**字符串**（不要输出 JSON 布尔或数字）：
    · method 含 `bool` 时，只能填 `"true"` 或 `"false"`；
    · method 含 `number` 时，填数字的字符串形式，如 `"3"`、`"12.5"`；
    · method 含 `object_is_empty` / `object_is_not_empty` 时，`expect` 必须为 null
      （这两种校验只看实际值，不看期望值）；
    · 其它情况填期望文本；
- ★ 每条 expect 不超过 %d 字符；
- 不要输出任何解释性文字，只输出 JSON。
""" % ('、'.join(METHODS), '、'.join(EXTRACT_KEYWORDS), _EXPECT_MAX)

_A2_USER_TMPL = """动作序列（JSON 数组，seq 为步骤号；covered=false 表示该步还没有断言）：
%s

请输出 JSON，结构严格如下（每个 seq 最多 3 条）：
{"assertions":[{"seq":5,"method":"check_object_is_not_empty",
"extract_keyword":"text_content","extract_args":{},
"expect":null,"reason":"点击登录后应出现成功提示，期望值需人工补"}]}
"""

_A3_SYSTEM = """你是测试用例命名专家。
根据一段浏览器录制的动作序列，给出**最多 3 个**简洁、可读、能一眼看出业务意图的
中文用例名。

要求：
- 长度不超过 40 个字符；
- 用「动词 + 对象 + 预期」的风格，例如「登录系统后新建脚本用例」；
- 不要包含日期、编号、环境名等易变信息；
- 不要输出任何解释性文字，只输出 JSON。
"""

_A3_USER_TMPL = """动作序列摘要：
%s

请输出 JSON，结构严格如下（names 最多 3 条）：
{"names":[{"name":"登录后新建脚本用例","reason":"覆盖登录与新建两条主干路径"}]}
"""


# ---------------------------------------------------------------------------
# AI 配置 / 客户端
# ---------------------------------------------------------------------------
def pick_ai_config(project_id, ai_config_id=None):
    """选一个启用的 AI 配置。没配到就抛 AiError（可读原因）。"""
    from apps.projects.models import AiConfig

    qs = AiConfig.objects.filter(project_id=project_id, is_active=True, is_delete=False)
    if ai_config_id:
        qs = qs.filter(id=ai_config_id)
    cfg = qs.order_by('id').first()
    if cfg is None:
        raise AiError(
            '项目 %s 下没有启用中的 AI 配置%s，请先到「AI 模型设置」里启用一个'
            % (project_id, ('（id=%s）' % ai_config_id) if ai_config_id else ''))
    return cfg


def _ask_json(client, system_prompt, user_prompt, max_tokens):
    """调一次模型，带「大幅精简」重试阶梯。返回 (payload, meta)。

    ★ 重试的必要性：`LLMClient.chat_json` 内部已处理「JSON 语法错」，
      但**外层的传输层失败（超时/限流/5xx）它不重试**。
      而流式网关抖动是线上最常见的一类偶发失败，重试一次能救回大部分。
    """
    try:
        got = client.chat_json(system_prompt, user_prompt, temperature=0.2,
                               max_tokens=max_tokens, return_meta=True)
        payload, meta = got if isinstance(got, tuple) else (got, {})
        meta['retried'] = False
        return payload, meta
    except Exception as e1:                       # noqa: BLE001 —— 必须兜住一切
        logger.warning('[REC-AI] 首次调用失败，按「大幅精简」重试一次: %s', e1)
        try:
            got = client.chat_json(system_prompt + _SHRINK_HINT, user_prompt,
                                   temperature=0.0, max_tokens=max_tokens,
                                   return_meta=True)
            payload, meta = got if isinstance(got, tuple) else (got, {})
            meta['retried'] = True
            return payload, meta
        except Exception as e2:                   # noqa: BLE001
            raise AiError('模型调用失败（已重试一次）：%s' % e2)


# ---------------------------------------------------------------------------
# A1 · 定位器优化
# ---------------------------------------------------------------------------
def _locator_targets(ir):
    """挑出「规则打分低、值得花 token」的元素动作。"""
    seqs = AR.low_confidence_seqs(ir, LOW_CONFIDENCE)
    by_seq = {}
    for a in (ir.get('actions') or []):
        if isinstance(a, dict) and a.get('seq') in seqs:
            by_seq[a.get('seq')] = a
    out = []
    for seq in seqs[:LOCATOR_BATCH]:
        act = by_seq.get(seq)
        if act and isinstance(act.get('element'), dict):
            out.append(act)
    return out


def suggest_locators(ir, client):
    """低分元素 → 最多 `MAX_LOCATOR_CANDS` 个候选定位器。"""
    targets = _locator_targets(ir)
    if not targets:
        return [], {}, []

    blocks = []
    for act in targets:
        el = act['element']
        cands = '\n'.join(
            '  - %s=%s' % (c.get('by'), AR._short(c.get('value'), 60))
            for c in (el.get('locators') or [])[:5] if isinstance(c, dict))
        blocks.append(
            '### seq=%s（当前置信度 %s）\n%s\n当前首选定位器：%s\n%s'
            % (act.get('seq'), act.get('confidence'),
               AR.build_dom_snippet(el),
               ((el.get('locators') or [{}])[0] or {}).get('by'),
               cands or '  (无)'))
    user = _A1_USER_TMPL % ('\n\n'.join(blocks), '见上')

    payload, meta = _ask_json(client, _A1_SYSTEM, user, max_tokens=2048)

    # ★ 模型返回的是「一批候选」，但没说清属于哪个 seq（多目标时它经常会乱）。
    #   稳妥做法：按顺序回填到 targets —— 并在 reason 前缀标出归属，便于人核对。
    got = payload.get('candidates') if isinstance(payload, dict) else None
    if not isinstance(got, list):
        got = []
    got = got[:MAX_LOCATOR_CANDS * len(targets)]

    out, dropped = [], []

    def _norm_loc(raw, act, idx):
        if not isinstance(raw, dict):
            dropped.append({'scope': SCOPE_LOCATOR, 'why': '不是对象',
                            'item': str(raw)[:120]})
            return None
        by = str(raw.get('by') or '').strip().lower()
        value = raw.get('value')
        if by not in ELEMENT_BY_CHOICES:
            dropped.append({'scope': SCOPE_LOCATOR,
                            'why': 'by 非法（%s）' % by, 'item': str(value)[:120]})
            return None
        if value in (None, '') or len(str(value)) > _VALUE_MAX:
            dropped.append({'scope': SCOPE_LOCATOR, 'why': 'value 空或过长',
                            'item': str(value)[:120]})
            return None
        opts = raw.get('opts') if isinstance(raw.get('opts'), dict) else {}
        try:
            conf = float(raw.get('confidence'))
        except (TypeError, ValueError):
            conf = 0.5
        return {
            'seq': act.get('seq'),
            'name': ((act.get('element') or {}).get('name') or '')[:60],
            'by': by,
            'value': str(value),
            'opts': opts,
            'confidence': max(0.0, min(1.0, conf)),
            'reason': str(raw.get('reason') or '')[:200],
            'source': 'ai',
            'order': idx,
        }

    # 单目标时直接对应；多目标时按顺序平均分配（并在前端展示 seq 供人核对）
    if len(targets) == 1:
        for i, raw in enumerate(got):
            rec = _norm_loc(raw, targets[0], i)
            if rec:
                out.append(rec)
    else:
        per = max(1, len(got) // len(targets)) if got else 0
        for ti, act in enumerate(targets):
            chunk = got[ti * per:(ti + 1) * per] if per else []
            for i, raw in enumerate(chunk):
                rec = _norm_loc(raw, act, i)
                if rec:
                    out.append(rec)

    return out[:MAX_LOCATOR_CANDS * len(targets)], meta, dropped


# ---------------------------------------------------------------------------
# A2 · 断言补全
# ---------------------------------------------------------------------------
def _summarize_actions(ir, seqs):
    """动作序列摘要（只带判断所需字段）—— 别把整份 IR 塞进 prompt。"""
    lines = []
    for a in (ir.get('actions') or []):
        if not isinstance(a, dict):
            continue
        seq = a.get('seq')
        el = a.get('element') if isinstance(a.get('element'), dict) else {}
        args = []
        for k, v in (a.get('args') or {}).items():
            if isinstance(v, dict):
                args.append('%s=%s' % (k, v.get('value') if v.get('kind') == 'literal'
                                       else '${%s}' % v.get('var_name')))
        lines.append(
            '{"seq":%s,"keyword":%s,"enabled":%s,"covered":%s,'
            '"element":%s,"args":%s,"note":%s}'
            % (seq, _j(a.get('keyword')), str(a.get('enabled', True) is not False).lower(),
               str(seq not in seqs).lower(), _j(el.get('name') or ''),
               _j(', '.join(args)), _j('; '.join(a.get('notes') or [])[:120])))
    return '[\n%s\n]' % ',\n'.join(lines)


def _j(v):
    import json
    return json.dumps(v, ensure_ascii=False)


# ---------------------------------------------------------------------------
# A2 · 断言补全
# ---------------------------------------------------------------------------
# ★★ 期望值（expect）的类型契约 —— 由 `core/com/check.py` 的**实际消费方式**决定，
#    这条不看源码是看不出来的，看了一定要按它办（P2 E2E 实测抓出来的真雷）：
#
#    · `check_bool_equal` / `check_bool_not_equal` 第一句就是
#        `if check_exp_value.upper() == check_act_value.upper()`
#      ⇒ exp_value **必须是字符串**。模型时而返回 JSON 布尔 `true`、时而返回字符串
#      `"True"` —— 前者在执行期抛 `AttributeError: 'bool' object has no attribute
#      'upper'`，**用例是「崩掉」而不是「断言失败」**，现场看起来像环境问题，
#      排查成本远高于期望值写错本身。
#    · `check_number_*`（6 个）走 `int()`，失败再退化 `float()`
#      ⇒ 期望值必须「可转数字」。
#    · `check_equal` / `check_not_equal` 用 `==` 直接比，而运行期的 act_value 来自
#      `${stepResponse.<step_id>.funcReturn}`，**恒为字符串**
#      ⇒ 期望值若保持数字形态，会出现 `'1' != 1` 这种「明明对却失败」。
#    · `check_object_is_empty` / `check_object_is_not_empty` **完全不看** exp_value
#      ⇒ 一律置 None，免得把噪声带进 `tb_step.check_params`。
#
#  ⇒ `_norm_expect` 的不变量：**返回值只可能是 `None` 或 `str`**，
#    永远不会是 bool / int / float。闸门里有专门的检查盯着这条不变量。
_BOOL_METHODS = ('check_bool_equal', 'check_bool_not_equal')
_NUM_METHODS = ('check_number_equal', 'check_number_not_equal', 'check_number_gt',
                'check_number_ge', 'check_number_lt', 'check_number_le')
_IGNORE_EXPECT = ('check_object_is_empty', 'check_object_is_not_empty')


def _norm_expect(method, raw):
    """把模型给的 expect 规范成运行期能安全消费的形状。

    返回 `(value, why)`：`why` 非空表示这条建议应当**丢弃**并说明原因
    （与其它白名单校验同款处理 —— 绝不「猜一个差不多的」）。
    """
    if method in _IGNORE_EXPECT:
        return None, ''
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None, '缺少 expect（该断言必须给出期望值）'
    # ★ bool 必须先于数字判断：Python 里 `isinstance(True, int)` 是 True，
    #   顺序反了会把 `True` 当数字处理（`float(True)` = 1.0，静默变成数字 1）。
    if method in _BOOL_METHODS:
        if isinstance(raw, bool):
            return ('true' if raw else 'false'), ''
        s = str(raw).strip().lower()
        if s in ('true', 'false'):
            return s, ''
        if s in ('1', '0', 'yes', 'no'):
            return ('true' if s in ('1', 'yes') else 'false'), ''
        return None, 'expect 不是布尔值（%s）' % str(raw)[:40]
    if method in _NUM_METHODS:
        s = str(raw).strip()
        try:
            float(s)
        except (TypeError, ValueError):
            return None, 'expect 不是数字（%s）' % s[:40]
        return s, ''
    s = str(raw).strip()
    if len(s) > _EXPECT_MAX:
        return None, 'expect 过长（%d 字符）' % len(s)
    return s, ''


def suggest_assertions(ir, client, manual_only_seqs=()):
    """未覆盖（+ 只有需人工补的）步骤 → 最多 `MAX_ASSERTS_PER_STEP` 条断言/步。"""
    rep = AR.report(ir)
    targets = list(rep['ai_target_seqs'])
    # 手工-only 的步骤也值得让模型试着补期望值（规则认得它重要，只是推不出值）
    extra = [s for s in manual_only_seqs if s not in targets]
    seqs = (targets + extra)[:ASSERT_BATCH]
    if not seqs:
        return [], {}, []

    user = _A2_USER_TMPL % _summarize_actions(ir, set(seqs))
    payload, meta = _ask_json(client, _A2_SYSTEM, user, max_tokens=3072)

    got = payload.get('assertions') if isinstance(payload, dict) else None
    if not isinstance(got, list):
        got = []

    valid_seqs = set(seqs)
    out, dropped, per_step = [], [], {}
    for raw in got:
        if not isinstance(raw, dict):
            dropped.append({'scope': SCOPE_ASSERTION, 'why': '不是对象',
                            'item': str(raw)[:120]})
            continue
        seq = raw.get('seq')
        if seq not in valid_seqs:
            dropped.append({'scope': SCOPE_ASSERTION,
                            'why': 'seq 不在目标集合内（%s）' % seq,
                            'item': str(raw)[:120]})
            continue
        if per_step.get(seq, 0) >= MAX_ASSERTS_PER_STEP:     # ★ 代码侧再截一次
            dropped.append({'scope': SCOPE_ASSERTION, 'why': '超过每步 %d 条上界'
                            % MAX_ASSERTS_PER_STEP, 'item': str(raw)[:120]})
            continue
        method = str(raw.get('method') or '').strip()
        if method not in METHODS:
            dropped.append({'scope': SCOPE_ASSERTION,
                            'why': 'method 非法（%s）' % method, 'item': str(raw)[:120]})
            continue
        ek = raw.get('extract_keyword')
        ek = None if ek in (None, '') else str(ek).strip()
        if ek is not None and ek not in EXTRACT_KEYWORDS:
            dropped.append({'scope': SCOPE_ASSERTION,
                            'why': 'extract_keyword 非法（%s）' % ek,
                            'item': str(raw)[:120]})
            continue
        # ★ 期望值必须按**运行期的消费方式**规范化，不能原样透传（见 _norm_expect docstring）
        expect, why = _norm_expect(method, raw.get('expect'))
        if why:
            dropped.append({'scope': SCOPE_ASSERTION, 'why': why,
                            'item': str(raw)[:120]})
            continue
        eargs = raw.get('extract_args') if isinstance(raw.get('extract_args'), dict) else {}
        per_step[seq] = per_step.get(seq, 0) + 1
        out.append({
            'seq': seq,
            'method': method,
            'extract_keyword': ek,
            'extract_args': eargs,
            'expect': expect,
            'confidence': 0.7,
            'reason': str(raw.get('reason') or '')[:200],
            'source': 'ai',
            'rule': 'ai_suggested',
            'auto': True,
        })
    return out, meta, dropped


# ---------------------------------------------------------------------------
# A3 · 用例命名
# ---------------------------------------------------------------------------
def suggest_names(ir, client):
    rep = AR.report(ir)
    if not rep['total']:
        return [], {}, []
    payload, meta = _ask_json(client, _A3_SYSTEM, _A3_USER_TMPL
                              % _summarize_actions(ir, set()), max_tokens=1024)
    got = payload.get('names') if isinstance(payload, dict) else None
    if not isinstance(got, list):
        got = []
    out, dropped = [], []
    for raw in got[:MAX_NAME_CANDS]:
        if not isinstance(raw, dict):
            dropped.append({'scope': SCOPE_NAMING, 'why': '不是对象',
                            'item': str(raw)[:120]})
            continue
        name = str(raw.get('name') or '').strip()
        if not name:
            dropped.append({'scope': SCOPE_NAMING, 'why': 'name 为空', 'item': ''})
            continue
        out.append({'name': name[:40], 'reason': str(raw.get('reason') or '')[:200],
                    'source': 'ai'})
    return out, meta, dropped


# ---------------------------------------------------------------------------
# 会话级调用记账
# ---------------------------------------------------------------------------
def calls_used(session):
    meta = session.ai_meta if isinstance(session.ai_meta, dict) else {}
    try:
        return int(meta.get('total_calls') or 0)
    except (TypeError, ValueError):
        return 0


def _bump_calls(session, records, calls):
    """把本次调用记进 `session.ai_meta`。

    ★ 用「先读快照再整体写回」在这里是安全的：`ai_meta` 只被本端点写，
      且并发同一会话做 AI 增强没有实际场景（前端按钮是人工点的）。
      不做 F() 自增是因为 ai_meta 是 JSONField，承载不了列级原子自增；
      真要并发，正确做法是行级 select_for_update，而不是假装原子。
    ★ 写失败只记日志、不影响响应 —— 记账坏了不该让用户拿不到建议。
    """
    meta = dict(session.ai_meta) if isinstance(session.ai_meta, dict) else {}
    hist = list(meta.get('calls') or [])
    hist.extend(records)
    meta['calls'] = hist[-30:]                     # 只留最近 30 条，避免无限膨胀
    meta['total_calls'] = calls_used(session) + calls
    meta['last_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        session.ai_meta = meta
        session.save(update_fields=['ai_meta', 'update_time'])
    except Exception as e:                         # noqa: BLE001
        logger.warning('[REC-AI] ai_meta 记账失败 session=%s err=%s', session.id, e)
    return meta


# ---------------------------------------------------------------------------
# 编排
# ---------------------------------------------------------------------------
def enhance(session, project_id, scopes=None, ai_config_id=None):
    """P2 总入口。返回响应体（**永不带 4xx**，失败信息在 `ai_error`）。

    设计要点：
      · 规则层**无条件**先跑（零 token），即使 AI 不可用也有东西可看；
      · 每 scope 只发 **1 次**模型调用（批量），调用量可预测；
      · 超会话上限时直接降级，不偷偷扣额度。
    """
    want = [s for s in (scopes or []) if s in SCOPES]
    ir = session.ir_payload if isinstance(session.ir_payload, dict) else {}

    # ---- 1) 规则层（零 token，始终产出） ----
    aug = AR.augment(ir)
    ir2 = aug['ir']
    rep = AR.report(ir2)
    rule_assertions = []
    for act in (ir2.get('actions') or []):
        if not isinstance(act, dict) or act.get('enabled', True) is False:
            continue
        for spec in (act.get('assertions') or []):
            if not isinstance(spec, dict):
                continue
            rule_assertions.append({
                'seq': act.get('seq'),
                'method': spec.get('method'),
                'extract_keyword': spec.get('extract_keyword'),
                'extract_args': spec.get('extract_args') or {},
                'expect': spec.get('expect'),
                'rule': spec.get('rule'),
                'auto': bool(spec.get('auto')),
                'brittle': bool(spec.get('brittle')),
                'note': spec.get('note') or '',
                'source': 'rule',
            })

    result = {
        'session_id': session.id,
        'scopes': want,
        'rule': {
            'added': aug['added'],
            'assertions': rule_assertions,
            'report': rep,
        },
        'locator': [],
        'assertion': [],
        'naming': [],
        'dropped': [],
        'ai_meta': {
            'used_calls': calls_used(session),
            'limit': MAX_AI_CALLS_PER_SESSION,
            'calls': [],
        },
        'ai_error': '',
    }

    if not want:
        return result

    # ---- 2) 目标盘点：没有可做的就别白调一次模型 ----
    todo = []
    if SCOPE_LOCATOR in want and _locator_targets(ir2):
        todo.append(SCOPE_LOCATOR)
    if SCOPE_ASSERTION in want and (rep['ai_target_seqs'] or rep['manual_only']):
        todo.append(SCOPE_ASSERTION)
    if SCOPE_NAMING in want and rep['total']:
        todo.append(SCOPE_NAMING)

    if not todo:
        result['ai_meta']['skipped'] = '规则层已覆盖全部步骤，无需调用模型（零 token）'
        return result

    # ---- 3) 会话级上限 ----
    used = calls_used(session)
    if used + len(todo) > MAX_AI_CALLS_PER_SESSION:
        result['ai_error'] = (
            '本会话 AI 调用已达上限（%d 次，本次还需 %d 次）。'
            '如需继续，请新建录制会话或显式确认提高上限。'
            % (MAX_AI_CALLS_PER_SESSION, len(todo)))
        result['ai_meta']['skipped'] = 'over_limit'
        return result

    # ---- 4) 建客户端（没配 AI 就降级，不 4xx） ----
    try:
        cfg = pick_ai_config(project_id, ai_config_id)
    except AiError as e:
        result['ai_error'] = str(e)
        return result
    try:
        from apps.ai_service.llm import LLMClient
        client = LLMClient(cfg.id)
    except Exception as e:                          # noqa: BLE001
        result['ai_error'] = 'AI 配置（id=%s，模型 %s）初始化失败：%s' % (
            cfg.id, getattr(cfg, 'model_name', '?'), e)
        return result

    # ---- 5) 逐个 scope 调模型；单个 scope 失败不影响其它 ----
    records, calls = [], 0
    errors = []

    def _run(scope, fn):
        nonlocal calls
        t0 = time.time()
        try:
            out, meta, dropped = fn()
        except AiError as e:
            calls += 1
            records.append({'scope': scope, 'ok': False, 'error': str(e)[:300],
                            'elapsed_ms': int((time.time() - t0) * 1000)})
            errors.append('%s：%s' % (SCOPE_LABEL[scope], e))
            return [], []
        except Exception as e:                      # noqa: BLE001
            calls += 1
            logger.exception('[REC-AI] %s 异常', scope)
            records.append({'scope': scope, 'ok': False, 'error': str(e)[:300],
                            'elapsed_ms': int((time.time() - t0) * 1000)})
            errors.append('%s：%s' % (SCOPE_LABEL[scope], e))
            return [], []
        calls += 1
        m = dict(meta or {})
        records.append({
            'scope': scope, 'ok': True,
            'model': m.get('model') or getattr(cfg, 'model_name', ''),
            'elapsed_ms': m.get('elapsed_ms', int((time.time() - t0) * 1000)),
            'prompt_tokens': m.get('prompt_tokens'),
            'completion_tokens': m.get('completion_tokens'),
            'total_tokens': m.get('total_tokens'),
            'attempts': m.get('attempts'),
            'repaired': m.get('repaired'),
            'retried': m.get('retried'),
            'suggestions': len(out),
        })
        return out, dropped

    if SCOPE_LOCATOR in todo:
        out, dropped = _run(SCOPE_LOCATOR, lambda: suggest_locators(ir2, client))
        result['locator'] = out
        result['dropped'].extend(dropped)
    if SCOPE_ASSERTION in todo:
        out, dropped = _run(SCOPE_ASSERTION,
                            lambda: suggest_assertions(ir2, client, rep['manual_only']))
        result['assertion'] = out
        result['dropped'].extend(dropped)
    if SCOPE_NAMING in todo:
        out, dropped = _run(SCOPE_NAMING, lambda: suggest_names(ir2, client))
        result['naming'] = out
        result['dropped'].extend(dropped)

    # ---- 6) 记账（含失败记录，便于成本核算与排障） ----
    meta_after = _bump_calls(session, records, calls)
    result['ai_meta'] = {
        'used_calls': meta_after.get('total_calls', calls_used(session)),
        'limit': MAX_AI_CALLS_PER_SESSION,
        'calls': records,
    }
    if errors:
        result['ai_error'] = '；'.join(errors)[:600]
    return result
