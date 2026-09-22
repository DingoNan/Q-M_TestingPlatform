<template>
  <el-popover
    v-model:visible="popoverVisible"
    placement="bottom-end"
    :width="320"
    trigger="click"
    popper-class="qm-col-popper"
  >
    <template #reference>
      <el-button
        class="qm-col-trigger"
        :class="{ 'is-narrowed': hiddenCount > 0 }"
        :title="triggerTitle"
      >
        <el-icon><Operation /></el-icon>
        <span>列设置</span>
        <span v-if="hiddenCount > 0" class="qm-col-badge">{{ hiddenCount }}</span>
      </el-button>
    </template>

    <div class="qm-col-panel">
      <div class="qm-col-head">
        <div class="qm-col-head-row">
          <span class="qm-col-mode" :class="mode === 'auto' ? 'is-auto' : 'is-manual'">
            {{ mode === 'auto' ? '自动适配' : '自定义' }}
          </span>
          <span class="qm-col-metric">
            可用 {{ availableWidth > 0 ? availableWidth : '—' }}px / 实需 {{ requiredWidth }}px
          </span>
        </div>
        <div v-if="overflowPx > 0" class="qm-col-tip is-warn">
          <el-icon><WarningFilled /></el-icon>
          <span>横向溢出 {{ overflowPx }}px，建议再收起 {{ suggestedHideCount }} 列</span>
        </div>
        <div v-else class="qm-col-tip is-ok">
          <el-icon><SuccessFilled /></el-icon>
          <span>当前无横向滚动</span>
        </div>
      </div>

      <div class="qm-col-ops">
        <button type="button" class="qm-col-op" @click="handleAutoAdapt">按当前宽度适配</button>
        <button type="button" class="qm-col-op" @click="handleShowAll">全部显示</button>
        <button type="button" class="qm-col-op" @click="handleReset">恢复默认</button>
      </div>

      <div class="qm-col-list">
        <div
          v-for="col in columns"
          :key="col.key"
          class="qm-col-item"
          :class="{ 'is-locked': col.hideable === false }"
        >
          <el-checkbox
            :model-value="isKeyVisible(col.key)"
            :disabled="col.hideable === false"
            @update:model-value="(v) => handleToggle(col.key, v)"
          />
          <span class="qm-col-name">{{ col.label }}</span>
          <span class="qm-col-w">{{ col.hideable === false ? '锁定' : widthLabel(col) }}</span>
        </div>
      </div>

      <div class="qm-col-foot">列显隐按页面记忆，保存在本机浏览器</div>
    </div>
  </el-popover>
</template>

<script>
/**
 * ColumnSetting · 列表「列设置」通用组件
 * ---------------------------------------------------------------
 * 解决的问题：宽表在 1366/1536 等小视口下出现横向滚动，操作列等关键列
 * 被挤出可视区。用户需要在「不看次要列」和「横向拖滚动条」之间二选一。
 *
 * 设计取向（对齐项目现有习惯）：
 * 1. el-table 初始化即锁定列宽 —— 所以本组件只切换列「显隐」(v-if)，
 *    绝不做「可见按钮数 × N」这类依赖异步状态去反推列宽的计算
 *    （详见 assets/css/global-table.css 的操作列规范注释）。
 * 2. 宽度来自父组件实测的**容器客户区宽**（ResizeObserver），
 *    不用 window.innerWidth 估算 —— 侧栏折叠/全屏时容器宽会变。
 * 3. 两档模式：
 *    - auto   自动适配：每次按当前容器宽，从低优先级列开始收起，
 *                       保证「无横向滚动」是默认行为，用户零操作。
 *    - manual 自定义：用户手动勾选后进入，持久化，不再被宽度变化覆盖。
 * 4. 不可隐藏列（选择框/序号/主信息/操作）在 UI 上显示「锁定」且禁用勾选，
 *    但它们的宽度**计入**自动适配的总宽 —— 否则算出来的可用余量是错的。
 *
 * props:
 *   columns       [{ key, label, width?, minWidth?, hideable?, priority? }]
 *                 priority 越小越「重要」，越晚被自动收起；缺省按 50。
 *   storageKey    持久化键后缀，建议一页一个（如 'case_list'）
 *   availableWidth 父组件实测的容器客户区宽（px）
 *   overflowPx    父组件实测的横向溢出量（px），>0 时给出建议
 *   modelValue    当前可见列的 key 数组（v-model）
 * emits: update:modelValue, change
 */
import { Operation, WarningFilled, SuccessFilled } from '@element-plus/icons-vue'

const MODE_AUTO = 'auto'
const MODE_MANUAL = 'manual'
/** 自动适配预留的安全余量：容器宽未计入纵向滚动条（≈8px）与边框 */
const SAFETY_MARGIN = 10

