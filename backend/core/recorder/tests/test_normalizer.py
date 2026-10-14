# -*- coding: utf-8 -*-
"""归一化引擎单测（P0-③）—— 离线可跑，不依赖 Django / 数据库 / 网络

运行方式（容器内或本地均可）：
    cd <backend>
    python core/recorder/tests/test_normalizer.py
    # 或
    python -m core.recorder.tests.test_normalizer

★ 为什么这个测试很重要
   整套「Web 自动化录制」方案里，只有归一化这一层是**纯函数**：
   输入固定事件流 → 输出确定的 IR。其余各层（接口、落库、前端）都要跑真实
   环境才能验证。所以这里是唯一能稳定、可复现、秒级反馈的防线 ——
   把它的覆盖做满，后面几层的调试成本会显著下降。

★ 最后一组断言刻意做了「跨层校验」
   本引擎产出的每一个 keyword 都必须是 run_playwright.py 里真实存在的方法。
   这条断言能拦住一类很隐蔽的错：引擎里写了 `select_options`（多了个 s）
   这种拼写错误，归一化测试全绿、接口也返 200，直到真正执行时
   才在 `playwright_func_map[keyword]` 处抛 KeyError。
"""

import json
import os
import sys
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from core.recorder import normalizer as NZ          # noqa: E402
from core.recorder import sources as SRC            # noqa: E402
from core.recorder import locator_score as LS       # noqa: E402

RUN_PLAYWRIGHT = os.path.join(_BACKEND, 'core', 'step', 'run_playwright.py')

# ---------------------------------------------------------------------------
# 极简测试框架（不引入 pytest，保证在容器里零依赖可跑）
# ---------------------------------------------------------------------------
_RESULTS = []
_CURRENT = {'name': '', 'fails': []}


def case(name):
    def deco(fn):
        _RESULTS.append((name, fn))
        return fn
    return deco


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def eq(actual, expected, label=''):
    if actual != expected:
        raise AssertionError('%s期望 %r，实际 %r' % (label and label + ': ' or '', expected, actual))


# ---------------------------------------------------------------------------
# 测试数据构造器
# ---------------------------------------------------------------------------
def sel(by, value, match_count=None, opts=None, source='native'):
    d = {'by': by, 'value': value, 'source': source}
    if match_count is not None:
        d['match_count'] = match_count
    if opts:
        d['opts'] = opts
    return d


def tgt(selectors, node_name=None, attrs=None, text=None, aria_label=None):
    return {
        'node_name': node_name,
        'attrs': attrs or {},
        'text': text,
        'aria_label': aria_label,
        'selectors': selectors or [],
    }


def act(seq, kind, t=None, target=None, value=None, url=None, key=None,
        scroll=None, viewport=None, asserted_events=None):
    a = {'seq': seq, 'kind': kind}
    if t is not None:
        a['t'] = t
    if target is not None:
        a['target'] = target
    if value is not None:
        a['value'] = value
    if url is not None:
        a['url'] = url
    if key is not None:
        a['key'] = key
    if scroll is not None:
        a['scroll'] = scroll
    if viewport is not None:
        a['viewport'] = viewport
    if asserted_events is not None:
        a['asserted_events'] = asserted_events
    return a


def build(actions, **opts):
    events, meta = SRC.normalize_source({'actions': actions}, source='native')
    return NZ.build_ir(events, meta, opts)


def kws(ir):
    return [a['keyword'] for a in ir['actions']]


def by_kw(ir, keyword):
    return [a for a in ir['actions'] if a['keyword'] == keyword]


# ===========================================================================
# 规则 1：输入防抖合并
# ===========================================================================
@case('01 输入防抖合并：3 次连续 input(200ms) ⇒ 1 个 fill，值取最后一次')
def t01():
    e = tgt([sel('css', '#kw', 1)], node_name='input', attrs={'name': 'search_kw', 'type': 'text'})
    ir = build([
        act(1, 'input', t=0, target=e, value='a'),
        act(2, 'input', t=200, target=e, value='ad'),
        act(3, 'input', t=400, target=e, value='adm'),
    ])
    fills = by_kw(ir, 'fill')
    eq(len(fills), 1, 'fill 步骤数')
    eq(fills[0]['args']['value']['value'], 'adm', 'fill 的最终值')
    eq(fills[0]['args']['value']['kind'], 'literal', '普通值应保持字面量')
    check('输入防抖合并' in json.dumps(ir['stats']['drop_reasons'], ensure_ascii=False),
          '丢弃原因里应记录防抖合并')


@case('02 输入防抖：2 次 input 间隔 1500ms ⇒ 保留 2 个动作')
def t02():
    e = tgt([sel('css', '#kw', 1)], node_name='input', attrs={'name': 'search_kw', 'type': 'text'})
    ir = build([
        act(1, 'input', t=0, target=e, value='a'),
        act(2, 'input', t=1500, target=e, value='b'),
    ])
    eq(len(by_kw(ir, 'fill')), 2, '间隔超过 800ms 应保留两次输入')


