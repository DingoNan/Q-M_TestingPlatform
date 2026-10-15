# -*- coding: utf-8 -*-
"""多来源适配：把三种录制来源统一成内部事件流（P0-③）

支持三种来源
  devtools_recorder  Chrome DevTools Recorder / Puppeteer Recorder 导出的 JSON
                     （schema 对齐 Puppeteer：{title, steps:[{type,target,selectors,...}]}）
  playwright_script  Playwright codegen 生成的 .js / .ts 脚本（文本）
  native             平台自有扩展上报的原生事件流（信息最全，含 match_count / bbox）
  raw_events         裸事件流（{'events':[...]} 或直接是 list），字段名按常见约定猜测

★ 三者统一到同一个内部事件结构，后续 normalizer 只认这一种形状 ——
   这样「新增一种录制来源」只需要在本文件加一个适配函数，不动归一化逻辑。

★ 纯 Python、零依赖 ⇒ 可离线单测。
"""

import json
import re

SOURCE_DEVTOOLS = 'devtools_recorder'
SOURCE_PLAYWRIGHT_SCRIPT = 'playwright_script'
SOURCE_NATIVE = 'native'
SOURCE_RAW = 'raw_events'

# Puppeteer / Chrome Recorder 的 selector 前缀 → 平台 by
_SELECTOR_PREFIX_MAP = {
    'aria': 'role',
    'text': 'text',
    'xpath': 'xpath',
    'pierce': 'css',
}

# 步骤类型 → 猜出来的无障碍角色。
# 为什么要猜：Chrome Recorder 的 `aria/登录` 只给了**无障碍名**，没给角色。
# 猜出来的候选会被 locator_score 扣 0.15，所以它不会盖过真·label 候选，
# 但能在 label 也不可用时提供一条可用的定位路径。
_ROLE_GUESS_BY_STEP = {
    'click': 'button',
    # ★ 2026-10-15 修：Chrome Recorder 的 `doubleClick` 类型。
    #   角色猜 'button' 与 click 一致（双击的目标多为按钮/单元格）。
    'double_click': 'button',
    'change': 'textbox',
    'input': 'textbox',
    'check': 'checkbox',
    'uncheck': 'checkbox',
    'hover': 'button',
}

# Puppeteer 步骤类型 → 内部事件类型
_STEP_TYPE_MAP = {
    'navigate': 'navigate',
    'click': 'click',
    # ★★★ 2026-10-15 修：漏映射 ⇒ 双击步骤被**静默丢弃**
    #   puppeteer-replay 的 `StepType.doubleClick = 'doubleClick'`（Chrome DevTools
    #   Recorder 的导出 schema 就是它）。这张表原来没有它，`.get(..., 'unknown')`
    #   会把它标成 unknown —— 虽不报错，但真机导入时会以「无法解析的动作」出现，
    #   用户看到的是「录制里明明双击了，用例里没这一步」。
    #   平台其实**早就有** `run_playwright.py:763 def double_click(obj, element_index,
    #   timeout)`，签名与 `click` 完全一致 —— 属于「关键字存在、只是永远走不到」
    #   那一类缺陷（同类前例：kind:'select' 白名单缺失）。
    'doubleclick': 'double_click',
    'change': 'change',
    'input': 'input',
    'keydown': 'keydown',
    'keyup': 'keyup',
    'hover': 'hover',
    'scroll': 'scroll',
    'waitforelement': 'wait',
    'waitforexpression': 'wait_expr',
    'setviewport': 'set_viewport',
    'close': 'close',
    'assert': 'assert',
    'customstep': 'custom',
    'emulatenetworkconditions': 'ignore',
}


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------
def _to_int(v, default=None):
    try:
        if v is None or v == '':
            return default
        return int(float(v))
    except (TypeError, ValueError):
        return default


def _frame_path_from(v):
    """Recorder 的 `frame` 是 FrameSelector = number[]（逐层 iframe 的序号）。

    转成内部的 frame_path（int 列表）；形状不合法时一律退化成「主文档」([])，
    绝不让它污染下游。
    """
    if not isinstance(v, (list, tuple)):
        return []
    out = []
    for x in v:
        try:
            out.append(int(x))
        except (TypeError, ValueError):
            return []
    return out


