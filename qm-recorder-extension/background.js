/**
 * Q·M 录制器 · MV3 Service Worker（后台）
 * ============================================================
 * 职责：
 *   1. 创建录制会话（拿 session_id + 会话级上传令牌）
 *   2. 收集 content script 采到的事件，按批缓冲
 *   3. 定时/定量 flush 到后端；**失败保留缓冲、指数退避重试**（断网补传）
 *   4. 结束录制：flush 后调 finish 让后端归一化成 IR
 *
 * ★ 断网补传的关键设计（三条，缺一不可）
 *   a) 只有收到 **2xx** 才清空缓冲 ⇒ 网络抖动不会丢事件；
 *   b) 每批事件都带**全局单调递增 seq**，后端按 `(session_id, seq)` 幂等去重
 *      ⇒ 重试同一批不会重复入库；
 *   c) 重试用**指数退避**且有上限 ⇒ 后端短暂不可用时不会把自己打死。
 */

const DEFAULT_BASE = 'http://172.16.21.161:8000';

// 批大小与节奏：够快（不拖沓）又不至于打爆后端
const FLUSH_EVENTS = 20;      // 累计多少条立即上传
const FLUSH_MS = 5000;        // 或每 5 秒上传一次
const MAX_BACKOFF_MS = 60000; // 退避上限 1 分钟
const MAX_BUFFER = 2000;      // 缓冲上限，防止长时间离线把内存撑爆

let STATE = {
  recording: false,
  sessionId: null,
  token: '',
  base: DEFAULT_BASE,
  siteOrigin: '',      // 平台前端地址（自动识别），用于「打开录制履历」跳转
  projectName: '',     // 当前项目名（自动识别，仅展示）
  userName: '',        // 当前登录用户名（自动识别，仅展示）
  seq: 0,
  buffer: [],
  sending: false,
  backoff: 0,
  lastError: '',
  uploaded: 0,
  dropped: 0,
};

// ---------------------------------------------------------------------------
// 工具
// ---------------------------------------------------------------------------
function normalizeBase(raw) {
  const s = String(raw || '').trim().replace(/\/+$/, '');
  return s || DEFAULT_BASE;
}

function api(path) {
  return STATE.base + path;
}

function authHeaders() {
  const h = { 'Accept': 'application/json' };
  if (STATE.token) h['Authorization'] = 'Bearer ' + STATE.token;
  return h;
}

function bump(payload) {
  STATE.seq += 1;
  return Object.assign({ seq: STATE.seq }, payload);
}

// ---------------------------------------------------------------------------
// ★ 零配置：凭据落库（v0.2.0）
// ---------------------------------------------------------------------------
// token / 项目 / 站点地址都来自平台页面自身的 localStorage（content.js 上报，
// 或 popup 打开时 executeScript 主动读一次）。用户从此不用手填任何东西。
//
// ★ 录制中不覆盖 base：一旦录制开始，上传地址必须保持稳定，
//   半途换 base 会让后续批次打到别的后端（且旧会话在新后端不存在）。
function applyCreds(c, opts) {
  const force = !!(opts && opts.force)
  if (STATE.recording && !force) return { applied: false, reason: 'recording' }
  let changed = false
  if (c.token && c.token !== STATE.token) { STATE.token = c.token; changed = true }
  if (c.apiBase) {
    const nb = normalizeBase(c.apiBase)
    if (nb && nb !== STATE.base) { STATE.base = nb; changed = true }
  }
  if (c.siteOrigin && c.siteOrigin !== STATE.siteOrigin) { STATE.siteOrigin = c.siteOrigin; changed = true }
  if (c.projectName !== undefined && c.projectName !== STATE.projectName) { STATE.projectName = c.projectName; changed = true }
  if (c.userName !== undefined && c.userName !== STATE.userName) { STATE.userName = c.userName; changed = true }
  if (changed || force) {
    chrome.storage.local.set({
      qmBase: STATE.base,
      qmToken: STATE.token,
      qmSiteOrigin: STATE.siteOrigin,
      qmProjectName: STATE.projectName,
      qmUserName: STATE.userName,
      qmCredsAt: Date.now(),
    })
    if (c.projectId) chrome.storage.local.set({ qmProjectId: String(c.projectId) })
  }
  return { applied: true, changed: changed }
}

// 在标签页里读一次平台凭据。
// ★ readCreds 必须自包含：executeScript 的 func 会被序列化后注入页面，
//   不能引用 background 作用域里的任何东西。
const PAGE_READ_CREDS = function () {
  function ls(k) {
    var v = null
    try { v = localStorage.getItem(k) } catch (e) { return null }
    if (v === null || v === undefined) return null
    var s = String(v).trim()
    if (!s || s === 'null' || s === 'undefined' || s === '""') return null
    try { return JSON.parse(s) } catch (e) { return s }
  }
  var tk = ls('token')
  var proj = ls('qm-projectInfo')
  var ui = ls('qm-userInfo')
  if (!tk || typeof tk !== 'string') return null
  return {
    token: tk,
    projectId: proj && proj.id ? String(proj.id) : '',
    projectName: proj && proj.name ? String(proj.name) : '',
    userName: String((ui && (ui.user_name || ui.username || ui.name)) || ''),
    siteOrigin: location.origin,
    apiBase: location.protocol + '//' + location.hostname + ':8000',
  }
}