# ===========================================================================
# 规则 2 / 3：hover 剪枝、重复点击去重
# ===========================================================================
@case('03 hover 剪枝：hover 后 600ms 内没有 click ⇒ 丢弃该 hover')
def t03():
    h = tgt([sel('css', '.menu', 1)], node_name='div', text='菜单')
    f = tgt([sel('css', '#kw', 1)], node_name='input', attrs={'name': 'search_kw'})
    ir = build([
        act(1, 'hover', t=0, target=h),
        act(2, 'input', t=600, target=f, value='x'),
    ])
    eq(len(by_kw(ir, 'move_to_element')), 0, 'hover 应被剪掉')
    check('hover 链剪枝' in json.dumps(ir['stats']['drop_reasons'], ensure_ascii=False),
          '丢弃原因里应记录 hover 剪枝')


@case('04 重复点击去重：同元素 200ms 内两次 click ⇒ 只留一次')
def t04():
    e = tgt([sel('css', '#ok', 1)], node_name='button', text='确定')
    ir = build([
        act(1, 'click', t=0, target=e),
        act(2, 'click', t=200, target=e),
    ])
    eq(len(by_kw(ir, 'click')), 1, '应只保留一次点击')


@case('05 时间戳缺失时点击**不**去重（宁冗余、不误删）')
def t05():
    e = tgt([sel('css', '#ok', 1)], node_name='button', text='确定')
    ir = build([
        act(1, 'click', target=e),
        act(2, 'click', target=e),
    ])
    eq(len(by_kw(ir, 'click')), 2, '无时间戳证据时必须保留两次点击')


# ===========================================================================
# 规则 6：敏感字段脱敏（含 raw 泄漏这条最隐蔽的路径）
# ===========================================================================
@case('06 敏感字段：密码值强制转变量，且原文不得出现在 IR 任何位置')
def t06():
    e = tgt([sel('css', '#pwd', 1)], node_name='input',
            attrs={'type': 'password', 'name': 'password'})
    ir = build([act(1, 'input', t=0, target=e, value='Aa123456')])
    fills = by_kw(ir, 'fill')
    eq(len(fills), 1)
    v = fills[0]['args']['value']
    eq(v['kind'], 'variable', '密码必须转成变量')
    eq(v['var_name'], 'Password', '变量名')
    eq(v.get('redacted'), True, '应带 redacted 标记')
    blob = json.dumps(ir, ensure_ascii=False)
    check('Aa123456' not in blob, '明文密码泄漏进了 IR（检查 act.raw 是否被保留）')


@case('07 敏感字段：access_token 命名的字段同样脱敏')
def t07():
    e = tgt([sel('css', '#tk', 1)], node_name='input', attrs={'name': 'access_token'})
    ir = build([act(1, 'input', t=0, target=e, value='abc123')])
    v = by_kw(ir, 'fill')[0]['args']['value']
    eq(v['kind'], 'variable', 'token 字段应脱敏')


# ===========================================================================
# 关键字映射
# ===========================================================================
@case('08 映射：点击 checkbox ⇒ check 关键字')
def t08():
    e = tgt([sel('css', '#agree', 1)], node_name='input', attrs={'type': 'checkbox'})
    ir = build([act(1, 'click', t=0, target=e)])
    eq(kws(ir), ['check'], 'checkbox 点击应映射为 check')


@case('09 映射：select 的 change ⇒ select_option 关键字')
def t09():
    e = tgt([sel('css', '#city', 1)], node_name='select', attrs={'name': 'city'})
    ir = build([act(1, 'change', t=0, target=e, value='bj')])
    eq(kws(ir), ['select_option'], 'select 变更应映射为 select_option')
    eq(by_kw(ir, 'select_option')[0]['args']['value']['value'], 'bj')


@case('10 映射：file input 的 change ⇒ upload_file 且留痕待补')
def t10():
    e = tgt([sel('css', '#file', 1)], node_name='input', attrs={'type': 'file'})
    ir = build([act(1, 'change', t=0, target=e, value='C:\\secret.txt')])
    eq(kws(ir), ['upload_file'])
    check(by_kw(ir, 'upload_file')[0]['needs_review'], '文件路径缺失应标记待复核')


@case('11 映射：页面级滚动 ⇒ scroll_page；位移 < 50px 被丢弃')
def t11():
    ir = build([
        act(1, 'scroll', t=0, scroll={'x': 0, 'y': 800}),
        act(2, 'scroll', t=100, scroll={'x': 0, 'y': 20}),
    ])
    eq(kws(ir), ['scroll_page'])
    eq(by_kw(ir, 'scroll_page')[0]['args']['direction']['value'], 'down')
    eq(by_kw(ir, 'scroll_page')[0]['args']['distance']['value'], 800)


@case('12 映射：Enter/Esc/Tab ⇒ press_enter/press_esc/press_tab')
def t12():
    ir = build([
        act(1, 'keydown', t=0, key='Enter'),
        act(2, 'keydown', t=10, key='Escape'),
        act(3, 'keydown', t=20, key='Tab'),
    ])
    eq(sorted(kws(ir)), ['press_enter', 'press_esc', 'press_tab'])


@case('13 映射：navigate ⇒ goto，并成为 meta.start_url')
def t13():
    ir = build([act(1, 'navigate', url='https://x.example/login')])
    eq(kws(ir), ['goto'])
    eq(by_kw(ir, 'goto')[0]['args']['uri']['value'], 'https://x.example/login')
    eq(ir['meta']['start_url'], 'https://x.example/login')


@case('14 映射：setViewport ⇒ set_viewport（不该被当成不支持类型丢弃）')
def t14():
    ir = build([act(1, 'set_viewport', viewport={'width': 1920, 'height': 1080})])
    eq(kws(ir), ['set_viewport'])
    eq(by_kw(ir, 'set_viewport')[0]['args']['width']['value'], 1920)