def _first_quoted(text):
    """从 `'role', { name: '用户名' }` 这类片段里取第一个引号字符串。"""
    if not text:
        return None
    m = re.search(r"""'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)\"""", text)
    if not m:
        return None
    return m.group(1) if m.group(1) is not None else m.group(2)


def _target_key_from(attrs=None, aria_label=None, text=None, selectors=None, explicit=None):
    """为 target 生成一个**元素身份键**。

    ★ 为什么需要它（这是踩过的坑）
      归一化时要用「是否同一元素」来做输入防抖合并、重复点击去重。
      如果拿「打分最高的定位器」去比，role 类候选的 value 是**角色名**
      （textbox / button），所有文本输入框都会得到同一个 key ⇒
      多个不同输入框会被误判成同一个，进而被错误合并成一步。
      所以身份键必须在**适配层**就算好，且优先用能区分个体的信息
      （data-testid / id / name / 无障碍名 / 原始目标描述）。
    """
    if explicit:
        return str(explicit)
    attrs = attrs or {}
    for k in ('data-testid', 'id', 'name', 'placeholder', 'title', 'alt', 'aria-label'):
        v = attrs.get(k)
        if v:
            return '%s=%s' % (k, v)
    if aria_label:
        return 'aria=' + str(aria_label)
    if text:
        return 'text=' + str(text).strip()[:60]
    for s in (selectors or []):
        if isinstance(s, dict) and s.get('value'):
            nm = (s.get('opts') or {}).get('name')
            return '%s:%s:%s' % (s.get('by'), s.get('value'), nm or '')
        if isinstance(s, str) and s:
            return 'sel:' + s
    return None


def _parse_named_opts(text):
    """从 `{ name: 'x', exact: true }` 里取出 name / exact。"""
    opts = {}
    if not text:
        return opts
    m = re.search(r"""name\s*:\s*(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")""", text)
    if m:
        opts['name'] = m.group(1) if m.group(1) is not None else m.group(2)
    if re.search(r'exact\s*:\s*true', text):
        opts['exact'] = True
    return opts


def _split_selector(raw):
    """把 Puppeteer 的一条 selector 拆成 (by, value, extra_flags)。

    Puppeteer 形式：`aria/用户名`、`text/登录`、`xpath///*[@id="x"]`、
    `pierce/#foo`、裸 CSS `#username`。
    """
    if raw is None:
        return None, None, {}
    s = str(raw)
    if '/' in s:
        prefix, rest = s.split('/', 1)
        key = prefix.strip().lower()
        if key in _SELECTOR_PREFIX_MAP:
            flags = {}
            if key == 'pierce':
                flags['in_shadow'] = True
            if key == 'role' or key == 'aria':
                # `aria/用户名` 只给无障碍名 → 语义上等价于「按名字找」，
                # 具体角色在上层按步骤类型推测，这里把名字放进 value/opts
                return 'role', rest, flags
            if key == 'xpath':
                return 'xpath', rest, flags
            if key == 'text':
                return 'text', rest, flags
            return 'css', rest, flags
    return 'css', s, {}


def _candidates_from_selectors(selectors, event_type):
    """把 Puppeteer selectors 数组转成候选定位器列表。

    selectors 的每一项可能是字符串，也可能是单元素数组（Puppeteer 两种都出现过）。
    """
    out = []
    if not selectors:
        return out
    if isinstance(selectors, str):
        selectors = [selectors]

    for item in selectors:
        if isinstance(item, (list, tuple)):
            # 单元素数组是常见形态；多元素数组表示「组合定位」，本版本只取首项
            raw = item[0] if item else None
        else:
            raw = item
        by, value, flags = _split_selector(raw)
        if not by or not value:
            continue
        cand = {'by': by, 'value': value, 'source': 'devtools', 'origin': str(raw)}
        if flags.get('in_shadow'):
            cand['in_shadow'] = True
        if by == 'role':
            role = _ROLE_GUESS_BY_STEP.get(event_type)
            if role:
                cand['opts'] = {'name': value, 'exact': False}
                cand['value'] = role
                cand['aria_guessed'] = True
                out.append(cand)
            else:
                # 猜不出角色时，退化成「按可见文本找」——至少是可执行的
                out.append({'by': 'text', 'value': value, 'source': 'devtools',
                            'origin': str(raw), 'aria_guessed': True})
            # 无论角色能否猜出，label 与 text 两条都值得作为备选
            out.append({'by': 'label', 'value': value, 'opts': {'exact': False},
                        'source': 'devtools', 'origin': str(raw)})
            out.append({'by': 'text', 'value': value, 'opts': {'exact': False},
                        'source': 'devtools', 'origin': str(raw)})
        else:
            out.append(cand)
    return out


