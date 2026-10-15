# -*- coding: utf-8 -*-
"""
JMeter (.jmx) 解析器 —— 把 jmx 转换成平台统一 IR。

★ 核心难点：hashTree 层级还原。
  JMeter 的 jmx 不是嵌套标签，而是「元素 + 紧跟其后的 <hashTree> 就是它的子容器」
  这种平铺写法：
      <hashTree>
        <ThreadGroup testname="..."/>
        <hashTree>                <!-- 紧跟 ThreadGroup，是它的子节点 -->
          <HTTPSamplerProxy .../>
          <hashTree/>            <!-- 叶子 -->
        </hashTree>
      </hashTree>
  遍历规则：顺序遍历父 hashTree 的子节点，遇到非 hashTree 节点 E，
  就把 E 后面紧跟着的那个 hashTree 当作 E 的 children 递归下去。

★ 尊重 enabled 属性：源脚本里被禁用的元素（实测大量存在：禁用线程组、
  禁用采样器、禁用的 HTTP 请求默认值）一律记入 skipped，不静默导入。
"""

import xml.etree.ElementTree as ET

from .ir import (new_ir, new_request, new_controller, add_skipped, add_warning,
                 finalize, trunc, scan_vars)

# ---------------------------------------------------------------- 属性读取

def _text(el, prop):
    """读取 <stringProp name="prop"> 的文本；找不到返回 ''。"""
    if el is None:
        return ''
    for ch in el:
        if ch.tag == 'stringProp' and ch.get('name') == prop:
            return ch.text or ''
    return ''


def _bool(el, prop, default=False):
    """读取 <boolProp name="prop">。"""
    if el is None:
        return default
    for ch in el:
        if ch.tag == 'boolProp' and ch.get('name') == prop:
            return str(ch.text).strip().lower() == 'true'
    return default


def _enabled(el):
    """JMeter 元素的启用状态（缺省视为启用）。"""
    v = el.get('enabled')
    if v is None:
        return True
    return str(v).strip().lower() != 'false'


def _collection_items(el, coll_name, name_prop, value_prop):
    """
    读取 <collectionProp name=coll_name> 下的键值对列表。
    HeaderManager.headers / Arguments.arguments 都是这种结构。
    返回 [{"name":..,"value":..}]（保序，允许重名 —— JMeter 允许同名 header）。
    """
    out = []
    if el is None:
        return out
    for ch in el:
        if ch.tag != 'collectionProp' or ch.get('name') != coll_name:
            continue
        for ep in ch:
            nm = vl = ''
            for sp in ep:
                if sp.get('name') == name_prop:
                    nm = sp.text or ''
                elif sp.get('name') == value_prop:
                    vl = sp.text or ''
            out.append({'name': nm, 'value': vl})
    return out


# ---------------------------------------------------------------- body / 参数

def _sampler_args(el):
    """
    读取采样器的参数（HTTPsampler.Arguments）。
    返回 (params, ) —— 每个元素 {"name","value","use_equals","always_encode"}
    """
    for ch in el:
        if ch.tag == 'elementProp' and ch.get('name') == 'HTTPsampler.Arguments':
            for cp in ch:
                if cp.tag != 'collectionProp':
                    continue
                out = []
                for ep in cp:
                    if ep.tag != 'elementProp':
                        continue
                    d = {'name': '', 'value': '', 'use_equals': True, 'always_encode': False}
                    for sp in ep:
                        n = sp.get('name')
                        if n == 'Argument.name':
                            d['name'] = sp.text or ''
                        elif n == 'Argument.value':
                            d['value'] = sp.text or ''
                        elif n == 'HTTPArgument.use_equals':
                            d['use_equals'] = str(sp.text).strip().lower() == 'true'
                        elif n == 'HTTPArgument.always_encode':
                            d['always_encode'] = str(sp.text).strip().lower() == 'true'
                    out.append(d)
                return out
    return []


def _split_query(path):
    """把 path 里的查询串拆成 params，返回 (纯路径, params)。"""
    if not path:
        return '', []
    if '?' not in path:
        return path, []
    base, qs = path.split('?', 1)
    params = []
    for kv in qs.split('&'):
        if not kv:
            continue
        if '=' in kv:
            k, v = kv.split('=', 1)
        else:
            k, v = kv, ''
        params.append({'name': k, 'value': v})
    return base, params


