# -*- coding: utf-8 -*-
"""
统一 IR（中间表示）定义与通用工具。

IR 结构：
    {
      "source":  "jmeter" | "locust" | "har" | "openapi",
      "meta":    {"title": str, "host": str, "protocol": str,
                  "load": {"concurrent_users": str, "ramp_up": str, "duration": str}},
      "vars":     [{"name": str, "value": str, "desc": str}],
      "datasets": [{"name": str, "columns": [str], "delimiter": str,
                    "ignore_first_line": bool, "filename": str}],
      "items":    [request | controller],   # 有序、可嵌套
      "skipped":  [{"type": str, "name": str, "reason": str}],   # ★ 必填
      "warnings": [str],
      "stats":    {"total", "requests", "controllers", "vars", "datasets", "skipped"}
    }

★ skipped 为什么是必填：
「导入成功但内容不对」是最难查的一类缺陷（教训：HAR 导入曾静默丢掉 /login，
返回体照样 200，用户看到的是「后续接口全是未登录」）。skipped 强制解析器
把被丢弃的每一条都点名 + 给原因，预览页直接摊给用户看。
"""

import re

# ---------------------------------------------------------------- 常量

#: 平台变量语法（实测 core/com/common.py:424  pattern=r'\${.*?}'）
#: 与 JMeter 的 ${var} 完全同源 —— 导入时零转换
VAR_PATTERN = re.compile(r'\$\{(.*?)\}')

#: ServiceModule.name 的实际列长度（实测 max_length=20）
#: 不截断会抛 Data too long，且整体仍返 200 —— 表现为「导入成功但少了几条」
MODULE_NAME_MAX = 20

#: 平台 Api.name 长度
API_NAME_MAX = 50

#: 控制器类型 → 平台 StepType=9 的 keyword（实测 core/run_case.py）
CONTROLLER_KEYWORD = {
    'if': '1',
    'for': '2',
    'while': '3',
    'transaction': '4',
    'sleep': '5',
    'foreach': '6',
}

#: 平台步骤类型（实测 core/run_case.py:79 StepType）
STEP_TYPE_REQUEST = 5      # HTTP 请求
STEP_TYPE_CONTROL = 9      # 控制器


# ---------------------------------------------------------------- 构造

def new_ir(source):
    """创建一个空的 IR 骨架。"""
    return {
        'source': source,
        'meta': {'title': '', 'host': '', 'protocol': '', 'load': {}},
        'vars': [],
        'datasets': [],
        'items': [],
        'skipped': [],
        'warnings': [],
        'stats': {},
    }


def new_request(name='', method='GET', path=''):
    """构造一个 request 类型的 IR 节点。"""
    return {
        'type': 'request',
        'name': name,
        'method': (method or 'GET').upper(),
        'path': path or '',
        'headers': [],          # [{"name":..,"value":..}]
        'params': [],           # [{"name":..,"value":..}]  查询串/表单参数
        'body': {'kind': 'none', 'value': None},
        'extract': [],          # [{"name":..,"expr":..,"from":..,"default":..}]
        'asserts': [],          # [{"target":..,"op":..,"value":..}]
        'weight': 1,
        'enabled': True,
        'raw': None,            # 解析不出时保留源片段，供人工补
        'note': '',             # 「需人工确认」之类的提示
        'children': [],         # 采样器下挂的提取器/断言也可作为子节点展示
    }


def new_controller(ctype, name='', config=None, children=None):
    """构造一个 controller 类型的 IR 节点。"""
    return {
        'type': 'controller',
        'ctype': ctype,
        'name': name,
        'config': config or {},
        'enabled': True,
        'children': children or [],
        'note': '',
    }


def add_skipped(ir, etype, name, reason):
    """记录一条被丢弃的源数据 —— 必须点名 + 给原因。"""
    ir['skipped'].append({'type': etype, 'name': name or '', 'reason': reason or ''})
    return ir


def add_warning(ir, msg):
    if msg and msg not in ir['warnings']:
        ir['warnings'].append(msg)
    return ir


# ---------------------------------------------------------------- 工具

def trunc(text, limit=MODULE_NAME_MAX):
    """按目标列长度截断。★ 建模块前必须调用（ServiceModule.name 只有 20）。"""
    s = ('' if text is None else str(text)).strip()
    if len(s) <= limit:
        return s
    return s[:limit]


def scan_vars(*texts):
    """扫描文本里引用的全部 ${var} 名字（去重、保序）。"""
    out = []
    for t in texts:
        if not t:
            continue
        s = t if isinstance(t, str) else str(t)
        for m in VAR_PATTERN.findall(s):
            nm = m.strip()
            # 过滤 JMeter 函数嵌套，如 ${__P(xx)} / ${__time(,)}
            if nm.startswith('__'):
                continue
            if nm and nm not in out:
                out.append(nm)
    return out


def _iter_requests(items):
    """深度优先遍历 IR 里的全部 request 节点。"""
    for it in items or []:
        if it.get('type') == 'request':
            yield it
        for sub in (it.get('children') or []):
            for x in _iter_requests([sub]):
                yield x


def defined_var_names(ir):
    """IR 里已定义的变量名：用户定义变量 + CSV 列名。"""
    names = [v.get('name') for v in (ir.get('vars') or []) if v.get('name')]
    for ds in (ir.get('datasets') or []):
        names += [c for c in (ds.get('columns') or []) if c]
    return names


def check_var_links(ir):
    """
    静态检查变量断链：IR 里引用了但没定义的 ${var}。

    返回 [{"name": str, "where": str}]。
    ★ 这是能提前拦住的，别留到运行期才炸。
    """
    defined = set(defined_var_names(ir))
    bad = []
    for req in _iter_requests(ir.get('items') or []):
        where = req.get('name') or req.get('path') or ''
        texts = [req.get('path') or '']
        texts += [p.get('value') or '' for p in (req.get('params') or [])]
        texts += [h.get('value') or '' for h in (req.get('headers') or [])]
        body = req.get('body') or {}
        if isinstance(body.get('value'), str):
            texts.append(body['value'])
        elif isinstance(body.get('value'), (dict, list)):
            texts.append(str(body['value']))
        for nm in scan_vars(*texts):
            if nm not in defined:
                bad.append({'name': nm, 'where': where})
    # 去重
    seen, out = set(), []
    for b in bad:
        k = (b['name'], b['where'])
        if k not in seen:
            seen.add(k)
            out.append(b)
    return out


def finalize(ir):
    """汇总统计。解析完成后必须调用。"""
    reqs = list(_iter_requests(ir.get('items') or []))
    ctrls = [i for i in (ir.get('items') or []) if i.get('type') == 'controller']

    def _count_ctrl(items):
        n = 0
        for it in items or []:
            if it.get('type') == 'controller':
                n += 1 + _count_ctrl(it.get('children'))
        return n

    ir['stats'] = {
        'total': len(reqs) + _count_ctrl(ir.get('items')),
        'requests': len(reqs),
        'controllers': _count_ctrl(ir.get('items')),
        'vars': len(ir.get('vars') or []),
        'datasets': len(ir.get('datasets') or []),
        'skipped': len(ir.get('skipped') or []),
        'warnings': len(ir.get('warnings') or []),
    }
    del ctrls
    return ir