# ---------------------------------------------------------------------------
# ① Chrome DevTools Recorder / Puppeteer Recorder
# ---------------------------------------------------------------------------
def from_devtools_recorder(payload):
    """把 Recorder 导出的 {title, steps:[...]} 转成内部事件流。"""
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        raise ValueError('DevTools Recorder 数据必须是对象')

    steps = payload.get('steps')
    if not isinstance(steps, list):
        raise ValueError('DevTools Recorder 数据缺少 steps 数组')

    events = []
    seq = 0
    for raw_step in steps:
        if not isinstance(raw_step, dict):
            continue
        raw_type = str(raw_step.get('type') or '').strip()
        etype = _STEP_TYPE_MAP.get(raw_type.lower(), 'unknown')
        if etype == 'ignore':
            continue
        seq += 1

        target = None
        selectors = raw_step.get('selectors')
        if selectors:
            # ★ 2026-10-14 修（真接口实测取证，见 _verify_devtools_recorder_parse.py）
            #   schema（puppeteer-replay —— Chrome DevTools Recorder 的导出格式就是它）里
            #   `BaseStep.target` 是 **frame 名**（`Target = string`，默认字面量 `'main'`），
            #   **不是**元素的可读描述。曾把它当 label_hint，造成两个真实后果：
            #     · Chrome Recorder 真实导出必带 `target:'main'` ⇒ 所有元素的身份键
            #       都变成 `'main'`，元素列表里全是 "main"，完全无法辨认是哪个元素；
            #     · 无 selectors 但带 target 的步骤（keyDown/keyUp）会凭空造出一个
            #       用 `text=main` 定位的垃圾元素。
            #   元素描述**只**从 selectors 推导（_target_key_from 的后续分支已覆盖）。
            cands = _candidates_from_selectors(selectors, etype)
            target = {
                'node_name': None,
                'attrs': {},
                'text': None,
                'aria_label': None,
                'selectors': cands,
                'bbox': None,
                'in_shadow': False,
                'key': _target_key_from(selectors=selectors),
            }

        ev = {
            'seq': seq,
            'type': etype,
            'raw_type': raw_type,
            'source': SOURCE_DEVTOOLS,
            't': _to_int(raw_step.get('timestamp')),
            'target': target,
            'value': None,
            'url': raw_step.get('url'),
            'key': raw_step.get('key'),
            # ★ frame 才是 iframe 信息（FrameSelector = number[]），别丢
            'frame_path': _frame_path_from(raw_step.get('frame')),
            'raw': raw_step,
        }

        if etype == 'change':
            ev['value'] = raw_step.get('value')
        elif etype == 'keydown' or etype == 'keyup':
            ev['key'] = raw_step.get('key')
        elif etype == 'scroll':
            ev['scroll'] = {'x': _to_int(raw_step.get('x'), 0),
                            'y': _to_int(raw_step.get('y'), 0)}
        elif etype == 'set_viewport':
            ev['viewport'] = {'width': _to_int(raw_step.get('width')),
                              'height': _to_int(raw_step.get('height'))}

        # Recorder 会把「动作引发的导航」挂在 assertedEvents 里 —— 这是免费来的
        # 断言素材，归一化阶段会用它推导 check_params。
        asserted = raw_step.get('assertedEvents')
        if isinstance(asserted, list) and asserted:
            ev['asserted_events'] = asserted

        events.append(ev)

    meta = {
        'title': payload.get('title'),
        'source': SOURCE_DEVTOOLS,
    }
    return events, meta


# ---------------------------------------------------------------------------
# ② Playwright codegen 脚本
# ---------------------------------------------------------------------------
# 定位方法 → (by, 是否需要 opts)
_PW_LOCATOR_METHODS = {
    'getByRole': 'role',
    'getByLabel': 'label',
    'getByPlaceholder': 'placeholder',
    'getByText': 'text',
    'getByAltText': 'alt text',
    'getByTitle': 'text',
    'getByTestId': 'css',
    'locator': 'css',
}