async function execReadCreds(tabId) {
  try {
    const res = await chrome.scripting.executeScript({ target: { tabId: tabId }, func: PAGE_READ_CREDS })
    return (res && res[0] && res[0].result) || null
  } catch (e) {
    // chrome:// 等受限页面不允许注入 ⇒ 视为「这里不是平台」
    return null
  }
}

// 读凭据：①当前激活标签页；②读不到（用户停在别的网页上）则扫描所有
// 标签页找平台页 —— 前端 8080 已在 host_permissions 里，后台标签页可注入。
async function readCredsFromActiveTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
  const tab = tabs && tabs[0]
  if (tab && tab.id) {
    const c = await execReadCreds(tab.id)
    if (c) return c
  }
  const all = await chrome.tabs.query({})
  for (const t of all) {
    if (!t || !t.id || t.id === (tab && tab.id)) continue
    if (!t.url || !/^https?:/i.test(t.url)) continue
    const c = await execReadCreds(t.id)
    if (c) return c
  }
  return null
}

// ---------------------------------------------------------------------------
// 与后端交互
// ---------------------------------------------------------------------------
async function createSession(projectId, name, startUrl) {
  const r = await fetch(api('/recording/session/'), {
    method: 'POST',
    headers: Object.assign(authHeaders(), { 'Content-Type': 'application/json' }),
    body: JSON.stringify({
      project_id: Number(projectId),
      name: name || '',
      // ★★ 这里是**会话**字母表，不是解析器字母表（踩过一次）：
      //    /recording/session/ 视图用 `source not in RecordingSession.Source.choices`
      //    做校验，合法值只有 manual_upload / extension / devtools_plugin / cdp /
      //    playwright_script。写 'native'（那是 core/recorder/sources.py 里
      //    **解析器**的来源标识，只在 /events/ 端点用）会被 400 拒掉，
      //    表现为「点开始录制没反应」。扩展实时推送 ⇒ 固定 'extension'。
      source: 'extension',
      start_url: startUrl || '',
    }),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error((j && (j.detail || j.msg || j.error)) || ('HTTP ' + r.status));
  return (j && j.result) || j || {};
}

async function postEvents(batch) {
  const body = new FormData();
  // ★ 用 file 字段而不是 JSON body：DATA_UPLOAD_MAX_MEMORY_SIZE(2.5MB) 只卡 JSON
  const ndjson = batch.map((x) => JSON.stringify(x)).join('\n');
  body.append('file', new Blob([ndjson], { type: 'application/x-ndjson' }), 'events.ndjson');
  body.append('append', 'true');
  // ★ 与上面的 session source 不同：这里是**解析器**字母表
  //   （core/recorder/sources.py 的 SOURCE_NATIVE='native'），别改。
  body.append('source', 'native');
  const r = await fetch(api('/recording/session/' + STATE.sessionId + '/events/'), {
    method: 'POST',
    headers: authHeaders(),
    body,
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error((j && (j.detail || j.msg || j.error)) || ('HTTP ' + r.status));
  return (j && j.result) || j || {};
}

async function finishSession() {
  const r = await fetch(api('/recording/session/' + STATE.sessionId + '/finish/'), {
    method: 'POST',
    headers: Object.assign(authHeaders(), { 'Content-Type': 'application/json' }),
    body: JSON.stringify({}),
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error((j && (j.detail || j.msg || j.error)) || ('HTTP ' + r.status));
  return (j && j.result) || j || {};
}

// ---------------------------------------------------------------------------
// 缓冲与上传
// ---------------------------------------------------------------------------
function enqueue(evt) {
  if (!STATE.recording) return
  if (STATE.buffer.length >= MAX_BUFFER) {
    // 缓冲满了：丢最旧的并计数（宁可丢也不能 OOM，且要把丢了几条告诉用户）
    STATE.buffer.shift()
    STATE.dropped += 1
  }
  STATE.buffer.push(evt)
  if (STATE.buffer.length >= FLUSH_EVENTS) {
    flush()
  }
}

async function flush() {
  if (STATE.sending) return
  if (!STATE.recording || !STATE.sessionId) return
  if (!STATE.buffer.length) return
  STATE.sending = true
  const batch = STATE.buffer.slice()
  try {
    const res = await postEvents(batch)
    // ★ 关键：只有真的写进去了才清缓冲
    STATE.buffer = STATE.buffer.slice(batch.length)
    STATE.uploaded += batch.length
    STATE.backoff = 0
    STATE.lastError = ''
    if (STATE.buffer.length) {
      // 还有剩的（边录边传），立刻续上
      setTimeout(flush, 0)
    }
  } catch (e) {
    // 失败：缓冲原样保留，退避后重试
    STATE.lastError = String((e && e.message) || e)
    STATE.backoff = Math.min(MAX_BACKOFF_MS, (STATE.backoff || 500) * 2)
    setTimeout(flush, STATE.backoff)
  } finally {
    STATE.sending = false
  }
}

// 定时兜底：一直没凑够一批也要传
chrome.alarms.create('qm-recorder-flush', { periodInMinutes: 0.1 })
chrome.alarms.onAlarm.addListener((a) => {
  if (a.name === 'qm-recorder-flush') flush()
})

// ---------------------------------------------------------------------------
// 消息路由
// ---------------------------------------------------------------------------
chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  const type = msg && msg.type

  if (type === 'qm-status') {
    reply({
      recording: STATE.recording,
      sessionId: STATE.sessionId,
      buffered: STATE.buffer.length,
      uploaded: STATE.uploaded,
      dropped: STATE.dropped,
      lastError: STATE.lastError,
      base: STATE.base,
      hasToken: !!STATE.token,
      siteOrigin: STATE.siteOrigin,
      projectName: STATE.projectName,
      userName: STATE.userName,
    })
    return true
  }

  if (type === 'qm-credentials') {
    // content.js 在平台页面上报（每次页面加载一次）
    const r = applyCreds(msg.creds || {})
    reply({ ok: true, applied: r.applied })
    return true
  }

  if (type === 'qm-sync-credentials') {
    // popup 打开时主动同步：到当前标签页读一次最新凭据。
    // 读不到（不是平台页/未登录）也回 ok —— popup 用 storage 里的旧值渲染。
    ;(async () => {
      const c = await readCredsFromActiveTab()
      let r = { applied: false }
      if (c) r = applyCreds(c)
      reply({ ok: true, creds: c, applied: r.applied })
    })()
    return true
  }

  if (type === 'qm-save-config') {
    // 手动兜底通道（设置面板）。自动识别仍会在页面加载时刷新 token。
    STATE.base = normalizeBase(msg.base)
    STATE.token = String(msg.token || '').trim()
    if (msg.siteOrigin !== undefined) STATE.siteOrigin = String(msg.siteOrigin || '').trim()
    chrome.storage.local.set({ qmBase: STATE.base, qmToken: STATE.token, qmSiteOrigin: STATE.siteOrigin })
    reply({ ok: true, base: STATE.base, hasToken: !!STATE.token })
    return true
  }

  if (type === 'qm-start') {
    ;(async () => {
      try {
        if (!STATE.token) {
          // 最后一次机会：到当前标签页现读一次（用户可能刚登录完没刷新）
          const c = await readCredsFromActiveTab()
          if (c) applyCreds(c, { force: true })
        }
        if (!STATE.token) {
          reply({ ok: false, error: '未识别到平台登录态：请先在浏览器打开并登录 Q·M 平台，再回到本页任意操作一下后重试。' })
          return
        }
        const s = await createSession(msg.projectId, msg.name, msg.startUrl)
        STATE.sessionId = s.session_id
        STATE.recording = true
        STATE.buffer = []
        STATE.seq = 0
        STATE.uploaded = 0
        STATE.dropped = 0
        STATE.lastError = ''
        // 注入采集脚本（刷新后 content_scripts 会自动回来）
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
        for (const t of tabs) {
          try {
            await chrome.scripting.executeScript({
              target: { tabId: t.id, allFrames: true },
              files: ['content.js'],
            })
          } catch (e) {
            /* 某些页面（chrome:// 等）不允许注入，忽略 */
          }
        }
        reply({ ok: true, sessionId: STATE.sessionId })
      } catch (e) {
        reply({ ok: false, error: String((e && e.message) || e) })
      }
    })()
    return true
  }

  if (type === 'qm-event') {
    enqueue(msg.event)
    reply({ ok: true })
    return true
  }

  if (type === 'qm-flush') {
    flush()
    reply({ ok: true })
    return true
  }

  if (type === 'qm-finish') {
    ;(async () => {
      try {
        // 先把残余事件全部传完
        while (STATE.buffer.length) {
          await flush()
          await new Promise((r) => setTimeout(r, 300))
        }
        const ir = await finishSession()
        STATE.recording = false
        reply({ ok: true, sessionId: STATE.sessionId, ir: ir })
      } catch (e) {
        STATE.recording = false
        reply({ ok: false, error: String((e && e.message) || e) })
      }
    })()
    return true
  }

  return false
})

// ---------------------------------------------------------------------------
// 启动：恢复配置
// ---------------------------------------------------------------------------
chrome.storage.local.get(['qmBase', 'qmToken', 'qmSiteOrigin', 'qmProjectName', 'qmUserName'], (o) => {
  if (o && o.qmBase) STATE.base = normalizeBase(o.qmBase)
  if (o && o.qmToken) STATE.token = String(o.qmToken)
  if (o && o.qmSiteOrigin) STATE.siteOrigin = String(o.qmSiteOrigin)
  if (o && o.qmProjectName) STATE.projectName = String(o.qmProjectName)
  if (o && o.qmUserName) STATE.userName = String(o.qmUserName)
})