export default {
  name: 'ColumnSetting',
  components: { Operation, WarningFilled, SuccessFilled },
  props: {
    columns: { type: Array, default: () => [] },
    storageKey: { type: String, default: 'default' },
    availableWidth: { type: Number, default: 0 },
    overflowPx: { type: Number, default: 0 },
    modelValue: { type: Array, default: () => [] },
  },
  emits: ['update:modelValue', 'change'],
  data() {
    return {
      popoverVisible: false,
      innerKeys: [],
      mode: MODE_AUTO,
      ready: false,
    }
  },
  computed: {
    allKeys() {
      return this.columns.map((c) => c.key)
    },
    lockedKeys() {
      return this.columns.filter((c) => c.hideable === false).map((c) => c.key)
    },
    hideableCols() {
      return this.columns.filter((c) => c.hideable !== false)
    },
    hiddenCount() {
      return this.hideableCols.filter((c) => !this.innerKeys.includes(c.key)).length
    },
    requiredWidth() {
      return this.columns
        .filter((c) => this.innerKeys.includes(c.key))
        .reduce((s, c) => s + this.colWidth(c), 0)
    },
    suggestedHideCount() {
      if (this.overflowPx <= 0) return 0
      // 从「最不重要」（priority 最大）开始数，看还需要收起几列才能填平溢出
      const pool = this.hideableCols
        .filter((c) => this.innerKeys.includes(c.key))
        .slice()
        .sort((a, b) => this.priorityOf(b) - this.priorityOf(a))
      let need = this.overflowPx
      let n = 0
      for (const c of pool) {
        if (need <= 0) break
        need -= this.colWidth(c)
        n += 1
      }
      return n
    },
    triggerTitle() {
      const base = '列设置'
      return this.hiddenCount > 0 ? `${base}（当前隐藏 ${this.hiddenCount} 列）` : base
    },
  },
  watch: {
    availableWidth(val) {
      if (!this.ready) return
      // 只有自动模式才跟随容器宽变化；自定义模式尊重用户选择
      if (this.mode === MODE_AUTO && val > 0) this.applyAutoAdapt()
    },
    columns() {
      if (!this.ready) return
      const valid = this.allKeys
      const next = this.innerKeys.filter((k) => valid.includes(k))
      for (const k of this.lockedKeys) if (!next.includes(k)) next.push(k)
      this.innerKeys = this.orderKeys(next)
      this.commit()
    },
  },
  created() {
    this.restore()
  },
  mounted() {
    this.ready = true
    if (this.mode === MODE_AUTO && this.availableWidth > 0) this.applyAutoAdapt()
  },
  methods: {
    /* ---------- 工具 ---------- */
    colWidth(col) {
      if (typeof col.width === 'number') return col.width
      if (typeof col.minWidth === 'number') return col.minWidth
      return 120
    },
    widthLabel(col) {
      if (typeof col.width === 'number') return col.width + 'px'
      if (typeof col.minWidth === 'number') return '≥' + col.minWidth + 'px'
      return '自适应'
    },
    priorityOf(col) {
      return typeof col.priority === 'number' ? col.priority : 50
    },
    orderKeys(keys) {
      const set = new Set(keys)
      return this.allKeys.filter((k) => set.has(k))
    },
    isKeyVisible(key) {
      return this.innerKeys.includes(key)
    },
    storageFullKey() {
      return 'qm_cols_' + this.storageKey + '_v1'
    },

    /* ---------- 持久化 ---------- */
    restore() {
      let saved = null
      try {
        saved = JSON.parse(localStorage.getItem(this.storageFullKey()) || 'null')
      } catch (e) {
        saved = null
      }
      const valid = this.allKeys
      // 初始值：优先用外部 v-model 传入的，其次 localStorage，最后全部可见
      const incoming = Array.isArray(this.modelValue) && this.modelValue.length ? this.modelValue : null
      let keys = null
      if (incoming) {
        this.mode = MODE_MANUAL
        keys = incoming.filter((k) => valid.includes(k))
      } else if (saved && Array.isArray(saved.keys)) {
        this.mode = saved.mode === MODE_MANUAL ? MODE_MANUAL : MODE_AUTO
        keys = saved.keys.filter((k) => valid.includes(k))
      } else {
        this.mode = MODE_AUTO
        keys = valid.slice()
      }
      for (const k of this.lockedKeys) if (!keys.includes(k)) keys.push(k)
      this.innerKeys = this.orderKeys(keys)
      this.emitKeys()
    },
    persist() {
      try {
        localStorage.setItem(
          this.storageFullKey(),
          JSON.stringify({ mode: this.mode, keys: this.innerKeys })
        )
      } catch (e) {
        /* 隐私模式 / 配额满：静默降级为「本次会话有效」 */
      }
    },

    /* ---------- 自动适配 ---------- */
    computeAutoKeys(avail) {
      const budget = avail > 0 ? avail - SAFETY_MARGIN : 0
      const keep = []
      let total = 0
      // 锁定列无条件保留，并计入总宽
      for (const c of this.columns) {
        if (c.hideable === false) {
          keep.push(c.key)
          total += this.colWidth(c)
        }
      }
      // 可隐藏列按重要性（priority 升序）依次尝试放入
      const pool = this.hideableCols
        .slice()
        .sort((a, b) => this.priorityOf(a) - this.priorityOf(b))
      for (const c of pool) {
        const w = this.colWidth(c)
        if (budget <= 0 || total + w <= budget) {
          keep.push(c.key)
          total += w
        }
      }
      return this.orderKeys(keep)
    },
    applyAutoAdapt() {
      this.innerKeys = this.computeAutoKeys(this.availableWidth)
      this.emitKeys()
    },

    /* ---------- 交互 ---------- */
    handleAutoAdapt() {
      this.mode = MODE_AUTO
      this.applyAutoAdapt()
      this.persist()
    },
    handleShowAll() {
      this.mode = MODE_MANUAL
      this.innerKeys = this.allKeys.slice()
      this.emitKeys()
      this.persist()
    },
    handleReset() {
      try {
        localStorage.removeItem(this.storageFullKey())
      } catch (e) {
        /* ignore */
      }
      this.mode = MODE_AUTO
      this.applyAutoAdapt()
      this.persist()
    },
    handleToggle(key, val) {
      const col = this.columns.find((c) => c.key === key)
      if (!col || col.hideable === false) return
      const set = new Set(this.innerKeys)
      if (val) set.add(key)
      else set.delete(key)
      for (const k of this.lockedKeys) set.add(k)
      this.innerKeys = this.orderKeys([...set])
      // 用户一旦手动干预，就切到自定义模式，不再被容器宽覆盖
      this.mode = MODE_MANUAL
      this.emitKeys()
      this.persist()
    },

    /* ---------- 对外 ---------- */
    commit() {
      this.emitKeys()
    },
    emitKeys() {
      const keys = this.innerKeys.slice()
      this.$emit('update:modelValue', keys)
      this.$emit('change', keys)
    },
  },
}
</script>