# ===========================================================================
# 定位器打分
# ===========================================================================
@case('15 打分：label 候选应排在 xpath 候选之前且分值更高')
def t15():
    e = tgt([
        sel('label', '用户名', 1),
        sel('xpath', '//form/div[1]/input', 1),
    ], node_name='input')
    ir = build([act(1, 'input', t=0, target=e, value='u1')])
    locs = ir['actions'][0]['element']['locators']
    eq(locs[0]['by'], 'label', '首位应是 label')
    check(locs[0]['score'] > locs[-1]['score'],
          'label 分数应高于 xpath：%s vs %s' % (locs[0]['score'], locs[-1]['score']))


@case('16 打分：含随机片段的 css 应被扣到 0.30 以下')
def t16():
    score, reasons = LS.score_locator('css', '.css-1x2y3z')
    check(score < 0.30, '随机类名 css 分数应 <0.30，实际 %.2f' % score)
    check(any('随机' in r for r in reasons), '应给出"含随机片段"的原因')


@case('17 打分：nth-child 与框架类名应被扣分，语义 id 应高于裸 css')
def t17():
    s_nth, r_nth = LS.score_locator('css', '.form > div:nth-child(2) > input')
    s_plain, _ = LS.score_locator('css', '#username')
    check(s_nth < s_plain, 'nth-child 的 CSS 应低于语义 id：%.2f vs %.2f' % (s_nth, s_plain))

    s_fw, r_fw = LS.score_locator('css', '.el-input__inner')
    check(s_fw < 0.52, '框架类名应低于 css 基准 0.52，实际 %.2f' % s_fw)

    s_num, r_num = LS.score_locator('id', '123456')
    check(s_num < 0.70, '纯数字 id 应低于语义 id 基准 0.70，实际 %.2f' % s_num)


@case('18 打分：唯一匹配有加成，多匹配扣分（避免默认选中歧义定位器）')
def t18():
    s_uniq, _ = LS.score_locator('css', '#a', match_count=1)
    s_multi, r_multi = LS.score_locator('css', '#a', match_count=5)
    check(s_uniq > s_multi, '唯一匹配应高于多匹配：%.2f vs %.2f' % (s_uniq, s_multi))


# ===========================================================================
# 断言推导
# ===========================================================================
@case('19 断言：点击"登录"按钮 ⇒ 生成"需人工确认成功标志"的断言')
def t19():
    e = tgt([sel('css', '#login', 1)], node_name='button', text='登录')
    ir = build([act(1, 'click', t=0, target=e)])
    a = by_kw(ir, 'click')[0]['assertions']
    eq(len(a), 1, '登录按钮应产生一条断言建议')
    eq(a[0]['rule'], 'mutating_button')
    eq(a[0]['auto'], False, '成功标志无法从录制得知，必须人工确认')


@case('20 断言：导航事件 ⇒ 生成 URL 断言并标记 brittle')
def t20():
    e = tgt([sel('css', '#go', 1)], node_name='button', text='进入')
    ir = build([act(1, 'click', t=0, target=e,
                    asserted_events=[{'type': 'navigation',
                                      'url': 'https://x.example/home'}]),
                act(2, 'navigate', t=100, url='https://x.example/home')])
    a = by_kw(ir, 'click')[0]['assertions']
    check(any(x['kind'] == 'page_url' for x in a), '应产生 URL 断言')
    check(any(x.get('brittle') for x in a), 'URL 断言应标记为脆弱（含易变查询参数风险）')


@case('21 断言：fill 之后 ⇒ 断言元素值等于所填内容')
def t21():
    e = tgt([sel('css', '#kw', 1)], node_name='input', attrs={'name': 'search_kw'})
    ir = build([act(1, 'input', t=0, target=e, value='hello')])
    a = by_kw(ir, 'fill')[0]['assertions']
    check(any(x['kind'] == 'element_value' and x['expect'] == 'hello' for x in a),
          '应生成"值回显"断言，期望值 hello')


# ===========================================================================
# 统计不变量
# ===========================================================================
@case('22 统计：drop_reasons 合计必须等于 dropped（否则页面上的统计是假的）')
def t22():
    e = tgt([sel('css', '#kw', 1)], node_name='input', attrs={'name': 'search_kw'})
    ir = build([
        act(1, 'navigate', url='https://x.example/'),
        act(2, 'input', t=0, target=e, value='a'),
        act(3, 'input', t=100, target=e, value='ab'),
        act(4, 'hover', t=200, target=tgt([sel('css', '.m', 1)], text='菜单')),
        act(5, 'scroll', t=300, scroll={'x': 0, 'y': 10}),          # 微滚动
        act(6, 'click', t=400, target=tgt([sel('css', '#a', 1)], node_name='div')),
        act(7, 'click', t=450, target=tgt([sel('css', '#a', 1)], node_name='div')),  # 重复
        act(8, 'keyup', t=500, key='Enter'),                         # keyup 丢弃
        act(9, 'close', t=600),                                      # close 丢弃
    ])
    st = ir['stats']
    total_drop = sum(st['drop_reasons'].values())
    eq(total_drop, st['dropped'],
       'drop_reasons 合计(%d) != dropped(%d)' % (total_drop, st['dropped']))
    eq(st['raw_events'], 9)
    check('未归因' not in ' '.join(st['drop_reasons'].keys()),
          '出现了未归因的丢弃，说明有分支在静默丢事件：%s' % st['drop_reasons'])


