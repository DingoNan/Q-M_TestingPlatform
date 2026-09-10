"""
异步任务 - AI自动生成元素（元素库）
- ai_generate_elements_task: 访问模块页面，Playwright 抓取交互元素，
  AI 生成业务命名 + Playwright 定位表达式，按三态(status)去重落库，并发送站内信。
"""
import json as _json
import logging
import re
from django.utils import timezone
from playwright.sync_api import sync_playwright

from apps.elements.models import Element
from apps.envs.models import EnvPlant, Cookies, Module
from apps.messages.models import Message
from apps.projects.models import Project
from apps.users.models import User

logger = logging.getLogger('elements')

# 候选/既有列表分块大小，控制单次 LLM 请求体量
_BATCH = 40

# 允许落库的 Web 定位方式（与 Element.ByChoice / run_playwright._build_locator 一致）
_ALLOWED_BY = {'role', 'label', 'placeholder', 'text', 'alt text', 'css', 'xpath', 'id'}

# Playwright 抓取候选元素的 JS 脚本。
# 第一轮抓原生元素 / 显式 ARIA role；第二轮补抓"可点击外观"的自定义元素——Vue/Element 等框架常把
# 交互控件渲染成没有 ARIA role 的 div/span（如 <div class="send-code-btn">获取验证码</div>、
# <div class="forgetPwd"><span>密码登录</span></div>），旧脚本只按原生标签选择器抓，这些全漏掉了。
# 自定义元素带 attrs.native_role=false 标记，下游据此避免生成 by=role（无真实 ARIA role 时，
# Playwright 的 role 定位会匹配不到，必须改用 text/css/xpath）。
# 每个候选还带 click 字段（可点击定位用 CSS 选择器），供"点击展开动态内容"时重新定位该元素。
_CANDIDATE_JS = """() => {
    const clean = (s, n) => { s = (s || '').trim(); if (s.length > n) s = s.slice(0, n); return s; };
    const attrs = el => {
      const a = {};
      ['id','name','class','placeholder','aria-label','title','alt','disabled','aria-disabled'].forEach(k => {
        const v = el.getAttribute ? el.getAttribute(k) : null;
        if (v && v.trim()) a[k] = v.trim();
      });
      const lb = el.labels && el.labels[0] ? clean(el.labels[0].textContent, 80) : '';
      if (lb) a['label'] = lb;
      return a;
    };
    const tagname = el => (el.tagName || '').toLowerCase();
    // 可点击定位用 CSS 选择器：优先 id，其次 tag+class（含 data-v- 等作用域类，定位最精确）
    const cssSel = el => {
      if (el.id) return '#' + CSS.escape(el.id);
      const cls = (el.className && el.className.toString().trim()) || '';
      if (cls) return tagname(el) + '.' + cls.split(/\\s+/).filter(Boolean).map(c => CSS.escape(c)).join('.');
      return '';
    };
    const visible = el => {
      const cs = getComputedStyle(el);
      if (cs.display === 'none' || cs.visibility === 'hidden') return false;
      const t = tagname(el);
      // 原生交互控件：即使视觉隐藏（Element Plus 等框架把 checkbox/radio 的 input 设为
      // width:0/height:0/opacity:0），依然真实可交互、可定位，必须抓取。
      if (t === 'input' || t === 'textarea' || t === 'select' || t === 'button' || t === 'a') return true;
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    };
    const results = [];
    const seen = new Set();
    const push = (el, role, kind, native) => {
      if (!el || !visible(el)) return;
      if (results.length >= 400) return;
      let a = attrs(el);
      a.role = role;
      // checkbox/radio 的 input 常被框架视觉隐藏（Element Plus 等设为 width:0/height:0/opacity:0），
      // 此时 Playwright 的 get_by_role 匹配不到隐藏 input，必须禁用 role 定位 → native_role=false；
      // 且隐藏 input 自身不可点击，定位基准必须换成最近可见的包裹容器
      // （label.el-checkbox / span.el-checkbox / span.el-checkbox__input 等），其 class/文本才可定位可点击。
      let hiddenCtrl = false;
      if (role === 'checkbox' || role === 'radio') {
        const cs = getComputedStyle(el);
        const r = el.getBoundingClientRect();
        if (r.width === 0 || r.height === 0 || parseFloat(cs.opacity || '1') === 0) {
          native = false;
          hiddenCtrl = true;
        }
      }
      a.native_role = native;   // 是否有真实 ARIA role / 原生语义（决定能否用 role 定位）
      let text = clean(el.textContent, 80);
      if (hiddenCtrl) {
        // 向上找最近可见的包裹容器作为新定位基准；原始 input 的 el-id-xxx 是 Element Plus
        // 每次渲染随机生成的 id，跨会话不稳定，绝不能用于定位。
        let wrap = el.parentElement;
        while (wrap && wrap !== document.body) {
          const wcs = getComputedStyle(wrap);
          const wr = wrap.getBoundingClientRect();
          if (wr.width > 0 && wr.height > 0 && wcs.display !== 'none' && wcs.visibility !== 'hidden') {
            el = wrap;
            a = attrs(wrap);
            a.role = role;
            a.native_role = false;
            text = clean(wrap.textContent, 80);
            break;
          }
          wrap = wrap.parentElement;
        }
      } else if ((role === 'checkbox' || role === 'radio') && !a['label'] && !a['aria-label'] && !text) {
        // 原生可见 checkbox/radio 无文本：向上取包裹 label/span 文本
        let p = el.parentElement;
        for (let i = 0; p && i < 2; p = p.parentElement, i++) {
          const t2 = clean(p.textContent, 80);
          if (t2) { a['label'] = t2; break; }
        }
      }
      const idSig = el.id ? '#' + el.id : '';
      if (idSig) { if (seen.has(idSig)) return; seen.add(idSig); }
      results.push({ tag: tagname(el), role, kind, text, attrs: a, click: cssSel(el) });
    };
    // ---- 第一轮：原生元素 + 显式 ARIA role ----
    document.querySelectorAll('button, input, textarea, select, a, [role]').forEach(el => {
      const tag = tagname(el);
      const ariaRole = el.getAttribute ? el.getAttribute('role') : null;
      const native = tag === 'button' || tag === 'a' || tag === 'textarea' || tag === 'select' ||
                     tag === 'input' || !!ariaRole;
      if (tag === 'button' || ariaRole === 'button') push(el, 'button', 'button', native);
      else if (tag === 'a' && el.getAttribute('href')) push(el, 'link', 'link', native);
      else if (tag === 'textarea') push(el, 'textbox', 'text', native);
      else if (tag === 'select') push(el, 'combobox', 'select', native);
      else if (tag === 'input') {
        const t = (el.getAttribute('type') || 'text').toLowerCase();
        if (t === 'checkbox') { push(el, 'checkbox', 'check', native); return; }
        if (t === 'radio') { push(el, 'radio', 'radio', native); return; }
        if (['text','search','email','password','tel','number','url'].includes(t)) { push(el, 'textbox', 'text', native); }
      }
    });
    // ---- 第二轮：自定义可点击元素（无 role 的 div/span/li 等）----
    const CLICK_RE = /(?:btn|button|send|code|tab|switch|check|radio|dropdown|select|menu|nav|link|login|logout|submit|cancel|confirm|close|search|forget|forgot|reg|register|more|icon|item)/i;
    const strongClick = el => !!(
      el.getAttribute('onclick') || el.getAttribute('ng-click') || el.getAttribute('@click') ||
      el.hasAttribute('disabled') || el.hasAttribute('aria-disabled') ||
      getComputedStyle(el).cursor === 'pointer');
    // 祖先是否"强可点击"(有点击事件/disabled/cursor:pointer)。
    // 注意不能拿祖先 class 参与判断：登录页常把 <div class="forgetPwd">密码登录</div> 包在
    // .login-form/.login-container 里，若 class 也判"可点击"，这类元素会被误跳过而漏抓。
    // 同文本的父子重复由结尾 keyOf 去重兜底，无需在此用 class 过度过滤。
    const clickLikeAncestor = el => {
      let p = el.parentElement;
      while (p && p !== document.body) {
        if (strongClick(p)) return true;
        p = p.parentElement;
      }
      return false;
    };
    document.querySelectorAll('div, span, li, i, em, b, a').forEach(el => {
      if (results.length >= 400) return;
      const text = clean(el.textContent, 80);
      if (!text) return;                                        // 无文本的装饰元素忽略
      if (el.getAttribute('href') || el.getAttribute('role')) return;  // 第一轮已处理
      if (el.closest('button, a[href], input, textarea, select, [role]')) return;  // 原生交互元素内部
      const cls = (el.className && el.className.toString()) || '';
      if (!strongClick(el) && !CLICK_RE.test(cls)) return;
      if (clickLikeAncestor(el)) return;                        // 祖先已是可点击元素，避免整组重复
      if (el.querySelector('button, a, input, textarea, select, [role]')) {  // 包裹容器仅靠 class 命中则跳过
        if (!strongClick(el)) return;
      }
      const linkish = tagname(el) === 'a' || /(?:link|url|more|详情|查看|跳转)/i.test(cls);
      push(el, linkish ? 'link' : 'button', linkish ? 'link' : 'button', false);
    });
    const keyOf = c => (c.role || '') + '|' + (c.attrs['aria-label'] || c.attrs['placeholder'] || c.attrs['label'] || c.text || '') + '|' + (c.tag || '');
    const seenKey = new Set();
    return results.filter(c => {
      const k = keyOf(c);
      if (seenKey.has(k)) return false; seenKey.add(k); return true;
    });
}"""


