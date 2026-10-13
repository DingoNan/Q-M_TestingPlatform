# -*- coding: utf-8 -*-
"""归一化引擎：录制事件流 → IR（P0-③）

职责边界（很重要，别把逻辑写串）
    sources.py        只做「来源 → 内部事件流」的形状转换
    locator_score.py  只做「定位器打分与排序」
    本文件            只做「事件流 → IR」：噪声过滤 / 关键字映射 / 参数化 / 断言推导 / 组装

★ 本文件不碰数据库、不碰 Django。
   落库所需的「元素 id」在这里只以 **引用（element_ref）** 形式出现，
   由落库层（apps/recording/importer.py）解析成真实 id。
   这样归一化逻辑才能离线单测 —— 这是整套方案里唯一能 100% 自动化验证的部分。

★ 生成的断言为什么能挂在本步骤自己身上
   run_step_playwright 在每步末尾会执行：
       case_params.stepResponse[f'{step_id}']['funcReturn'] = return_value
       loop_assert_by_check_list(step['check_params'], ...)
   也就是说，一个 `text_content` 步骤可以在 check_params 里用
   `${stepResponse.<自己这个步骤的 id>.funcReturn}` 断言自己的返回值。
   所以「断言」不需要额外插一个提取步骤 —— 本引擎产出的断言规格里带上
   `extract_keyword`，落库时把该步骤的 keyword 换成提取类关键字即可。

★ 关键字名的真源是 core/step/run_playwright.py。
   本文件只以字符串引用，不 import（那会拉进 playwright 与 Django）。
   单测里有一条断言专门校验「本引擎产出的所有 keyword 都真实存在于执行底座」。
"""

import hashlib
import re
from collections import Counter, OrderedDict

from core.recorder import locator_score as LS

# ---------------------------------------------------------------------------
# 事件类型分类
# ---------------------------------------------------------------------------
# 需要可定位目标的事件类型：没有目标 = 无意义动作（噪声过滤规则 7）
ELEMENT_EVENT_TYPES = {
    'click', 'change', 'input', 'check', 'uncheck', 'hover', 'assert', 'wait',
}

# 平台不支持 / 不需要的事件类型，直接丢弃并给出可读原因
DROP_EVENT_TYPES = {
    'wait_expr': '等待 JS 表达式的动作平台不支持（无对应关键字）',
    'close': '关闭浏览器动作由平台统一管理，不应出现在用例里',
    'ignore': '该动作类型与测试无关',
}

# 会被当作「值写入」的事件类型（用于输入防抖合并）
VALUE_EVENT_TYPES = ('input', 'change')

# 参数化只作用于这些「承载用户数据」的参数名（结构性参数保持字面量）
VALUE_ARG_KEYS = ('value', 'file_path')

# 页面级动作中允许没有 target 的
PAGE_LEVEL_TYPES = {'navigate', 'scroll', 'set_viewport', 'keydown', 'keyup'}

# ---------------------------------------------------------------------------
# 默认参数
# ---------------------------------------------------------------------------
DEFAULT_OPTIONS = {
    'debounce_ms': 800,        # 规则 1：输入防抖合并窗口
    'hover_prune_ms': 500,     # 规则 2：hover 链剪枝窗口
    'dedupe_click_ms': 300,    # 规则 3：重复点击去重窗口
    'min_scroll_px': 50,       # 规则 4：微滚动丢弃阈值
    'param_heuristics': True,  # 是否启用参数化启发式
    'assertion_rules': True,   # 是否启用规则式断言推导
    'max_actions': 0,          # 0 = 不限；>0 时超出部分丢弃并告警
}

# ---------------------------------------------------------------------------
# 敏感字段（规则 6）
# ---------------------------------------------------------------------------
SENSITIVE_NAME_RE = re.compile(
    r'(pwd|passwd|password|pass|secret|token|credential|auth|private[_-]?key|captcha|otp'
    r'|密码|口令|密钥|验证码|凭证)',
    re.I,
)
SENSITIVE_VALUE_RE = re.compile(
    r'^(ghp_|sk-|eyJ[A-Za-z0-9_-]{10,}\.)',  # 常见 token 前缀（JWT / GitHub / OpenAI）
)

# ---------------------------------------------------------------------------
# 扩展自身事件（规则 5）
# ---------------------------------------------------------------------------
SELF_MARKERS = ('qm-recorder', 'qm-recording-panel', 'data-qm-recorder', 'qm-ext-')

# ---------------------------------------------------------------------------
# 参数化启发式
# ---------------------------------------------------------------------------
RE_MOBILE = re.compile(r'^1[3-9]\d{9}$')
RE_EMAIL = re.compile(r'^[\w.+-]+@[\w-]+\.[\w.-]+$')
RE_IDCARD = re.compile(r'^\d{17}[\dXx]$')
RE_DATETIME = re.compile(r'^\d{4}[-/]\d{2}[-/]\d{2}([ T]\d{2}:\d{2}(:\d{2})?)?$')

USERNAME_FIELD_RE = re.compile(r'(user|account|login|username|loginname|operator|admin)', re.I)

# 表单按钮里「会改变状态」的那类 —— 命中即建议加断言
MUTATING_BUTTON_RE = re.compile(
    r'(提交|保存|登录|登陆|查询|搜索|删除|移除|新增|添加|确定|确认|发布|导出|导入|重置|'
    r'save|submit|login|search|delete|remove|add|create|confirm|ok|publish|export)',
    re.I,
)


def _merge_options(options):
    opts = dict(DEFAULT_OPTIONS)
    if options:
        opts.update({k: v for k, v in options.items() if v is not None})
    return opts


# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------
def _element_ref(by, value, opts=None):
    """由定位表达式生成稳定的元素引用。

    ★ 为什么用 hash 而不是递增序号：录制里同一个元素往往出现多次
      （先 fill 后 click、或多次操作同一个下拉）。用定位表达式做 key，
      同一元素天然映射到同一 ref ⇒ 落库时能复用同一条元素记录，
      而不是给元素库灌进 N 条重复元素。

    ★ 为什么 opts 也必须参与指纹（踩过的坑）：
      role 类候选的 value 是**角色名**（textbox/button），真正区分元素的是
      opts.name（无障碍名）。只 hash by+value 的话，页面上所有文本框会算出
      同一个 ref ⇒ 几十个输入框在元素库里被合并成一条，回放时全部指向第一个。
    """
    raw = '%s|%s|%s' % (by or '', value or '', json_dumps_safe(opts or {}))
    return 'el_' + hashlib.md5(raw.encode('utf-8')).hexdigest()[:8]


def _best_locator(target):
    """取打分最高的候选定位器；没有候选返回 (None, None)。"""
    if not target:
        return None, None
    cands = target.get('selectors') or []
    if not cands:
        return None, None
    top = cands[0]
    return top.get('by'), top.get('value')


def _target_identity(tgt):
    """元素身份键：判断两个事件是否作用于"同一个元素"。

    ★ 必须优先用适配层算好的 tgt['key']（见 sources._target_key_from）。
      不要退回到"打分最高定位器"来当身份 —— role 候选的 value 是角色名，
      那样会把页面上所有同类控件判成同一个元素，进而被防抖合并吞掉。
    """
    if not tgt:
        return None
    if tgt.get('key'):
        return str(tgt['key'])
    attrs = tgt.get('attrs') or {}
    for k in ('data-testid', 'id', 'name', 'placeholder', 'title', 'alt', 'aria-label'):
        v = attrs.get(k)
        if v:
            return '%s=%s' % (k, v)
    if tgt.get('aria_label'):
        return 'aria=' + str(tgt['aria_label'])
    if tgt.get('text'):
        return 'text=' + str(tgt['text']).strip()[:60]
    for s in (tgt.get('selectors') or []):
        if isinstance(s, dict) and s.get('value'):
            nm = (s.get('opts') or {}).get('name')
            return '%s|%s|%s' % (s.get('by'), s.get('value'), nm or '')
    if tgt.get('node_name'):
        return 'node=' + str(tgt['node_name'])
    return None


def _target_key(ev):
    """用于「是否同一个元素」的比较键。"""
    return _target_identity(ev.get('target'))


def _has_usable_target(ev):
    """是否拿得到任何可用于定位目标的信息。"""
    tgt = ev.get('target') or {}
    return bool(_target_identity(tgt) or tgt.get('node_name') or tgt.get('attrs'))


def _gap(prev, cur):
    """返回两个事件的时间差（ms）；任一时间戳缺失时返回 None（= 未知）。"""
    a, b = prev.get('t'), cur.get('t')
    if a is None or b is None:
        return None
    try:
        return int(b) - int(a)
    except (TypeError, ValueError):
        return None


def _within(prev, cur, window_ms):
    """是否在时间窗内。

    ★ 返回值有三态，别当成 bool 用：
        True  = 时间戳齐全且确实在窗口内（证据充分）
        False = 时间戳齐全但超出窗口（确定不在）
        None  = 时间戳缺失，无法判定（证据不足）

    三态设计的原因：不同规则的「证据不足」处理方式不同 ——
      · 输入防抖合并：证据不足时按「相邻即同一段输入」处理（安全，见规则 1）
      · 重复点击去重：证据不足时必须**保留两次点击**（删掉一次真实点击会改变用例行为）
      · hover 剪枝：证据不足时看后续事件类型（见规则 2）
    把这三个规则统一写成「时间戳缺失就当真」会静默改坏用例。
    """
    gap = _gap(prev, cur)
    if gap is None:
        return None
    return gap <= window_ms


def _field_haystack(ev):
    """把这个字段「是什么」的所有可用线索拼成一串，供正则判定。

    ★ 为什么要抽成唯一一处：判断「这个字段是不是账号 / 是不是敏感字段」有两条
      独立路径 —— `_is_sensitive`（决定原文会不会落库）与 `_value_obj` 的参数化
      启发式（决定值要不要提升成变量）。历史上两处各自维护「该看哪些线索」的
      清单，于是**两次出现同一个漏洞**：
        · 一次是 `_is_sensitive` 补了选择器线索，参数化那侧没补 ⇒ 密码明文进 IR；
        · 一次是 `_is_sensitive` 有了选择器线索，参数化的账号识别没有 ⇒
          账号被写死成字面量，换账号回放必须手改。
      线索清单收敛到本函数后，改一处即全局生效。

    线索来源（按可靠性排序，全部保留）：
      1) 显式 DOM 属性（attrs）—— 平台自有扩展 / 原生事件才带；
      2) 元素描述（text / aria_label / node_name）—— Chrome Recorder 的 `aria/xxx`；
      3) **选择器**（CSS / role 候选 + opts）—— DevTools Recorder 导出**唯一**的线索，
         例如 `input[type="password"]`、`#username`、`select#region`。
    """
    tgt = ev.get('target') or {}
    attrs = tgt.get('attrs') or {}
    parts = []
    for key in ('name', 'id', 'placeholder', 'autocomplete', 'aria_label',
                'title', 'data-testid', 'role', 'type'):
        v = attrs.get(key) or tgt.get(key)
        if v:
            parts.append(str(v))
    for key in ('text', 'key', 'aria_label', 'node_name', 'tag'):
        v = tgt.get(key)
        if v:
            parts.append(str(v))
    for c in (tgt.get('selectors') or []):
        if isinstance(c, dict):
            parts.append(str(c.get('value') or ''))
            parts.append(json_dumps_safe(c.get('opts') or {}))
        elif c:
            parts.append(str(c))
    return ' '.join(parts)


