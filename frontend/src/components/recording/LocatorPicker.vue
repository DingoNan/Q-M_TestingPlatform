<template>
  <div class="loc-picker">
    <div class="loc-head">
      <span class="loc-title">定位器候选</span>
      <span class="loc-hint">分数由规则算出（语义强度 + 唯一性 − 脆弱性扣分）</span>
    </div>

    <div v-if="!candidates.length" class="loc-empty">
      该动作没有元素定位器（例如 <code>goto</code> / <code>scroll_page</code> 这类页面级动作）。
    </div>

    <div v-else class="loc-list">
      <div
        v-for="(c, i) in candidates"
        :key="i"
        class="loc-item"
        :class="{ 'is-active': i === 0, 'is-pinned': c.pinned }"
        @click="$emit('pick', c)"
      >
        <div class="loc-row1">
          <span class="loc-idx">{{ i === 0 ? '主' : i + 1 }}</span>
          <span class="loc-by">{{ c.by }}</span>
          <span class="loc-score" :class="scoreClass(c)">{{ fmtScore(c) }}</span>
          <el-tag v-if="c.pinned" size="small" type="success" effect="plain">人工固化</el-tag>
          <el-tag v-else-if="i === 0" size="small" type="primary" effect="plain">当前主定位</el-tag>
        </div>
        <div class="loc-row2" :title="String(c.value)">{{ c.value }}</div>
        <div v-if="c.opts && Object.keys(c.opts).length" class="loc-row3">
          {{ optsText(c) }}
        </div>
        <div v-if="reasonText(c)" class="loc-reason">{{ reasonText(c) }}</div>
      </div>
    </div>

    <!-- ★ 为什么这里给的是「一行 Playwright 代码」而不是一个「试定位」按钮
         设计里写的是「在真实页面上高亮验证」，那需要后端拉起浏览器，
         属于 P3 的执行期能力。在 P1 阶段给按钮却调不通，比没有按钮更糟
         （用户会以为功能坏了）。这里改为给可直接粘进 DevTools console 的一行
         代码 —— 零依赖、当场可验证，且验证方式是「官方的」而不是「我方的」。 -->
    <div v-if="topLocator" class="loc-try">
      <div class="loc-try-head">在浏览器控制台验证（复制即用）</div>
      <div class="loc-try-code" :title="playwrightLine" @click="copyLine">
        {{ playwrightLine }}
      </div>
      <div class="loc-try-note">
        先在目标页面打开 DevTools console，粘进去回车；返回元素数量应为 1。
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 定位器候选切换（P1 审阅台）
 *
 * IR 的 `action.element.locators` 已由 `locator_score.rank_candidates` 排好序，
 * 数组首项即当前主定位。本组件只做「展示 + 挑选」，不改分数 —— 分数是规则产物，
 * 人工挑选用 `pinned: true` 表达（后端 patch 会把它提到首位并保分不降）。
 */
import { ElMessage } from 'element-plus'