# ===== 点击展开（激进模式）相关常量与工具 =====
_MAX_DEPTH = 3        # 点击展开的最大层级
_MAX_CLICKS = 100     # 单次抓取的点击预算，防止无限展开
_MAX_TOTAL = 600      # 合并后的候选总数上限（下游按 40/批送 LLM 命名）
_CLICKABLE_KINDS = {'button', 'link', 'check', 'radio'}

# 高副作用/破坏性操作黑名单：即使激进模式也避免点击（防止退出登录/提交表单/删除数据/支付等）。
# 用词边界匹配，避免误伤如"密码登录"（含"登录"子串）这类安全的页内切换元素。
_CLICK_BLACKLIST_RE = re.compile(
    r'(^|\s)(退出|注销|登出|登录|注册|删除|移除|提交|下单|支付|付款|结算|购买|'
    r'确认|确定|保存|取消|关闭|下载|上传|清空|重置|导入|导出)(\s|$)|'
    r'(logout|signin|signout|login|register|delete|remove|submit|checkout|pay|save|cancel|close|'
    r'upload|download|reset|import|export)',
    re.IGNORECASE)


def _cand_key(c):
    """候选元素去重键，与 _CANDIDATE_JS 内 keyOf 保持一致"""
    attrs = c.get('attrs') or {}
    return (c.get('role') or '',
            attrs.get('aria-label') or attrs.get('placeholder') or attrs.get('label') or (c.get('text') or ''),
            c.get('tag') or '')