def _is_sensitive(ev):
    """敏感字段判定。

    判据（任一命中即为敏感）：
      1) 明确的 DOM 属性：type=password
      2) 字段名/占位符/无障碍名命中敏感词（含中文：密码/口令/密钥/验证码）
      3) 值本身形似 token（JWT / GitHub / OpenAI 前缀）
      4) ★ 选择器线索：Chrome DevTools Recorder 的导出**不带 DOM 属性**，
         只在 CSS 选择器里留下 `input[type="password"]`；
         元素描述是 `aria/密码`。这两处是 DevTools 来源唯一能拿到判据的地方 ——
         漏掉它们就等于"从 Chrome 录进来的密码全部明文落库"。

    ★ 这个函数决定了「原文会不会进数据库」，宁可多判（把普通字段当敏感），
      也不可漏判。多判的代价是用户要手工填一个变量；漏判的代价是明文凭据入库。
    """
    tgt = ev.get('target') or {}
    attrs = tgt.get('attrs') or {}

    # 1) 明确的 DOM 属性
    if str(attrs.get('type') or '').lower() == 'password':
        return True

    # 2) / 4) 字段名、元素描述、选择器线索 —— 统一走 _field_haystack
    hay = _field_haystack(ev)
    if hay and SENSITIVE_NAME_RE.search(hay):
        return True
    if re.search(r'type\s*=\s*[\'"]?password', hay, re.I):
        return True

    # 3) 值形似 token
    val = ev.get('value')
    if val and SENSITIVE_VALUE_RE.search(str(val)):
        return True
    return False


def _is_extension_self(ev):
    """规则 5：扩展自身面板 / DevTools 产生的事件。"""
    tgt = ev.get('target') or {}
    blob = []
    blob.append(str(tgt.get('node_name') or ''))
    blob.append(str(tgt.get('text') or ''))
    blob.append(json_dumps_safe(tgt.get('attrs')))
    for cand in (tgt.get('selectors') or []):
        blob.append(str(cand.get('value') or ''))
    hay = ' '.join(blob).lower()
    return any(m in hay for m in SELF_MARKERS)


def json_dumps_safe(obj):
    try:
        import json
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)


# ---------------------------------------------------------------------------
# 噪声过滤（7 条规则）
# ---------------------------------------------------------------------------
def filter_noise(events, options=None):
    """按 7 条规则过滤噪声。

    返回 (kept_events, drop_reasons:Counter, merged_count:int)

    ★ 规则清单（与设计方案第 08 章一一对应）
      1 输入防抖合并    同一元素 800ms 内的连续 input/change ⇒ 只留最后一次的值
      2 hover 链剪枝     hover 后 500ms 内没有 click ⇒ 丢弃该 hover
      3 重复点击去重     同元素 300ms 内重复 click ⇒ 只留一次
      4 微滚动丢弃       单次滚动位移 < 50px ⇒ 丢弃
      5 扩展自身事件     命中扩展面板标记 ⇒ 丢弃
      6 敏感字段脱敏     不在本函数处理（本函数只负责"丢"），见 map_to_actions
      7 无目标动作剔除   元素类事件拿不到任何可定位目标 ⇒ 丢弃
    """
    opts = _merge_options(options)
    drop = Counter()
    merged = 0
    out = []

    ordered = sorted(events or [], key=lambda e: (e.get('seq') if e.get('seq') is not None else 0))

    for ev in ordered:
        etype = ev.get('type')

        # 平台不支持的动作类型
        if etype in DROP_EVENT_TYPES:
            drop[DROP_EVENT_TYPES[etype]] += 1
            continue

        # 规则 5：扩展自身事件
        if _is_extension_self(ev):
            drop['扩展自身事件（录制面板/Debugger 自身操作）'] += 1
            continue

        # 规则 7：无目标动作
        if etype in ELEMENT_EVENT_TYPES and not _has_usable_target(ev):
            drop['无目标元素（无法定位的动作，如纯键盘快捷键）'] += 1
            continue

        # 规则 4：微滚动
        if etype == 'scroll':
            s = ev.get('scroll') or {}
            try:
                magnitude = abs(int(s.get('x') or 0)) + abs(int(s.get('y') or 0))
            except (TypeError, ValueError):
                magnitude = 0
            if magnitude < opts['min_scroll_px']:
                drop['微滚动（位移 < %dpx，多为惯性/抖动）' % opts['min_scroll_px']] += 1
                continue

        # 规则 1：输入防抖合并
        if etype in VALUE_EVENT_TYPES and out:
            prev = out[-1]
            if (prev.get('type') in VALUE_EVENT_TYPES
                    and _target_key(prev) and _target_key(prev) == _target_key(ev)):
                w = _within(prev, ev, opts['debounce_ms'])
                # 证据充分且在窗口内 ⇒ 合并；证据不足但相邻同元素 ⇒ 也合并
                # （同字段相邻的输入事件在真实录制里几乎必然是同一次输入过程；
                #   不合并会把 "输入 admin" 变成 5 条 fill 步骤）
                if w is True or w is None:
                    prev['value'] = ev.get('value')
                    prev['merged'] = int(prev.get('merged') or 1) + 1
                    if prev.get('t') is None and ev.get('t') is not None:
                        prev['t'] = ev.get('t')
                    merged += 1
                    drop['输入防抖合并（同一输入框 <= %dms，保留最终值）' % opts['debounce_ms']] += 1
                    continue

        # 规则 3：重复点击去重
        if etype == 'click' and out:
            prev = out[-1]
            if prev.get('type') == 'click' and _target_key(prev) and _target_key(prev) == _target_key(ev):
                w = _within(prev, ev, opts['dedupe_click_ms'])
                # ★ 这里刻意要求 w is True（证据充分）：
                #   时间戳缺失时保留两次点击。删掉一次真实点击会改变用例行为，
                #   而多留一次点击最多是冗余 —— 宁冗余、不误删。
                if w is True:
                    drop['重复点击去重（同元素 <= %dms）' % opts['dedupe_click_ms']] += 1
                    continue

        out.append(dict(ev))

    # 规则 2：hover 链剪枝（需要看后续事件，故单独一轮）
    kept = []
    for i, ev in enumerate(out):
        if ev.get('type') != 'hover':
            kept.append(ev)
            continue
        nxt = None
        for j in range(i + 1, len(out)):
            if out[j].get('type') != 'hover':
                nxt = out[j]
                break
        keep_it = False
        if nxt is not None and nxt.get('type') == 'click':
            w = _within(ev, nxt, opts['hover_prune_ms'])
            # 证据充分且在窗口内 ⇒ 这是"悬停后点开子菜单"的真实操作链
            # 证据不足但紧邻 click ⇒ 同样按操作链处理
            keep_it = (w is True) or (w is None)
        if not keep_it:
            drop['hover 链剪枝（后续 %dms 内没有点击，多为无意义悬停）' % opts['hover_prune_ms']] += 1
            continue
        kept.append(ev)

    return kept, drop, merged


