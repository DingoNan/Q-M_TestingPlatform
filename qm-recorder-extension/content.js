/**
 * Q·M 录制器 · 采集脚本（注入到被测页面）
 * ============================================================
 * 只做一件事：把用户在页面上的真实操作，尽可能完整地描述下来，
 * 交给后台统一编号（seq）后回传平台。
 *
 * ★ 三个容易踩的坑（下面都已处理）
 *   1) 选择器不能只靠 class：Vue/Element 的 class 常带 hash（el-button--primary、
 *      css-1x2y3z），每次构建都变 ⇒ 优先 data-testid/id/name，再退化到
 *      稳定属性选择器，最后才是 css 路径 / xpath。
 *   2) iframe / shadow DOM：只录主文档会大面积漏元素 ⇒ 每个事件带 frame_path
 *      （从顶层到当前帧的层级链）与 in_shadow 标记。
 *   3) 输入类事件要防抖：连续打字会产生上百条 ⇒ 按「同一元素 + 500ms 静默」
 *      合并成一条，只保留最后一次的值。
 */

(function () {
  if (window.__QM_RECORDER_READY__) return
  window.__QM_RECORDER_READY__ = true

  const DEBOUNCE_MS = 500
  const ATTR_PRIORITY = [
    'data-testid', 'data-test', 'data-cy', 'data-qa',
    'id', 'name', 'placeholder', 'title', 'aria-label', 'alt', 'type',
  ]

  // ★ seq 由**采集端**统一自增：这是后端幂等去重的锚点。
  //   若留空让后端自动补，重传的批次会被当成新事件重复入库。
  let _seq = 0
  function bump(evt) {
    _seq += 1
    evt.seq = _seq
    return evt
  }

  const pending = { key: null, handle: null, evt: null }

  // -------------------------------------------------------------------------
  // 元素描述
  // -------------------------------------------------------------------------
  function xpathOf(el) {
    if (!el) return ''
    if (el.id) return '//*[@id="' + el.id + '"]'
    const parts = []
    let node = el
    let guard = 0
    while (node && node.nodeType === 1 && guard++ < 12) {
      let idx = 1
      let s = node.previousSibling
      while (s) {
        if (s.nodeType === 1 && s.nodeName === node.nodeName) idx += 1
        s = s.previousSibling
      }
      parts.unshift(String(node.nodeName).toLowerCase() + '[' + idx + ']')
      node = node.parentElement
    }
    return '/' + parts.join('/')
  }

  function inShadowRoot(el) {
    try {
      return !!(el && el.getRootNode && el.getRootNode() !== document)
    } catch (e) {
      return false
    }
  }

  function stableClassList(el) {
    const raw = (el.getAttribute && el.getAttribute('class')) || ''
    return raw.trim().split(/\s+/).filter(function (c) {
      if (!c) return false
      // 过滤带 6 位以上 hex / 随机片段的动态类名（tailwind、css-modules、emotion）
      if (/[0-9a-f]{6,}/i.test(c)) return false
      if (/[_-][0-9a-z]{6,}$/.test(c)) return false
      return true
    })
  }

  function cssPath(el) {
    if (!el || el.nodeType !== 1) return ''
    const parts = []
    let node = el
    let guard = 0
    while (node && node.nodeType === 1 && guard++ < 12) {
      let part = String(node.nodeName || '').toLowerCase()
      if (node.id) {
        parts.unshift('#' + node.id)
        break
      }
      const cls = stableClassList(node).slice(0, 2)
      if (cls.length) part += '.' + cls.join('.')
      const parent = node.parentElement
      if (parent) {
        const same = Array.prototype.filter.call(parent.children, function (c) {
          return c.nodeName === node.nodeName
        })
        if (same.length > 1) part += ':nth-of-type(' + (same.indexOf(node) + 1) + ')'
      }
      parts.unshift(part)
      node = parent
    }
    return parts.join(' > ')
  }

  function describe(el) {
    if (!el || el.nodeType !== 1) return null
    const attrs = {}
    const skip = new Set(['style', 'src', 'srcdoc', 'value'])
    for (let i = 0; i < el.attributes.length; i++) {
      const a = el.attributes[i]
      if (skip.has(a.name)) continue
      if (a.value && a.value.length <= 200) attrs[a.name] = a.value
    }

    const selectors = []
    for (let i = 0; i < ATTR_PRIORITY.length; i++) {
      const k = ATTR_PRIORITY[i]
      const v = attrs[k]
      if (!v) continue
      if (k === 'id') selectors.push('#' + v)
      else if (k === 'href') selectors.push('a[href="' + v + '"]')
      else selectors.push('[' + k + '="' + v + '"]')
    }
    selectors.push(cssPath(el))
    selectors.push('xpath=' + xpathOf(el))

    let text = (el.innerText || el.textContent || '').trim()
    if (text.length > 80) text = text.slice(0, 80)

    return {
      node_name: String(el.nodeName || '').toLowerCase(),
      attrs: attrs,
      text: text || undefined,
      aria_label: attrs['aria-label'],
      selectors: selectors.filter(Boolean),
      bbox: (function () {
      try {
        const r = el.getBoundingClientRect()
        if (!r.width && !r.height) return undefined
        return {
          x: Math.round(r.x), y: Math.round(r.y),
          width: Math.round(r.width), height: Math.round(r.height),
        }
      } catch (e) { return undefined }
    })(),
      in_shadow: inShadowRoot(el),
    }
  }

  const T0 = Date.now()
  function relT() { return Date.now() - T0 }

  function flushPending() {
    if (pending.handle) { clearTimeout(pending.handle); pending.handle = null }
    if (pending.evt) { send(pending.evt); pending.evt = null }
    pending.key = null
  }

  function recordInput(el) {
    const value = (el.value !== undefined && el.value !== null) ? String(el.value) : ''
    const key = xpathOf(el) + '|' + (el.name || el.id || '')
    if (pending.key && pending.key !== key) flushPending()
    pending.key = key
    pending.evt = {
      kind: el.tagName === 'SELECT' ? 'select' : 'input',
      t: relT(),
      url: location.href,
      target: describe(el),
      value: value,
    }
    if (pending.handle) clearTimeout(pending.handle)
    pending.handle = setTimeout(flushPending, DEBOUNCE_MS)
  }

  function send(evt) {
    try {
      chrome.runtime.sendMessage({ type: 'qm-event', event: evt })
    } catch (e) {
      /* 扩展重载 / 上下文失效时忽略 */
    }
  }

  // -------------------------------------------------------------------------
  // 监听
  // -------------------------------------------------------------------------
  document.addEventListener('click', function (e) {
    const el = e.target
    if (!el || el.nodeType !== 1) return
    const key = 'click|' + xpathOf(el)
    if (pending.key === key) return   // 连续点同一元素 → 合并，避免误触产生两条
    flushPending()
    send(bump({ kind: 'click', t: relT(), url: location.href, target: describe(el) }))
    pending.key = key
    setTimeout(function () { if (pending.key === key) pending.key = null }, 300)
  }, true)

  document.addEventListener('input', function (e) {
    const el = e.target
    if (!el || el.nodeType !== 1) return
    if (!/^(INPUT|TEXTAREA|SELECT)$/.test(String(el.nodeName))) return
    recordInput(el)
  }, true)

  document.addEventListener('change', function (e) {
    const el = e.target
    if (!el || el.nodeType !== 1) return
    if (el.nodeName === 'INPUT' || el.nodeName === 'SELECT') {
      flushPending()
      send(bump({
        kind: el.nodeName === 'SELECT' ? 'select' : 'check',
        t: relT(),
        url: location.href,
        target: describe(el),
        value: el.type === 'checkbox' || el.type === 'radio'
          ? String(!!el.checked)
          : String(el.value ?? ''),
      }))
    }
  }, true)

  document.addEventListener('keydown', function (e) {
    const el = e.target
    if (!el || el.nodeType !== 1) return
    if (e.key !== 'Enter' && e.key !== 'Tab') return  // 只录提交型按键，普通打字不录
    flushPending()
    send(bump({ kind: 'keydown', t: relT(), url: location.href, target: describe(el), key: e.key }))
  }, true)

  // ★ 为什么必须 hook History API：SPA 点菜单不触发 load，
  //   不 hook 就丢掉「跳到新页面」这个最重要的上下文。
  const _push = history.pushState
  const _replace = history.replaceState
  function emitNav(href) {
    flushPending()
    send(bump({ kind: 'navigate', t: relT(), url: href || location.href }))
  }
  history.pushState = function () {
    const r = _push.apply(this, arguments)
    emitNav()
    return r
  }
  history.replaceState = function () {
    const r = _replace.apply(this, arguments)
    emitNav()
    return r
  }
  window.addEventListener('popstate', () => emitNav())
  window.addEventListener('hashchange', () => emitNav())

  window.addEventListener('pagehide', flushPending)

  window.addEventListener('message', function (e) {
    const d = e.data
    if (!d || d.__qm !== 'recorder') return
    if (d.action === 'stop') flushPending()
  })

  // -------------------------------------------------------------------------
  // ★ 零配置：在平台上自动上报登录态与当前项目（v0.2.0）
  // -------------------------------------------------------------------------
  // 背景：旧版要求用户在弹窗里手工粘贴 token（F12 → Console 敲
  //   JSON.parse(localStorage.token)），再手填「项目 ID」—— 用户反馈根本找不到。
  // 事实：这两样东西本来就躺在平台页面的 localStorage 里：
  //   token           —— 登录后写入（JSON 字符串）
  //   qm-projectInfo  —— 「我的项目」点卡片后写入，形如 {id, name, ...}
  // content script 与页面共享 localStorage（isolated world 只隔离 JS 对象，
  // 不隔离 storage），所以这里直接读出来交给 background 保存即可，
  // 用户什么都不用填。
  // 识别「这是平台页」的标志：同时存在 token 与 qm-projectInfo/qm-userInfo
  //（都是平台专有键，别的网站撞名的概率可忽略）。
  function readPlatformCreds() {
    function ls(k) {
      let v = null
      try { v = localStorage.getItem(k) } catch (e) { return null }
      if (v === null || v === undefined) return null
      const s = String(v).trim()
      if (!s || s === 'null' || s === 'undefined' || s === '""') return null
      try { return JSON.parse(s) } catch (e) { return s }
    }
    const tk = ls('token')
    const proj = ls('qm-projectInfo')
    const ui = ls('qm-userInfo')
    if (!tk || typeof tk !== 'string') return null
    if (!proj || !proj.id) return null   // 没进过项目 ⇒ 至少知道登录了，但项目要等选
    return {
      token: tk,
      projectId: String(proj.id),
      projectName: proj.name ? String(proj.name) : '',
      userName: String((ui && (ui.user_name || ui.username || ui.name)) || ''),
      siteOrigin: location.origin,
      // 与平台前端 api/index.js 的 base_url 拼法保持一致（hostname:8000）
      apiBase: location.protocol + '//' + location.hostname + ':8000',
    }
  }

  function reportCreds() {
    const c = readPlatformCreds()
    if (!c) return
    try {
      chrome.runtime.sendMessage({ type: 'qm-credentials', creds: c }, function () {
        void chrome.runtime.lastError   // 扩展上下文失效时静默
      })
    } catch (e) { /* ignore */ }
  }
  reportCreds()
})()