def _clickable(c):
    """是否值得点击展开：按钮/链接/勾选/单选/Tab 等交互控件（排除输入框与原生下拉）"""
    if c.get('kind') in _CLICKABLE_KINDS:
        return True
    return c.get('role') in ('button', 'link', 'checkbox', 'radio', 'tab', 'menuitem', 'option')


def _click_blacklisted(c):
    """命中高副作用黑名单则跳过点击"""
    text = (c.get('text') or '')
    cls = (c.get('attrs') or {}).get('class') or ''
    return bool(_CLICK_BLACKLIST_RE.search(text) or _CLICK_BLACKLIST_RE.search(cls))


# ===== LLM 提示词 =====
_SYSTEM_NAMING = (
    '你是资深 Web UI 自动化测试元素命名专家。给定网页交互元素的结构化信息，为每个元素输出：'
    '业务含义明确的中文名 name（≤20字，如"登录按钮/用户名输入框"）、以及 Playwright 定位表达式 by/value/opts。'
    'by 只能是 role/label/placeholder/text/alt text/css/xpath/id 之一。'
    '若输入 attrs.native_role=false，说明是无真实 ARIA role 的自定义控件(div/span，如 class=send-code-btn/forgetPwd，'
    '或视觉隐藏的 checkbox/radio input)，禁止使用 by=role，应改用 by=label(取包裹标签文本)/by=text(取可见文本)/css/xpath。'
    '规则：by=role 时 value=角色(button/link/textbox/combobox/checkbox/radio 等)，opts={"name":"可见文本或aria-label或label","exact":false}；'
    'by=label 时 value=label 文本，opts={"exact":false}；by=placeholder 时 value=placeholder，opts={"exact":false}；'
    'by=text 时 value=可见文本，opts={"exact":false}；by=alt text 时 value=alt 属性；by=id 时 value=id；by=css/xpath 时 value=合法表达式。'
    'opts 可省略或为空对象。必须以输入元素的实际字段为准，不能编造不存在的属性值。'
    '输出 {"results":[{"index":..,"name":"..","by":"..","value":"..","opts":{}}]}，顺序与数量与输入一致。')

_SYSTEM_DEDUP = (
    '你是 Web UI 自动化测试元素维护专家。给定【本次页面发现的候选元素】和【元素库既有元素】，'
    '判断每个候选是否与某个既有元素描述的是同一个业务控件（业务语义一致：可见文本/placeholder/label/aria-label 指向同一业务用途），'
    '用于决定更新(existing)还是新增(create)。规则：action=update 时必须给出匹配的既有下标 ei；action=create 表示无既有可匹配。'
    '每个既有元素最多只能匹配一个候选；候选与输入两者处理顺序一致。'
    '输入 {"candidates":[{"ci":..,"name":"..","by":"..","value":".."}],"existing":[{"ei":..,"name":".."}]}'
    '输出 {"decisions":[{"ci":..,"action":"update|create","ei":..}]}，candidates 一一对应。')


