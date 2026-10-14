<template>
  <div class="irb" v-loading="loading">
    <!-- ===================== 统计条 =====================
         ★ 为什么统计条要统一：HAR 导入与录制导入此前各有一套统计呈现
           （drawer 里的 har-summary 卡片 / 审阅台顶栏的 rr-stat 文本）。
           同一个「我这次导入了多少、被丢了多少」的问题，在两条链路上长得不一样，
           用户换个入口就得重新认一遍。 -->
    <div v-if="stats.length" class="irb-stats">
      <div v-for="(s, i) in stats" :key="'s' + i" class="irb-stat" :class="'is-' + (s.tone || 'plain')">
        <div class="irb-stat-num" :class="s.numClass">{{ s.value }}</div>
        <div class="irb-stat-lbl">{{ s.label }}</div>
      </div>
      <div class="irb-stats-extra"><slot name="stats-extra" /></div>
    </div>

    <!-- ===================== 被自动忽略的条目（透明化） =====================
         ★★ 这一块是「统一」里最有价值的一块。
           用户最常问的是「我明明点了 30 下 / 抓了 60 个请求，怎么只有 12 条？」
           答案全在这里。藏起来 = 用户认为工具在偷偷丢数据。
           HAR 侧是「跳过的静态资源」，录制侧是「解析时忽略的动作」——
           同一个问题，以前只有录制侧回答了。 -->
    <div v-if="drops.length" class="irb-drops">
      <div class="irb-drops-head" @click="dropOpen = !dropOpen">
        <el-icon><component :is="dropOpen ? 'ArrowDown' : 'ArrowRight'" /></el-icon>
        <span>{{ dropTitle }} {{ dropTotal }} 条（点击{{ dropOpen ? '收起' : '查看原因' }}）</span>
      </div>
      <div v-if="dropOpen" class="irb-drops-body">
        <div v-for="(d, i) in dropEntries" :key="i" class="irb-drop-item">
          <span class="irb-drop-n">{{ d.count }}</span>
          <span class="irb-drop-t">{{ d.reason }}</span>
        </div>
        <div v-if="dropHint" class="irb-drop-hint">{{ dropHint }}</div>
      </div>
    </div>

    <!-- ===================== 主体（各业务自己渲染清单/编辑区） ===================== -->
    <div class="irb-body">
      <slot />
    </div>

    <!-- ===================== 底栏 ===================== -->
    <div v-if="footerTip || $slots.actions" class="irb-foot">
      <div class="irb-foot-left">
        <el-icon class="irb-foot-icon"><InfoFilled /></el-icon>
        <span>{{ footerTip }}</span>
      </div>
      <div class="irb-foot-right">
        <slot name="actions" />
      </div>
    </div>

    <!-- ===================== 落库 / 导入结果回执 =====================
         ★ 为什么要统一：两边都要回答「到底落了什么」，以前是两套写法
           （HAR 走向导第 3 步的 stats-grid，录制走 rr-result 弹窗）。
           统一后无论从哪个入口进来，回执长得一样，跳过明细也不会漏。 -->
    <el-dialog
      :model-value="resultVisible"
      :title="(result && result.title) || '导入结果'"
      width="640"
      :append-to-body="true"
      :z-index="1010"
      destroy-on-close
      @update:model-value="(v) => $emit('update:resultVisible', v)"
    >
      <div v-if="result" class="irb-result">
        <div v-for="(l, i) in (result.lines || [])" :key="'l' + i" class="irb-result-line">
          <span class="irb-result-lb">{{ l.label }}</span>
          <span class="irb-result-vv">
            {{ l.value }}
            <el-tag v-for="(t, j) in (l.tags || [])" :key="'t' + j" size="small"
                    :type="t.type" effect="plain" class="irb-var-tag">{{ t.text }}</el-tag>
          </span>
        </div>

        <div v-if="(result.variables || []).length" class="irb-result-line">
          <span class="irb-result-lb">{{ result.variablesLabel || '变量' }}</span>
          <span class="irb-result-vv">
            <el-tag v-for="v in result.variables" :key="v" size="small" effect="plain"
                    class="irb-var-tag">{{ v }}</el-tag>
          </span>
        </div>

        <!-- ★ 跳过明细：不说清楚就等于「工具把你的一部分输入吃了」 -->
        <div v-if="(result.skips || []).length" class="irb-result-line">
          <span class="irb-result-lb">跳过</span>
          <span class="irb-result-vv">
            {{ result.skips.length }} 条
            <div v-for="(s, i) in result.skips" :key="'k' + i" class="irb-skip">
              {{ s.seq !== undefined && s.seq !== null ? ('#' + s.seq + '：') : '' }}{{ s.reason }}
            </div>
          </span>
        </div>

        <div v-if="(result.errors || []).length" class="irb-result-line">
          <span class="irb-result-lb">失败</span>
          <span class="irb-result-vv">
            {{ result.errors.length }} 条
            <div v-for="(e, i) in result.errors.slice(0, 20)" :key="'e' + i" class="irb-skip is-err">{{ e }}</div>
          </span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="$emit('update:resultVisible', false)">关闭</el-button>
          <el-button v-if="result && result.primaryText" type="primary" size="small"
                     @click="$emit('result-primary')">{{ result.primaryText }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 统一「导入审阅台」骨架（P4a）
 *
 * ============================ 它统一了什么 ============================
 * 接口自动化的 HAR 导入 与 Web 自动化的录制导入，差异只在「解析器」和「产物类型」，
 * 审阅这一段的交互是同构的：看统计 → 看为什么少了几条 → 勾选 → 落库 → 看回执。
 * 这个组件把同构的部分收成一份实现，业务差异走 slot。
 *
 * ============================ 它刻意不管什么 ============================
 * 不碰「条目长什么样」「怎么编辑」——那是 HAR 与录制真正不同的地方，
 * 强行抽象只会得到一个谁都用不顺的巨型配置对象。主体一律走 default slot。
 */
export default {
  name: 'ImportReviewBoard',
  props: {
    /** 统计条：[{label, value, tone: 'plain'|'ok'|'warn'|'bad', numClass}] */
    stats: { type: Array, default: () => [] },
    /** 被自动忽略的条目：[{reason, count}]；也接受 ['原因字符串', ...] */
    drops: { type: Array, default: () => [] },
    dropTitle: { type: String, default: '解析时自动忽略' },
    dropHint: { type: String, default: '' },
    footerTip: { type: String, default: '' },
    loading: { type: Boolean, default: false },
    /** 结果回执：{title, lines:[{label,value,tags}], variables, variablesLabel, skips, errors, primaryText} */
    result: { type: Object, default: null },
    resultVisible: { type: Boolean, default: false },
  },
  emits: ['update:resultVisible', 'result-primary'],
  data() {
    return { dropOpen: false }
  },
  computed: {
    // 兼容两种入参：对象数组（带计数）与纯字符串数组（计数一律 1）
    dropEntries() {
      return (this.drops || []).map((d) => (
        typeof d === 'string' ? { reason: d, count: 1 } : d
      )).filter((d) => d && d.reason)
    },
    dropTotal() {
      return this.dropEntries.reduce((n, d) => n + (Number(d.count) || 0), 0)
    },
  },
}
</script>

<style scoped>
.irb {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* ---- 统计条 ---- */
.irb-stats {
  display: flex;
  align-items: stretch;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.irb-stat {
  flex: 1 1 120px;
  min-width: 110px;
  background: #f7f8fa;
  border: 1px solid #eceef2;
  border-radius: 10px;
  padding: 10px 12px;
  text-align: center;
}
.irb-stat.is-ok { background: #f0f9f2; border-color: #d7ead9; }
.irb-stat.is-warn { background: #fdf6ec; border-color: #f5e3c3; }
.irb-stat.is-bad { background: #fef0f0; border-color: #f8d4d4; }
.irb-stat-num {
  font-size: 20px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}
.irb-stat.is-ok .irb-stat-num { color: #3aa05a; }
.irb-stat.is-warn .irb-stat-num { color: #c8871a; }
.irb-stat.is-bad .irb-stat-num { color: #e06b6b; }
.irb-stat-lbl { margin-top: 4px; font-size: 12px; color: #909399; }
.irb-stats-extra { display: flex; align-items: center; }

/* ---- 忽略项透明化 ---- */
.irb-drops {
  border: 1px solid #f0e2c2;
  background: #fdf9ef;
  border-radius: 10px;
  margin-bottom: 12px;
  overflow: hidden;
}
.irb-drops-head {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 13px;
  color: #a1701a;
  cursor: pointer;
  user-select: none;
}
.irb-drops-body { padding: 0 12px 10px; }
.irb-drop-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 3px 0;
  font-size: 12px;
  color: #6b5330;
}
.irb-drop-n {
  flex: 0 0 auto;
  min-width: 22px;
  padding: 0 6px;
  height: 18px;
  line-height: 18px;
  text-align: center;
  border-radius: 9px;
  background: #f0e2c2;
  color: #8a5f14;
  font-weight: 600;
}
.irb-drop-t { word-break: break-all; }
.irb-drop-hint { margin-top: 6px; font-size: 12px; color: #a08a63; }

/* ---- 主体 ---- */
.irb-body { flex: 1 1 auto; min-height: 0; }

/* ---- 底栏 ---- */
.irb-foot {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #eceef2;
}
.irb-foot-left {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
  flex: 1 1 auto;
  min-width: 0;
}
.irb-foot-icon { color: #c0c4cc; flex: 0 0 auto; }
.irb-foot-right { display: flex; align-items: center; gap: 8px; flex: 0 0 auto; }

/* ---- 结果回执 ---- */
.irb-result { display: flex; flex-direction: column; gap: 10px; }
.irb-result-line { display: flex; gap: 12px; font-size: 13px; }
.irb-result-lb { flex: 0 0 72px; color: #909399; }
.irb-result-vv { flex: 1 1 auto; color: #303133; word-break: break-all; }
.irb-var-tag { margin-left: 6px; }
.irb-skip { color: #a1701a; font-size: 12px; margin-top: 2px; }
.irb-skip.is-err { color: #d9534f; }
</style>
