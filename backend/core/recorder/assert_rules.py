# -*- coding: utf-8 -*-
"""断言规则层（P2-A2 里「规则优先」的那一半）。

职责
--------------------------------------------------------------------------
零 token 地把「录制里能推出来的断言」全部推出来，并明确标出
**「规则推不出、才值得交给模型」** 的步骤。

为什么不并进 normalizer
--------------------------------------------------------------------------
`normalize` 里的 `derive_assertions` 只在归一化那一刻跑一次，拿到的是当时的信息。
而审阅台里用户可以改定位器、取消动作、改参数 —— 规则层必须能**对任意版本的 IR
重算**，否则「补一条断言」会基于过期信息。所以这里做成纯函数：输入 IR、输出
新 IR + 覆盖报告。

与 normalizer 的分工（不是替代，是补强 + 盘点）
--------------------------------------------------------------------------
  · normalizer 已实现规则 1（变更类按钮）/ 2（导航）/ 3（fill 回显）/ 5（点击后跳转）；
  · 本模块补 **规则 4：提示类节点**（el-message / toast / role=alert）；
  · 并把「哪些步骤已被规则覆盖 / 只有需人工补期望值的 / 一条都没有的」算清楚
    —— `report()` 的 `ai_target_seqs` 就是「唯一值得花 token 的步骤集合」。

★ 本模块遵守 `core/recorder/` 包的硬约束：不 import Django / DRF / ORM，
  也不 import `core.step.run_playwright`（那会拉进 playwright 与 Django）。
  关键字与非关键字名一律以字符串引用，由单测保证与执行底座一致。
"""
import copy
import re

from core.recorder import normalizer as NZ

# ---------------------------------------------------------------------------
# 规则 4：提示类节点（消息 / 通知 / Toast）
# ---------------------------------------------------------------------------
# ★ 只匹配 class 前缀 / role / aria-live，**不匹配文案**。
#   文案是业务内容（「保存成功」「已提交」「操作失败」），任何基于文案的规则
#   在换一个站点后就失效；而 class 前缀与 aria-live 是各家 UI 框架的稳定约定：
#     Element Plus → el-message / el-notification
#     Ant Design   → ant-message / ant-notification
#     通用         → toast / snackbar / swal / role=alert|status / aria-live
TOAST_HINT_RE = re.compile(
    r'el-message|el-notification|el-alert|ant-message|ant-notification'
    r'|toast|snackbar|notifi|swal|message-box|messagebox',
    re.I,
)

# `build_dom_snippet` 的属性白名单。
# 顺序即重要性：超长截断时后面的先掉。
_SNIPPET_ATTRS = (
    'id', 'name', 'type', 'placeholder', 'role',
    'aria-label', 'aria-labelledby', 'title', 'alt', 'data-testid', 'data-test',
    'value', 'for', 'class',
)

SNIPPET_ATTR_LIMIT = 160       # 单个属性值的上限（class 常常几百字符）
SNIPPET_TEXT_LIMIT = 120       # 元素文本上限
SNIPPET_ALT_LIMIT = 220        # 候选定位器描述上限
DOM_SNIPPET_LIMIT = 4096       # 整块上限 —— 设计文档「成本控制五招」第 3 条的硬数字

DEFAULT_OPTIONS = {
    'toast_rules': True,       # 是否启用规则 4
}


def _enabled_actions(ir):
    """IR 里的有效动作（人工取消的不算 —— 审阅台取消后不该再补断言）。"""
    out = []
    for a in (ir.get('actions') or []):
        if isinstance(a, dict) and a.get('enabled', True) is not False:
            out.append(a)
    return out


def looks_like_toast(snapshot):
    """判断一个元素快照是不是「提示类节点」（规则 4 的识别器）。"""
    if not isinstance(snapshot, dict):
        return False
    attrs = snapshot.get('attrs') or {}
    if TOAST_HINT_RE.search(str(attrs.get('class') or '')):
        return True
    if str(attrs.get('role') or '').strip().lower() in ('alert', 'status'):
        return True
    if str(attrs.get('aria-live') or '').strip().lower() in ('polite', 'assertive'):
        return True
    return False


def _toast_spec(snapshot):
    """提示类节点 → 断言规格。

    ★ 为什么是 `check_object_is_not_empty` 而不是断言具体文案：
      期望值只能来自「录制那一刻这句话是什么」，而它是失败态的占位。
      真正有价值的断言是「点完之后，这个提示节点出现了」——
      文案留给人在审阅台补（note 里提示了）。
    """
    txt = (snapshot or {}).get('text') or ''
    return {
        'method': 'check_object_is_not_empty',
        'kind': 'element_text',
        'expect': None,
        'extract_keyword': 'text_content',
        'extract_args': {},
        'rule': 'toast_appeared',
        'auto': True,
        # 不 brittle：提示节点缺失/为空才是真失败，这本身就是我们要抓的
        'brittle': False,
        'note': '录到了提示类节点（%s），已生成「提示文本非空」断言；'
                '建议在审阅台把它改成具体文案' % (str(txt).strip()[:24] or '无文本'),
    }