def _heuristic_locator(c):
    """启发式定位兜底：按 Playwright 推荐优先级生成 {by, value, opts}"""
    attrs = c.get('attrs', {})
    role = c.get('role')
    native_role = attrs.get('native_role', True)   # 无真实 ARIA role 的自定义控件(div/span)不能用 role 定位
    text = c.get('text') or ''
    aria = attrs.get('aria-label')
    label = attrs.get('label')
    placeholder = attrs.get('placeholder')
    alt = attrs.get('alt')
    eid = attrs.get('id')
    nm = attrs.get('name')
    if native_role and role and (aria or label or text):
        return {'by': 'role', 'value': role, 'opts': {'name': aria or label or text, 'exact': False}}
    if placeholder:
        return {'by': 'placeholder', 'value': placeholder, 'opts': {'exact': False}}
    if label:
        return {'by': 'label', 'value': label, 'opts': {'exact': False}}
    # 自定义控件没有真实 role，按可见文本定位最可靠（如 <div class="send-code-btn">获取验证码</div>）
    if text and ((native_role and role in ('button', 'link')) or not native_role):
        return {'by': 'text', 'value': text, 'opts': {'exact': False}}
    if alt:
        return {'by': 'alt text', 'value': alt, 'opts': {}}
    # 视觉隐藏的 checkbox/radio（或框架随机 id）：el-id-* 是 Element Plus 每次渲染随机生成的 id，
    # 跨会话不稳定，不能用于定位，跳过改走 class/css 兜底（定位基准已在抓取时换成可见包裹容器）。
    if eid and not str(eid).startswith('el-id-'):
        return {'by': 'id', 'value': eid, 'opts': {}}
    if nm:
        return {'by': 'css', 'value': f'[name="{nm}"]', 'opts': {}}
    # 视觉隐藏控件无文本/label/id 时，用包裹容器 class 生成 css（容器可见、可点击、class 稳定）
    cls = attrs.get('class') or ''
    if cls and not native_role:
        tag = c.get('tag') or ''
        sel = (tag + '.' + '.'.join(cls.split())) if tag else '.' + '.'.join(cls.split())
        return {'by': 'css', 'value': sel, 'opts': {}}
    return None


def _fallback_name(c):
    attrs = c.get('attrs', {})
    return (attrs.get('aria-label') or attrs.get('placeholder') or attrs.get('label')
            or (c.get('text') or '')[:10] or f"元素({c.get('role', '')})")


def _apply_cookies(context, page, cookies_qs):
    """注入环境 Cookie/Session/LocalStorage 登录态，复用 run_playwright.__deal_cookies 逻辑"""
    for ck in cookies_qs:
        value = ck.value
        if ck.type == Cookies.CookieType.Cookie:
            if isinstance(value, list):
                context.add_cookies(value)
            elif isinstance(value, dict):
                context.add_cookies([value])
        elif ck.type == Cookies.CookieType.Session:
            if isinstance(value, dict):
                for k, v in value.items():
                    page.evaluate(f"sessionStorage.setItem({k!r}, {json_dumps(v)});")
        else:  # LocalStorage
            if isinstance(value, dict):
                for k, v in value.items():
                    page.evaluate(f"localStorage.setItem({k!r}, {json_dumps(v)});")


def json_dumps(value):
    return _json.dumps(value, ensure_ascii=False)


