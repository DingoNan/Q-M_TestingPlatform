/**
 * Q·M 录制器 · 弹窗控制（v0.2.0 零配置版）
 * ============================================================
 * 只负责 UI：把用户意图转成消息发给 background.js，
 * 所有网络与缓冲逻辑都不在这里（MV3 的 service worker 会休眠，
 * 放弹窗里一关就断）。
 *
 * ★ v0.2.0 变化：登录 token 与当前项目**全自动识别**（content.js 在平台
 *   页面上报 + 本弹窗打开时 executeScript 主动读一次），用户不再需要
 *   F12 手工抠 token，也看不到「项目 ID」这种内部概念 —— 项目用
 *   /projects/ 拉回来按**中文名**展示成下拉框。
 *
 * ★ 弹窗**关闭即销毁**：不保存"是否正在录制"状态，每次打开都向
 *   background 问一次 qm-status。
 */

const $ = (id) => document.getElementById(id)

let CFG = {
  base: 'http://172.16.21.161:8000',
  site: '',
  token: '',
  projectId: '',
  projectName: '',
  userName: '',
}

// ---------------------------------------------------------------------------
// 配置读写
// ---------------------------------------------------------------------------
function loadCfg(cb) {
  chrome.storage.local.get(
    ['qmBase', 'qmToken', 'qmSiteOrigin', 'qmProjectId', 'qmProjectName', 'qmUserName'],
    (o) => {
      o = o || {}
      CFG.base = o.qmBase || CFG.base
      CFG.site = o.qmSiteOrigin || ''
      CFG.token = o.qmToken || ''
      CFG.projectId = o.qmProjectId || ''
      CFG.projectName = o.qmProjectName || ''
      CFG.userName = o.qmUserName || ''
      $('base').value = CFG.base
      $('site').value = CFG.site
      $('token').value = CFG.token
      if (cb) cb()
    }
  )
}

function saveCfg(silent) {
  CFG.base = ($('base').value || '').trim().replace(/\/+$/, '') || CFG.base
  CFG.site = ($('site').value || '').trim().replace(/\/+$/, '')
  CFG.token = ($('token').value || '').trim()
  CFG.projectId = ($('projectId').value || '').trim()
  chrome.runtime.sendMessage(
    { type: 'qm-save-config', base: CFG.base, token: CFG.token, siteOrigin: CFG.site },
    () => {
      chrome.storage.local.set({
        qmProjectId: CFG.projectId,
        qmProjectName: CFG.projectName,
      })
      if (!silent) flash('设置已保存', true)
    }
  )
}

// ---------------------------------------------------------------------------
// 连接状态卡
// ---------------------------------------------------------------------------
function renderConn(opts) {
  const hasToken = !!CFG.token
  const justSynced = opts && opts.justSynced
  const ic = $('connIc')
  const card = $('conn')
  if (hasToken) {
    card.className = 'conn on'
    ic.textContent = '✅'
    $('connT1').textContent = '已自动连接平台' + (CFG.userName ? ' · ' + CFG.userName : '')
    $('connT2').textContent = CFG.projectName
      ? '当前项目：' + CFG.projectName
      : '已登录，但还没进入过任何项目'
  } else {
    card.className = 'conn off'
    ic.textContent = justSynced ? '⚠️' : '⏳'
    $('connT1').textContent = '未识别到平台登录态'
    $('connT2').textContent = '请先在浏览器打开并登录 Q·M 平台，插件会自动完成配置'
  }
}

// ---------------------------------------------------------------------------
// 项目下拉（中文名，来自 /projects/）
// ---------------------------------------------------------------------------
function fillProjectSelect(list) {
  const sel = $('projectId')
  sel.innerHTML = ''
  const ph = document.createElement('option')
  ph.value = ''
  ph.textContent = list.length ? '-- 选择项目 --' : '-- 暂无可选项目 --'
  sel.appendChild(ph)
  list.forEach((p) => {
    const opt = document.createElement('option')
    opt.value = String(p.id)
    opt.textContent = p.name ? p.name + ' (ID ' + p.id + ')' : '项目 #' + p.id
    sel.appendChild(opt)
  })
  // 默认选中：自动识别到的当前项目；不在列表里也保留（append 一条兜底）
  if (CFG.projectId) {
    let hit = null
    for (const opt of sel.options) {
      if (opt.value === String(CFG.projectId)) { hit = opt; break }
    }
    if (!hit && CFG.projectName) {
      const opt = document.createElement('option')
      opt.value = String(CFG.projectId)
      opt.textContent = CFG.projectName + ' (ID ' + CFG.projectId + ')'
      sel.appendChild(opt)
      hit = opt
    }
    if (hit) sel.value = String(CFG.projectId)
  }
}

async function loadProjects() {
  if (!CFG.token) { fillProjectSelect([]); return }
  try {
    const r = await fetch(CFG.base + '/projects/?size=200', {
      headers: { 'Authorization': 'Bearer ' + CFG.token, 'Accept': 'application/json' },
    })
    const j = await r.json().catch(() => ({}))
    // CustomRender 契约：列表被包进 result（{count, results} 或直接数组）
    const payload = (j && j.result) || j || {}
    const rows = payload.results || payload.data || (Array.isArray(payload) ? payload : [])
    fillProjectSelect(rows.filter((x) => x && x.id))
    $('projHint').textContent = rows.length
      ? '共 ' + rows.length + ' 个项目；默认选中平台当前项目。'
      : '未取到项目列表（可能没有项目权限）。'
  } catch (e) {
    fillProjectSelect([])
    $('projHint').textContent = '项目列表拉取失败（' + String((e && e.message) || e).slice(0, 60) + '），可先用自动识别的项目。'
  }
}