@case('23 统计：空输入不应崩，且返回结构完整')
def t23():
    ir = NZ.build_ir([], {})
    eq(ir['stats']['raw_events'], 0)
    eq(ir['stats']['kept_actions'], 0)
    eq(ir['actions'], [])
    check('drop_reasons' in ir['stats'], '空输入也应返回完整的 stats 结构')
    s = NZ.summarize(ir)
    eq(s['kept_actions'], 0)


# ===========================================================================
# 多来源适配
# ===========================================================================
@case('24 来源：Chrome DevTools Recorder 导出格式可被识别与归一化')
def t24():
    payload = {
        'title': '登录流程',
        'steps': [
            {'type': 'navigate', 'url': 'https://x.example/login'},
            {'type': 'change', 'value': 'admin',
             'target': 'aria/用户名',
             'selectors': [['aria/用户名'], ['#username'], ['form > div:nth-child(1) > input']]},
            {'type': 'change', 'value': 'secret',
             'target': 'aria/密码',
             'selectors': [['aria/密码'], ['#password']]},
            {'type': 'click', 'target': 'aria/登录', 'selectors': [['aria/登录'], ['#login']]},
            {'type': 'setViewport', 'width': 1536, 'height': 864},
            {'type': 'waitForElement', 'target': 'aria/首页',
             'selectors': [['aria/首页'], ['.home']]},
        ],
    }
    src = SRC.detect_source(payload)
    eq(src, SRC.SOURCE_DEVTOOLS, '应识别为 DevTools Recorder 来源')
    events, meta = SRC.normalize_source(payload)
    eq(len(events), 6, '事件数')
    ir = NZ.build_ir(events, meta)
    eq(kws(ir), ['goto', 'fill', 'fill', 'click', 'set_viewport', 'wait_element_located'])
    # aria/ 来源的候选必须带上"角色是猜的"标记，否则会盖过真·label 候选
    cands = ir['actions'][1]['element']['locators']
    check(any(c.get('aria_guessed') for c in cands), 'aria/ 候选应标记 role 为推测值')
    check(any(c['by'] == 'label' for c in cands), '应为 aria/ 候补一条 label 候选')
    eq(ir['meta']['start_url'], 'https://x.example/login')


@case('25 来源：Playwright codegen 脚本可被解析')
def t25():
    script = """import { test, expect } from '@playwright/test';

test('login', async ({ page }) => {
  await page.goto('https://x.example/login');
  await page.getByRole('textbox', { name: '用户名' }).click();
  await page.getByRole('textbox', { name: '用户名' }).fill('admin');
  await page.getByLabel('密码').fill('secret');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText('欢迎回来')).toBeVisible();
  await page.keyboard.press('Enter');
  helperDoSomething();
});
"""
    src = SRC.detect_source(script)
    eq(src, SRC.SOURCE_PLAYWRIGHT_SCRIPT, '应识别为 Playwright 脚本来源')
    events, meta = SRC.normalize_source(script)
    ir = NZ.build_ir(events, meta)
    got = kws(ir)
    check('goto' in got, '应解析出 goto')
    check(got.count('fill') >= 2, '应解析出至少 2 个 fill，实际 %s' % got)
    check('click' in got, '应解析出 click')
    check('press_enter' in got, '应解析出 press_enter')
    # 无法解析的行必须被保留并告警，绝不能静默丢步
    check(ir['stats']['unparsed_actions'] >= 1, '无法解析的行应被保留并计数')
    check(any('无法解析' in w for w in ir['meta']['warnings']), '应给出解析告警')


# ===========================================================================
# 跨层校验：产出的 keyword 必须真实存在于执行底座
# ===========================================================================
@case('26 跨层：所有产出的 keyword 都必须在 run_playwright.py 里真实存在')
def t26():
    import ast
    check(os.path.exists(RUN_PLAYWRIGHT), '找不到执行底座文件：%s' % RUN_PLAYWRIGHT)
    tree = ast.parse(open(RUN_PLAYWRIGHT, encoding='utf-8').read())
    real = set()
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == 'PlaywrightBaseAction':
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    real.add(sub.name)
    check(real, '未能从执行底座中解析出任何方法')

    e = tgt([sel('css', '#x', 1)], node_name='input', attrs={'name': 'search_kw'})
    ce = tgt([sel('css', '#c', 1)], node_name='input', attrs={'type': 'checkbox'})
    se = tgt([sel('css', '#s', 1)], node_name='select', attrs={'name': 'city'})
    fe = tgt([sel('css', '#f', 1)], node_name='input', attrs={'type': 'file'})
    produced = set()
    for ir in [
        build([act(1, 'navigate', url='https://x/')]),
        build([act(1, 'input', t=0, target=e, value='v')]),
        build([act(1, 'click', t=0, target=ce)]),
        build([act(1, 'change', t=0, target=se, value='bj')]),
        build([act(1, 'change', t=0, target=fe, value='p')]),
        build([act(1, 'scroll', t=0, scroll={'x': 0, 'y': 900})]),
        build([act(1, 'keydown', t=0, key='Enter')]),
        build([act(1, 'keydown', t=0, key='Escape')]),
        build([act(1, 'keydown', t=0, key='Tab')]),
        build([act(1, 'wait', t=0, target=e)]),
        build([act(1, 'set_viewport', viewport={'width': 800, 'height': 600})]),
        build([act(1, 'click', t=0, target=tgt([sel('css', '#b', 1)], node_name='div'))]),
    ]:
        # 断言推导产生的提取关键字也要一并校验
        for a in ir['actions']:
            if a['keyword']:
                produced.add(a['keyword'])
            if a.get('extract_keyword'):
                produced.add(a['extract_keyword'])

    missing = sorted(produced - real)
    check(not missing,
          '引擎产出的关键字在执行底座里不存在（执行期会 KeyError）：%s\n'
          '实际产出的关键字：%s' % (missing, sorted(produced)))