def _scrape_candidates(url, need_login, module, env_id=None):
    """访问页面并抓取候选元素列表。

    激进模式：除初始扫描外，还会逐个点击可点击元素展开动态内容
    （下拉/Tab/弹窗/更多等点击后才出现的元素），每层重新扫描并把新出现的
    元素合并进结果；受深度 _MAX_DEPTH 与点击预算 _MAX_CLICKS 约束。
    自动关闭浏览器原生弹窗、自动关闭新标签页；检测到页面跳转/路由变化时
    先扫描新页面内容再回退原页继续，保证不会越点越远。
    """
    logger.info(f"[AI元素任务] 模块「{module.name}」启动 Playwright（url={url}）")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        try:
            context = browser.new_context(viewport={'width': 1366, 'height': 900})
            page = context.new_page()
            page.set_default_timeout(30000)
            page.goto(url, wait_until='domcontentloaded')
            page.wait_for_timeout(1200)
            need_apply = False
            if need_login:
                _cookies_qs = Cookies.objects.filter(
                    plant_id=module.plant_id, project_id=module.project_id, is_delete=False)
                if env_id:
                    _cookies_qs = _cookies_qs.filter(env_id=env_id)
                cookies_qs = _cookies_qs.all()
                if cookies_qs:
                    _apply_cookies(context, page, cookies_qs)
                    need_apply = True
            if need_apply:
                page.goto(url, wait_until='domcontentloaded')
                page.wait_for_timeout(1000)

            # 浏览器原生弹窗一律自动关闭，避免点击过程被阻塞
            page.on('dialog', lambda d: d.dismiss())
            # 点击展开可能弹出新标签页，自动关闭，保持单页扫描
            def _close_extra_pages(_pg):
                for pg in list(context.pages):
                    if pg is not page:
                        try:
                            pg.close()
                        except Exception:
                            pass
            context.on('page', _close_extra_pages)

            merged = {}      # 去重键 -> 候选
            clicked = set()  # 已点击过（含跳过）的去重键
            budget = {'n': 0}

            def _merge(cands):
                for c in cands or []:
                    k = _cand_key(c)
                    if k not in merged and len(merged) < _MAX_TOTAL:
                        merged[k] = c

            def _expand(level):
                if level > _MAX_DEPTH:
                    return
                cands = page.evaluate(_CANDIDATE_JS) or []
                _merge(cands)
                for c in cands:
                    if budget['n'] >= _MAX_CLICKS or len(merged) >= _MAX_TOTAL:
                        return
                    k = _cand_key(c)
                    if k in clicked:
                        continue
                    clicked.add(k)
                    if not _clickable(c) or _click_blacklisted(c):
                        continue
                    sel = (c.get('click') or '').strip()
                    try:
                        if sel:
                            loc = page.locator(sel).first
                        else:
                            text = (c.get('text') or '').strip()
                            if not text:
                                continue
                            loc = page.get_by_text(text, exact=False).first
                        before = page.url.split('#')[0]
                        budget['n'] += 1
                        if budget['n'] == 1 or budget['n'] % 20 == 0:
                            logger.info(f"[AI元素任务] 模块「{module.name}」点击展开中 {budget['n']}/{_MAX_CLICKS}（候选 {len(merged)}）")
                        loc.click(timeout=1500, force=True)
                        page.wait_for_timeout(400)
                        after = page.url.split('#')[0]
                        if after != before:
                            # 发生跳转/路由变化：扫完新页面内容后回退原页继续
                            _expand(level + 1)
                            try:
                                page.go_back(timeout=5000)
                            except Exception:
                                try:
                                    page.goto(url, wait_until='domcontentloaded')
                                except Exception:
                                    pass
                            page.wait_for_timeout(400)
                        else:
                            # 页内展开（下拉/Tab/弹窗等）：就地深入
                            _expand(level + 1)
                    except Exception:
                        pass

            logger.info(f"[AI元素任务] 开始抓取候选元素 模块「{module.name}」url={url}")
            _expand(1)
            logger.info(f"[AI元素任务] 模块「{module.name}」抓取完成，共 {len(merged)} 个候选")
            return list(merged.values())
        finally:
            try:
                browser.close()
            except Exception:
                pass


def ai_generate_elements_task(task_id: str, project_id: int, module_ids, env_id: int,
                              ai_config_id: int, need_login: bool,
                              user_id: int, message_id: int = None,
                              vector_threshold: float = 0.6,
                              page_path: str = None):
    """
    异步任务：AI 自动生成元素（支持单模块或平台下全部模块）
    1. 逐模块：解析 host → 登录态注入 → Playwright 抓取候选元素
    2. AI 生成 业务命名 + 定位表达式
    3. 按业务语义与既有元素去重，三态落库（覆盖/新增/待废弃）
    4. 更新站内信任务状态
    """
    logger.info(f"[AI元素任务 {task_id}] 开始 - project={project_id}, modules={module_ids}, env={env_id}")
    start = timezone.now()
    user = User.objects.filter(id=user_id).first()

    stats = {
        'added_published': 0, 'added_tomodify': 0, 'updated': 0,
        'deprecated': 0, 'skipped': 0, 'failed': 0,
        'names': [],
    }
    error = None

    try:
        project = Project.objects.filter(id=project_id).first()
        if not project:
            raise ValueError('项目不存在')
        for mid in module_ids or []:
            module = Module.objects.filter(id=int(mid), is_delete=False).first()
            if not module:
                stats['failed'] += 1
                stats['names'].append(f"模块#{mid}(不存在)")
                continue
            logger.info(f"[AI元素任务 {task_id}] 开始处理模块「{module.name}」({module_ids.index(mid) + 1}/{len(module_ids)})")
            try:
                _process_module(task_id, module, project, env_id, ai_config_id,
                                need_login, user, stats, vector_threshold,
                                page_path=(page_path if len(module_ids or []) == 1 else None))
            except Exception as e:
                stats['failed'] += 1
                stats['names'].append(f"{module.name}(失败)")
                logger.error(f"[AI元素任务 {task_id}] 模块「{module.name}」处理失败: {e}", exc_info=True)
    except Exception as e:
        error = str(e)
        logger.error(f"[AI元素任务 {task_id}] 失败: {e}", exc_info=True)
    finally:
        _update_message(task_id, project_id, message_id, user, stats, error,
                        duration=(timezone.now() - start).total_seconds())