def _build_body(el, args, method):
    """
    根据采样器属性与参数构造 body/params。
    返回 (params, body)。
    """
    method = (method or 'GET').upper()
    # ★ postBodyRaw 属性「存在」与否要区分：
    #   存在 → 严格按它的值判定（JMeter 自己的语义）；
    #   不存在（旧版 jmx）→ 才用「单个无名参数」兜底。
    raw_node = el.find("boolProp[@name='HTTPSampler.postBodyRaw']")
    if raw_node is not None:
        raw = str(raw_node.text).strip().lower() == 'true'
    else:
        raw = bool(len(args) == 1 and not args[0]['name'])

    if not args:
        return [], {'kind': 'none', 'value': None}

    # GET/HEAD/DELETE 且非 raw：参数是查询串
    if method in ('GET', 'HEAD', 'DELETE') and not raw:
        return [{'name': a['name'], 'value': a['value']} for a in args], \
               {'kind': 'none', 'value': None}

    if raw:
        v = args[0]['value']
        body = {'kind': 'raw', 'value': v}
        try:
            import json
            obj = json.loads(v)
            body = {'kind': 'json', 'value': obj}
        except Exception:
            pass
        return [], body

    # 表单
    return [], {'kind': 'form', 'value': [{'name': a['name'], 'value': a['value']}
                                          for a in args]}


# ---------------------------------------------------------------- 断言 / 提取

# JMeter ResponseAssertion 的 test_type 是位掩码
_ASSERT_TYPE = {1: 'contains', 2: 'matches', 4: 'equals', 8: 'substring'}
_ASSERT_NOT = 16
_ASSERT_FIELD = {
    'Assertion.response_data': 'body',
    'Assertion.response_code': 'status_code',
    'Assertion.response_headers': 'headers',
    'Assertion.response_message': 'message',
    'Assertion.sample_label': 'name',
    'Assertion.response_data_as_document': 'body',
}


def _parse_assertion(el):
    """解析 ResponseAssertion → [assert dict]。"""
    field = _text(el, 'Assertion.test_field')
    target = _ASSERT_FIELD.get(field, 'body')
    try:
        t = int(el.findtext("intProp[@name='Assertion.test_type']") or '1')
    except (TypeError, ValueError):
        t = 1
    neg = bool(t & _ASSERT_NOT)
    base = t & 15
    if base not in _ASSERT_TYPE:
        base = 1
    op = _ASSERT_TYPE[base]
    if neg:
        op = 'not_' + op

    # 期望值：可能多条目（collectionProp 下既有 stringProp 也有 elementProp）
    values = []
    for ch in el:
        if ch.tag != 'collectionProp' or ch.get('name') != 'Asserion.test_strings':
            continue
        for item in ch:
            if item.tag == 'stringProp':
                values.append(item.text or '')
            else:
                for sp in item:
                    if sp.get('name') in ('Assertion.test_string', 'Argument.value'):
                        values.append(sp.text or '')
    if not values:
        values = ['']
    return [{'target': target, 'op': op, 'value': v} for v in values]


def _parse_json_extractor(el):
    """解析 JSONPostProcessor。JMeter 用分号分隔多组 name/expr —— 必须拆开。"""
    names = _text(el, 'JSONPostProcessor.referenceNames')
    exprs = _text(el, 'JSONPostProcessor.jsonPathExprs')
    matchs = _text(el, 'JSONPostProcessor.match_numbers')
    defaults = _text(el, 'JSONPostProcessor.defaultValues')

    def _sp(v):
        return [x for x in (v or '').split(';')]

    ns, es = _sp(names), _sp(exprs)
    ms, ds = _sp(matchs), _sp(defaults)
    out = []
    for i, n in enumerate(ns):
        if not n.strip():
            continue
        out.append({
            'name': n.strip(),
            'expr': es[i] if i < len(es) else '',
            'from': 'json',
            'match': ms[i].strip() if i < len(ms) else '0',
            'default': ds[i].strip() if i < len(ds) else '',
        })
    return out


def _parse_regex_extractor(el):
    """解析 RegexExtractor。"""
    return [{
        'name': _text(el, 'RegexExtractor.refname'),
        'expr': _text(el, 'RegexExtractor.regex'),
        'from': 'regex',
        'match': _text(el, 'RegexExtractor.match_number') or '1',
        'default': _text(el, 'RegexExtractor.default') or '',
        'template': _text(el, 'RegexExtractor.template') or '$1$',
    }]