# 动作方法 → 内部事件类型
_PW_ACTION_METHODS = {
    'click': 'click',
    'dblclick': 'click',
    'fill': 'change',
    'type': 'change',
    'press': 'keydown',
    'check': 'check',
    'uncheck': 'uncheck',
    'selectOption': 'change',
    'setInputFiles': 'change',
    'hover': 'hover',
    'scrollIntoViewIfNeeded': 'scroll',
    'focus': 'click',
}

_PAGE_LEVEL_ACTIONS = {
    'goto': 'navigate',
    'reload': 'navigate',
    'goBack': 'navigate',
    'keyboard': 'keydown',
    'mouse': 'scroll',
}

_CALL_RE = re.compile(r"^([A-Za-z_$][\w$]*)\s*\(")


def _read_calls(text):
    """把一个 `page.a(x).b(y)` 形式的表达式拆成 [(name, args)]，args 为字符串。

    只做括号配平，不解析 JS 语法 —— 够用即可（这是 codegen 输出的受限子集）。
    """
    segments = []
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i] in ' \t\r\n':
            i += 1
        if i < n and text[i] == '.':
            i += 1
            continue
        m = _CALL_RE.match(text[i:])
        if not m:
            # 不是调用（可能是 `keyboard` 这类属性），跳到下一个 '.'
            nxt = text.find('.', i)
            if nxt == -1:
                break
            segments.append((text[i:nxt].strip(), None))
            i = nxt
            continue
        name = m.group(1)
        i += m.end()
        depth = 1
        start = i
        in_s = None
        while i < n and depth > 0:
            ch = text[i]
            if in_s:
                if ch == '\\':
                    i += 2
                    continue
                if ch == in_s:
                    in_s = None
            elif ch in '\'"`':
                in_s = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        args = text[start:i]
        segments.append((name, args))
        i += 1
    return segments