def _process_module(task_id, module, project, env_id, ai_config_id, need_login, user, stats,
                    vector_threshold=0.6, page_path=None):
    """单模块处理：抓取→命名→去重→三态落库"""
    # 1. host 与 URL（单模块使用前端传入的页面地址；根节点/多模块使用模块自带页面地址，无则跳过）
    env_plant = EnvPlant.objects.filter(env_id=env_id, plant=module.plant,
                                        is_delete=False, host__isnull=False).exclude(host='').first()
    if not env_plant or not env_plant.host:
        raise ValueError(f'平台「{module.plant.name if module.plant else module.plant_id}」未配置该环境的 WEB 域名')
    if page_path is not None:
        if not page_path.strip():
            raise ValueError('页面地址不能为空')
        path = page_path.strip()
    else:
        if not module.url:
            stats['skipped'] += 1
            stats['names'].append(f"{module.name}(无页面地址，已跳过)")
            return
        path = module.url
    url = env_plant.host.rstrip('/') + path

    # 2. 抓取
    candidates = _scrape_candidates(url, need_login, module, env_id)
    if not candidates:
        stats['names'].append(f"{module.name}(无可识别元素)")
        return
    logger.info(f"[AI元素任务 {task_id}] 模块「{module.name}」抓取到 {len(candidates)} 个候选元素")

    # 3. 命名 + 定位
    named = []
    _batches = (len(candidates) + _BATCH - 1) // _BATCH
    logger.info(f"[AI元素任务 {task_id}] 模块「{module.name}」开始 LLM 命名（{len(candidates)} 个候选，分 {_batches} 批）")
    for ci in range(0, len(candidates), _BATCH):
        batch = candidates[ci:ci + _BATCH]
        named.extend(_name_batch(ai_config_id, batch))
    logger.info(f"[AI元素任务 {task_id}] 模块「{module.name}」LLM 命名完成，有效定位 {sum(1 for n in named if n.get('loc'))}/{len(named)}")

    # 4. 去重：确定性匹配(by+value/名称) + LLM 语义兜底 → 决定覆盖/新增/待废弃
    existing = list(Element.objects.filter(project_id=project.id, module_id=module.id,
                                           is_delete=False).all())
    existing_by_id = {e.id: e for e in existing}
    existing_list = [{'ei': e.id, 'name': e.name} for e in existing]
    decision_by_ci = _resolve_decisions(ai_config_id, named, existing_list, existing_by_id,
                                        vector_threshold=vector_threshold,
                                        module_id=module.id, project_id=project.id)

    # 5. 三态落库（覆盖/新增/待废弃）
    matched_ids = set()
    created_ids = set()
    for ci, it in enumerate(named):
        loc_obj = it.get('loc')  # {'by','value','opts'} 或 None（定位失败）
        name = (it.get('name') or '')[:50]
        decision = decision_by_ci.get(ci, {})
        action = decision.get('action', 'create')
        ei = decision.get('ei')
        target = existing_by_id.get(ei) if action == 'update' and ei else None

        if target is not None:
            matched_ids.add(target.id)
            ok = bool(loc_obj)
            if ok:
                target.name = name
                target.web = loc_obj
                target.status = Element.ElementStatus.PUBLISHED
                stats['updated'] += 1
            else:
                target.status = Element.ElementStatus.TO_MODIFY
                stats['failed'] += 1
            target.update_by = user
            target.save(update_fields=['name', 'web', 'status', 'update_by', 'update_time'])
            stats['names'].append(f"{target.name}({'更新' if ok else '待修改'})")
        else:
            if not loc_obj:
                stats['added_tomodify'] += 1
                stats['names'].append(f"{name}(待修改)")
            else:
                stats['added_published'] += 1
                stats['names'].append(f"{name}(新增)")
            try:
                new_el = Element.objects.create(
                    project_id=project.id, module_id=module.id,
                    name=name or _fallback_name(candidates[ci]),
                    type='web',
                    web=loc_obj or {},
                    ios=[], android=[],
                    status=Element.ElementStatus.PUBLISHED if loc_obj else Element.ElementStatus.TO_MODIFY,
                    create_by=user, update_by=user,
                )
                created_ids.add(new_el.id)
            except Exception as e:
                stats['failed'] += 1
                logger.warning(f"[AI元素任务 {task_id}] 创建元素失败: {e}")

    # 已发布但本次未命中/未新增的 → 待废弃（软删除，可恢复）
    protected = matched_ids | created_ids
    qs = Element.objects.filter(project_id=project.id, module_id=module.id,
                                is_delete=False, status=Element.ElementStatus.PUBLISHED)
    if protected:
        qs = qs.exclude(id__in=protected)
    deprecated = qs.update(status=Element.ElementStatus.TO_DEPRECATE, update_by=user,
                           update_time=timezone.now())
    stats['deprecated'] += deprecated
    logger.info(f"[AI元素任务 {task_id}] 模块「{module.name}」完成 - 新增{stats['added_published']}, "
                f"新增待修改{stats['added_tomodify']}, 更新{stats['updated']}, 待废弃{deprecated}")