# ---------------------------------------------------------------------------
# 元素命名
# ---------------------------------------------------------------------------
def _element_name(ev, fallback_seq):
    """给元素取一个人类可读的名字（元素库列表里显示的就是它）。"""
    tgt = ev.get('target') or {}
    attrs = tgt.get('attrs') or {}
    for cand in (tgt.get('aria_label'), tgt.get('text')):
        if cand and str(cand).strip():
            name = str(cand).strip().replace('\n', ' ')
            # Chrome Recorder 的 target 描述形如 'aria/用户名'，
            # 直接拿来当元素名会带上 'aria/' 前缀，元素库里很难看
            name = re.sub(r'^(aria|text|xpath|pierce)/', '', name).strip()
            if name:
                return name[:24]
    for key in ('placeholder', 'name', 'title', 'alt', 'id', 'data-testid'):
        v = attrs.get(key)
        if v and str(v).strip():
            return str(v).strip()[:24]
    # 退回到定位表达式：role 类候选取 opts.name（可访问名），否则取 value
    for c in (tgt.get('selectors') or []):
        if isinstance(c, dict):
            nm = (c.get('opts') or {}).get('name')
            if nm:
                return str(nm).strip()[:24]
            if c.get('value'):
                return str(c['value']).strip()[:24]
            break
    return '元素_%s' % fallback_seq


# ---------------------------------------------------------------------------
# 关键字映射
# ---------------------------------------------------------------------------
# ★ 识别「原生 <select>」的正则（本文件唯一一处，改动前先看这段注释）
#   原实现是 `(^|[\s,>"'])(select|option)([\s,>"'.:\[]|$)`
#   —— 后边界字符集漏了 `#`，导致 `select#region`、`select#city` 这种
#   「标签 + id」的常见写法**匹配不上**，`change` 事件被降级成 `fill`，
#   落库出来的步骤在回放时必然失败（往 select 里填值不是合法操作）。
#   现改为「独立词」判定：前边界是选择器分隔符、后边界不是标识符字符。
#     ✓ select#region   ✓ select.foo   ✓ select[multiple]   ✓ input > select
#     ✗ selected   ✗ unselected   ✗ .el-select（前边界是 `-`，属框架组件而非原生）
_SELECT_TOKEN_RE = re.compile(r'(?:^|[\s>+~(,])select(?![\w-])')
_SELECT_OPTION_TOKEN_RE = re.compile(r'(?:^|[\s>+~(,])option(?![\w-])')


def _input_kind(ev):
    """判断输入类控件的具体种类 —— 决定事件映射到哪个关键字。

    ★ 三条信息源的优先级（后两条是必需的兜底）
      1) 明确的 DOM 信息：attrs.type / node_name（平台自有扩展会上报）
      2) **选择器里的线索**：Chrome DevTools Recorder 的导出**不带 DOM 属性**，
         只在 selectors 里留一条 `input[type="checkbox"]` 这样的 CSS。
         不从这里读，checkbox 就会被当成普通按钮点一下（语义丢失）。
      3) role 线索：`[role=checkbox]` / `[role=combobox]`
    """
    tgt = ev.get('target') or {}
    attrs = tgt.get('attrs') or {}
    node = str(tgt.get('node_name') or '').lower()
    itype = str(attrs.get('type') or '').lower()
    role = str(attrs.get('role') or '').lower()

    blob = []
    for c in (tgt.get('selectors') or []):
        if isinstance(c, dict):
            blob.append(str(c.get('value') or ''))
            blob.append(json_dumps_safe(c.get('opts') or {}))
            if c.get('by') == 'role':
                blob.append(str(c.get('value') or ''))
    hay = ' '.join(blob).lower()

    # ---- 1) 明确 DOM 信息 ----
    if itype == 'file' or 'type="file"' in hay or "type='file'" in hay:
        return 'file'
    if itype in ('checkbox', 'radio'):
        return 'checkbox'
    if node == 'select' or role in ('combobox', 'listbox') or 'select' == node:
        return 'select'

    # ---- 2) 选择器线索（DevTools Recorder 唯一可用的信息） ----
    if 'type="checkbox"' in hay or "type='checkbox'" in hay \
            or 'type="radio"' in hay or "type='radio'" in hay:
        return 'checkbox'
    if '[role="checkbox"]' in hay or "[role='checkbox']" in hay \
            or '[role="radio"]' in hay or "[role='radio']" in hay:
        return 'checkbox'
    if 'type="file"' in hay:
        return 'file'
    if _SELECT_TOKEN_RE.search(hay) or _SELECT_OPTION_TOKEN_RE.search(hay):
        return 'select'
    if '[role="combobox"]' in hay or "[role='combobox']" in hay:
        return 'select'

    # ---- 3) role 候选里的角色名 ----
    for c in (tgt.get('selectors') or []):
        if isinstance(c, dict) and c.get('by') == 'role':
            r = str((c.get('opts') or {}).get('role') or c.get('value') or '').lower()
            if r in ('checkbox', 'radio'):
                return 'checkbox'
            if r in ('combobox', 'listbox'):
                return 'select'
    return 'text'


def _press_keyword(key):
    if not key:
        return None, None
    k = str(key).strip()
    low = k.lower()
    if low in ('enter', 'return'):
        return 'press_enter', {}
    if low == 'tab':
        return 'press_tab', {}
    if low in ('esc', 'escape'):
        return 'press_esc', {}
    return 'press_other', {'key_name': k}


