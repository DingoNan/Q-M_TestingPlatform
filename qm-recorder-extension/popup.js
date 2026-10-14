/**
 * Q·M 录制器 · 弹窗控制
 * ============================================================
 * 只负责 UI：把用户意图转成消息发给 background.js，
 * 所有网络与缓冲逻辑都不在这里（MV3 的 service worker 会休眠，
 * 放弹窗里一关就断）。
 *
 * ★ 一个必须记住的点：弹窗**关闭即销毁**。所以这里不保存"是否正在录制"
 *   的状态，每次打开都向后台问一次 `qm-status` —— 否则会出现
 *   「关掉弹窗再打开，显示未录制，但实际还在录」的错位。
 */

const $ = (id) => document.getElementById(id)

let CFG = { base: 'http://172.16.21.161:8000', token: '', projectId: '' }

// ---------------------------------------------------------------------------
// 配置读写
// ---------------------------------------------------------------------------
function loadCfg(cb) {
  chrome.storage.local.get(['qmBase', 'qmToken', 'qmProjectId'], (o) => {
    CFG.base = (o && o.qmBase) || CFG.base
    CFG.token = (o && o.qmToken) || ''
    CFG.projectId = (o && o.qmProjectId) || ''
    $('base').value = CFG.base
    $('token').value = CFG.token
    $('projectId').value = CFG.projectId
    if (cb) cb()
  })
}

function saveCfg(silent) {
  CFG.base = ($('base').value || '').trim().replace(/\/+$/, '') || CFG.base
  CFG.token = ($('token').value || '').trim()
  CFG.projectId = ($('projectId').value || '').trim()
  chrome.runtime.sendMessage(
    { type: 'qm-save-config', base: CFG.base, token: CFG.token },
    () => {
      chrome.storage.local.set({ qmProjectId: CFG.projectId })
      if (!silent) flash('配置已保存', true)
    }
  )
}

// ---------------------------------------------------------------------------
// 状态渲染
// ---------------------------------------------------------------------------
function flash(text, good) {
  const el = $('err')
  el.style.display = 'block'
  el.className = 'err' + (good ? ' ok' : '')
  el.textContent = text
  if (good) setTimeout(() => { if (el.textContent === text) el.style.display = 'none' }, 2000)
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
  loadCfg(refresh)

  $('toggleCfg').addEventListener('click', () => {
    $('cfgBox').classList.toggle('show')
  })

  $('saveCfg').addEventListener('click', () => saveCfg(false))

  $('openPlatform').addEventListener('click', () => {
    // ★ 录制履历不是独立路由，它是「脚本用例列表」页里的一个弹窗
    //   （views/case/CaseList.vue 的「录制履历」按钮）。所以只能跳到
    //   /#/resource/scriptCase，再由用户在页面上点按钮打开。
    const pid = ($('projectId').value || '').trim()
    const url = (CFG.base || '') + '/#/resource/scriptCase' + (pid ? '?project=' + pid : '')
    chrome.tabs.create({ url })
  })

  $('startBtn').addEventListener('click', () => {
    const pid = ($('projectId').value || '').trim()
    if (!pid) {
      flash('请先填写「项目 ID」（在 ⚙ 配置 里）', false)
      $('cfgBox').classList.add('show')
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