# ===========================================================================
# 真实样本端到端（DevTools Recorder 的 login 录制）
# ===========================================================================
@case('27 端到端：真实登录录制样本 ⇒ 产出可读 IR，且关键动作齐全')
def t27():
    payload = {
        'title': '登录 + 进入首页',
        'steps': [
            {'type': 'navigate', 'url': 'https://x.example/login'},
            {'type': 'setViewport', 'width': 1536, 'height': 864},
            {'type': 'change', 'value': 'admin',
             'target': 'aria/用户名',
             'selectors': [['aria/用户名'], ['input[name="username"]'], ['#app > form > div:nth-child(1) > input']]},
            {'type': 'change', 'value': 'Aa123456',
             'target': 'aria/密码',
             'selectors': [['aria/密码'], ['input[type="password"]']]},
            {'type': 'click', 'target': 'aria/记住我',
             'selectors': [['aria/记住我'], ['input[type="checkbox"]']]},
            {'type': 'click', 'target': 'aria/登录',
             'selectors': [['aria/登录'], ['button.el-button--primary']],
             'assertedEvents': [{'type': 'navigation', 'url': 'https://x.example/home'}]},
            {'type': 'waitForElement', 'target': 'aria/仪表盘',
             'selectors': [['aria/仪表盘'], ['.dashboard']]},
            {'type': 'scroll', 'x': 0, 'y': 600},
        ],
    }
    events, meta = SRC.normalize_source(payload)
    ir = NZ.build_ir(events, meta)
    st = ir['stats']

    check(st['kept_actions'] >= 7, '保留动作数应 >=7，实际 %d' % st['kept_actions'])
    check(st['elements_unique'] >= 4, '唯一元素数应 >=4，实际 %d' % st['elements_unique'])
    check(st['assertions'] >= 1, '应至少推导出 1 条断言')
    eq(sum(st['drop_reasons'].values()), st['dropped'], '统计不变量')

    got = kws(ir)
    for need in ('goto', 'fill', 'check', 'click', 'wait_element_located', 'scroll_page'):
        check(need in got, '应包含关键字 %s，实际 %s' % (need, got))

    blob = json.dumps(ir, ensure_ascii=False)
    check('Aa123456' not in blob, '密码明文泄漏进 IR')
    # 密码字段应已转变量
    pwd_actions = [a for a in ir['actions']
                   if 'password' in json.dumps(a.get('element') or {}, ensure_ascii=False)]
    check(pwd_actions, '应识别出密码字段所在动作')
    check(any((a['args'].get('value') or {}).get('kind') == 'variable' for a in pwd_actions),
          '密码字段的值应为变量')

    # IR 必须可 JSON 序列化（要存进 JSONField）
    json.dumps(ir, ensure_ascii=False)
    s = NZ.summarize(ir)
    check(s['kept_actions'] == st['kept_actions'], 'summarize 与 stats 的动作数应一致')
    check(isinstance(st['needs_review'], list), 'needs_review 应是列表（待复核动作序号）')


# ===========================================================================
# 变量提升必须带上原文（否则落库出来的用例「结构对、一跑就失败」）
# ===========================================================================
@case('28 参数化：账号字段提升为变量时必须带上录到的原文作为默认值')
def t28():
    e = tgt([sel('css', '#user', 1)], node_name='input',
            attrs={'type': 'text', 'name': 'username'})
    ir = build([act(1, 'input', t=0, target=e, value='admin')])
    v = by_kw(ir, 'fill')[0]['args']['value']
    eq(v['kind'], 'variable', '账号字段应提升为变量')
    eq(v['var_name'], 'Username', '变量名')
    # ★ 这一条是「录制即可回放」的底线：不带 value 的话落库层只能写空串
    eq(v.get('value'), 'admin', '变量必须带原文作为默认值')


@case('29 参数化：敏感字段的变量对象不得携带任何原文')
def t29():
    e = tgt([sel('css', '#pwd', 1)], node_name='input',
            attrs={'type': 'password', 'name': 'password'})
    ir = build([act(1, 'input', t=0, target=e, value='Aa123456')])
    v = by_kw(ir, 'fill')[0]['args']['value']
    eq(v['kind'], 'variable', '密码必须是变量')
    eq(v.get('redacted'), True, '必须带 redacted 标记')
    check('value' not in v or v.get('value') in (None, ''),
          '敏感字段的变量对象不允许带原文，实际 %r' % (v.get('value'),))