def from_playwright_script(script_text):
    """解析 Playwright codegen 生成的脚本（best-effort）。

    ★ 这是**尽力而为**的解析：只覆盖 codegen 实际会产出的受限语法子集
      （`await page.xxx(...).yyy(...)`）。真实项目里的手写脚本、
      循环、变量、helper 函数一律解析不了 —— 那种情况应引导用户改用
      DevTools Recorder 导出 JSON，或直接用平台的扩展录制。
      解析失败的行不会被丢弃，而是以 `unknown` 事件保留，并在 warnings 里点名，
      避免「静默少了几步」这种最危险的失败模式。
    """
    if not isinstance(script_text, str):
        raise ValueError('Playwright 脚本必须是文本')

    events = []
    warnings = []
    seq = 0

    # 去掉注释，避免把注释里的代码当真实步骤
    cleaned = re.sub(r'/\*.*?\*/', '', script_text, flags=re.S)
    cleaned = re.sub(r'^\s*//.*$', '', cleaned, flags=re.M)

    for lineno, line in enumerate(cleaned.split('\n'), 1):
        stmt = line.strip()
        if not stmt:
            continue
        if not stmt.startswith('await ') and not stmt.startswith('expect('):
            continue
        stmt = stmt.rstrip(';').strip()

        # ---- 断言 ----
        if stmt.startswith('expect('):
            inner = stmt[len('expect('):]
            # 取 expect(...) 里的接收者表达式
            depth = 1
            k = 0
            in_s = None
            while k < len(inner) and depth > 0:
                ch = inner[k]
                if in_s:
                    if ch == '\\':
                        k += 2
                        continue
                    if ch == in_s:
                        in_s = None
                elif ch in '\'"`':
                    in_s = ch
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            recv = inner[:k]
            matcher = inner[k + 1:].strip().lstrip('.')
            mname = _CALL_RE.match(matcher)
            matcher_name = mname.group(1) if mname else 'toBeVisible'
            margs = matcher[mname.end():] if mname else ''
            if not margs.endswith(')') and mname:
                margs = margs + ')'
            seq += 1
            cands = _candidates_from_pw_expr(recv)
            events.append({
                'seq': seq, 'type': 'assert', 'raw_type': matcher_name,
                'source': SOURCE_PLAYWRIGHT_SCRIPT, 't': None,
                'target': _target_from_candidates(cands, explicit_key=recv.strip()),
                'value': _first_quoted(margs),
                'url': None, 'key': None, 'frame_path': [],
                'assert_kind': matcher_name,
                'raw': stmt,
            })
            continue

        body = stmt[len('await '):].strip()
        if not body.startswith('page'):
            # 变量、helper、循环等 —— 保留为 unknown，别静默丢
            seq += 1
            events.append({
                'seq': seq, 'type': 'unknown', 'raw_type': 'unparsed',
                'source': SOURCE_PLAYWRIGHT_SCRIPT, 't': None,
                'target': None, 'value': None, 'url': None, 'key': None,
                'frame_path': [], 'raw': stmt,
            })
            warnings.append('第 %d 行无法解析，已保留为待人工确认的步骤：%s'
                            % (lineno, stmt[:90]))
            continue

        segments = _read_calls(body[4:])  # 跳过开头的 'page'
        if not segments:
            continue

        # 页面级动作：page.goto / page.keyboard.press / page.mouse.wheel
        head = segments[0][0]
        if head in _PAGE_LEVEL_ACTIONS and len(segments) >= 1:
            if head == 'keyboard':
                args = segments[1][1] if len(segments) > 1 else ''
                seq += 1
                events.append({
                    'seq': seq, 'type': 'keydown', 'raw_type': 'keyboard.press',
                    'source': SOURCE_PLAYWRIGHT_SCRIPT, 't': None,
                    'target': None, 'value': _first_quoted(args),
                    'url': None, 'key': _first_quoted(args), 'frame_path': [],
                    'raw': stmt,
                })
                continue
            if head == 'mouse':
                args = segments[1][1] if len(segments) > 1 else ''
                nums = re.findall(r'-?\d+', args or '')
                scroll = {'x': _to_int(nums[0], 0) if nums else 0,
                          'y': _to_int(nums[1], 0) if len(nums) > 1 else 0}
                seq += 1
                events.append({
                    'seq': seq, 'type': 'scroll', 'raw_type': 'mouse.wheel',
                    'source': SOURCE_PLAYWRIGHT_SCRIPT, 't': None,
                    'target': None, 'value': None, 'url': None, 'key': None,
                    'scroll': scroll, 'frame_path': [], 'raw': stmt,
                })
                continue
            url = _first_quoted(segments[0][1] or '')
            seq += 1
            events.append({
                'seq': seq, 'type': 'navigate', 'raw_type': 'goto',
                'source': SOURCE_PLAYWRIGHT_SCRIPT, 't': None,
                'target': None, 'value': None, 'url': url, 'key': None,
                'frame_path': [], 'raw': stmt,
            })
            continue

        # 定位器 + 动作：page.getByRole(...).click()
        loc_method = segments[0][0]
        if loc_method not in _PW_LOCATOR_METHODS:
            seq += 1
            events.append({
                'seq': seq, 'type': 'unknown', 'raw_type': loc_method,
                'source': SOURCE_PLAYWRIGHT_SCRIPT, 't': None,
                'target': None, 'value': None, 'url': None, 'key': None,
                'frame_path': [], 'raw': stmt,
            })
            warnings.append('第 %d 行使用了不支持的定位方法 %s，已保留待人工确认'
                            % (lineno, loc_method))
            continue

        pw_expr = 'page.' + _rebuild_expr(segments)
        cands = _candidates_from_pw_expr(pw_expr)
        action_name = segments[-1][0]
        action_args = segments[-1][1] or ''
        etype = _PW_ACTION_METHODS.get(action_name, 'unknown')

        ev = {
            'seq': seq + 1, 'type': etype, 'raw_type': action_name,
            'source': SOURCE_PLAYWRIGHT_SCRIPT, 't': None,
            'target': _target_from_candidates(cands, explicit_key=pw_expr),
            'value': None, 'url': None, 'key': None, 'frame_path': [],
            'raw': stmt,
        }
        seq += 1
        if etype in ('change', 'keydown'):
            v = _first_quoted(action_args)
            ev['value'] = v
            if etype == 'keydown':
                ev['key'] = v
        if action_name == 'setInputFiles':
            ev['value'] = _first_quoted(action_args)
            ev['is_upload'] = True
        if etype == 'unknown':
            warnings.append('第 %d 行的动作 %s 暂不支持，已保留待人工确认'
                            % (lineno, action_name))
        events.append(ev)

    return events, {'source': SOURCE_PLAYWRIGHT_SCRIPT, 'warnings': warnings}