# ---------------------------------------------------------------- 主解析

# 容器类元素 → 平台控制器类型（None 表示本身就是压测分组，见 ThreadGroup 处理）
_CONTROLLER_MAP = {
    'TransactionController': 'transaction',
    'GenericController': 'transaction',     # 简单控制器：纯分组，降级为事务控制器
    'IfController': 'if',
    'LoopController': 'for',
    'WhileController': 'while',
    'ForeachController': 'foreach',
    'PostThreadGroup': 'transaction',
    'SetupThreadGroup': 'transaction',
}

# 明确忽略的元素 → skipped 原因
_IGNORE_MAP = {
    'ResultCollector': 'JMeter 监听器（结果收集），平台用自带报告，不需要',
    'CookieManager': '平台按 host 维护 requests.Session，Cookie 自动串联，无需显式配置',
    'CacheManager': 'HTTP 缓存管理器，平台请求不复用缓存语义',
    'SyncTimer': '集合点（同步定时器），平台压测无对应能力',
    'ProxyControl': 'HTTP 代理服务器（录制控制器），与用例无关',
    'TestPlan': '测试计划根节点，仅取名称',
    'jmeterTestPlan': '文件根节点',
}


def parse_jmx(text):
    """
    解析 jmx 文本 → 平台统一 IR。

    :param text: jmx 文件文本（str 或 bytes）
    :return: IR dict（含 stats / skipped）
    """
    ir = new_ir('jmeter')
    if isinstance(text, bytes):
        text = text.decode('utf-8', 'replace')
    if not text or not text.strip():
        add_warning(ir, '文件内容为空')
        return finalize(ir)

    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        add_warning(ir, 'XML 解析失败：%s' % e)
        ir['error'] = 'XML 解析失败：%s' % e
        return finalize(ir)

    top = root.find('hashTree')
    if top is None:
        top = root

    # TestPlan 名称作为建议用例名（它在顶层 hashTree 里，不是 root 的直接子）
    tp = root.find('.//TestPlan')
    if tp is not None:
        ir['meta']['title'] = trunc(tp.get('testname') or '', 50)

    state = {
        'defaults': {},          # HTTP 请求默认值 domain/port/protocol
        'load_done': False,      # 是否已写入 meta.load
    }
    ir['items'] = _walk(top, ir, [], state, depth=0)
    return finalize(ir)


def _walk(ht, ir, inherited_headers, state, depth=0, sink=None):
    """
    遍历一个 hashTree 容器，返回 IR items。

    :param inherited_headers: 上层 HeaderManager 累积下来的头（向下继承）
    :param state: 跨层级共享状态（HTTP 默认值 / 是否已取过压测参数）
    :param sink: 若非空，表示这是某个采样器的子容器 —— 其中的提取器/断言
                 挂到该采样器上，而不是寻找新的宿主
    """
    items = []
    headers = [dict(h) for h in inherited_headers]
    defaults = dict(state.get('defaults') or {})
    last_req = [sink]        # 最近一个 request 节点（供提取器/断言挂载）

    kids = list(ht)
    i = 0
    while i < len(kids):
        e = kids[i]
        if e.tag == 'hashTree':
            i += 1
            continue
        sub = None
        if i + 1 < len(kids) and kids[i + 1].tag == 'hashTree':
            sub = kids[i + 1]
            i += 2
        else:
            i += 1

        consumed = _dispatch(e, sub, items, ir, headers, defaults, state, last_req, depth)

        # ★ 关键：自身不产生 item 的元素（TestPlan / 头管理器 / 变量 / CSV …），
        #   它后面紧跟的 hashTree 里可能还有内容，必须继续往下钻，
        #   否则整棵树会被丢掉（TestPlan 之后就是全部业务内容）。
        if not consumed and sub is not None and len(sub):
            items += _walk(sub, ir, headers, state, depth + 1)
    return items