// ---------------------------------------------------------------------------
// 自动识别（popup 打开时主动同步一次）
// ---------------------------------------------------------------------------
function syncCreds() {
  chrome.runtime.sendMessage({ type: 'qm-sync-credentials' }, (r) => {
    if (chrome.runtime.lastError) { renderConn(); return }
    loadCfg(() => {
      renderConn({ justSynced: true })
      loadProjects()
    })
  })
}

// ---------------------------------------------------------------------------
// 状态渲染
// ---------------------------------------------------------------------------
function flash(text, good) {
  const el = $('err')
  el.style.display = 'block'
  el.className = 'err' + (good ? ' ok' : '')
  el.textContent = text
  if (good) setTimeout(() => { if (el.textContent === text) el.style.display = 'none' }, 2600)
}

function render(s) {
  const rec = !!(s && s.recording)
  document.getElementById('title').className = rec ? 'rec' : ''
  $('startBtn').style.display = rec ? 'none' : 'block'
  $('stopBtn').style.display = rec ? 'block' : 'none'

  if (!rec) {
    $('stat').innerHTML = s && s.lastError
      ? '状态：上次有未上传成功的事件 <b>' + (s.buffered || 0) + '</b> 条（会自动重试）'
      : '状态：待开始'
  } else {
    $('stat').innerHTML =
      '录制中 · 会话 <b>#' + (s.sessionId || '-') + '</b><br>' +
      '已上传 <b>' + (s.uploaded || 0) + '</b> 条 · 待传 <b>' + (s.buffered || 0) + '</b> 条' +
      (s.dropped ? ' · <span style="color:#f56c6c">丢弃 ' + s.dropped + '</span>' : '')
  }

  if (s && s.lastError) {
    $('err').style.display = 'block'
    $('err').className = 'err'
    $('err').textContent = '最近错误：' + s.lastError
  }
}

function refresh() {
  chrome.runtime.sendMessage({ type: 'qm-status' }, (s) => {
    if (chrome.runtime.lastError) {
      flash('与后台通信失败，请重新加载扩展', false)
      return
    }
    render(s || {})
  })
}

// ---------------------------------------------------------------------------
// 事件绑定
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  loadCfg(() => {
    renderConn()
    loadProjects()
    refresh()
    // 打开弹窗即同步一次最新登录态（activeTab 权限此时已授予）
    syncCreds()
  })

  $('reSync').addEventListener('click', syncCreds)

  $('toggleCfg').addEventListener('click', () => {
    $('cfgBox').classList.toggle('show')
  })

  $('saveCfg').addEventListener('click', () => saveCfg(false))

  $('openPlatform').addEventListener('click', () => {
    // ★ 录制履历不是独立路由，它是「脚本用例列表」页里的一个弹窗
    //   （views/case/CaseList.vue 的「录制履历」按钮）。所以只能跳到
    //   /#/resource/scriptCase，再由用户在页面上点按钮打开。
    // 站点地址优先用自动识别的前端 origin；没有则把 API 地址的端口换成 8080 猜测。
    let site = CFG.site
    if (!site && CFG.base) {
      try {
        const u = new URL(CFG.base)
        site = u.protocol + '//' + u.hostname + ':8080'
      } catch (e) { site = '' }
    }
    if (!site) { flash('暂无平台地址，请先打开一次平台页面（自动识别）。', false); return }
    const pid = ($('projectId').value || '').trim()
    const url = site + '/#/resource/scriptCase' + (pid ? '?project=' + pid : '')
    chrome.tabs.create({ url })
  })

  $('startBtn').addEventListener('click', () => {
    const pid = ($('projectId').value || '').trim()
    if (!pid) {
      flash('请先选择项目（下拉框），或先到平台进入任一项目后点「重新识别」。', false)
      return
    }
    saveCfg(true)

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tab = tabs && tabs[0]
      chrome.runtime.sendMessage({
        type: 'qm-start',
        projectId: pid,
        name: ($('name').value || '').trim(),
        startUrl: (tab && tab.url) || '',
      }, (r) => {
        if (chrome.runtime.lastError) { flash(chrome.runtime.lastError.message, false); return }
        if (!r || !r.ok) {
          flash('开始失败：' + ((r && r.error) || '未知错误'), false)
        } else {
          flash('已开始录制，请在页面上正常操作；结束后点「结束并生成」。', true)
        }
        refresh()
      })
    })
  })

  $('stopBtn').addEventListener('click', () => {
    const btn = $('stopBtn')
    btn.disabled = true
    btn.textContent = '正在上传并生成…'
    chrome.runtime.sendMessage({ type: 'qm-finish' }, (r) => {
      btn.disabled = false
      btn.textContent = '■ 结束并生成'
      if (!r || !r.ok) {
        flash('结束失败：' + ((r && r.error) || '未知错误'), false)
      } else {
        const sum = (r.ir && r.ir.stats) || {}
        flash('已生成 IR：步骤 ' + (sum.step_count || sum.steps || 0) +
              ' 条，可到平台「录制履历」审阅后导入。', true)
      }
      refresh()
    })
  })

  setInterval(refresh, 1500)
})