def _name_batch(ai_config_id, candidates):
    """LLM 生成 name+locator；失败/空 value 用启发式兜底"""
    from apps.ai_service.llm import LLMClient
    results = []
    found = {}
    try:
        client = LLMClient(ai_config_id)
        payload = [{'index': i, 'tag': c.get('tag'), 'role': c.get('role'),
                    'kind': c.get('kind'), 'text': c.get('text'), 'attrs': c.get('attrs')}
                   for i, c in enumerate(candidates)]
        resp = client.chat_json(_SYSTEM_NAMING, _json.dumps(payload, ensure_ascii=False), temperature=0.3)
        for r in resp.get('results', []) or []:
            found[r.get('index')] = r
    except Exception as e:
        logger.warning(f"[AI元素任务] 命名 LLM 调用失败: {e}")

    seen_keys = set()
    for i, c in enumerate(candidates):
        r = found.get(i) or {}
        name = (r.get('name') or '').strip()
        by = (r.get('by') or '').strip()
        value = (r.get('value') or '').strip()
        opts = r.get('opts') or {}
        loc = {'by': by, 'value': value, 'opts': opts} if by in _ALLOWED_BY and value else None
        # 自定义控件(attrs.native_role=false)没有真实 ARIA role，强制不用 by=role：
        # 视觉隐藏的 checkbox/radio 也会被抓取时标为 native_role=false，
        # Playwright 的 get_by_role 匹配不到，同样禁用，改用 label/text/css/xpath 兜底
        if loc and loc['by'] == 'role' and not (c.get('attrs') or {}).get('native_role', True):
            loc = None
        # 视觉隐藏控件的原始 input 类名带 __original（如 el-checkbox__original / el-radio__original），
        # 定位到也点不到：Playwright click 要求元素可见。抓到的是可见包裹容器，LLM 若仍
        # 生成这类 css 一律拦截，改走启发式（label/text/容器 css 兜底）。
        if loc and loc['by'] == 'css' and re.search(r'__original\b', loc.get('value') or ''):
            loc = None
        if not loc:
            loc = _heuristic_locator(c)  # 可能为 None(定位失败)
        # 空 value / 定位表达式重复(by+value+opts) → 视为定位失败(可避免歧义选择器)
        if loc:
            if not loc.get('value'):
                loc = None
            else:
                _key = _json.dumps({'by': loc.get('by'), 'value': loc.get('value'),
                                    'opts': loc.get('opts')}, ensure_ascii=False, sort_keys=True)
                if _key in seen_keys:
                    loc = None
                else:
                    seen_keys.add(_key)
        if loc:
            loc['value'] = loc['value'][:200]
        results.append({'name': name or _fallback_name(c), 'loc': loc})
    return results


def _resolve_decisions(ai_config_id, named, existing_list, existing_by_id,
                       vector_threshold=0.6, module_id=None, project_id=None):
    """
    判断每个候选命中哪个既有元素（三态去重）。
    三层匹配：
      1) 确定性匹配（定位表达式 by+value 相同 / 业务名称相同）——保证重复执行不重复；
      2) 向量语义匹配（hybrid_search 检索元素分块，相似度≥阈值）——识别名称/定位有变化的同一业务元素；
      3) LLM 业务语义兜底。
    """
    decisions = {}       # ci -> {'action': ..., 'ei': ...}
    used = set()         # 已匹配的既有元素 id，保证 1:1

    by_val_map = {}
    for eid, el in existing_by_id.items():
        w = el.web or {}
        if w.get('by') and w.get('value'):
            by_val_map.setdefault((w.get('by'), w.get('value')), []).append(eid)
    name_to_el = {}
    for eid, el in existing_by_id.items():
        name_to_el.setdefault((el.name or '').strip(), []).append(eid)

    unmatched = []
    for ci, it in enumerate(named):
        loc = it.get('loc') or {}
        by = loc.get('by')
        value = loc.get('value')
        nm = (it.get('name') or '').strip()
        found = None
        if by and value:
            for eid in by_val_map.get((by, value), []):
                if eid not in used:
                    found = eid
                    break
        if found is None and nm:
            for eid in name_to_el.get(nm, []):
                if eid not in used:
                    found = eid
                    break
        if found is not None:
            used.add(found)
            decisions[ci] = {'action': 'update', 'ei': found}
        else:
            unmatched.append(ci)

    # 2) 向量语义匹配（可配置阈值）
    if unmatched and project_id and vector_threshold is not None and vector_threshold > 0:
        try:
            from apps.ai_service.vectorstore import hybrid_search, SOURCE_ELEMENT
            for ci in unmatched:
                it = named[ci]
                loc = it.get('loc') or {}
                q = f"元素: {it.get('name', '')}\n元素类型: web\nWeb元素定位: {loc.get('by', '')}={loc.get('value', '')}".strip()
                hits = hybrid_search(project_id, q, source_types=[SOURCE_ELEMENT],
                                     module_id=module_id, top_k=3, min_similarity=vector_threshold)
                for hit in hits:
                    ei = (hit.get('metadata') or {}).get('source_id')
                    if ei in existing_by_id and ei not in used:
                        used.add(ei)
                        decisions[ci] = {'action': 'update', 'ei': ei}
                        break
        except Exception as e:
            logger.warning(f"[向量去重] 检索失败，跳过向量层: {e}")

    # 3) LLM 语义兜底：仅对仍未命中的候选，且只接受未占用且有效的既有元素
    unmatched = [ci for ci in unmatched if ci not in decisions]
    if unmatched:
        un_named = [named[ci] for ci in unmatched]
        leftover = [{'ei': eid, 'name': el.name} for eid, el in existing_by_id.items() if eid not in used]
        llm = _dedup_batch(ai_config_id, un_named, leftover)
        for dec in llm:
            ci_local = dec.get('ci')
            if ci_local is None or ci_local >= len(unmatched):
                continue
            ci = unmatched[ci_local]
            ei = dec.get('ei')
            if dec.get('action') == 'update' and ei is not None \
                    and ei in existing_by_id and ei not in used:
                used.add(ei)
                decisions[ci] = {'action': 'update', 'ei': ei}
    return decisions