def _rebuild_expr(segments):
    out = []
    for nm, args in segments:
        if args is None:
            out.append(nm)
        else:
            out.append('%s(%s)' % (nm, args))
    return '.'.join(out)


def _candidates_from_pw_expr(expr):
    """从 `page.getByRole('textbox', { name: '用户名' })` 提取候选定位器。"""
    segs = _read_calls(expr[5:] if expr.startswith('page.') else expr)
    if not segs:
        return []
    name, args = segs[0]
    by = _PW_LOCATOR_METHODS.get(name)
    if not by:
        return []

    if name == 'getByRole':
        role = _first_quoted(args)
        opts = _parse_named_opts(args)
        cand = {'by': 'role', 'value': role, 'source': 'playwright'}
        if opts.get('name'):
            cand['opts'] = {'name': opts['name'], 'exact': bool(opts.get('exact'))}
        elif opts.get('exact'):
            cand['opts'] = {'exact': True}
        return [cand]

    if name == 'getByTestId':
        v = _first_quoted(args)
        return [{'by': 'css', 'value': '[data-testid="%s"]' % v,
                 'source': 'playwright'}] if v else []

    v = _first_quoted(args)
    if not v:
        return []
    cand = {'by': by, 'value': v, 'source': 'playwright'}
    if by in ('label', 'text') and re.search(r'exact\s*:\s*true', args or ''):
        cand['opts'] = {'exact': True}
    if name == 'locator' and v.startswith('//'):
        cand['by'] = 'xpath'
    if name == 'locator' and v.startswith('xpath='):
        cand['by'] = 'xpath'
        cand['value'] = v[len('xpath='):]
    return [cand]


def _target_from_candidates(cands, explicit_key=None):
    if not cands:
        return None
    first = cands[0]
    return {
        'node_name': None,
        'attrs': {},
        'text': first.get('value') if first.get('by') == 'text' else None,
        'aria_label': (first.get('opts') or {}).get('name'),
        'selectors': cands,
        'bbox': None,
        'in_shadow': any(c.get('in_shadow') for c in cands),
        'key': _target_key_from(
            aria_label=(first.get('opts') or {}).get('name'),
            text=first.get('value') if first.get('by') == 'text' else None,
            selectors=cands,
            explicit=explicit_key,
        ),
    }


# ---------------------------------------------------------------------------
# ③ 平台扩展上报的原生事件流 / 裸事件流
# ---------------------------------------------------------------------------
# ★★ selectors 的形状必须在这里收敛（v0.20.3 修复的真缺陷）
#
# 规范形状（devtools / playwright 两个适配器产出的都是它）：
#     selectors = [{'by': 'css', 'value': '#username', 'opts': {...}}, ...]
#
# 但扩展早期版本（以及「裸事件流」导入）上传的是**纯字符串数组**
# —— content.js 的 describe() 直接给 '#id' / '[name="x"]' / 'div > input'。
# 下游 normalizer / locator_score 全程按 dict 处理：
#     normalizer._is_extension_self   → cand.get('value')  ⇒ AttributeError
#     locator_score.dedupe_candidates → cand.get('by')     ⇒ AttributeError
# 后果：**native 来源的录制永远归一化失败** —— finish 返 400
# 「归一化失败：'str' object has no attribute 'get'」，且崩溃发生在
# "扩展自身事件过滤"这一步，报错信息与"选择器格式"毫无关联，极难定位。
#
# 修法：在**适配层**（本文件，职责就是"形状转换"）统一收敛，而不是给下游
# 每个消费点补 isinstance —— 那样等于把同一个坑留给下一种新来源。
_ID_ONLY_RE = re.compile(r'^#([A-Za-z_][\w-]*)$')