@case('30 参数化：同值多次出现的常量变量同样带原文')
def t30():
    e1 = tgt([sel('css', '#kw', 1)], node_name='input', attrs={'name': 'keyword'})
    e2 = tgt([sel('css', '#kw2', 1)], node_name='input', attrs={'name': 'keyword2'})
    ir = build([
        act(1, 'input', t=0, target=e1, value='订单查询'),
        act(2, 'input', t=100, target=e2, value='订单查询'),
    ])
    fills = by_kw(ir, 'fill')
    eq(len(fills), 2, '两个不同元素不应被合并')
    v = fills[0]['args']['value']
    eq(v['kind'], 'variable', '重复值应提升为常量变量')
    eq(v.get('value'), '订单查询', '常量变量同样必须带原文')


@case('31 参数化：结构化参数（uri/direction）不得被提升为变量')
def t31():
    """goto 的 uri、scroll_page 的 direction 是「做什么」而非「用什么数据」，
    被提升成 ${Constant} 只会让用例不可读，且没有任何收益。"""
    ir = NZ.build_ir([
        {'seq': 1, 'type': 'navigate', 'raw_type': 'navigate', 't': 0,
         'url': 'https://x.test/home', 'target': None, 'value': None,
         'asserted_events': []},
        {'seq': 2, 'type': 'scroll', 'raw_type': 'scroll', 't': 100,
         'target': None, 'value': None, 'scroll': {'x': 0, 'y': 600}},
    ], {'source': SRC.SOURCE_NATIVE})
    got = {}
    for a in ir['actions']:
        for k, v in (a.get('args') or {}).items():
            got[k] = v
    eq(len(ir['actions']), 2, '应产出 goto 与 scroll_page 两条动作')
    for k in ('uri', 'direction', 'distance'):
        check(k in got, '应包含参数 %s，实际 %s' % (k, list(got)))
        eq(got[k].get('kind'), 'literal', '%s 应保持字面量，实际 %r' % (k, got[k]))


# ===========================================================================
# 敏感判定必须在「信息最全」的阶段拍板
# ===========================================================================
@case('32 脱敏：没有 target、只能靠选择器认出的密码字段也必须脱敏')
def t32():
    """真实 Chrome DevTools Recorder 导出常常**不带 target**（只有 selectors），
    密码字段的唯一线索就是 `input[type="password"]`。

    这条断言是一次真实缺陷的回归守卫：早期实现把敏感判定放在参数化阶段，
    而那时手上只有 element.snapshot（**没有 selectors**），于是
    `input[type="password"]` 这条线索彻底丢失 ⇒ 密码被当成字面量写进 IR ⇒
    明文落进平台数据库。单测 27 因为样本恰好带了 `target: 'aria/密码'` 而没能暴露它。
    """
    payload = {
        'steps': [
            {'type': 'navigate', 'url': 'https://x.example/login'},
            {'type': 'change', 'value': 'admin',
             'selectors': [['aria/用户名'], ['#username'], ['input[name="username"]']]},
            # ★ 关键：没有 target，只有 selectors
            {'type': 'change', 'value': 'Aa123456',
             'selectors': [['aria/密码'], ['input[type="password"]']]},
        ],
    }
    events, meta = SRC.normalize_source(payload)
    ir = NZ.build_ir(events, meta)

    blob = json.dumps(ir, ensure_ascii=False)
    check('Aa123456' not in blob, '★ 密码明文泄漏进 IR（敏感判定丢失了选择器线索）')

    fills = [a for a in ir['actions'] if a.get('keyword') == 'fill']
    eq(len(fills), 2, '应有两个 fill')
    pwd = fills[1]
    v = pwd['args']['value']
    eq(v['kind'], 'variable', '密码必须提升为变量')
    eq(v['var_name'], 'Password', '变量名')
    eq(v.get('redacted'), True, '必须带 redacted 标记')
    eq(pwd.get('sensitive'), True, '★ 动作本身要带 sensitive 标记（审阅台据此提示）')
    # 用户名同样带原文（不是敏感字段，要能被回放）
    eq(fills[0]['args']['value'].get('value'), 'admin', '账号应保留原文作为默认值')


@case('33 敏感判定：act.sensitive 与 raw 的保留互斥（raw 绝不能带明文）')
def t33():
    payload = {
        'steps': [
            {'type': 'change', 'value': 'ghp_abcdefghijklmnopqrstuvwxyz0123456789',
             'selectors': [['#token']]},
        ],
    }
    events, meta = SRC.normalize_source(payload)
    ir = NZ.build_ir(events, meta)
    blob = json.dumps(ir, ensure_ascii=False)
    check('ghp_' not in blob, '★ token 明文泄漏进 IR')
    for a in ir['actions']:
        if a.get('sensitive'):
            eq(a.get('raw'), None, '敏感动作不得保留 raw')


@case('34 映射：`select#id` 这类「标签+id」写法也必须识别为 select')
def t34():
    """原正则的后边界字符集漏了 `#`，`select#region` 匹配不上 ⇒ change 被降级成
    fill ⇒ 回放时往 <select> 里填值，必然失败。这是从真实录制样本里暴露出来的。"""
    for selector, want in (
        ('select#region', 'select_option'),
        ('select.city', 'select_option'),
        ('select[multiple]', 'select_option'),
        ('div.form > select', 'select_option'),
        ('select#province option', 'select_option'),
    ):
        e = tgt([sel('css', selector, 1)], node_name=None)
        ir = build([act(1, 'change', t=0, target=e, value='北京')])
        eq(len(ir['actions']), 1, '%s 应产出 1 条动作' % selector)
        eq(ir['actions'][0]['keyword'], want, '%s 应映射为 %s' % (selector, want))