def map_to_actions(events, options=None):
    """把过滤后的事件映射成 IR 动作列表（此时还没有断言与参数化）。

    返回 (actions, drop_reasons:Counter, warnings:list)
    """
    opts = _merge_options(options)
    actions = []
    drop = Counter()
    warnings = []

    for ev in events:
        etype = ev.get('type')
        tgt = ev.get('target') or {}
        keyword = None
        args = {}                 # 逻辑参数（不含 obj）
        extract_keyword = None    # 若该动作需要取实际值做断言，这里给出提取关键字
        needs_review = False
        notes = []

        if etype == 'navigate':
            url = ev.get('url')
            if not url:
                drop['navigate 缺少 url'] += 1
                continue
            keyword = 'goto'
            args = {'uri': url}

        elif etype == 'click':
            # 注：这里不再用「有没有定位器」来决定丢不丢动作。
            #     filter_noise 的规则 7 已经滤掉了「完全无目标」的事件；
            #     剩下「有 attrs 但没 selectors」的情况宁可保留 + 标记待复核，
            #     也不静默丢弃 —— 少一步动作是最难排查的失败模式。
            kind = _input_kind(ev)
            if kind == 'checkbox':
                keyword = 'check'
                notes.append('源动作为点击 checkbox/radio，已映射为 check（幂等，比 click 更稳）')
            else:
                keyword = 'click'

        elif etype in ('change', 'input'):
            kind = _input_kind(ev)
            if kind == 'file':
                keyword = 'upload_file'
                args = {'file_path': None}   # 本地路径无法录制，落库时生成变量占位
                needs_review = True
                notes.append('文件上传的本地路径无法从录制中获得，已留空待补')
            elif kind == 'checkbox':
                # change 事件在 checkbox 上既可能是勾选也可能是取消；
                # 源数据（Chrome Recorder）不带 checked 终值，这里按「勾选」处理并提示复核
                keyword = 'check'
                needs_review = True
                notes.append('源数据未带勾选终值，默认按「勾选」处理，请复核是否应为「取消勾选」')
            elif kind == 'select':
                keyword = 'select_option'
                args = {'value': ev.get('value')}
            else:
                keyword = 'fill'
                args = {'value': ev.get('value')}

        elif etype == 'check':
            keyword = 'check'
        elif etype == 'uncheck':
            keyword = 'uncheck'

        elif etype == 'hover':
            keyword = 'move_to_element'

        elif etype == 'scroll':
            s = ev.get('scroll') or {}
            try:
                dx = int(s.get('x') or 0)
                dy = int(s.get('y') or 0)
            except (TypeError, ValueError):
                dx, dy = 0, 0
            # 元素级滚动（有 target 时优先用元素级关键字，视口滚动才用页面级）
            if tgt and _has_usable_target(ev):
                keyword = 'scroll_into_view_if_needed'
            else:
                if abs(dy) >= abs(dx):
                    direction = 'down' if dy >= 0 else 'up'
                    distance = abs(dy)
                else:
                    direction = 'right' if dx >= 0 else 'left'
                    distance = abs(dx)
                keyword = 'scroll_page'
                args = {'direction': direction, 'distance': distance}

        elif etype == 'keydown':
            kw, kargs = _press_keyword(ev.get('key') or ev.get('value'))
            if kw is None:
                drop['无法识别的按键（未提供 key）'] += 1
                continue
            keyword = kw
            args = kargs
            # 有目标的按键（在某个输入框里按 Enter）应挂到该元素上
            if tgt and _has_usable_target(ev) and kw == 'press_other':
                pass

        elif etype == 'keyup':
            drop['keyup 事件（keydown 已覆盖，避免重复按键）'] += 1
            continue

        elif etype == 'wait':
            keyword = 'wait_element_located'
            if not _has_usable_target(ev):
                drop['等待类动作缺少目标元素'] += 1
                continue

        elif etype == 'set_viewport':
            vp = ev.get('viewport') or {}
            w, h = vp.get('width'), vp.get('height')
            if not w or not h:
                drop['setViewport 缺少宽高'] += 1
                continue
            # 平台已有 set_viewport 关键字，且录制器几乎必然先设视口
            # （不映射的话它会以「不支持的事件类型」被丢掉，看起来像功能缺失）
            keyword = 'set_viewport'
            args = {'width': int(w), 'height': int(h)}
            if not any(a.get('keyword') == 'set_viewport' for a in actions):
                notes.append('录制起始视口，用于保证回放时布局一致')

        elif etype == 'assert':
            # 显式断言转换为「提取 + 断言」的步骤：
            # 平台没有"断言元素可见"这种一步到位的步骤，而是
            # 「关键字取回实际值 + check_params 比对」的组合。
            # 这里的 extract_keyword 就是取回实际值要用的关键字，
            # 断言规格（derive_assertions）会说明拿它跟什么比。
            has_locator = bool(tgt.get('selectors'))
            kind = str(ev.get('assert_kind') or 'toBeVisible')
            if 'visible' in kind.lower():
                keyword = 'is_visible'
                extract_keyword = 'is_visible'
            elif 'value' in kind.lower():
                keyword = 'get_attribute'
                args = {'name': 'value'}
                extract_keyword = 'get_attribute'
            elif has_locator:
                keyword = 'text_content'
                extract_keyword = 'text_content'
            else:
                keyword = 'is_visible'
                extract_keyword = 'is_visible'
                needs_review = True

        elif etype == 'unknown':
            # sources 层已经把它保留下来并给了告警，这里不能静默丢掉
            keyword = None
            needs_review = True
            notes.append('无法解析的动作，已原样保留待人工确认')
            actions.append(_make_action(ev, None, {}, None, needs_review, notes, warnings))
            continue

        else:
            drop['不支持的事件类型：%s' % etype] += 1
            continue

        actions.append(_make_action(ev, keyword, args, extract_keyword, needs_review, notes, warnings))

    if opts['max_actions'] and len(actions) > opts['max_actions']:
        overflow = len(actions) - opts['max_actions']
        warnings.append('动作数 %d 超过上限 %d，已截断 %d 条（可调大 max_actions）'
                        % (len(actions), opts['max_actions'], overflow))
        drop['超出动作数上限被截断'] += overflow
        actions = actions[:opts['max_actions']]

    return actions, drop, warnings