def augment(ir, options=None):
    """补出规则 4 的断言，返回**新的** IR（绝不原地改）。

    IR 是要落库的产物，原地改会让调用方拿到「改过但不知道改了什么」的状态；
    返回新对象 + 变更摘要，调用方才能决定是否采用。
    """
    opts = dict(DEFAULT_OPTIONS)
    opts.update(options or {})

    out = copy.deepcopy(ir if isinstance(ir, dict) else {})
    added = []

    if not opts.get('toast_rules'):
        return {'ir': out, 'added': added}

    for act in _enabled_actions(out):
        snapshot = ((act.get('element') or {}).get('snapshot') or {})
        if not looks_like_toast(snapshot):
            continue
        specs = act.setdefault('assertions', [])
        if not isinstance(specs, list):
            specs = act['assertions'] = []
        # 幂等：重算两次不该变成两条（审阅台会反复点「补断言」）
        if any(isinstance(s, dict) and s.get('rule') == 'toast_appeared' for s in specs):
            continue
        specs.append(_toast_spec(snapshot))
        # ★ `added` 里带上**完整 spec**，而不只是 seq：
        #   前端要把「采纳规则建议」走 `patch/assertions` 提交，
        #   而 patch 的报文就是 [{seq, method, extract_keyword, expect, extract_args}]。
        #   只给 seq 会逼前端自己再拼一份 spec —— 两份口径必然漂移。
        added.append({'seq': act.get('seq'), 'rule': 'toast_appeared',
                      'spec': _toast_spec(snapshot)})

    return {'ir': out, 'added': added}


def report(ir):
    """规则覆盖报告 —— 决定「哪些步骤才值得花 token 交给模型」。

    三分类的语义必须分清，否则会把 token 浪费在规则已经解决的地方：
      covered     —— 已有 `auto=True` 的断言，AI 不必管；
      manual_only —— 只有 `auto=False`（规则认得这一步重要，但推不出期望值），
                     AI 可以尝试补期望值，价值中等；
      uncovered   —— 一条断言都没有，**AI 的主战场**（`ai_target_seqs`）。
    """
    covered, manual_only, uncovered = [], [], []
    by_rule = {}

    for act in _enabled_actions(ir):
        seq = act.get('seq')
        specs = [s for s in (act.get('assertions') or []) if isinstance(s, dict)]
        for s in specs:
            rule = str(s.get('rule') or '(未知)')
            by_rule[rule] = by_rule.get(rule, 0) + 1
        if any(s.get('auto') for s in specs):
            covered.append(seq)
        elif specs:
            manual_only.append(seq)
        else:
            uncovered.append(seq)

    return {
        'total': len(_enabled_actions(ir)),
        'covered': covered,
        'manual_only': manual_only,
        'uncovered': uncovered,
        # ★ 这个字段就是「AI 调用量能压到多低」的唯一依据
        'ai_target_seqs': uncovered,
        'by_rule': by_rule,
        'counts': {
            'covered': len(covered),
            'manual_only': len(manual_only),
            'uncovered': len(uncovered),
        },
    }


# ---------------------------------------------------------------------------
# 精简 DOM 片段（A1 的输入）
# ---------------------------------------------------------------------------
def _short(v, limit):
    s = '' if v is None else str(v)
    s = re.sub(r'\s+', ' ', s).strip()
    if len(s) > limit:
        return s[:limit] + '…'
    return s


def build_dom_snippet(element, limit=DOM_SNIPPET_LIMIT):
    """把一个 IR 元素压成 ≤ `limit` 字符的可读描述，供模型判断「该用什么定位器」。

    ★ 绝不整页 HTML —— 单次输入压到 4KB 以内是成本控制的核心手段之一。
      表达方式刻意选「伪标签 + 白名单属性 + 文本 + 已录到的候选」：
      模型判断定位器稳定性需要的信息就这些，其余全是噪声与 token 账单。
    ★ 超限时从**尾部**截断并显式标注 `[截断]` —— 静默截断会让模型基于
      不完整的输入给出看似合理的错误答案，比直接告诉它「信息不全」更糟。
    """
    if not isinstance(element, dict):
        return '(无元素信息)'

    snap = element.get('snapshot') or {}
    tag = str(snap.get('tag') or (element.get('name') or 'element'))
    attrs = snap.get('attrs') or {}

    parts = []
    for k in _SNIPPET_ATTRS:
        v = attrs.get(k)
        if v in (None, ''):
            continue
        parts.append('%s="%s"' % (k, _short(v, SNIPPET_ATTR_LIMIT)))

    head = '<%s%s>' % (tag, (' ' + ' '.join(parts)) if parts else '')
    text = _short(snap.get('text'), SNIPPET_TEXT_LIMIT)
    aria = _short(snap.get('aria_label'), SNIPPET_ATTR_LIMIT)
    bits = [head]
    if text:
        bits.append('text=%s' % text)
    if aria:
        bits.append('aria-label=%s' % aria)
    if snap.get('in_shadow_dom'):
        bits.append('in_shadow_dom=true')

    cands = []
    for loc in ((element.get('locators') or [])[:5]):
        if isinstance(loc, dict) and loc.get('value') not in (None, ''):
            cands.append('%s=%s' % (loc.get('by'), _short(loc.get('value'), 60)))
    if cands:
        bits.append('已录到的候选: ' + ' | '.join(cands))

    body = '\n'.join(bits)
    if len(body) > limit:
        body = body[:limit] + '\n[截断：仅提供前 %d 字符]' % limit
    return body


def low_confidence_seqs(ir, threshold):
    """规则打分偏低、值得交给 A1 的动作 seq（只在低分元素上花钱）。"""
    out = []
    for act in _enabled_actions(ir):
        el = act.get('element')
        if not isinstance(el, dict):
            continue
        conf = act.get('confidence')
        if act.get('needs_review') or (conf is not None and conf < threshold):
            out.append(act.get('seq'))
    return out


# 让调用方不必再 import normalizer（也便于单测只依赖本模块）
mutating_label_re = NZ.MUTATING_BUTTON_RE