<style scoped>
.qm-col-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border-radius: 8px;
  border: 1px solid var(--qm-line);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.18s ease;
}
.qm-col-trigger:hover {
  border-color: var(--qm-accent-line);
  color: var(--qm-accent-strong);
  background: var(--qm-warning-soft);
}
.qm-col-trigger.is-narrowed {
  border-color: var(--qm-accent-line);
  color: var(--qm-accent-strong);
}
.qm-col-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 8px;
  background: var(--qm-accent);
  color: #1f2937;
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
}
</style>

<!-- popover 内容 teleport 到 body，scoped 命中不到，故单独用非 scoped 块 -->
<style>
.qm-col-popper.el-popover.el-popper {
  padding: 0;
  border-radius: 12px;
  border: 1px solid var(--qm-line);
  background: var(--qm-bg-2);
  box-shadow: var(--qm-shadow);
}
.qm-col-panel {
  padding: 12px 14px 10px;
  color: var(--qm-text-1);
  font-size: 13px;
}
.qm-col-head {
  padding-bottom: 10px;
  border-bottom: 1px solid var(--qm-line);
}
.qm-col-head-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.qm-col-mode {
  padding: 1px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
}
.qm-col-mode.is-auto {
  background: var(--qm-accent-soft);
  color: var(--qm-accent-strong);
}
.qm-col-mode.is-manual {
  background: var(--qm-bg-3);
  color: var(--qm-text-2);
}
.qm-col-metric {
  color: var(--qm-text-3);
  font-size: 11px;
  font-variant-numeric: tabular-nums;
}
.qm-col-tip {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 8px;
  font-size: 12px;
  line-height: 1.4;
}
.qm-col-tip.is-ok {
  color: var(--qm-green);
}
.qm-col-tip.is-warn {
  color: var(--qm-accent-strong);
}
.qm-col-ops {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 10px 0;
}
.qm-col-op {
  flex: 1 1 auto;
  padding: 5px 8px;
  border-radius: 6px;
  border: 1px solid var(--qm-line);
  background: var(--qm-bg-3);
  color: var(--qm-text-2);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.16s ease;
}
.qm-col-op:hover {
  border-color: var(--qm-accent-line);
  color: var(--qm-accent-strong);
  background: var(--qm-warning-soft);
}
.qm-col-list {
  max-height: 268px;
  overflow-y: auto;
  padding-right: 2px;
}
.qm-col-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 2px;
  border-radius: 6px;
}
.qm-col-item:hover {
  background: var(--qm-bg-3);
}
.qm-col-item.is-locked {
  opacity: 0.72;
}
.qm-col-name {
  flex: 1 1 auto;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--qm-text-1);
}
.qm-col-w {
  flex: 0 0 auto;
  color: var(--qm-text-3);
  font-size: 11px;
  font-variant-numeric: tabular-nums;
}
.qm-col-foot {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--qm-line);
  color: var(--qm-text-3);
  font-size: 11px;
}
</style>