def _make_action(ev, keyword, args, extract_keyword, needs_review, notes, warnings):
    """组装一个 IR 动作（定位器候选在这里打分排序）。"""
    tgt = ev.get('target') or {}
    ranked = LS.rank_candidates(LS.dedupe_candidates(tgt.get('selectors') or []))
    top = ranked[0] if ranked else None

    # ★ 敏感判定必须在这里算，而且要把它**带下去**。
    #   原因：参数化阶段（apply_parameterization）只能拿到 element.snapshot，
    #   而 snapshot 里没有 selectors —— DevTools 来源的密码字段往往**只能**靠
    #   `input[type="password"]` 这个选择器线索认出来。一旦到了参数化阶段才发现
    #   「认不出来」，明文密码就已经被当成字面量写进 IR 了。
    #   （实测：不带 target 的 DevTools 导出，密码会明文落进 IR/数据库。）
    sensitive = _is_sensitive(ev)

    element = None
    if top:
        element = {
            'element_ref': _element_ref(top.get('by'), top.get('value'), top.get('opts')),
            'name': _element_name(ev, ev.get('seq')),
            'locators': ranked,
            'snapshot': {
                'tag': tgt.get('node_name'),
                'attrs': tgt.get('attrs') or {},
                'text': tgt.get('text'),
                'aria_label': tgt.get('aria_label'),
                'bbox': tgt.get('bbox'),
                'in_shadow_dom': bool(tgt.get('in_shadow')),
            },
        }
    else:
        needs_review = True

    top_score = ranked[0]['score'] if ranked else 0.0
    if top_score < 0.5 and element is not None:
        notes.append('最优定位器可信度偏低（%.2f），建议在审阅台中确认' % top_score)

    # ★ 只有「无法解析、需要人工确认」的动作才保留原始事件，
    #   其余动作一律不存 raw。两个原因：
    #     1) IR 是要落库的产物，塞进原始事件会让体积膨胀数倍（且事件里含 bbox/DOM 快照）；
    #     2) **敏感字段的原文会随 raw 一起泄漏进数据库** —— 这是最容易漏掉的一条泄密路径：
    #        值本身已经脱敏成变量了，但 raw 里还原封不动留着明文密码。
    keep_raw = (keyword is None) and not sensitive

    return {
        'seq': ev.get('seq'),
        'event_type': ev.get('type'),
        'raw_type': ev.get('raw_type'),
        'keyword': keyword,
        'element': element,
        'sensitive': sensitive,            # 审阅台据此显示「原文未落库」，参数化据此脱敏
        'args': args,                      # 逻辑参数，不含 obj；值可能是 dict（变量/字面量）
        'extract_keyword': extract_keyword,
        'assertions': [],                  # 由 attach_assertions 填充
        'confidence': round(top_score, 4) if element else 0.30,
        'needs_review': bool(needs_review),
        'notes': notes,
        't': ev.get('t'),
        'frame_path': ev.get('frame_path') or [],
        'asserted_events': act_safe_asserted_events(ev.get('asserted_events')),
        'raw': ev.get('raw') if keep_raw else None,
    }


def act_safe_asserted_events(asserted_events):
    """只保留断言需要的字段（type/url），不要把录制器给的整块元数据带进 IR。"""
    out = []
    for ae in (asserted_events or []):
        if isinstance(ae, dict):
            slim = {k: ae.get(k) for k in ('type', 'url', 'title', 'name') if ae.get(k)}
            if slim:
                out.append(slim)
    return out


# ---------------------------------------------------------------------------
# 参数化启发式
# ---------------------------------------------------------------------------
def _value_obj(raw, ev, seen_values, sensitive=None):
    """把一个原始值变成 IR 的 value 对象。

    kind = 'literal'  直接写死在步骤里
    kind = 'variable' 提升为用例变量（落库时写成 ${caseParams.<var_name>}）

    ★ 为什么 variable 也要带 'value'（本轮补的关键修正）：
      「提升为变量」只是把值挪到用例变量表里，**不是把值丢掉**。
      不带 value 的话，落库器只能给变量写一个空串，用户拿到的用例
      「结构对、一跑就失败」，还得手工把每个变量逐个补回来 ——
      「录制即回放」的承诺当场破产。所以除敏感字段外一律把原值作为
      变量默认值带下去（用户可在审阅台改写），敏感字段才真正丢弃原文。

    ★ 敏感字段（规则 6）：kind='variable' 且 `redacted=True`、**不带 value** ——
      原文一旦落库就等于把凭据写进了测试平台的数据库。

    sensitive: 显式的敏感判定结果。**调用方应当传它**。理由：参数化阶段手上只有
      `element.snapshot`，里面没有 selectors，靠 `_is_sensitive` 现推推不准 ——
      DevTools 来源的密码字段常常只有 `input[type="password"]` 这一条线索，
      于是「认不出来 ⇒ 明文当字面量写进 IR ⇒ 明文落库」。实测复现过。
      传 None 时才退回现推（兼容外部直接调用本函数）。
    """
    if raw is None or raw == '':
        return {'kind': 'literal', 'value': raw}

    text = str(raw)

    if sensitive is None:
        sensitive = _is_sensitive(ev)
    if sensitive:
        return {
            'kind': 'variable',
            'var_name': 'Password',
            'reason': '敏感字段（密码/令牌/验证码）：原文不落库，已强制提升为变量',
            'redacted': True,
        }

    tgt = ev.get('target') or {}
    attrs = tgt.get('attrs') or {}
    # 变量命名用「短线索」（attrs 名 / 无障碍名），保持变量名可读（Username 而不是
    # inputnameusername）。匹配判定用 _field_haystack 的**全量线索** ——
    # DevTools 导出没有 attrs，账号线索只存在于 `#username` / `[name="username"]`
    # 这些选择器里，不看选择器就认不出账号。
    name_hint = str(attrs.get('name') or attrs.get('id') or tgt.get('aria_label') or '')

    # ① 用户名字段
    if USERNAME_FIELD_RE.search(_field_haystack(ev)):
        return {'kind': 'variable', 'var_name': 'Username', 'value': text,
                'reason': '字段疑似账号（%s）' % (name_hint or '由选择器线索判定')[:24]}

    # ② 手机号 / 邮箱 / 身份证
    if RE_MOBILE.match(text):
        return {'kind': 'variable', 'var_name': 'Mobile', 'value': text,
                'reason': '值形如手机号'}
    if RE_EMAIL.match(text):
        return {'kind': 'variable', 'var_name': 'Email', 'value': text,
                'reason': '值形如邮箱'}
    if RE_IDCARD.match(text):
        return {'kind': 'variable', 'var_name': 'IdCard', 'value': text,
                'reason': '值形如身份证号'}

    # ③ 日期时间
    if RE_DATETIME.match(text):
        return {'kind': 'variable', 'var_name': 'DateTime', 'value': text,
                'reason': '值形如日期/时间'}

    # ④ 同值多次出现 ⇒ 提升为常量变量，便于一处修改
    if seen_values.get(text, 0) >= 2:
        return {'kind': 'variable', 'value': text,
                'var_name': _constant_var_name(name_hint, text),
                'reason': '同一取值在本段录制中出现多次，提升为常量便于复用'}

    return {'kind': 'literal', 'value': text}