def _dedup_batch(ai_config_id, named, existing):
    """LLM 判 para 每个候选命中哪个既有元素"""
    from apps.ai_service.llm import LLMClient
    candidates = [{'ci': i, 'name': it.get('name'),
                   'by': (it.get('loc') or {}).get('by'), 'value': (it.get('loc') or {}).get('value')}
                  for i, it in enumerate(named)]
    if not existing:
        return [{'ci': i, 'action': 'create', 'ei': None} for i in range(len(named))]
    try:
        client = LLMClient(ai_config_id)
        payload = {'candidates': candidates, 'existing': existing}
        resp = client.chat_json(_SYSTEM_DEDUP, _json.dumps(payload, ensure_ascii=False), temperature=0.2)
        return resp.get('decisions', []) or []
    except Exception as e:
        logger.warning(f"[AI元素任务] 去重 LLM 调用失败: {e}")
        return [{'ci': i, 'action': 'create', 'ei': None} for i in range(len(named))]


def _update_message(task_id, project_id, message_id, user, stats, error, duration):
    """更新站内信状态为已完成/失败"""
    try:
        project = Project.objects.filter(id=project_id).first()
        names = stats['names']
        total = sum([stats['added_published'], stats['added_tomodify'], stats['updated'],
                     stats['deprecated'], stats['failed']])
        if error:
            title = 'AI元素生成失败'
            content = f"项目: {project.name if project else ''}\n任务ID: {task_id}\n失败原因: {error}"
            task_status = Message.TaskStatus.FAILED
            fail_reason = error
        else:
            title = 'AI元素生成完成'
            name_text = "\n".join([f"  {i + 1}. {n[:60]}" for i, n in enumerate(names)])
            content = (
                f"项目: {project.name if project else ''}\n"
                f"新增(已发布): {stats['added_published']}\n"
                f"新增(待修改): {stats['added_tomodify']}\n"
                f"更新: {stats['updated']}\n"
                f"待废弃: {stats['deprecated']}\n"
                f"失败/跳过: {stats['failed']}\n"
                f"耗时: {duration:.1f} 秒\n"
                f"明细:\n{name_text}"
            )
            task_status = Message.TaskStatus.SUCCESS
            if stats['failed'] or stats['added_tomodify']:
                fail_reason = '部分元素定位失败或待补充，请到元素库完善'
            else:
                fail_reason = ''

        if message_id:
            Message.objects.filter(id=message_id).update(
                title=title,
                content=content,
                task_status=task_status,
                total_count=total,
                success_count=stats['added_published'] + stats['updated'],
                failed_count=stats['failed'] + stats['added_tomodify'],
                fail_reason=fail_reason,
                related_url='/common/element',
                is_read=False,
                read_time=None,
                duration=duration,
                update_by=user,
                update_time=timezone.now(),
            )
            logger.info(f"[AI元素任务 {task_id}] 站内信 {message_id} 已更新为 {title}")
            _push_updated_message(message_id)
    except Exception as e:
        logger.error(f"[AI元素任务 {task_id}] 更新站内信失败: {e}")


def _push_updated_message(message_id):
    """推送最新消息到前端"""
    if not message_id:
        return
    try:
        from apps.messages.models import Message
        from apps.messages.push import push_message_to_user, build_message_payload
        msg = Message.objects.filter(id=message_id).first()
        if msg:
            logger.info(f"[AI元素任务] 推送站内信 message_id={message_id} user_id={msg.user_id}")
            push_message_to_user(msg.user_id, build_message_payload(msg))
            logger.info(f"[AI元素任务] 推送站内信完成 message_id={message_id}")
    except Exception as e:
        logger.error(f"[AI元素任务] 推送站内信失败: {e}", exc_info=True)