@case('35 映射：名字含 select 的普通输入框不得被误判为 select')
def t35():
    for selector in ('#select-region', '.el-select__wrapper', 'input[name="select_x"]',
                     'input.selected-item'):
        e = tgt([sel('css', selector, 1)], node_name='input')
        ir = build([act(1, 'change', t=0, target=e, value='北京')])
        eq(ir['actions'][0]['keyword'], 'fill',
           '%s 是普通输入框，应映射为 fill 而不是 select_option' % selector)


@case('36 参数化：账号线索只在选择器里时也必须提升为 Username')
def t36():
    """与测试 32 同源：判定线索的清单必须只有一份。
    早期 `_is_sensitive` 看选择器、参数化启发式只看 attrs/aria_label，
    于是 DevTools 导出（没有 target）的账号被写死成字面量 ——
    换账号回放必须手工改用例，「用例变量」的意义全丢了。"""
    payload = {'steps': [
        {'type': 'navigate', 'url': 'https://x.example/login'},
        {'type': 'change', 'value': 'admin',
         'selectors': [['aria/用户名'], ['#username'], ['input[name="username"]']]},
    ]}
    events, meta = SRC.normalize_source(payload)
    ir = NZ.build_ir(events, meta)
    fills = [a for a in ir['actions'] if a.get('keyword') == 'fill']
    eq(len(fills), 1, '应有 1 个 fill')
    v = fills[0]['args']['value']
    eq(v['kind'], 'variable', '账号应提升为变量')
    eq(v['var_name'], 'Username', '变量名')
    eq(v.get('value'), 'admin', '仍要带原文作为默认值')


@case('37 参数化：毫无线索的普通输入框保持字面量（不要乱提升）')
def t37():
    payload = {'steps': [
        {'type': 'change', 'value': '备注内容',
         'selectors': [['#remark-field']]},
    ]}
    events, meta = SRC.normalize_source(payload)
    ir = NZ.build_ir(events, meta)
    v = ir['actions'][0]['args']['value']
    eq(v['kind'], 'literal', '普通字段不应被提升')
    eq(v.get('value'), '备注内容')


@case('38 native 来源：字符串 selectors 必须能归一化（曾经整条链路崩溃）')
def t38():
    """回归：扩展上报的 selectors 是**字符串数组**（content.js 的 describe()）。

    下游 normalizer/_is_extension_self 与 locator_score/dedupe_candidates
    都按 dict 取值（cand.get('value') / cand.get('by')），字符串会在
    **过滤阶段**抛 `'str' object has no attribute 'get'` —— 表现为
    finish 返 400「归一化失败：'str' object has no attribute 'get'」，
    且报错信息与"选择器格式"毫无关联。修法是在 sources 层收敛。
    """
    payload = [
        {'seq': 1, 'kind': 'navigate', 'url': 'http://x.example/login'},
        {'seq': 2, 'kind': 'input', 'value': 'admin',
         'target': {'node_name': 'input', 'attrs': {'name': 'username'},
                    'selectors': ['#username', '[name="username"]', 'div > input']}},
        {'seq': 3, 'kind': 'click',
         'target': {'node_name': 'button', 'text': '登录',
                    'selectors': ['.login-btn', 'xpath=//button[1]']}},
    ]
    events, meta = SRC.normalize_source(payload, 'native')
    ir = NZ.build_ir(events, meta)
    eq(len(ir['actions']), 3, '三个动作都应保留（不得整条链路崩掉）')
    locs = ir['actions'][1]['element']['locators']
    bys = [c['by'] for c in locs]
    eq('id' in bys, True, '`#username` 应收敛成 by=id 的候选，实际 %s' % bys)
    idc = [c for c in locs if c['by'] == 'id'][0]
    eq(idc['value'], 'username', 'id 候选的 value 不能带 # ')
    eq('xpath' in [c['by'] for c in ir['actions'][2]['element']['locators']], True,
       '`xpath=...` 应收敛成 by=xpath')


@case('39 native 来源：单条裸事件不能被静默丢光')
def t39():
    """回归：NDJSON 只传 1 条时，from_native 会落到 `actions=[]` 分支。

    那会让视图返 200 + received:0 —— 看起来"成功了"，实际一个事件都没入库，
    用户看到的却是「已生成 IR：步骤 0 条」。带 kind/type 的裸 dict 必须当单条事件。
    """
    events, meta = SRC.normalize_source(
        {'seq': 1, 'kind': 'navigate', 'url': 'http://x.example/a'}, 'native')
    eq(len(events), 1, '单条裸事件应被识别为 1 条')
    ir = NZ.build_ir(events, meta)
    eq(len(ir['actions']), 1, '应产出 1 个 goto 动作')
    eq(ir['actions'][0]['keyword'], 'goto')


