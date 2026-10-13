<template>
  <el-dialog
    v-model="visible"
    :title="view === 'review' ? '录制审阅台' : '录制履历'"
    width="94%"
    top="4vh"
    :append-to-body="true"
    :z-index="1002"
    class="rec-history-dialog"
    :before-close="handleBeforeClose"
    @closed="onClosed"
  >
    <div class="rh-body" :class="{ 'is-review': view === 'review' }">
      <!-- ==================== 视图一：履历列表 ==================== -->
      <template v-if="view === 'list'">
        <div class="rh-toolbar">
          <el-input
            v-model="query.keyword"
            size="small"
            clearable
            placeholder="按会话名 / 起始地址搜索"
            class="rh-kw"
            @keyup.enter="search"
            @clear="search"
          />
          <el-select v-model="query.status" size="small" clearable placeholder="全部状态" class="rh-sel" @change="search">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
          <el-select v-model="query.source" size="small" clearable placeholder="全部来源" class="rh-sel" @change="search">
            <el-option v-for="s in sourceOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
          <el-button size="small" type="primary" @click="search">查询</el-button>
          <el-button size="small" @click="reset">重置</el-button>
          <span class="rh-flex"></span>
          <span class="rh-count">共 {{ count }} 个会话</span>
        </div>

        <div class="rh-table-wrap">
          <el-table
            v-loading="loading"
            :data="rows"
            size="small"
            class="elegant-table"
            height="100%"
            @row-dblclick="goReview"
          >
            <el-table-column prop="name" label="会话名称" min-width="220" show-overflow-tooltip />
            <el-table-column label="来源" width="140">
              <template #default="{ row }">
                {{ row.source_display || row.source || '—' }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="96" align="center">
              <template #default="{ row }">
                <el-tag :type="statusTagType(row.status)" size="small" effect="plain">
                  {{ row.status_display || row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="动作/元素/断言" width="130" align="center">
              <template #default="{ row }">
                <span class="rh-stat">{{ statOf(row, 'kept_actions') }}</span>
                <span class="rh-sep">/</span>
                <span class="rh-stat">{{ statOf(row, 'elements_unique') }}</span>
                <span class="rh-sep">/</span>
                <span class="rh-stat">{{ statOf(row, 'assertions') }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="start_url" label="起始地址" min-width="200" show-overflow-tooltip>
              <template #default="{ row }">
                <span class="rh-url">{{ row.start_url || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="创建时间" width="160">
              <template #default="{ row }">
                {{ fmtTime(row.create_time) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="184" fixed="right" align="center">
              <template #default="{ row }">
                <el-button link size="small" type="primary" @click="goReview(row)">审阅</el-button>
                <el-button
                  v-if="row.imported_case_id"
                  link
                  size="small"
                  @click="openCase(row)"
                >用例</el-button>
                <el-button
                  v-if="row.status !== 5"
                  link
                  size="small"
                  type="danger"
                  @click="discardSession(row)"
                >丢弃</el-button>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty description="还没有录制会话。在「脚本用例 → 新建 Web 自动化用例 → 导入录制」上传第一份录制文件后，这里就会出现记录。" :image-size="70" />
            </template>
          </el-table>
        </div>

        <div class="rh-pager">
          <el-pagination
            v-model:current-page="query.page"
            v-model:page-size="query.size"
            :total="count"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            background
            size="small"
            @current-change="fetchList"
            @size-change="onSizeChange"
          />
        </div>
      </template>

      <!-- ==================== 视图二：审阅台 ==================== -->
      <template v-else>
        <div class="rh-review-head">
          <el-button link size="small" @click="backToList">
            <el-icon><ArrowLeft /></el-icon>返回履历
          </el-button>
          <span class="rh-review-title">{{ currentName || ('会话 #' + currentSessionId) }}</span>
        </div>
        <div class="rh-review-wrap">
          <RecordingReview
            ref="review"
            :session-id="currentSessionId"
            @imported="onImported"
            @discarded="onDiscarded"
          />
        </div>
      </template>
    </div>
  </el-dialog>
</template>

<script>
/**
 * 录制履历 + 审阅台入口（P1）
 *
 * 为什么做成「一个弹窗里的两个视图」而不是新开一个路由页：
 *   本平台的路由与菜单是后端权限表驱动的（navigation/nav 表 + pathPermission），
 *   新增页面要同步改后端菜单数据，跨环境（161 / 本地）还要各配一遍。
 *   HAR 导入当初也是走「既有页面里开弹窗」这条路，复用同一套约定，零额外配置。
 *
 * 两个视图：
 *   · list   —— 会话列表（分页 / 状态 / 来源 / 关键词），双击一行即进入审阅
 *   · review —— 复用 RecordingReview 三栏审阅台
 */
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

import RecordingReview from './RecordingReview.vue'

const STATUS_OPTIONS = [
  { value: 1, label: '录制中' },
  { value: 2, label: '已结束' },
  { value: 3, label: '审阅中' },
  { value: 4, label: '已导入' },
  { value: 5, label: '已丢弃' }
]

// 取值来源 = RecordingSession.Source（会话侧字母表，不是解析器侧那套）
const SOURCE_OPTIONS = [
  { value: 'manual_upload', label: '手动导入录制文件' },
  { value: 'devtools_plugin', label: 'DevTools Recorder 插件' },
  { value: 'playwright_script', label: 'Playwright 脚本' },
  { value: 'extension', label: '浏览器扩展' },
  { value: 'cdp', label: 'CDP 接管' }
]

export default {
  name: 'RecordingHistory',
  components: { RecordingReview, ArrowLeft },
  props: {
    modelValue: { type: Boolean, default: false },
    /** 打开时直接进入该会话的审阅台（由「导入录制」流程跳转过来时用） */
    initialSessionId: { type: [Number, String], default: null }
  },
  emits: ['update:modelValue', 'imported'],
  data() {
    return {
      view: 'list',
      currentSessionId: null,
      currentName: '',
      loading: false,
      rows: [],
      count: 0,
      query: { page: 1, size: 20, keyword: '', status: '', source: '' },
      statusOptions: STATUS_OPTIONS,
      sourceOptions: SOURCE_OPTIONS,
      discarding: false
    }
  },
  computed: {
    visible: {
      get() { return this.modelValue },
      set(v) { this.$emit('update:modelValue', v) }
    }
  },
  watch: {
    modelValue: {
      immediate: true,
      handler(v) {
        if (!v) return
        // 每次打开都回到确定的状态：给了 initialSessionId 就直接进审阅，
        // 否则一定回到列表（否则会看到上次残留的那个会话）
        if (this.initialSessionId) {
          this.openSession(this.initialSessionId, '')
        } else {
          this.view = 'list'
          this.currentSessionId = null
          this.query.page = 1
          this.fetchList()
        }
      }
    }
  },
  methods: {
    liveProjectId() {
      const p = this.$store && this.$store.state && this.$store.state.projectInfo
      return (p && p.id) ? p.id : ''
    },
    statOf(row, key) {
      const s = row && row.stats
      if (!s || typeof s !== 'object') return 0
      return typeof s[key] === 'number' ? s[key] : 0
    },
    statusTagType(s) {
      switch (s) {
        case 1: return 'info'
        case 2: return 'primary'
        case 3: return 'warning'
        case 4: return 'success'
        default: return 'info'
      }
    },
    fmtTime(t) {
      if (!t) return '—'
      return String(t).replace('T', ' ').slice(0, 19)
    },
    async fetchList() {
      this.loading = true
      try {
        const params = {
          page: this.query.page,
          // ★ 分页参数是 size（后端 BasePageNumberPagination.page_size_query_param）
          size: this.query.size,
          project_id: this.liveProjectId() || undefined
        }
        if (this.query.keyword) params.keyword = this.query.keyword
        if (this.query.status !== '' && this.query.status !== null) params.status = this.query.status
        if (this.query.source) params.source = this.query.source
        const resp = await this.$api.recordingSessionList(params)
        if (resp.status !== 200) {
          const eb = resp.data || {}
          ElMessage({ type: 'error', showClose: true, duration: 8000,
            message: (eb.result || eb).detail || '加载录制履历失败' })
          return
        }
        // 分页响应含 results 键 ⇒ CustomRender 原样透传，不解 result
        const d = resp.data || {}
        this.rows = d.results || []
        this.count = typeof d.count === 'number' ? d.count : 0
      } catch (e) {
        ElMessage({ type: 'error', showClose: true, duration: 8000,
          message: '加载录制履历失败：' + (e && e.message ? e.message : e) })
      } finally {
        this.loading = false
      }
    },
    search() {
      this.query.page = 1
      this.fetchList()
    },
    reset() {
      this.query = { page: 1, size: this.query.size, keyword: '', status: '', source: '' }
      this.fetchList()
    },
    onSizeChange() {
      this.query.page = 1
      this.fetchList()
    },
    openSession(id, name) {
      this.currentSessionId = id
      this.currentName = name || ''
      this.view = 'review'
    },
    goReview(row) {
      if (!row) return
      this.openSession(row.id, row.name)
    },
    backToList() {
      this.view = 'list'
      this.currentSessionId = null
      this.currentName = ''
      this.fetchList()
    },
    openCase(row) {
      if (!row || !row.imported_case_id) return
      this.visible = false
      this.$router.push({ path: '/case/step/create/' + row.imported_case_id }).catch(() => {})
    },
    onImported() {
      // 落库后停在审阅台（用户可能还想改），只是刷新一下列表数据备用
      this.$emit('imported')
    },
    onDiscarded() {
      this.backToList()
    },
    async discardSession(row) {
      if (!row) return
      try {
        await ElMessageBox.confirm(
          `确定丢弃会话「${row.name}」？丢弃后不再出现在履历里（已生成的用例不受影响）。`,
          '提示',
          { type: 'warning', confirmButtonText: '确定丢弃', cancelButtonText: '取消' }
        )
      } catch (e) {
        return
      }
      this.discarding = true
      try {
        const resp = await this.$api.recordingSessionDiscard(row.id, {})
        if (resp.status !== 200) {
          const eb = resp.data || {}
          ElMessage({ type: 'error', message: (eb.result || eb).detail || '丢弃失败' })
          return
        }
        ElMessage.success('已丢弃')
        this.fetchList()
      } catch (e) {
        ElMessage({ type: 'error', message: '丢弃失败：' + (e && e.message ? e.message : e) })
      } finally {
        this.discarding = false
      }
    },
    /**
     * ★ 关闭前必须把审阅台里未保存的改动 flush 掉。
     *   审阅台的 patch 是 600ms 防抖的，用户改完最后一笔立刻点关闭，
     *   这 600ms 内的改动就丢了 —— 而且是「静默丢失」，最伤信任。
     */
    async handleBeforeClose(done) {
      const r = this.$refs.review
      if (this.view === 'review' && r) {
        const hasPending = r.patchTimer
          || r.saveState === 'dirty'
          || r.saveState === 'saving'
          || Object.keys(r.pendingEdits || {}).length
          || (r.pendingAssertions || []).length
          || (r.pendingDrops || []).length
        if (hasPending) {
          try {
            await r.flushPatch({ silent: true })
          } catch (e) {
            // 保存失败也不能把用户卡在弹窗里：改成显式提示
            ElMessage({ type: 'warning', showClose: true, duration: 8000,
              message: '有改动未能保存到录制会话（不影响已生成的用例），可稍后在审阅台重新加载确认。' })
          }
        }
      }
      done()
    },
    onClosed() {
      this.view = 'list'
      this.currentSessionId = null
      this.currentName = ''
    }
  }
}
</script>

<style scoped>
.rh-body {
  display: flex;
  flex-direction: column;
  height: 72vh;
  min-height: 0;
}
.rh-body.is-review { height: 76vh; }

/* ---------------- 列表视图 ---------------- */
.rh-toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex: none;
}
.rh-kw { width: 240px; }
.rh-sel { width: 150px; }
.rh-flex { flex: 1; }
.rh-count { color: var(--qm-text-3); font-size: 12px; }
.rh-table-wrap {
  flex: 1;
  min-height: 0;
}
.rh-stat { font-variant-numeric: tabular-nums; color: var(--qm-text-2); }
.rh-sep { color: var(--qm-text-3); margin: 0 2px; }
.rh-url {
  color: var(--qm-text-2);
  font-size: 12px;
}
.rh-pager {
  flex: none;
  display: flex;
  justify-content: flex-end;
  padding-top: 10px;
}

/* ---------------- 审阅视图 ---------------- */
.rh-review-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-bottom: 8px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--qm-line);
  flex: none;
}
.rh-review-title {
  font-weight: 600;
  color: var(--qm-text-1);
}
.rh-review-wrap {
  flex: 1;
  min-height: 0;
}
</style>