def _canon_one_selector(item):
    """把一条选择器（字符串或 dict）收敛成规范候选 dict；认不出返回 None。"""
    if isinstance(item, dict):
        by = item.get('by')
        value = item.get('value')
        if not by or value in (None, ''):
            return None
        out = {'by': by, 'value': value,
               'source': item.get('source') or SOURCE_NATIVE}
        # 只搬运**下游会用到**的键，避免把杂质带进去
        for k in ('opts', 'match_count', 'in_shadow', 'origin', 'pinned', 'score'):
            if item.get(k) is not None:
                out[k] = item[k]
        return out
    if item is None:
        return None
    s = str(item).strip()
    if not s:
        return None
    low = s.lower()
    if s.startswith('xpath='):
        return {'by': 'xpath', 'value': s[len('xpath='):],
                'source': SOURCE_NATIVE, 'origin': s}
    if low.startswith('xpath:'):
        return {'by': 'xpath', 'value': s[len('xpath:'):],
                'source': SOURCE_NATIVE, 'origin': s}
    if s.startswith('//') or s.startswith('(/'):
        return {'by': 'xpath', 'value': s, 'source': SOURCE_NATIVE, 'origin': s}
    if s.startswith('text='):
        return {'by': 'text', 'value': s[len('text='):],
                'source': SOURCE_NATIVE, 'origin': s}
    m = _ID_ONLY_RE.match(s)
    if m:
        # `#username` ⇒ 语义化 id：比裸 css 稳（打分 0.70 vs 0.52），
        # 且是平台 ByChoice 支持的合法值
        return {'by': 'id', 'value': m.group(1),
                'source': SOURCE_NATIVE, 'origin': s}
    return {'by': 'css', 'value': s, 'source': SOURCE_NATIVE, 'origin': s}


def _canon_selectors(selectors):
    """选择器数组 → 规范候选数组（字符串与 dict 混排也能吃）。"""
    if isinstance(selectors, str):
        selectors = [selectors]
    out = []
    for item in (selectors or []):
        c = _canon_one_selector(item)
        if c:
            out.append(c)
    return out


def from_native(payload):
    """平台自有扩展的事件流。已是规范形状，主要做字段兜底与 seq 补齐。"""
    if isinstance(payload, str):
        payload = json.loads(payload)
    if isinstance(payload, list):
        actions = payload
        meta = {}
    elif isinstance(payload, dict):
        actions = payload.get('actions') or payload.get('events') or []
        meta = payload.get('meta') or {}
        # ★ 单条事件的兜底：既没有 actions/events 数组，本身又长得像一条事件
        #   （带 kind/type）⇒ 当成只有一个元素的数组。
        #   不这么做的话，NDJSON 只传了 1 条时会走 `[]` 分支被**静默丢光**
        #   （视图返 200 + received:0，看起来"成功了"，实际什么都没录到）。
        if not actions and (payload.get('kind') or payload.get('type')):
            actions = [payload]
            meta = {}
    else:
        raise ValueError('原生事件流必须是对象或数组')

    events = []
    for idx, raw in enumerate(actions, 1):
        if not isinstance(raw, dict):
            continue
        tgt = raw.get('target')
        target = None
        if isinstance(tgt, dict):
            attrs = tgt.get('attrs') or {}
            # ★ 必须先收敛成 dict 候选，下游才可用（见上方 _canon_selectors 说明）
            cands = _canon_selectors(tgt.get('selectors'))
            target = {
                'node_name': tgt.get('node_name') or tgt.get('tag'),
                'attrs': attrs,
                'text': tgt.get('text'),
                'aria_label': tgt.get('aria_label') or tgt.get('ariaLabel'),
                'selectors': cands,
                'bbox': tgt.get('bbox'),
                'in_shadow': bool(tgt.get('in_shadow')),
                'key': tgt.get('key') or _target_key_from(
                    attrs=attrs,
                    aria_label=tgt.get('aria_label') or tgt.get('ariaLabel'),
                    text=tgt.get('text'),
                    selectors=cands,
                ),
            }
        events.append({
            'seq': _to_int(raw.get('seq'), idx),
            'type': str(raw.get('kind') or raw.get('type') or 'unknown').lower(),
            'raw_type': str(raw.get('kind') or raw.get('type') or ''),
            'source': SOURCE_NATIVE,
            't': _to_int(raw.get('t') if raw.get('t') is not None else raw.get('timestamp')),
            'target': target,
            'value': raw.get('value'),
            'url': raw.get('url'),
            'key': raw.get('key'),
            'frame_path': raw.get('frame_path') or [],
            'scroll': raw.get('scroll'),
            'viewport': raw.get('viewport') or (
                {'width': raw.get('width'), 'height': raw.get('height')}
                if raw.get('width') and raw.get('height') else None),
            'asserted_events': raw.get('asserted_events'),
            'raw': raw,
        })
    return events, dict(meta, source=SOURCE_NATIVE)