export default {
  name: 'RecLocatorPicker',
  props: {
    /** 当前动作的 element 对象（可为空） */
    element: { type: Object, default: null }
  },
  emits: ['pick'],
  computed: {
    candidates() {
      const locs = (this.element || {}).locators
      return Array.isArray(locs) ? locs.filter((c) => c && c.value) : []
    },
    topLocator() {
      return this.candidates.length ? this.candidates[0] : null
    },
    playwrightLine() {
      const c = this.topLocator
      if (!c) return ''
      const opts = c.opts || {}
      const esc = (s) => String(s == null ? '' : s).replace(/\\/g, '\\\\').replace(/'/g, "\\'")
      const nameOpt = opts.name ? `, { name: '${esc(opts.name)}'${opts.exact ? ', exact: true' : ''} }` : ''
      switch (c.by) {
        case 'role':
          return opts.name
            ? `page.getByRole('${esc(c.value)}'${nameOpt})`
            : `page.getByRole('${esc(c.value)}')`
        case 'label':
          return `page.getByLabel('${esc(c.value)}'${opts.exact ? ", { exact: true }" : ''})`
        case 'placeholder':
          return `page.getByPlaceholder('${esc(c.value)}')`
        case 'text':
          return `page.getByText('${esc(c.value)}'${opts.exact ? ", { exact: true }" : ''})`
        case 'alt text':
          return `page.getByAltText('${esc(c.value)}')`
        case 'xpath':
          return `page.locator('xpath=${esc(c.value)}')`
        case 'id':
          return `page.locator('#${esc(c.value)}')`
        default:
          return `page.locator('${esc(c.value)}')`
      }
    }
  },
  methods: {
    fmtScore(c) {
      const s = c.score
      return typeof s === 'number' ? s.toFixed(2) : '—'
    },
    scoreClass(c) {
      const s = typeof c.score === 'number' ? c.score : 0
      if (s >= 0.85) return 'is-high'
      if (s >= 0.6) return 'is-mid'
      return 'is-low'
    },
    optsText(c) {
      const o = c.opts || {}
      const parts = []
      if (o.name) parts.push('name=' + o.name)
      if (o.exact) parts.push('exact')
      const alts = o.alternatives
      if (Array.isArray(alts) && alts.length) parts.push('备选 ' + alts.length)
      if (o.in_shadow) parts.push('shadow DOM')
      return parts.join(' · ')
    },
    /** 把规则扣分的原因说人话 —— 用户最常问「为什么这个分数低」 */
    reasonText(c) {
      const out = []
      if (c.aria_guessed) out.push('角色是按动作类型推测的（非页面真实语义）')
      if (c.source === 'manual') out.push('人工选定')
      if (c.in_shadow) out.push('位于 shadow DOM 内部')
      const s = typeof c.score === 'number' ? c.score : null
      if (s !== null && s < 0.35) {
        out.push('分数偏低：多为结构路径或含随机片段，目标系统改版后容易失效')
      }
      return out.join('；')
    },
    async copyLine() {
      const text = this.playwrightLine
      if (!text) return
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text)
          ElMessage.success('已复制，粘到目标页面的控制台即可验证')
        } else {
          ElMessage.info('当前环境不支持自动复制，请手动选中这行代码')
        }
      } catch (e) {
        ElMessage.info('复制失败，请手动选中这行代码')
      }
    }
  }
}
</script>

<style scoped>
.loc-picker {
  font-size: 13px;
}
.loc-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}
.loc-title {
  font-weight: 600;
  color: var(--qm-text-1);
}
.loc-hint {
  font-size: 12px;
  color: var(--qm-text-3);
}
.loc-empty {
  padding: 10px 12px;
  border: 1px dashed var(--qm-line-strong);
  border-radius: 8px;
  color: var(--qm-text-3);
  font-size: 12px;
}
.loc-empty code {
  padding: 1px 4px;
  border-radius: 3px;
  background: var(--qm-bg-3);
}
.loc-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.loc-item {
  padding: 7px 10px;
  border: 1px solid var(--qm-line);
  border-radius: 8px;
  background: var(--qm-bg-2);
  cursor: pointer;
  transition: border-color .16s, background .16s;
}
.loc-item:hover {
  border-color: var(--qm-line-strong);
}
.loc-item.is-active {
  border-color: var(--qm-accent);
  background: var(--qm-accent-soft);
}
.loc-row1 {
  display: flex;
  align-items: center;
  gap: 6px;
}
.loc-idx {
  min-width: 18px;
  height: 18px;
  line-height: 18px;
  text-align: center;
  border-radius: 4px;
  background: var(--qm-bg-3);
  color: var(--qm-text-2);
  font-size: 11px;
}
.loc-by {
  font-weight: 600;
  color: var(--qm-text-1);
}
.loc-score {
  font-variant-numeric: tabular-nums;
  font-size: 12px;
}
.loc-score.is-high { color: var(--qm-green); }
.loc-score.is-mid { color: var(--qm-text-2); }
.loc-score.is-low { color: var(--el-color-warning); }
.loc-row2 {
  margin-top: 3px;
  color: var(--qm-text-2);
  font-family: ui-monospace, Consolas, monospace;
  font-size: 12px;
  word-break: break-all;
}
.loc-row3 {
  margin-top: 2px;
  color: var(--qm-text-3);
  font-size: 12px;
}
.loc-reason {
  margin-top: 3px;
  color: var(--el-color-warning);
  font-size: 12px;
  line-height: 1.5;
}
.loc-try {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px dashed var(--qm-line-strong);
  border-radius: 8px;
  background: var(--qm-bg-3);
}
.loc-try-head {
  font-size: 12px;
  color: var(--qm-text-2);
  margin-bottom: 5px;
}
.loc-try-code {
  padding: 6px 8px;
  border-radius: 6px;
  background: var(--qm-bg-2);
  border: 1px solid var(--qm-line);
  font-family: ui-monospace, Consolas, monospace;
  font-size: 12px;
  color: var(--qm-text-1);
  word-break: break-all;
  cursor: copy;
}
.loc-try-note {
  margin-top: 5px;
  font-size: 12px;
  color: var(--qm-text-3);
  line-height: 1.5;
}
</style>
