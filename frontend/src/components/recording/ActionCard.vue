<template>
  <div
    class="rec-card"
    :class="{
      'is-active': active,
      'is-off': !enabled,
      'is-low': isLow && enabled,
      'is-pinned': !!pinnedLocator
    }"
    @click="$emit('select', action)"
  >
    <!-- 置信度色条：<0.6 琥珀（需人工复核），>=0.85 绿，其余灰。
         ★ 为什么用左边条而不是徽标：一屏可能有几十张卡，
           边条能让人「扫一眼就看到该复核哪几条」，徽标要逐张读文字。 -->
    <span class="rec-card-bar" :class="barClass"></span>

    <div class="rec-card-head">
      <span class="rec-card-idx">{{ index + 1 }}</span>
      <el-icon class="rec-card-icon"><component :is="iconComp" /></el-icon>
      <span class="rec-card-kw">{{ action.keyword || action.raw_type || '—' }}</span>
      <el-tag v-if="action.sensitive" size="small" type="warning" effect="plain">凭据</el-tag>
      <el-tag v-if="pinnedLocator" size="small" type="success" effect="plain">已固化</el-tag>
      <el-tag v-if="isLow && enabled" size="small" type="warning" effect="plain">待复核</el-tag>
      <span class="rec-card-flex"></span>
      <el-checkbox
        :model-value="enabled"
        @click.stop
        @update:model-value="(v) => $emit('toggle', action, v)"
      />
    </div>

    <div class="rec-card-target" :title="targetText">{{ targetText }}</div>

    <div v-if="valueText" class="rec-card-value">
      <span class="rec-card-lb">{{ valueLabel }}</span>
      <span class="rec-card-vv">{{ valueText }}</span>
      <el-tag v-if="valueObj && valueObj.kind === 'variable'" size="small" effect="plain">
        ${{ valueObj.var_name || 'Var' }}
      </el-tag>
    </div>

    <div v-if="assertionCount" class="rec-card-assert">
      断言 {{ assertionCount }} 条
    </div>
  </div>
</template>

<script>
/**
 * 录制动作卡片（P1 审阅台）
 *
 * 只负责「把一条 IR 动作渲染成一张能看懂、能勾选的卡片」，不含任何编辑逻辑 ——
 * 编辑统一由父级 RecordingReview 通过 patch 端点提交。这样卡片可以随便重绘，
 * 不会出现「子组件改了一份本地状态、父组件又改了一份」的双写问题。
 */
import {
  Pointer, EditPen, Compass, Timer, RefreshRight, Document, Aim, Finished
} from '@element-plus/icons-vue'

// 关键字 → 图标。取不到就退化成通用文档图标（不要让它渲染成空气）。
const ICON_MAP = {
  click: Pointer,
  fill: EditPen,
  goto: Compass,
  wait_element_located: Timer,
  scroll_page: RefreshRight,
  scroll_into_view_if_needed: RefreshRight,
  move_to_element: Aim,
  select_option: Finished,
  check: Finished,
  uncheck: Finished,
  upload_file: Document,
  url: Compass,
  title: Document,
  get_attribute: Document,
  is_visible: Aim,
  text_content: Document
}

