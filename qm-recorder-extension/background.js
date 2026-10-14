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
  nextTryAt: 0,        // 退避窗口的到期时间戳（0 = 立即可试）
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
  // ★★ 必须是**一个合法 JSON**（数组），不能是 NDJSON（v0.2.1 修复的真缺陷）
  //    旧实现把每批事件拼成「每行一个 JSON 对象」的 NDJSON 文本，
  //    而后端 `_read_upload` 只做 `json.loads(text)` ⇒ 抛
  //    `Extra data: line 2 column 1 (char N)` ⇒ HTTP 400 ⇒ 视图把这句话
  //    原样当 detail 返回 ⇒ 弹窗显示「最近错误：Extra data: line 2 column 1」。
  //    实测后果：**事件一条都传不上来**，录制完 finish 只能生成 0 步的 IR。
  //    用 file 字段而不是 JSON body：DATA_UPLOAD_MAX_MEMORY_SIZE(2.5MB) 只卡 JSON body。
  body.append('file',
    new Blob([JSON.stringify(batch)], { type: 'application/json' }),
    'events.json');
  body.append('append', 'true');
  // ★ 与创建会话的 source 不同：这里是**解析器**字母表
  //   （core/recorder/sources.py 的 SOURCE_NATIVE='native'），别改。
  body.append('source', 'native');
  const r = await fetch(api('/recording/session/' + STATE.sessionId + '/events/'), {
    method: 'POST',
    headers: authHeaders(),
    body,
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) {
    const e = new Error((j && (j.detail || j.msg || j.error)) || ('HTTP ' + r.status));
    // 4xx 是「这批数据后端不要」—— 重试一万次也一样，必须让上层区别对待
    e.permanent = r.status >= 400 && r.status < 500;
    e.status = r.status;
    throw e;
  }
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

// 上传一批事件。返回状态字符串（**别再返回 boolean**，
// 因为「正在发送」与「发送失败」在上层要做完全不同的事）：
//   'busy'  已有一批在飞 —— 等它落地即可
//   'empty' 没东西可传
//   'ok'    这一批成功写进后端
//   'fail'  失败（缓冲原样保留，退避后重试）
async function flush() {
  if (STATE.sending) return 'busy';
  if (!STATE.recording || !STATE.sessionId) return 'empty';
  if (!STATE.buffer.length) return 'empty';
  // ★ 退避窗口内不再尝试：否则 alarm（每 6 秒）+ setTimeout 会形成
  //   「失败后立刻再打一发」的循环，把后端打得更惨
  if (STATE.nextTryAt && Date.now() < STATE.nextTryAt) return 'fail';
  STATE.sending = true;
  const batch = STATE.buffer.slice();
  try {
    await postEvents(batch);
    // ★ 关键：只有真的写进去了才清缓冲
    STATE.buffer = STATE.buffer.slice(batch.length);
    STATE.uploaded += batch.length;
    STATE.backoff = 0;
    STATE.nextTryAt = 0;
    STATE.lastError = '';
    if (STATE.buffer.length) {
      // 还有剩的（边录边传），立刻续上
      setTimeout(flush, 0);
    }
    return 'ok';
  } catch (e) {
    // 失败：缓冲原样保留，退避后重试
    STATE.lastError = String((e && e.message) || e);
    if (e && e.permanent) {
      // 4xx：这批数据后端根本不要（格式错/会话已丢弃/超上限）。
      // 无限重试没有意义，退到最长间隔并让用户在面板上看到原因。
      STATE.backoff = MAX_BACKOFF_MS;
    } else {
      STATE.backoff = Math.min(MAX_BACKOFF_MS, (STATE.backoff || 500) * 2);
    }
    STATE.nextTryAt = Date.now() + STATE.backoff;
    setTimeout(flush, STATE.backoff);
    return 'fail';
  } finally {
    STATE.sending = false;
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

  if (type === 'qm-list-projects') {
    // 项目列表由 **service worker** 来拉（v0.2.1）
    //   旧版在弹窗里直接 fetch：弹窗是短命页面，fetch 一旦不返回（被环境拦、
    //   代理黑洞、SW 唤醒竞态），下拉框就永远停在初始态 —— 连「自动识别到的
    //   当前项目」都放不进去，用户被「请先选择项目」卡死，录制根本开始不了。
    //   本文件开头就写了「所有网络逻辑都不放在弹窗」，这条是漏网的。
    ;(async () => {
      try {
        if (!STATE.token) {
          const c = await readCredsFromActiveTab()
          if (c) applyCreds(c, { force: true })
        }
        if (!STATE.token) { reply({ ok: false, error: '未识别到平台登录态' }); return }
        const r = await fetch(api('/projects/?size=200'), {
          headers: authHeaders(),
        })
        const j = await r.json().catch(() => ({}))
        if (!r.ok) {
          throw new Error('HTTP ' + r.status + ' ' + ((j && (j.detail || j.msg)) || ''))
        }
        // CustomRender 契约：列表被包进 result（{count, results} 或直接数组）
        const payload = (j && j.result) || j || {}
        const rows = payload.results || payload.data || (Array.isArray(payload) ? payload : [])
        reply({ ok: true, projects: rows.filter((x) => x && x.id) })
      } catch (e) {
        reply({ ok: false, error: String((e && e.message) || e) })
      }
    })()
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
        // ★★ drain 循环**必须有上限**（v0.2.1 修复的真缺陷）
        //   旧写法 `while (STATE.buffer.length) { await flush(); sleep 300 }`：
        //   flush() 内部吞掉异常、缓冲原样保留 ⇒ 上传只要失败一次，
        //   这个循环就**永远不退出** ⇒ 弹窗按钮一直卡在「正在上传并生成…」，
        //   用户看到的就是「点了结束并生成，没反应/没正确生成」。
        //   现在最多 20 轮×250ms（≈5 秒 + 网络耗时），传不完就如实上报条数。
        let tries = 0;
        while (STATE.buffer.length && tries < 20) {
          tries += 1;
          const r = await flush();
          if (r === 'fail' && STATE.buffer.length) break;
          await new Promise((res) => setTimeout(res, 250));
        }
        const unsent = STATE.buffer.length;
        const ir = await finishSession();
        STATE.recording = false;
        reply({ ok: true, sessionId: STATE.sessionId, ir: ir,
                unsent: unsent, uploaded: STATE.uploaded });
      } catch (e) {
        STATE.recording = false;
        reply({ ok: false, error: String((e && e.message) || e),
                unsent: STATE.buffer.length });
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
