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
  // 默认选中：自动识别到的当前项目；不在列表里也保留（append 一条兜底）。
  // ★ 这一条是「开始录制」的底线 —— 就算项目列表拉不到，
  //   自动识别到的项目也必须可选（fail-open）。
  if (CFG.projectId) {
    let hit = null
    for (const opt of sel.options) {
      if (opt.value === String(CFG.projectId)) { hit = opt; break }
    }
    if (!hit) {
      const opt = document.createElement('option')
      opt.value = String(CFG.projectId)
      opt.textContent = CFG.projectName
        ? CFG.projectName + ' (ID ' + CFG.projectId + ')'
        : '当前项目 (ID ' + CFG.projectId + ')'
      sel.appendChild(opt)
      hit = opt
    }
    sel.value = String(CFG.projectId)
  }
}

// ---------------------------------------------------------------------------
// 项目下拉（v0.2.1：fail-open，两段式）
//   第一段（本地、零网络）：立刻把「自动识别到的当前项目」放进下拉并选中
//     —— 就算平台接口挂了，用户也能直接开始录制（默认项目就是对的）。
//   第二段（后台拉全量）：由 service worker 拉 /projects/ 补齐其他项目；
//     后台消息 8 秒不回就放弃，绝不让「开始录制」被一个网络请求卡死。
//   旧版在弹窗里直接 fetch 且没有任何超时：一旦请求不返回，下拉框永远
//   停在初始态，用户被「请先选择项目」卡死 —— 真机复现过。
// ---------------------------------------------------------------------------
function renderAutoProject() {
  fillProjectSelect([])
  $('projHint').textContent = CFG.projectId
    ? '已自动选中平台当前项目' + (CFG.projectName ? '：' + CFG.projectName : '') + '。'
    : '打开过「我的项目」页面后会自动选中当前项目。'
}

function refreshProjects() {
  let settled = false
  const done = (r) => {
    if (settled) return
    settled = true
    if (r && r.ok && r.projects && r.projects.length) {
      fillProjectSelect(r.projects)
      $('projHint').textContent = '共 ' + r.projects.length +
        ' 个项目；默认选中平台当前项目。'
    }
    // 拉不到就维持第一段的自动识别结果（不报错、不清空）
  }
  try {
    chrome.runtime.sendMessage({ type: 'qm-list-projects' }, done)
    setTimeout(() => done(null), 8000)
  } catch (e) { done(null) }
}

// ---------------------------------------------------------------------------
// 自动识别（popup 打开时主动同步一次）
// ---------------------------------------------------------------------------
function syncCreds() {
  chrome.runtime.sendMessage({ type: 'qm-sync-credentials' }, (r) => {
    if (chrome.runtime.lastError) { renderConn(); return }
    loadCfg(() => {
      renderConn({ justSynced: true })
      renderAutoProject()
      refreshProjects()
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
    renderAutoProject()   // ★ 先落「自动识别的项目」，网络没回来也能开始录制
    refresh()
    refreshProjects()
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
        // ★ 真源是 finish 响应里的 `summary`（NZ.summarize 的产物）：
        //     {kept_actions, dropped, elements_unique, assertions, ...}
        //   旧代码读 `r.ir.stats.step_count` —— 三处都错
        //   （嵌套少了一层 + 统计块里根本没有 step_count/steps 这两个键），
        //   结果**永远显示「步骤 0 条」**，用户以为没生成成功。
        const sum = (r.ir && r.ir.summary) || {}
        let msg = '已生成：步骤 ' + (sum.kept_actions || 0) + ' 条'
        if (sum.elements_unique) msg += '、元素 ' + sum.elements_unique + ' 个'
        if (sum.assertions) msg += '、断言 ' + sum.assertions + ' 条'
        if (r.unsent) msg += '（注意：仍有 ' + r.unsent + ' 条事件未上传成功）'
        msg += '。可到平台「录制履历」审阅后导入。'
        flash(msg, true)
      }
      refresh()
    })
  })

  setInterval(refresh, 1500)
})