def _dispatch(e, sub, items, ir, headers, defaults, state, last_req, depth):
    """
    处理单个 JMeter 元素。

    :return: True 表示已自行消费 sub 容器（容器类/采样器）；
             False 表示未消费，由 _walk 继续下钻。
    """
    tag = e.tag
    name = e.get('testname') or ''
    en = _enabled(e)

    # ---------- 未启用：整棵子树跳过（JMeter 里它也不会执行） ----------
    if not en:
        # 整棵子树跳过（JMeter 里它也不会执行），不再下钻
        add_skipped(ir, tag, name, '源脚本中已禁用（enabled=false）')
        return True

    # ---------- HTTP 请求默认值 ----------
    if tag == 'ConfigTestElement':
        gui = (e.get('guiclass') or '')
        if gui == 'HttpDefaultsGui' or '默认值' in name or 'Defaults' in name:
            d = {
                'domain': _text(e, 'HTTPSampler.domain'),
                'port': _text(e, 'HTTPSampler.port'),
                'protocol': _text(e, 'HTTPSampler.protocol'),
                'contentEncoding': _text(e, 'HTTPSampler.contentEncoding'),
            }
            # 只覆盖非空值，且只在同层及下层生效
            for k, v in d.items():
                if v:
                    defaults[k] = v
                    state['defaults'][k] = v
            if not ir['meta'].get('host') and d.get('domain'):
                host = '%s://%s' % (d.get('protocol') or 'http', d['domain'])
                if d.get('port'):
                    host += ':' + d['port']
                ir['meta']['host'] = host
                ir['meta']['protocol'] = d.get('protocol') or 'http'
            return False
        add_skipped(ir, tag, name, '未识别的 ConfigTestElement（guiclass=%s）' % gui)
        return False

    # ---------- 用户定义的变量 ----------
    if tag == 'Arguments':
        for a in _collection_items(e, 'Arguments.arguments', 'Argument.name', 'Argument.value'):
            if a['name']:
                ir['vars'].append({'name': a['name'], 'value': a['value'],
                                   'desc': '来自 JMeter 用户定义的变量'})
        add_warning(ir, '用户定义的变量已导入；若含环境相关值请在执行前核对')
        return False

    # ---------- 头管理器：向下继承 ----------
    if tag == 'HeaderManager':
        hs = _collection_items(e, 'HeaderManager.headers', 'Header.name', 'Header.value')
        for h in hs:
            if not h['name']:
                continue
            replaced = False
            for x in headers:
                if x['name'].lower() == h['name'].lower():
                    x['value'] = h['value']
                    replaced = True
                    break
            if not replaced:
                headers.append(dict(h))
        return False

    # ---------- CSV 数据文件 ----------
    if tag == 'CSVDataSet':
        cols = [c.strip() for c in (_text(e, 'variableNames') or '').split(',') if c.strip()]
        ir['datasets'].append({
            'name': name or 'CSV 数据文件设置',
            'columns': cols,
            'delimiter': _text(e, 'delimiter') or ',',
            'ignore_first_line': _bool(e, 'ignoreFirstLine'),
            'filename': _text(e, 'filename'),
            'recycle': _bool(e, 'recycle', True),
            'stop_thread': _bool(e, 'stopThread'),
        })
        return False

    # ---------- 采样器 ----------
    if tag == 'HTTPSamplerProxy':
        req = new_request(name, _text(e, 'HTTPSampler.method') or 'GET',
                          _text(e, 'HTTPSampler.path'))
        dom = _text(e, 'HTTPSampler.domain') or defaults.get('domain', '')
        port = _text(e, 'HTTPSampler.port') or defaults.get('port', '')
        proto = _text(e, 'HTTPSampler.protocol') or defaults.get('protocol', '')
        req['host'] = dom
        req['port'] = port
        req['protocol'] = proto
        if dom:
            host = '%s://%s' % (proto or 'http', dom)
            if port:
                host += ':' + port
            req['base_url'] = host
            if not ir['meta'].get('host'):
                ir['meta']['host'] = host

        base, qp = _split_query(req['path'])
        req['path'] = base
        args = _sampler_args(e)
        aparams, body = _build_body(e, args, req['method'])
        req['params'] = qp + aparams
        req['body'] = body
        req['headers'] = [dict(h) for h in headers]
        req['enabled'] = True
        req['timeout'] = _text(e, 'HTTPSampler.response_timeout') or ''
        items.append(req)
        # 采样器紧跟的 hashTree 里是它的头/提取器/断言 —— 挂到这个采样器上
        if sub is not None and len(sub):
            req['children'] += _walk(sub, ir, [dict(h) for h in headers], state,
                                     depth + 1, sink=req)
        last_req[0] = req
        return True

    # ---------- 提取器 ----------
    if tag == 'JSONPostProcessor':
        ex = _parse_json_extractor(e)
        if last_req[0] is not None:
            last_req[0]['extract'] += ex
        else:
            add_skipped(ir, tag, name, '提取器前面没有采样器，无法挂载（%d 个变量）' % len(ex))
        return False

    if tag == 'RegexExtractor':
        ex = _parse_regex_extractor(e)
        if last_req[0] is not None:
            last_req[0]['extract'] += ex
        else:
            add_skipped(ir, tag, name, '正则提取器前面没有采样器，无法挂载')
        return False

    # ---------- 断言 ----------
    if tag == 'ResponseAssertion':
        az = _parse_assertion(e)
        if last_req[0] is not None:
            last_req[0]['asserts'] += az
        else:
            add_skipped(ir, tag, name, '断言前面没有采样器，无法挂载（%d 条）' % len(az))
        return False

    # ---------- 定时器 → 等待 ----------
    if tag == 'ConstantTimer':
        try:
            sec = int(_text(e, 'ConstantTimer.delay') or '0') / 1000.0
        except (TypeError, ValueError):
            sec = 0
        items.append(new_controller('sleep', name or '固定定时器',
                                    {'timeout': sec}, []))
        return True

    if tag in ('TestAction', 'FlowControlAction'):
        try:
            sec = int(_text(e, 'Action.duration') or '0') / 1000.0
        except (TypeError, ValueError):
            sec = 0
        items.append(new_controller('sleep', name or '测试活动', {'timeout': sec}, []))
        return True

    # ---------- 线程组：压测参数 + 分组容器 ----------
    if tag in ('ThreadGroup', 'SetupThreadGroup', 'PostThreadGroup'):
        load = {
            'concurrent_users': _text(e, 'ThreadGroup.num_threads'),
            'ramp_up': _text(e, 'ThreadGroup.ramp_time'),
            'duration': _text(e, 'ThreadGroup.duration'),
            'scheduler': _bool(e, 'ThreadGroup.scheduler'),
        }
        if not state.get('load_done'):
            ir['meta']['load'] = dict(load)
            state['load_done'] = True
        children = _walk(sub, ir, headers, state, depth + 1) if sub is not None else []
        ctrl = new_controller('transaction', name, {'load': load}, children)
        ctrl['note'] = '由 JMeter 线程组转换（并发 %s / ramp %s / 时长 %s）' % (
            load['concurrent_users'] or '-', load['ramp_up'] or '-',
            load['duration'] or '-')
        items.append(ctrl)
        return True

    # ---------- 逻辑控制器 ----------
    if tag in _CONTROLLER_MAP:
        ctype = _CONTROLLER_MAP[tag]
        cfg = {}
        if tag == 'IfController':
            cfg['expr'] = _text(e, 'IfController.condition')
        elif tag == 'LoopController':
            forever = _bool(e, 'LoopController.continue_forever')
            cfg['loop'] = -1 if forever else (_text(e, 'LoopController.loops') or '1')
        elif tag == 'WhileController':
            cfg['condition'] = _text(e, 'WhileController.condition')
        elif tag == 'ForeachController':
            cfg['input_var'] = _text(e, 'ForeachController.inputValString')
            cfg['output_var'] = _text(e, 'ForeachController.returnValString')
        children = _walk(sub, ir, headers, state, depth + 1) if sub is not None else []
        ctrl = new_controller(ctype, name, cfg, children)
        if tag == 'GenericController':
            ctrl['note'] = '由 JMeter 简单控制器转换（仅分组，无执行语义）'
        if tag == 'TransactionController':
            cfg['include_timers'] = _bool(e, 'TransactionController.includeTimers')
            cfg['generate_parent'] = _bool(e, 'TransactionController.parent')
        items.append(ctrl)
        return True

    # ---------- 明确忽略 ----------
    if tag in _IGNORE_MAP:
        add_skipped(ir, tag, name, _IGNORE_MAP[tag])
        return False

    # ---------- 其余：必须点名，不允许静默丢 ----------
    add_skipped(ir, tag, name, '未识别的 JMeter 元素，已忽略')
    return False