def from_raw_events(payload):
    """裸事件流：字段名按常见约定猜测（nodeName/name/value/ts 等）。"""
    return from_native(payload)


# ---------------------------------------------------------------------------
# 入口：自动识别来源
# ---------------------------------------------------------------------------
def detect_source(payload):
    """按形状猜来源；猜不出返回 None（由调用方要求用户显式指定）。"""
    if isinstance(payload, str):
        s = payload.strip()
        if not s:
            return None
        if s[0] in '{[':
            try:
                payload = json.loads(s)
            except ValueError:
                return SOURCE_PLAYWRIGHT_SCRIPT
        else:
            return SOURCE_PLAYWRIGHT_SCRIPT
    if isinstance(payload, list):
        return SOURCE_RAW
    if isinstance(payload, dict):
        if isinstance(payload.get('steps'), list):
            return SOURCE_DEVTOOLS
        if isinstance(payload.get('actions'), list) or isinstance(payload.get('events'), list):
            return SOURCE_NATIVE
    return None


def normalize_source(payload, source=None):
    """统一入口。

    返回 (events, meta, ) —— meta 里会带上 source 与 warnings。

    ★ 关于「两套字母表」（踩过的坑，务必分清）
      · `SOURCE_*`（本文件）= **解析器**来源，描述「这份数据长什么样」，
        取值 devtools_recorder / playwright_script / native / raw_events。
      · `RecordingSession.Source`（apps/recording/models.py）= **会话**来源，
        描述「用户是从哪个入口拿到的」，取值
        manual_upload / extension / devtools_plugin / cdp / playwright_script。
      两者的 `playwright_script` 恰好同名，其余都不同名。

      入参 `source` 可能来自**任意一侧**（前端下拉框给的是会话侧，
      内部的 raw_payload 存的是解析器侧），所以别名表必须把两侧都认下来。
      历史上这里只认解析器侧的四个词 + 少数口语别名，导致前端
      下拉框一选「Chrome DevTools Recorder JSON」（值 = `devtools_plugin`）
      就抛「无法识别录制数据来源」，功能直接不可用。
    """
    raw = (source or '').strip().lower()
    # 「没指定」的几种写法一律走自动识别（手动上传的内容可能是 JSON，也可能是脚本）
    if raw in ('', 'auto', 'none', 'manual_upload', 'manual', 'upload'):
        src = detect_source(payload)
    elif raw in ('devtools', 'devtools_recorder', 'chrome_recorder', 'puppeteer',
                 'devtools_plugin', 'devtools-plugin', 'recorder'):
        src = SOURCE_DEVTOOLS
    elif raw in ('playwright', 'playwright_script', 'codegen', 'script', 'pw'):
        src = SOURCE_PLAYWRIGHT_SCRIPT
    elif raw in ('native', 'extension', 'cdp', 'chrome_extension'):
        src = SOURCE_NATIVE
    elif raw in ('raw', 'raw_events', 'events'):
        src = SOURCE_RAW
    else:
        src = None

    if src == SOURCE_DEVTOOLS:
        events, meta = from_devtools_recorder(payload)
    elif src == SOURCE_PLAYWRIGHT_SCRIPT:
        events, meta = from_playwright_script(payload)
    elif src == SOURCE_NATIVE:
        events, meta = from_native(payload)
    elif src == SOURCE_RAW:
        events, meta = from_raw_events(payload)
    else:
        raise ValueError('无法识别录制数据来源，请显式指定 source '
                         '（devtools_recorder / playwright_script / native）')

    meta = dict(meta or {})
    meta['source'] = src
    meta.setdefault('warnings', [])
    return events, meta