def _constant_var_name(field_name, text):
    base = re.sub(r'[^0-9A-Za-z]+', ' ', field_name).strip()
    if base:
        parts = [p for p in base.split() if p]
        # PascalCase 且首字母大写 —— 本项目的变量命名约定
        name = ''.join(p[:1].upper() + p[1:] for p in parts)
        if name and name[0].isalpha():
            return name[:28]
    return 'Constant'


def apply_parameterization(actions, options=None):
    """把动作参数里的字面量按启发式提升为变量。

    ★ 只处理「承载用户数据」的参数（value / file_path）。
      uri、name、direction、distance、key_name 这些是**结构性参数**，
      它们描述"做什么"而不是"用什么数据做"，一旦被提升成变量会让用例不可读
      （例如把 goto 的 uri 变成 ${Constant}），且没有任何收益。
    """
    opts = _merge_options(options)
    if not opts['param_heuristics']:
        return actions

    # 先统计「同值出现次数」——规则 5 需要
    seen = Counter()
    for act in actions:
        for k, v in (act.get('args') or {}).items():
            if k in VALUE_ARG_KEYS and isinstance(v, str) and v:
                seen[v] += 1

    for act in actions:
        new_args = {}
        el = act.get('element') or {}
        snap = el.get('snapshot') or {}
        locators = el.get('locators') or []
        # ★ 敏感判定优先用「录制阶段算好的 act['sensitive']」——
        #   那时手上是完整事件（含 selectors）。只有在字段缺失时（例如审阅台
        #   手工构造的 IR）才退回现推，且现推时必须把 locators 一起喂进去，
        #   否则 DevTools 来源的 `input[type="password"]` 线索就丢了。
        sensitive = act.get('sensitive')
        if sensitive is None:
            sensitive = _is_sensitive({
                'target': {'attrs': snap.get('attrs') or {}, 'text': snap.get('text'),
                           'aria_label': snap.get('aria_label'),
                           'node_name': snap.get('tag'), 'selectors': locators},
                'value': None,
            })
        for k, v in (act.get('args') or {}).items():
            if k not in VALUE_ARG_KEYS:
                new_args[k] = {'kind': 'literal', 'value': v}
                continue
            new_args[k] = _value_obj(
                v,
                {'target': {'attrs': snap.get('attrs') or {}, 'text': snap.get('text'),
                            'aria_label': snap.get('aria_label'), 'selectors': locators},
                 'value': v},
                seen, sensitive=bool(sensitive))
        act['args'] = new_args
        # 敏感字段进变量后，元素级提示
        for obj in new_args.values():
            if isinstance(obj, dict) and obj.get('redacted'):
                if '该步骤含敏感字段，原文未落库' not in act['notes']:
                    act['notes'].append('该步骤含敏感字段，原文未落库')
    return actions