export default {
  name: 'RecActionCard',
  props: {
    action: { type: Object, required: true },
    index: { type: Number, default: 0 },
    active: { type: Boolean, default: false }
  },
  emits: ['select', 'toggle'],
  computed: {
    enabled() {
      return this.action.enabled !== false
    },
    iconComp() {
      return ICON_MAP[this.action.keyword] || Document
    },
    confidence() {
      const c = this.action.confidence
      return typeof c === 'number' ? c : 1
    },
    isLow() {
      // 0.6 是设计里定的阈值：低于它的定位器在真实页面上「大概一半会失效」，
      // 强制人工看一眼比事后回来查便宜得多。
      return this.confidence < 0.6
    },
    barClass() {
      if (!this.enabled) return 'is-off'
      if (this.confidence >= 0.85) return 'is-high'
      if (this.confidence >= 0.6) return 'is-mid'
      return 'is-low'
    },
    /** 主定位器（IR 里 element.locators 已按分排序，[0] 即当前主定位） */
    topLocator() {
      const locs = (this.action.element || {}).locators
      return (Array.isArray(locs) && locs.length) ? locs[0] : null
    },
    pinnedLocator() {
      return this.topLocator && this.topLocator.pinned ? this.topLocator : null
    },
    targetText() {
      const el = this.action.element || {}
      const snap = el.snapshot || {}
      const name = snap.aria_label || snap.text
        || (el.ref || '').replace(/^[a-z]+:/, '')
      const loc = this.topLocator
      const locText = loc ? `${loc.by}=${loc.value}` : '（无定位器）'
      return (name ? name + ' · ' : '') + locText
    },
    /** 取第一个「值对象」，用于显示 fill/select 填了什么 */
    valueObj() {
      const args = this.action.args
      if (!args || typeof args !== 'object') return null
      for (const k of ['value', 'text', 'key', 'file_path', 'direction']) {
        const v = args[k]
        if (v && typeof v === 'object' && v.kind) return v
        if (typeof v === 'string' && v) return { kind: 'literal', value: v }
      }
      return null
    },
    valueLabel() {
      const args = this.action.args || {}
      for (const k of ['value', 'text', 'key', 'file_path', 'direction']) {
        if (args[k] !== undefined) return k
      }
      return '值'
    },
    valueText() {
      const v = this.valueObj
      if (!v) return ''
      if (v.redacted) return '（原文未落库）'
      if (v.kind === 'variable') {
        return v.value === undefined || v.value === ''
          ? '（变量，无默认值）' : String(v.value)
      }
      return String(v.value === undefined ? '' : v.value)
    },
    assertionCount() {
      const a = this.action.assertions
      return Array.isArray(a) ? a.length : 0
    }
  }
}
</script>

<style scoped>
.rec-card {
  position: relative;
  display: block;
  padding: 8px 10px 8px 14px;
  margin-bottom: 6px;
  border: 1px solid var(--qm-line);
  border-radius: 8px;
  background: var(--qm-bg-2);
  cursor: pointer;
  transition: border-color .16s, background .16s;
}
.rec-card:hover {
  border-color: var(--qm-line-strong);
}
.rec-card.is-active {
  border-color: var(--qm-accent);
  background: var(--qm-accent-soft);
}
.rec-card.is-off {
  opacity: .48;
}
/* 低置信度：琥珀左边条 + 浅底，一眼能看出该复核哪里 */
.rec-card.is-low {
  background: var(--qm-warning-soft);
}
.rec-card-bar {
  position: absolute;
  left: 0;
  top: 6px;
  bottom: 6px;
  width: 3px;
  border-radius: 3px;
  background: var(--qm-text-3);
}
.rec-card-bar.is-high { background: var(--qm-green); }
.rec-card-bar.is-mid { background: var(--qm-text-3); }
.rec-card-bar.is-low { background: var(--el-color-warning); }
.rec-card-bar.is-off { background: transparent; }

.rec-card-head {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.rec-card-idx {
  min-width: 18px;
  color: var(--qm-text-3);
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}
.rec-card-icon { color: var(--qm-text-2); }
.rec-card-kw {
  font-weight: 600;
  color: var(--qm-text-1);
}
.rec-card-flex { flex: 1; }
.rec-card-target {
  margin-top: 3px;
  font-size: 12px;
  color: var(--qm-text-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.rec-card-value {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
  font-size: 12px;
  color: var(--qm-text-3);
}
.rec-card-lb {
  padding: 0 4px;
  border-radius: 3px;
  background: var(--qm-bg-3);
}
.rec-card-vv {
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.rec-card-assert {
  margin-top: 3px;
  font-size: 12px;
  color: var(--qm-accent-strong);
}
</style>