@case('40 native 来源：字符串选择器的分类规则')
def t40():
    eq(SRC._canon_one_selector('#user-name')['by'], 'id', '纯 id 选择器')
    eq(SRC._canon_one_selector('xpath=//div[2]')['by'], 'xpath', 'xpath= 前缀')
    eq(SRC._canon_one_selector('//div[2]')['by'], 'xpath', '裸 // 前缀')
    eq(SRC._canon_one_selector('text=登录')['value'], '登录', 'text= 前缀')
    eq(SRC._canon_one_selector('div > input')['by'], 'css', '普通 css 路径')
    eq(SRC._canon_one_selector('#a.b')['by'], 'css', '复合选择器不能当 id')
    eq(SRC._canon_one_selector({'by': 'role', 'value': 'button',
                                'opts': {'name': '登录'}})['opts'],
       {'name': '登录'}, 'dict 候选原样保留 opts')


@case('41 native 来源：kind:select 必须映射为 select_option（曾有整步静默丢弃）')
def t41():
    """回归：浏览器扩展对 <select> 的变更发的是 `kind:'select'`。

    而 `sources.from_native` 里 **kind 优先于 type** ⇒ etype 成了 'select'，
    但 map_to_actions 只认 ('change','input') ⇒ 掉进末尾的
    「不支持的事件类型：select」被**静默丢弃**（下拉框选择整步消失），
    尽管平台早有 select_option 关键字。

    甘肃 242 站点用的是 easyui 自定义下拉（非原生 select），
    所以真机验收 16/16 也覆盖不到这条路径 —— 必须由本用例兜住。
    """
    payload = {'events': [
        {'seq': 1, 'kind': 'navigate', 'url': 'http://x.example/form'},
        {'seq': 2, 'kind': 'select', 't': 100, 'url': 'http://x.example/form',
         'value': 'bj',
         'target': {'node_name': 'select', 'attrs': {'name': 'city'},
                    'selectors': [{'by': 'css', 'value': 'select#city'}]}},
    ]}
    events, meta = SRC.normalize_source(payload, 'native')
    eq(events[1]['type'], 'select', 'kind 应优先于 type，etype 应为 select')

    _kept, dropc, _merged = NZ.filter_noise(events)
    eq('不支持的事件类型：select' in dict(dropc), False,
       'select 不应再被 filter_noise 当作不支持类型丢弃，实际丢弃项 %r' % dict(dropc))

    ir = NZ.build_ir(events, meta)
    eq(kws(ir), ['goto', 'select_option'],
       'select 变更必须产出 select_option，实际 %r' % kws(ir))
    eq(by_kw(ir, 'select_option')[0]['args']['value']['value'], 'bj',
       'select_option 的取值应取事件里的 value')


@case('42 native 来源：select 的显式声明优先于 DOM 反推（缺 node_name 也不能退化成 fill）')
def t42():
    """反证：Chrome DevTools Recorder 导出的数据**不带 DOM 属性**。

    若实现改成「靠 _input_kind 从选择器反推 select」，缺 node_name 时就会
    退化成 fill（对下拉框执行填值必然失败，且失败点远在回放期）。
    所以 etype == 'select' 必须**直接**决定关键字，不走反推。
    """
    payload = {'events': [
        {'seq': 1, 'kind': 'select', 't': 100, 'url': 'http://x.example/form',
         'value': 'opt-1',
         'target': {'selectors': [{'by': 'css', 'value': '#city'}]}},
    ]}
    events, meta = SRC.normalize_source(payload, 'native')
    ir = NZ.build_ir(events, meta)
    eq(kws(ir), ['select_option'],
       '缺 node_name 时仍应为 select_option 而不是 fill，实际 %r' % kws(ir))


@case('43 native 来源：同一 select 的连续变更应合并为一步（不拆成多步）')
def t43():
    payload = {'events': [
        {'seq': 1, 'kind': 'select', 't': 0, 'url': 'u', 'value': 'a',
         'target': {'node_name': 'select', 'attrs': {'name': 'city'},
                    'selectors': [{'by': 'css', 'value': 'select#city'}]}},
        {'seq': 2, 'kind': 'select', 't': 200, 'url': 'u', 'value': 'bj',
         'target': {'node_name': 'select', 'attrs': {'name': 'city'},
                    'selectors': [{'by': 'css', 'value': 'select#city'}]}},
    ]}
    events, meta = SRC.normalize_source(payload, 'native')
    ir = NZ.build_ir(events, meta)
    eq(kws(ir), ['select_option'], '200ms 内的两次选择应合并为 1 步，实际 %r' % kws(ir))
    eq(by_kw(ir, 'select_option')[0]['args']['value']['value'], 'bj',
       '合并后应保留最后一次选择的值')


# ---------------------------------------------------------------------------
# 运行
# ---------------------------------------------------------------------------
def main():
    lines = []
    passed = failed = 0
    for name, fn in _RESULTS:
        try:
            fn()
            passed += 1
            lines.append('  PASS  %s' % name)
        except Exception as e:
            failed += 1
            lines.append('  FAIL  %s' % name)
            lines.append('        %s' % e)
            tb = traceback.format_exc().strip().split('\n')
            for ln in tb[-4:]:
                lines.append('        | ' + ln)

    header = [
        '=' * 78,
        'P0-③ 归一化引擎单测',
        '=' * 78,
        '用例数: %d   通过: %d   失败: %d' % (len(_RESULTS), passed, failed),
        '',
    ]
    out = header + lines + [
        '',
        '=' * 78,
        'P0_3_RESULT = %s' % ('FAIL' if failed else 'PASS'),
        '=' * 78,
    ]
    text = '\n'.join(out)
    print(text)

    try:
        with open(os.path.join(_BACKEND, '..', '_p0_3_verify.txt'), 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception:
        pass
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