# ---------------------------------------------------------------------------
# 规则式断言推导
# ---------------------------------------------------------------------------
def derive_assertions(actions, meta=None, options=None):
    """给动作挂上断言规格。

    断言规格结构（落库层据此生成 check_params）：
        {'method': 'check_equal', 'kind': 'page_url',
         'expect': '...', 'extract_keyword': 'url', 'extract_args': {...},
         'rule': 'nav_observed', 'auto': True, 'brittle': False,
         'note': '...'}

    ★ 为什么规则优先：设计方案的立场是「规则能推的先推，规则推不出的才交给模型」。
      这六个规则覆盖了录制场景里绝大多数值得断言的点，且零 token 成本。
    """
    opts = _merge_options(options)
    if not opts['assertion_rules']:
        return actions

    for idx, act in enumerate(actions):
        etype = act.get('event_type')
        pending = []

        # ---- 规则 2：发生了导航（Recorder 在 assertedEvents 里免费给了我们） ----
        for ae in (act.get('asserted_events') or []):
            if not isinstance(ae, dict):
                continue
            if str(ae.get('type') or '').lower() == 'navigation' and ae.get('url'):
                pending.append({
                    'method': 'check_equal',
                    'kind': 'page_url',
                    'expect': str(ae['url']),
                    'extract_keyword': 'url',
                    'extract_args': {},
                    'rule': 'nav_observed',
                    'auto': True,
                    'brittle': True,
                    'note': '断言导航后的完整 URL。URL 可能含易变查询参数，'
                            '建议在审阅台改成更稳定的片段或改为断言页面标题。',
                })

        # ---- 规则 1：点击「会改变状态」的按钮 → 建议断言结果 ----
        if etype == 'click':
            snap = (act.get('element') or {}).get('snapshot') or {}
            label = ' '.join(str(x) for x in (
                snap.get('text'), snap.get('aria_label'),
                (snap.get('attrs') or {}).get('value')) if x)
            if label and MUTATING_BUTTON_RE.search(label):
                pending.append({
                    'method': 'check_object_is_not_empty',
                    'kind': 'manual',
                    'expect': None,
                    'extract_keyword': None,
                    'extract_args': {},
                    'rule': 'mutating_button',
                    'auto': False,
                    'brittle': False,
                    'note': '这是一步会改变数据的操作（%s）。录制无法得知"成功的标志"，'
                            '请在此指定成功提示文本或结果列表的元素。' % label.strip()[:20],
                })

        # ---- 规则 3：fill 之后断言元素值确实等于所填值 ----
        if act.get('keyword') == 'fill':
            v = (act.get('args') or {}).get('value') or {}
            if v.get('kind') == 'literal':
                pending.append({
                    'method': 'check_equal',
                    'kind': 'element_value',
                    'expect': v.get('value'),
                    'extract_keyword': 'get_attribute',
                    'extract_args': {'name': 'value'},
                    'rule': 'fill_value_echo',
                    'auto': True,
                    'brittle': False,
                    'note': '断言输入框的值确实等于所填内容（可捕获输入被前端拦截的情况）',
                })

        # ---- 显式断言事件：源里写明的，直接带过来 ----
        if etype == 'assert' and act.get('extract_keyword'):
            kw = act['extract_keyword']
            if kw == 'is_visible':
                pending.append({
                    'method': 'check_bool_equal', 'kind': 'element_visible',
                    'expect': 'True', 'extract_keyword': 'is_visible', 'extract_args': {},
                    'rule': 'explicit_assert', 'auto': True, 'brittle': False,
                    'note': '录制中显式记录的"元素可见"断言',
                })
            elif kw == 'text_content':
                pending.append({
                    'method': 'check_equal', 'kind': 'element_text',
                    'expect': None, 'extract_keyword': 'text_content', 'extract_args': {},
                    'rule': 'explicit_assert', 'auto': False, 'brittle': False,
                    'note': '录制中的文本断言未带期望值，请在审阅台补上',
                })

        # ---- 规则 5：点击导致 URL 变化（用后续 navigate 事件推断） ----
        if etype == 'click' and not pending:
            nxt = actions[idx + 1] if idx + 1 < len(actions) else None
            uri_obj = ((nxt or {}).get('args') or {}).get('uri') if nxt else None
            if (nxt and nxt.get('event_type') == 'navigate'
                    and isinstance(uri_obj, dict) and uri_obj.get('kind') == 'literal'):
                uri = uri_obj.get('value')
                if uri:
                    pending.append({
                        'method': 'check_equal', 'kind': 'page_url', 'expect': uri,
                        'extract_keyword': 'url', 'extract_args': {},
                        'rule': 'url_changed_after_click', 'auto': True, 'brittle': True,
                        'note': '点击后发生了页面跳转，已按跳转后的 URL 生成断言',
                    })

        act['assertions'] = pending

    return actions


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def build_ir(events, meta=None, options=None):
    """事件流 → IR。

    返回 IR dict（可直接 JSON 序列化后存 RecordingSession.ir_payload）。
    """
    opts = _merge_options(options)
    meta = dict(meta or {})
    raw_count = len(events or [])

    kept_events, drop_reasons, merged = filter_noise(events, opts)
    actions, map_drops, warnings = map_to_actions(kept_events, opts)
    actions = apply_parameterization(actions, opts)
    actions = derive_assertions(actions, meta, opts)

    for k, v in map_drops.items():
        drop_reasons[k] += v

    # 重新编号：IR 里的 seq 是「归一化后的动作序号」，从 1 开始且连续 ——
    # 后面用户删除/排序动作时，这个序号会被重排，所以不能让源事件序号穿透进来。
    for i, act in enumerate(actions, 1):
        act['seq'] = i

    dropped_total = raw_count - len(actions)
    counted = sum(drop_reasons.values())
    if dropped_total > counted:
        # 不变量：drop_reasons 合计必须等于丢弃数，否则用户看到的统计是假的
        drop_reasons['未归因（内部计数差额，出现即说明有分支在静默丢弃）'] += (dropped_total - counted)
    elif counted > dropped_total:
        warnings.append('丢弃计数(%d)大于实际丢弃数(%d)，统计口径存在偏差'
                        % (counted, dropped_total))

    # 元素去重统计（同一 ref 只应落一条元素）
    refs = OrderedDict()
    for act in actions:
        el = act.get('element')
        if el and el.get('element_ref'):
            refs.setdefault(el['element_ref'], el)

    assertion_count = sum(len(a.get('assertions') or []) for a in actions)
    needs_review = [a['seq'] for a in actions if a.get('needs_review')]
    unparsed = [a['seq'] for a in actions if not a.get('keyword')]

    placeholder = None
    for act in actions:
        if act.get('event_type') == 'navigate':
            placeholder = (act.get('args') or {}).get('uri', {}).get('value')
            break

    ir = {
        'version': 'ir/1',
        'meta': {
            'source': meta.get('source'),
            'title': meta.get('title'),
            'start_url': meta.get('start_url') or placeholder,
            'viewport': meta.get('viewport') or {},
            'user_agent': meta.get('user_agent'),
            'host': meta.get('host'),
            'warnings': list(meta.get('warnings') or []) + warnings,
        },
        'actions': actions,
        'elements': list(refs.values()),
        'stats': {
            'raw_events': raw_count,
            'kept_actions': len(actions),
            'dropped': dropped_total,
            'merged_inputs': merged,
            'unparsed_actions': len(unparsed),
            'elements_unique': len(refs),
            'assertions': assertion_count,
            'needs_review': needs_review,
            'drop_reasons': dict(drop_reasons.most_common()),
        },
    }
    return ir


def summarize(ir):
    """给前端一个轻量摘要（用于「解析完成」提示，不必传整个 IR）。"""
    stats = (ir or {}).get('stats') or {}
    return {
        'kept_actions': stats.get('kept_actions', 0),
        'dropped': stats.get('dropped', 0),
        'elements_unique': stats.get('elements_unique', 0),
        'assertions': stats.get('assertions', 0),
        'needs_review': stats.get('needs_review', []),
        'unparsed_actions': stats.get('unparsed_actions', 0),
        'drop_reasons': stats.get('drop_reasons', {}),
        'start_url': ((ir or {}).get('meta') or {}).get('start_url'),
    }
