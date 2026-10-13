<template>
  <div class="rec-review" v-loading="loading">
    <!-- ===================== 顶栏：会话身份 + 统计 ===================== -->
    <div class="rr-top">
      <div class="rr-top-left">
        <el-input
          v-model="sessionName"
          size="small"
          class="rr-name-input"
          placeholder="会话名称"
          maxlength="128"
          @change="onNameCommit"
        />
        <el-tag size="small" effect="plain">{{ sourceText }}</el-tag>
        <el-tag v-if="statusText" size="small" effect="plain" type="info">{{ statusText }}</el-tag>
        <span v-if="startUrl" class="rr-url" :title="startUrl">{{ startUrl }}</span>
      </div>
      <div class="rr-top-right">
        <span class="rr-stat"><b>{{ stat.kept }}</b> 条保留</span>
        <span class="rr-stat is-drop"><b>{{ stat.off }}</b> 条已取消</span>
        <span class="rr-stat"><b>{{ stat.elems }}</b> 个元素</span>
        <span class="rr-stat"><b>{{ stat.asserts }}</b> 条断言</span>
        <el-tag v-if="saveState === 'saving'" size="small" type="warning" effect="plain">保存中…</el-tag>
        <el-tag v-else-if="saveState === 'error'" size="small" type="danger" effect="plain">保存失败</el-tag>
        <el-tag v-else-if="saveState === 'dirty'" size="small" type="info" effect="plain">有未保存修改</el-tag>
        <el-tag v-else size="small" type="success" effect="plain">已同步</el-tag>
        <el-button link size="small" @click="reload">重新加载</el-button>
      </div>
    </div>

    <!-- ===================== 被自动忽略的动作（可折叠） =====================
         ★ 为什么一定要把这块露出来：用户最常问的是「我明明点了 30 下，怎么只有
           12 个步骤」。答案全在这里。藏起来 = 用户认为工具丢数据。 -->
    <div v-if="dropEntries.length" class="rr-drops">
      <div class="rr-drops-head" @click="dropOpen = !dropOpen">
        <el-icon><component :is="dropOpen ? 'ArrowDown' : 'ArrowRight'" /></el-icon>
        <span>解析时自动忽略 {{ dropTotal }} 条动作（点击{{ dropOpen ? '收起' : '查看原因' }}）</span>
      </div>
      <div v-if="dropOpen" class="rr-drops-body">
        <div v-for="(d, i) in dropEntries" :key="i" class="rr-drop-item">
          <span class="rr-drop-n">{{ d.count }}</span>
          <span class="rr-drop-t">{{ d.reason }}</span>
        </div>
      </div>
    </div>

    <!-- ===================== 三栏主体 ===================== -->
    <div class="rr-body">
      <!-- ---------- 左：动作列表 ---------- -->
      <section class="rr-col rr-left">
        <div class="rr-col-head">
          <span class="rr-col-title">动作（{{ actions.length }}）</span>
          <span class="rr-col-sub">{{ stat.kept }} 条将生成步骤</span>
        </div>
        <div class="rr-tools">
          <el-button link size="small" @click="setAll(true)">全选</el-button>
          <el-button link size="small" @click="setAll(false)">全不选</el-button>
          <el-button link size="small" @click="invert">反选</el-button>
          <span class="rr-flex"></span>
          <el-button link size="small" :disabled="!canMoveUp" @click="moveSel(-1)">上移</el-button>
          <el-button link size="small" :disabled="!canMoveDown" @click="moveSel(1)">下移</el-button>
          <el-button link size="small" :disabled="!canMoveUp" @click="moveToTop">置顶</el-button>
        </div>
        <div class="rr-left-list">
          <RecActionCard
            v-for="(a, i) in actions"
            :key="actionKey(a, i)"
            :action="a"
            :index="i"
            :active="a.seq === activeSeq"
            @select="selectAction"
            @toggle="onToggle"
          />
          <el-empty v-if="!actions.length" description="这份录制没有解析出任何动作" :image-size="70" />
        </div>
      </section>

      <!-- ---------- 中：定位器 + 参数 ---------- -->
      <section class="rr-col rr-mid">
        <template v-if="activeAction">
          <div class="rr-col-head">
            <span class="rr-col-title">第 {{ activeIndex + 1 }} 步 · {{ activeAction.keyword || activeAction.raw_type || '未映射关键字' }}</span>
            <el-tag v-if="activeAction.needs_review" size="small" type="warning" effect="plain">需复核</el-tag>
            <el-tag v-if="activeAction.sensitive" size="small" type="warning" effect="plain">凭据</el-tag>
          </div>

          <el-alert
            v-if="!activeAction.keyword"
            class="rr-alert"
            type="warning"
            :closable="false"
            show-icon
            title="这条动作没有映射到可执行关键字，落库时会被跳过。可以在描述里记录它的用途，或取消勾选把它排除。"
          />

          <div class="rr-block">
            <div class="rr-lb">步骤描述<span class="rr-lb-hint">（限 100 字，留空由平台按「关键字 + 元素名」自动生成）</span></div>
            <el-input
              :model-value="activeAction.desc || ''"
              size="small"
              maxlength="100"
              show-word-limit
              placeholder="例如 输入用户名"
              @update:model-value="onDescInput"
            />
          </div>

          <div class="rr-block">
            <RecLocatorPicker :element="activeAction.element || null" @pick="onPickLocator" />
          </div>

          <div class="rr-block">
            <div class="rr-lb">
              参数
              <span class="rr-lb-hint">（字面量 = 固定值；变量 = 落库时提取为用例变量，可跨步骤复用）</span>
            </div>
            <div v-if="!argKeys.length" class="rr-inline-empty">这一步没有可调参数。</div>
            <div v-for="k in argKeys" :key="k" class="rr-arg">
              <div class="rr-arg-head">
                <span class="rr-arg-key">{{ k }}</span>
                <el-radio-group
                  :model-value="argKind(k)"
                  size="small"
                  @update:model-value="(v) => onArgKind(k, v)"
                >
                  <el-radio-button label="literal">字面量</el-radio-button>
                  <el-radio-button label="variable">变量</el-radio-button>
                </el-radio-group>
                <el-tag v-if="argRedacted(k)" size="small" type="warning" effect="plain">原文未落库</el-tag>
              </div>
              <div class="rr-arg-body">
                <el-input
                  v-if="argKind(k) === 'variable'"
                  :model-value="argVarName(k)"
                  size="small"
                  maxlength="60"
                  placeholder="变量名，例如 Username"
                  @update:model-value="(v) => onArgVarName(k, v)"
                />
                <el-input
                  v-else
                  :model-value="argValue(k)"
                  size="small"
                  :disabled="argRedacted(k)"
                  :placeholder="argRedacted(k) ? '录进去的是凭据，原文没有入库；需要时改成变量并填默认值' : '参数值'"
                  @update:model-value="(v) => onArgValue(k, v)"
                />
              </div>
            </div>
          </div>

          <div v-if="activeAction.notes && activeAction.notes.length" class="rr-block">
            <div class="rr-lb">解析备注</div>
            <div v-for="(n, i) in activeAction.notes" :key="i" class="rr-note">{{ n }}</div>
          </div>
        </template>
        <el-empty
          v-else
          description="从左侧选一条动作，这里就能改它的定位器与参数"
          :image-size="70"
        />
      </section>

      <!-- ---------- 右：断言 + 落库归属 ---------- -->
      <section class="rr-col rr-right">
        <div class="rr-col-head">
          <span class="rr-col-title">断言</span>
          <span class="rr-col-sub">共 {{ activeAssertions.length }} 条</span>
        </div>
        <RecAssertionPanel
          :assertions="activeAssertions"
          :seq="activeSeq"
          @add="onAddAssertion"
          @remove="onRemoveAssertion"
        />

        <el-divider class="rr-divider" />

        <div class="rr-col-head">
          <span class="rr-col-title">落库归属</span>
        </div>
        <div class="rr-block">
          <div class="rr-lb">导入方式</div>
          <el-radio-group v-model="importMode" size="small">
            <el-radio-button label="new_case">新建用例</el-radio-button>
            <el-radio-button label="append_steps">追加到已有用例</el-radio-button>
          </el-radio-group>
        </div>
        <div v-if="importMode === 'new_case'" class="rr-block">
          <div class="rr-lb">用例名称<span class="rr-lb-hint">（限 50 字，留空自动命名）</span></div>
          <el-input v-model="caseName" size="small" maxlength="50" placeholder="例如 登录流程录制回放" />
        </div>
        <div v-else class="rr-block">
          <div class="rr-lb">目标用例<span class="rr-lb-hint">（只列 Web 自动化用例）</span></div>
          <el-select
            v-model="targetCaseId"
            size="small"
            filterable
            style="width: 100%"
            placeholder="选择要追加的用例"
            :loading="casesLoading"
          >
            <el-option v-for="c in webCases" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </div>
        <div class="rr-block">
          <div class="rr-lb">所属模块<span class="rr-lb-hint">（留空由平台建「录制-日期」模块）</span></div>
          <el-select
            v-model="moduleId"
            size="small"
            filterable
            clearable
            style="width: 100%"
            placeholder="默认：自动创建录制模块"
            :loading="modulesLoading"
          >
            <el-option
              v-for="m in flatModules"
              :key="m.id"
              :label="m.label"
              :value="m.id"
              :disabled="m.disabled"
            />
          </el-select>
        </div>
        <div class="rr-block">
          <el-checkbox v-model="importAssertions" size="small">把断言一并落库</el-checkbox>
        </div>
      </section>
    </div>

    <!-- ===================== 底栏 ===================== -->
    <div class="rr-foot">
      <div class="rr-foot-left">
        <el-icon class="rr-foot-icon"><InfoFilled /></el-icon>
        <span>编辑只写入录制会话，不产生任何用例数据；点「生成步骤用例」才真正落库。</span>
      </div>
      <div class="rr-foot-right">
        <el-button size="small" :loading="discarding" @click="discardSession">丢弃本次录制</el-button>
        <el-button size="small" :loading="saveState === 'saving'" @click="flushPatch({})">保存审阅</el-button>
        <el-button type="primary" size="small" :loading="importing" @click="doImport">
          生成步骤用例
        </el-button>
      </div>
    </div>

    <!-- ===================== 落库结果 ===================== -->
    <el-dialog
      v-model="resultVisible"
      title="落库结果"
      width="640"
      :append-to-body="true"
      :z-index="1010"
      destroy-on-close
    >
      <div v-if="result" class="rr-result">
        <div class="rr-result-line">
          <span class="rr-result-lb">用例</span>
          <span class="rr-result-vv">
            {{ result.case_name }}
            <el-tag v-if="result.case_created" size="small" type="success" effect="plain">新建</el-tag>
            <el-tag v-else size="small" effect="plain">追加</el-tag>
          </span>
        </div>
        <div class="rr-result-line">
          <span class="rr-result-lb">模块</span>
          <span class="rr-result-vv">{{ result.module_name }}</span>
        </div>
        <div class="rr-result-line">
          <span class="rr-result-lb">步骤</span>
          <span class="rr-result-vv">
            共 {{ result.step_count }} 条（动作 {{ result.action_step_count }} / 校验 {{ result.verify_step_count }}）
          </span>
        </div>
        <div class="rr-result-line">
          <span class="rr-result-lb">断言</span>
          <span class="rr-result-vv">{{ result.assertion_count }} 条</span>
        </div>
        <div class="rr-result-line">
          <span class="rr-result-lb">元素</span>
          <span class="rr-result-vv">
            新增 {{ (result.elements || {}).created || 0 }} / 复用 {{ (result.elements || {}).reused || 0 }}
          </span>
        </div>
        <div v-if="(result.variables || []).length" class="rr-result-line">
          <span class="rr-result-lb">变量</span>
          <span class="rr-result-vv">
            <el-tag
              v-for="v in result.variables"
              :key="v.name"
              size="small"
              effect="plain"
              class="rr-var-tag"
            >{{ v.name }}</el-tag>
          </span>
        </div>
        <div v-if="(result.skipped_actions || []).length" class="rr-result-line">
          <span class="rr-result-lb">跳过</span>
          <span class="rr-result-vv">
            {{ result.skipped_actions.length }} 条
            <div v-for="(s, i) in result.skipped_actions" :key="i" class="rr-skip">
              seq={{ s.seq }}：{{ s.reason }}
            </div>
          </span>
        </div>
        <div v-if="(result.deferred_assertions || []).length" class="rr-result-line">
          <span class="rr-result-lb">待补断言</span>
          <span class="rr-result-vv">
            {{ result.deferred_assertions.length }} 条（期望值需要人工填写）
          </span>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="small" @click="resultVisible = false">关闭</el-button>
          <el-button type="primary" size="small" @click="goToCase">打开用例</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
/**
 * 录制审阅台（P1 核心）
 *
 * ============================ 三条铁律 ============================
 * ① **编辑不落库，落库是一次原子动作**
 *    所有改动都通过 `/recording/session/<id>/patch/` 写进会话的 `ir_payload`，
 *    一个 `tb_step` 都不会产生。只有「生成步骤用例」那一次 `/recording/import/`
 *    才真正写库。好处：用户反复试错不产生脏数据，中途关掉浏览器也不留垃圾。
 *
 * ② **patch 是「绝对覆盖式」的，所以本组件永远发全量结构状态**
 *    `keep_seqs` 给全 → 服务端以此为准把其余置 `enabled=false`；
 *    `order` 给全 → 服务端按它稳定排序。
 *    因为是覆盖式，重复发送天然幂等 —— 这正是防抖/重试安全的根据。
 *
 * ③ **显示侧的统计口径必须与后端三方一致**
 *    `element_ref` → 解析期 / 落库期 / 重算期都用它。
 *    ★ 踩过的坑：曾用 `locators[0]` 的 `by:value` 拼串去重，丢掉了 `opts`，
 *      而 role 类候选的 value 只是角色名（textbox/button），真正的区分度在
 *      `opts.name` 上 ⇒ 页面上所有文本框被算成一个元素，且「改一下定位器
 *      元素数就跳」。详见后端 `_recount_ir` 的注释。
 *
 * ======================= 为什么是「防抖 patch」而不是「每次点击都 patch」=======
 * 每次勾选都发一次 patch 意味着：一次 50 条动作的会话，用户连点几下就会
 * 触发十几次「整块 JSONField 重写」。所以本地立即生效（乐观更新）+ 600ms
 * 防抖合并成一次请求；同时保留「保存审阅」做显式落盘。
 *
 * ★ 断言是**追加语义**（后端 `assertions[]` 是 append），所以必须「发送即出队」：
 *   若像其它字段那样留在本地等下一次防抖合并，同一条断言会被追加两次。
 *   本组件为此单独维护 `pendingAssertions` / `pendingDrops` 两个缓冲。
 */
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowRight, ArrowDown, InfoFilled } from '@element-plus/icons-vue'

import RecActionCard from './ActionCard.vue'
import RecLocatorPicker from './LocatorPicker.vue'
import RecAssertionPanel from './AssertionPanel.vue'

// 与会话侧 `RecordingSession.Source` 对齐（后端 get_source_display 已给中文，这里只做兜底）
const SOURCE_TEXT = {
  manual_upload: '手动导入录制文件',
  extension: '浏览器扩展（实时推送）',
  devtools_plugin: 'DevTools Recorder 插件',
  cdp: 'CDP 接管',
  playwright_script: 'Playwright 脚本'
}

// 可调参数白名单：其余键（selector / opts / frame_path 之类）是结构信息，改它们没有意义
const ARG_WHITELIST = [
  'value', 'text', 'key', 'key_name', 'uri', 'url', 'direction',
  'file_path', 'expect', 'timeout', 'index', 'option', 'label', 'name'
]

export default {
  name: 'RecordingReview',
  components: { RecActionCard, RecLocatorPicker, RecAssertionPanel, ArrowRight, ArrowDown, InfoFilled },
  props: {
    /** 录制会话 id */
    sessionId: { type: [Number, String], required: true }
  },
  emits: ['imported', 'discarded'],
  data() {
    return {
      loading: false,
      session: null,
      ir: { actions: [], stats: {} },
      sessionName: '',
      activeSeq: null,
      dropOpen: false,

      // 保存状态机：idle（已同步）/ dirty（有未保存）/ saving / error
      saveState: 'idle',
      patchTimer: null,

      // 待提交缓冲
      pendingEdits: {},        // seq -> { desc?, locator?, value? }，value 内含 arg
      pendingAssertions: [],   // 追加语义，发送即出队
      pendingDrops: [],        // 删除语义，发送即出队
      enabledDirty: false,     // 启停变更（决定是否发 keep_seqs）
      orderDirty: false,       // 顺序变更（决定是否发 order）

      // 落库归属
      importMode: 'new_case',
      caseName: '',
      targetCaseId: null,
      moduleId: null,
      importAssertions: true,
      moduleTree: [],
      modulesLoading: false,
      webCases: [],
      casesLoading: false,

      importing: false,
      discarding: false,
      resultVisible: false,
      result: null,

      // 服务端回传的统计（显示权威值 + 校验本地口径是否漂移）
      serverSummary: null,
      // 口径漂移告警限流：只在控制台吼一声，不自动重载（避免打断用户）
      mismatchGuard: 0
    }
  },
  computed: {
    actions() {
      return Array.isArray(this.ir.actions) ? this.ir.actions : []
    },
    startUrl() {
      return (this.session && this.session.start_url) || (this.ir.meta && this.ir.meta.start_url) || ''
    },
    sourceText() {
      if (this.session && this.session.source_display) return this.session.source_display
      const s = (this.session && this.session.source) || ''
      return SOURCE_TEXT[s] || s || '未知来源'
    },
    statusText() {
      return (this.session && this.session.status_display) || ''
    },
    /**
     * 本地乐观统计 —— 口径必须与后端 `_recount_ir` **严格一致**。
     * ★ 元素去重一律用 `element_ref`（normalizer 用 `by|value|opts` 三重指纹生成），
     *   退化时才用 `name|by|value`。绝不能用 `locators[0]` 的 `by:value` 拼串：
     *   role 类候选的 value 只是角色名（textbox/button），丢了 opts 就会把页面上
     *   所有文本框算成同一个元素，还会出现「改一下定位器元素数自己跳」。
     */
    localStat() {
      const kept = this.actions.filter((a) => a.enabled !== false)
      const refs = new Set()
      kept.forEach((a) => {
        const el = a.element || {}
        let r = el.element_ref
        if (!r) {
          const l0 = (el.locators || [])[0]
          if (l0) r = `${el.name || ''}|${l0.by}|${l0.value}`
        }
        if (r) refs.add(r)
      })
      return {
        kept: kept.length,
        off: this.actions.length - kept.length,
        elems: refs.size,
        asserts: kept.reduce((n, a) => n + ((a.assertions || []).length), 0)
      }
    },
    /** 服务端权威统计（来自 detail 的 summary 或 patch 回传的 summary） */
    serverStat() {
      const s = this.serverSummary
      if (!s) return null
      const kept = typeof s.kept_actions === 'number' ? s.kept_actions : null
      if (kept === null) return null
      return {
        kept,
        off: this.actions.length - kept,
        elems: typeof s.elements_unique === 'number' ? s.elements_unique : 0,
        asserts: typeof s.assertions === 'number' ? s.assertions : 0
      }
    },
    /**
     * 显示用统计。
     * ★ 为什么分两套：有未提交改动时必须显示本地乐观值 —— 否则用户勾掉几条，
     *   顶上数字纹丝不动，会以为「勾选坏了」；而一旦同步完成，就该显示服务端
     *   权威值 —— 那才是真正会被落库的口径。两套值不一致只可能是本地公式有
     *   偏差，`_verifyAgainstServer` 会在控制台留痕。
     */
    stat() {
      if (this.saveState === 'idle' && this.serverStat) return this.serverStat
      return this.localStat
    },
    dropEntries() {
      const d = (this.ir.stats && this.ir.stats.drop_reasons) || {}
      return Object.keys(d).map((k) => ({ reason: k, count: d[k] }))
        .sort((a, b) => b.count - a.count)
    },
    dropTotal() {
      return this.dropEntries.reduce((n, d) => n + d.count, 0)
    },
    activeIndex() {
      return this.actions.findIndex((a) => a.seq === this.activeSeq)
    },
    activeAction() {
      return this.activeIndex >= 0 ? this.actions[this.activeIndex] : null
    },
    activeAssertions() {
      const a = this.activeAction
      return (a && Array.isArray(a.assertions)) ? a.assertions : []
    },
    canMoveUp() {
      return this.activeIndex > 0
    },
    canMoveDown() {
      return this.activeIndex >= 0 && this.activeIndex < this.actions.length - 1
    },
    argKeys() {
      const a = this.activeAction
      if (!a || !a.args || typeof a.args !== 'object') return []
      const out = []
      Object.keys(a.args).forEach((k) => {
        if (this._normVal(a.args[k]) === null) return
        // 白名单优先；白名单外的字符串值也允许改（不同关键字参数名不统一）
        if (ARG_WHITELIST.indexOf(k) >= 0 || typeof a.args[k] === 'string') out.push(k)
      })
      return out
    },
    flatModules() {
      const out = []
      const walk = (nodes, depth) => {
        (nodes || []).forEach((n) => {
          out.push({
            id: n.id,
            label: '　'.repeat(depth) + (n.name || ('模块 ' + n.id)),
            // 根节点 id < 0，是「产品」层，不能作为用例所属模块
            disabled: typeof n.id === 'number' && n.id < 0
          })
          if (n.children && n.children.length) walk(n.children, depth + 1)
        })
      }
      walk(this.moduleTree, 0)
      return out
    }
  },
  watch: {
    sessionId: {
      immediate: true,
      handler(v) {
        if (!v) {
          this.session = null
          this.ir = { actions: [], stats: {} }
          this.activeSeq = null
          return
        }
        this.load()
      }
    }
  },
  created() {
    this.loadModules()
    this.loadWebCases()
  },
  beforeUnmount() {
    // ★ 必须是 beforeUnmount（Vue 3）：`beforeDestroy` 在 Vue 3 里**根本不会被调用**，
    //   写成后者等于「组件销毁了定时器还在跑」，回调里再摸 this.$api 就会报错。
    //   全站统一用 beforeUnmount，改的时候别顺手写回老名字。
    if (this.patchTimer) clearTimeout(this.patchTimer)
  },
  methods: {
    liveProjectId() {
      const p = this.$store && this.$store.state && this.$store.state.projectInfo
      return (p && p.id) ? p.id : ''
    },
    actionKey(a, i) {
      return (a && a.seq !== null && a.seq !== undefined) ? 's' + a.seq : 'i' + i
    },
    resetPending() {
      this.pendingEdits = {}
      this.pendingAssertions = []
      this.pendingDrops = []
      this.enabledDirty = false
      this.orderDirty = false
      if (this.patchTimer) {
        clearTimeout(this.patchTimer)
        this.patchTimer = null
      }
    },

    // ---------------------------------------------------------------
    // 加载
    // ---------------------------------------------------------------
    async load() {
      this.loading = true
      try {
        const resp = await this.$api.recordingSessionDetail(this.sessionId)
        if (resp.status !== 200) {
          const eb = resp.data || {}
          ElMessage({
            type: 'error', duration: 8000, showClose: true,
            message: (eb.result || eb).detail || '加载录制会话失败'
          })
          return
        }
        // ★ CustomRender 会把 dict 包成 {code,msg,result}，必须解一层
        const rb = resp.data || {}
        const d = rb.result || rb
        this.session = d
        const ir = d.ir_payload || {}
        if (!Array.isArray(ir.actions)) ir.actions = []
        if (!ir.stats) ir.stats = {}
        this.ir = ir
        // 详情端点会附带 summary（= NZ.summarize(ir_payload)），作为统计的权威值
        this.serverSummary = d.summary || null
        this.mismatchGuard = 0
        this.sessionName = d.name || ''
        // 默认选中第一条「未取消」的动作（全是取消的就选第一条，便于整体复核）
        const first = ir.actions.find((a) => a.enabled !== false) || ir.actions[0]
        this.activeSeq = first ? first.seq : null
        this.resetPending()
        this.saveState = 'idle'
      } catch (e) {
        ElMessage({ type: 'error', duration: 8000, showClose: true,
          message: '加载录制会话失败：' + (e && e.message ? e.message : e) })
      } finally {
        this.loading = false
      }
    },
    async reload() {
      if (this.saveState === 'dirty' || this.saveState === 'saving') {
        try {
          await ElMessageBox.confirm(
            '当前有未保存的修改，重新加载会丢弃它们。确定继续？', '提示',
            { type: 'warning', confirmButtonText: '丢弃并重新加载', cancelButtonText: '取消' }
          )
        } catch (e) {
          return
        }
      }
      await this.load()
    },
    async loadModules() {
      const pid = this.liveProjectId()
      if (!pid) return
      this.modulesLoading = true
      try {
        const resp = await this.$api.getAllPlantModule({ project: pid })
        if (resp.status === 200) {
          // ★ 必须回落成 []：后端在空上下文下不返回 results，
          //   直接赋值会让 el-tree / v-for 拿到 undefined
          const body = (resp.data && resp.data.results) || []
          this.moduleTree = body
        }
      } catch (e) {
        this.moduleTree = []
      } finally {
        this.modulesLoading = false
      }
    },
    async loadWebCases() {
      const pid = this.liveProjectId()
      if (!pid) return
      this.casesLoading = true
      try {
        // type=2 即 Case.FunctionCaseType.WEB_UI —— 录制只能追加到 Web 自动化用例
        const resp = await this.$api.getCases({ project: pid, type: 2, size: 200 })
        if (resp.status === 200) {
          const d = resp.data || {}
          this.webCases = (d.results) || []
        }
      } catch (e) {
        this.webCases = []
      } finally {
        this.casesLoading = false
      }
    },

    // ---------------------------------------------------------------
    // 选择 / 勾选 / 排序
    // ---------------------------------------------------------------
    selectAction(a) {
      this.activeSeq = a.seq
    },
    onToggle(action, v) {
      if (!action) return
      action.enabled = !!v
      this.enabledDirty = true
      this.schedulePatch()
    },
    setAll(v) {
      this.actions.forEach((a) => { a.enabled = !!v })
      this.enabledDirty = true
      this.schedulePatch()
    },
    invert() {
      this.actions.forEach((a) => { a.enabled = a.enabled === false })
      this.enabledDirty = true
      this.schedulePatch()
    },
    _move(from, to) {
      const arr = this.ir.actions
      if (to < 0 || to >= arr.length) return
      const [x] = arr.splice(from, 1)
      arr.splice(to, 0, x)
      // 选中项跟着走，用户视线不会丢
      this.orderDirty = true
      this.schedulePatch()
    },
    moveSel(dir) {
      const i = this.activeIndex
      if (i < 0) return
      this._move(i, i + dir)
    },
    moveToTop() {
      const i = this.activeIndex
      if (i <= 0) return
      this._move(i, 0)
    },
    onNameCommit(v) {
      const name = (v || '').trim()
      if (!name) {
        ElMessage.warning('会话名不能为空')
        this.sessionName = (this.session && this.session.name) || ''
        return
      }
      if (name === ((this.session && this.session.name) || '')) return
      this.schedulePatch()
    },

    // ---------------------------------------------------------------
    // 定位器 / 描述 / 参数
    // ---------------------------------------------------------------
    _pe(seq) {
      if (!Number.isInteger(seq)) return null
      // ★ Vue 3 的响应式是 Proxy 实现的，**新增键本身就是响应式的**，
      //   所以不需要（也没有）`this.$set`。写成 `this.$set(...)` 会直接
      //   `TypeError: this.$set is not a function` —— 本项目 Vue 3.3，
      //   main.js 里也没有注册 $set 垫片。全站残留的 2 处 $set 是历史遗留缺陷。
      if (!this.pendingEdits[seq]) this.pendingEdits[seq] = {}
      return this.pendingEdits[seq]
    },
    onDescInput(v) {
      const a = this.activeAction
      if (!a) return
      a.desc = (v || '').slice(0, 100)
      const pe = this._pe(a.seq)
      if (pe) pe.desc = a.desc
      this.schedulePatch()
    },
    onPickLocator(cand) {
      const a = this.activeAction
      if (!a || !cand) return
      if (!Number.isInteger(a.seq)) {
        ElMessage.warning('这条动作没有 seq，无法单独保存定位器修改')
        return
      }
      // 本地立即生效：提到首位 + 标 pinned + 置信度拉满（与后端 patch 行为一致，
      // 否则用户会看到「点了以后琥珀色标记没消失」，以为没生效）
      const el = a.element || (a.element = {})
      const locs = Array.isArray(el.locators) ? el.locators : []
      const head = Object.assign({}, cand, {
        source: 'manual', pinned: true,
        score: Math.max(cand.score || 0, 0.99)
      })
      el.locators = [head].concat(locs.filter(
        (c) => !(String(c.by || '').toLowerCase() === String(cand.by || '').toLowerCase()
          && String(c.value || '') === String(cand.value || ''))
      ))
      // ★ 刻意不重算 el.element_ref（设计决策）：它是「同一元素在本次录制里的身份」，
      //   改的只是「用哪个定位器找它」。保持 ref 不变，同一元素的另一处出现仍能
      //   合并成一条元素记录；旧定位器则被落库时的 _merge_alternatives 收进备选链。
      //   详见后端 patch 处的说明。
      a.confidence = 1.0
      a.needs_review = false
      const pe = this._pe(a.seq)
      if (pe) pe.locator = { by: cand.by, value: cand.value, opts: cand.opts || {} }
      this.schedulePatch()
    },
    _normVal(v) {
      if (v === null || v === undefined) return null
      if (typeof v === 'object' && !Array.isArray(v)) {
        if (!v.kind) return null
        return {
          kind: v.kind === 'variable' ? 'variable' : 'literal',
          value: v.value,
          var_name: v.var_name,
          redacted: !!v.redacted
        }
      }
      if (typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean') {
        return { kind: 'literal', value: v }
      }
      return null
    },
    argKind(k) {
      const a = this.activeAction
      const nv = a ? this._normVal((a.args || {})[k]) : null
      return nv ? nv.kind : 'literal'
    },
    argValue(k) {
      const a = this.activeAction
      const nv = a ? this._normVal((a.args || {})[k]) : null
      if (!nv) return ''
      return nv.value === null || nv.value === undefined ? '' : String(nv.value)
    },
    argVarName(k) {
      const a = this.activeAction
      const nv = a ? this._normVal((a.args || {})[k]) : null
      return (nv && nv.var_name) ? nv.var_name : ''
    },
    argRedacted(k) {
      const a = this.activeAction
      const nv = a ? this._normVal((a.args || {})[k]) : null
      return !!(nv && nv.redacted)
    },
    _commitArg(k, next) {
      const a = this.activeAction
      if (!a) return
      if (!a.args || typeof a.args !== 'object') a.args = {}
      a.args[k] = next
      const pe = this._pe(a.seq)
      if (pe) pe.value = { arg: k, kind: next.kind, var_name: next.var_name || '', value: next.value }
      this.schedulePatch()
    },
    onArgKind(k, kind) {
      const prev = this.argValue(k)
      if (kind === 'variable') {
        this._commitArg(k, { kind: 'variable', var_name: this.argVarName(k) || '', value: prev })
      } else {
        this._commitArg(k, { kind: 'literal', value: prev })
      }
    },
    onArgValue(k, v) {
      const cur = this.activeAction && this._normVal((this.activeAction.args || {})[k])
      if (cur && cur.kind === 'variable') {
        this._commitArg(k, { kind: 'variable', var_name: this.argVarName(k), value: v })
      } else {
        this._commitArg(k, { kind: 'literal', value: v })
      }
    },
    onArgVarName(k, v) {
      const cur = this.activeAction && this._normVal((this.activeAction.args || {})[k])
      this._commitArg(k, {
        kind: 'variable',
        var_name: (v || '').slice(0, 60),
        value: cur ? cur.value : ''
      })
    },

    // ---------------------------------------------------------------
    // 断言（追加 / 删除，都是「发送即出队」）
    // ---------------------------------------------------------------
    onAddAssertion(spec) {
      const a = this.activeAction
      if (!a) return
      if (!Number.isInteger(a.seq)) {
        ElMessage.warning('这条动作没有 seq，无法挂断言')
        return
      }
      const item = {
        method: spec.method,
        expect: spec.expect,
        extract_keyword: spec.extract_keyword,
        extract_args: spec.extract_args || {},
        rule: 'manual',
        auto: true,
        brittle: false,
        manual: true
      }
      if (!Array.isArray(a.assertions)) a.assertions = []
      a.assertions.push(item)
      this.pendingAssertions.push({
        seq: a.seq,
        method: item.method,
        expect: item.expect,
        extract_keyword: item.extract_keyword,
        extract_args: item.extract_args
      })
      // ★ 不等防抖：追加语义的东西留在缓冲里会被重复发送
      this.flushPatch({ silent: true })
    },
    onRemoveAssertion(idx) {
      const a = this.activeAction
      if (!a || !Array.isArray(a.assertions)) return
      const item = a.assertions[idx]
      if (!item) return
      a.assertions.splice(idx, 1)
      // 若这条断言从未成功发送过，直接从缓冲里撤掉，不必打扰服务端
      const bi = this.pendingAssertions.findIndex((x) => x.seq === a.seq
        && x.method === item.method
        && x.extract_keyword === item.extract_keyword
        && String(x.expect === null || x.expect === undefined ? '' : x.expect)
            === String(item.expect === null || item.expect === undefined ? '' : item.expect))
      if (bi >= 0) {
        this.pendingAssertions.splice(bi, 1)
        return
      }
      this.pendingDrops.push({
        seq: a.seq,
        method: item.method,
        extract_keyword: item.extract_keyword,
        expect: item.expect
      })
      this.flushPatch({ silent: true })
    },

    // ---------------------------------------------------------------
    // patch：防抖 + 显式 flush
    // ---------------------------------------------------------------
    schedulePatch() {
      this.saveState = 'dirty'
      if (this.patchTimer) clearTimeout(this.patchTimer)
      this.patchTimer = setTimeout(() => {
        this.patchTimer = null
        this.flushPatch({ silent: true })
      }, 600)
    },
    _buildPatch() {
      const body = {}
      let any = false
      if (this.sessionName && this.sessionName.trim()
          && this.sessionName.trim() !== ((this.session && this.session.name) || '')) {
        body.name = this.sessionName.trim().slice(0, 128)
        any = true
      }
      if (this.enabledDirty) {
        body.keep_seqs = this.actions
          .filter((a) => a.enabled !== false && Number.isInteger(a.seq))
          .map((a) => a.seq)
        any = true
      }
      if (this.orderDirty) {
        body.order = this.actions.filter((a) => Number.isInteger(a.seq)).map((a) => a.seq)
        any = true
      }
      const edits = this.pendingEdits
      const editKeys = Object.keys(edits)
      if (editKeys.length) {
        body.actions = {}
        editKeys.forEach((k) => {
          if (Object.keys(edits[k] || {}).length) body.actions[k] = edits[k]
        })
        if (Object.keys(body.actions).length) any = true
        else delete body.actions
      }
      if (this.pendingAssertions.length) {
        body.assertions = this.pendingAssertions.slice()
        any = true
      }
      if (this.pendingDrops.length) {
        body.drop_assertions = this.pendingDrops.slice()
        any = true
      }
      return any ? body : null
    },
    /**
     * 把当前全部待提交改动发给 patch 端点。
     * @returns {Promise<boolean>} 是否成功（失败时调用方应中止后续动作）
     */
    async flushPatch(opts) {
      const silent = !!(opts && opts.silent)
      if (this.patchTimer) {
        clearTimeout(this.patchTimer)
        this.patchTimer = null
      }
      if (!this.sessionId) return false
      const body = this._buildPatch()
      if (!body) {
        this.saveState = 'idle'
        return true
      }

      // ★ 发送前快照 + 立即出队：防抖/重试/并发都不会造成重复追加
      const snapEdits = JSON.parse(JSON.stringify(this.pendingEdits))
      const snapAsserts = this.pendingAssertions.slice()
      const snapDrops = this.pendingDrops.slice()
      const sentEnabled = this.enabledDirty
      const sentOrder = this.orderDirty
      this.pendingEdits = {}
      this.pendingAssertions = []
      this.pendingDrops = []
      this.enabledDirty = false
      this.orderDirty = false

      this.saveState = 'saving'
      let resp
      try {
        resp = await this.$api.recordingSessionPatch(this.sessionId, body)
      } catch (e) {
        this._restorePending(snapEdits, snapAsserts, snapDrops, sentEnabled, sentOrder)
        this.saveState = 'error'
        ElMessage({ type: 'error', duration: 8000, showClose: true,
          message: '保存审阅失败：' + (e && e.message ? e.message : e) })
        return false
      }
      if (resp.status !== 200) {
        this._restorePending(snapEdits, snapAsserts, snapDrops, sentEnabled, sentOrder)
        this.saveState = 'error'
        if (!silent) {
          const eb = resp.data || {}
          ElMessage({ type: 'error', duration: 8000, showClose: true,
            message: (eb.result || eb).detail || '保存审阅失败' })
        }
        return false
      }

      const rb = resp.data || {}
      const d = rb.result || rb
      // 后端权威统计回传 —— 用它校验「本地口径」与「服务端口径」是否漂移。
      // 正常永远一致；一旦不一致说明本地模型偏了，静默重载一次硬对齐
      // （只做一次，避免任何形式的循环）。
      this._verifyAgainstServer(d)

      // 若期间又有新改动（用户还在打字），保持 dirty；否则回到 idle
      if (this._buildPatch() || this.patchTimer) this.saveState = 'dirty'
      else this.saveState = 'idle'
      return true
    },
    _restorePending(snapEdits, snapAsserts, snapDrops, sentEnabled, sentOrder) {
      // 恢复为「未发送」状态：先合并回快照，再叠加用户在飞行期间产生的新改动
      const cur = this.pendingEdits
      Object.keys(snapEdits).forEach((k) => {
        this.pendingEdits[k] = Object.assign({}, snapEdits[k], cur[k] || {})
      })
      this.pendingAssertions = snapAsserts.concat(this.pendingAssertions)
      this.pendingDrops = snapDrops.concat(this.pendingDrops)
      this.enabledDirty = this.enabledDirty || sentEnabled
      this.orderDirty = this.orderDirty || sentOrder
    },
    _verifyAgainstServer(d) {
      const s = d && d.summary
      if (!s) return
      // ★ 必须在覆盖 ir 之前先取本地快照，否则拿到的是「覆盖之后」的值，
      //   两边永远相等，这个校验就变成了永远不会响的摆设。
      const localKept = this.localStat.kept
      const localElems = this.localStat.elems

      // 服务端已按 enabled 过滤、按 order 重排、按 desc 截断 —— 它是权威。
      // 但只有在「没有待提交改动」时才替换，否则会盖掉用户正在输入的文本。
      if (d.ir && Array.isArray(d.ir.actions) && !this._buildPatch() && !this.patchTimer) {
        this.ir = d.ir
        if (this.activeIndex < 0 && this.ir.actions.length) {
          this.activeSeq = this.ir.actions[0].seq
        }
      }
      this.serverSummary = s

      const srvKept = s.kept_actions
      const srvElems = s.elements_unique
      const driftKept = (typeof srvKept === 'number' && localKept !== srvKept)
      const driftElems = (typeof srvElems === 'number' && localElems !== srvElems)
      if ((driftKept || driftElems) && this.mismatchGuard < 3) {
        this.mismatchGuard += 1
        // eslint-disable-next-line no-console
        console.warn('[REC-REVIEW] 本地统计与后端口径不一致：'
          + '动作 本地=%s 后端=%s；元素 本地=%s 后端=%s。'
          + '显示已切换为后端权威值，请核对两侧的统计公式。',
          localKept, srvKept, localElems, srvElems)
      }
      if (this.session) {
        this.session.status_display = d.status_display || this.session.status_display
        this.session.name = d.name || this.session.name
      }
    },

    // ---------------------------------------------------------------
    // 落库
    // ---------------------------------------------------------------
    async doImport() {
      if (!this.actions.length) {
        ElMessage.warning('这份录制没有可落库的动作')
        return
      }
      if (!this.localStat.kept) {
        ElMessage.warning('所有动作都已被取消，没有可落库的内容')
        return
      }
      if (this.importMode === 'append_steps' && !this.targetCaseId) {
        ElMessage.warning('追加模式需要先选择目标用例')
        return
      }
      // ★ 先 flush：确保服务端 IR 就是用户眼前这一份。
      //   只传 session_id 而不传整份 ir，可以避开 2.5MB JSON body 上限的风险。
      const ok = await this.flushPatch({ silent: false })
      if (!ok) {
        ElMessage.warning('还有修改没有保存成功，已中止落库（避免落进旧版本）')
        return
      }
      this.importing = true
      try {
        const payload = {
          project_id: this.liveProjectId(),
          session_id: this.sessionId,
          mode: this.importMode,
          import_assertions: this.importAssertions
        }
        if (this.importMode === 'append_steps') payload.case_id = this.targetCaseId
        if (this.caseName && this.caseName.trim()) payload.case_name = this.caseName.trim()
        if (this.moduleId) payload.module_id = this.moduleId

        const resp = await this.$api.recordingImport(payload)
        if (resp.status !== 200) {
          const eb = resp.data || {}
          ElMessage({ type: 'error', duration: 8000, showClose: true,
            message: (eb.result || eb).detail || '落库失败' })
          return
        }
        const rb = resp.data || {}
        const d = rb.result || rb
        this.result = d
        this.resultVisible = true
        this.saveState = 'idle'
        ElMessage.success(`已生成用例「${d.case_name}」，共 ${d.step_count} 条步骤`)
        this.$emit('imported', d)
        await this.load()
      } catch (e) {
        ElMessage({ type: 'error', duration: 8000, showClose: true,
          message: '落库失败：' + (e && e.message ? e.message : e) })
      } finally {
        this.importing = false
      }
    },
    goToCase() {
      const id = this.result && this.result.case_id
      if (!id) return
      this.resultVisible = false
      this.$emit('imported', this.result)
      this.$router.push({ path: '/case/step/create/' + id }).catch(() => {})
    },
    async discardSession() {
      try {
        await ElMessageBox.confirm(
          '丢弃后这个录制会话不会再出现在履历里（已生成的用例不受影响）。确定丢弃？',
          '提示',
          { type: 'warning', confirmButtonText: '确定丢弃', cancelButtonText: '取消' }
        )
      } catch (e) {
        return
      }
      this.discarding = true
      try {
        const resp = await this.$api.recordingSessionDiscard(this.sessionId, {})
        if (resp.status !== 200) {
          const eb = resp.data || {}
          ElMessage({ type: 'error', message: (eb.result || eb).detail || '丢弃失败' })
          return
        }
        ElMessage.success('已丢弃')
        this.$emit('discarded', this.sessionId)
      } catch (e) {
        ElMessage({ type: 'error', message: '丢弃失败：' + (e && e.message ? e.message : e) })
      } finally {
        this.discarding = false
      }
    }
  }
}
</script>

<style scoped>
.rec-review {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  font-size: 13px;
}

/* ---------------- 顶栏 ---------------- */
.rr-top {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--qm-line);
  background: var(--qm-bg-2);
  flex: none;
}
.rr-top-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}
.rr-name-input { width: 240px; flex: none; }
.rr-url {
  color: var(--qm-text-3);
  font-size: 12px;
  max-width: 420px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.rr-top-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: none;
}
.rr-stat {
  color: var(--qm-text-2);
  font-size: 12px;
}
.rr-stat b {
  color: var(--qm-text-1);
  font-variant-numeric: tabular-nums;
}
.rr-stat.is-drop b { color: var(--qm-accent-strong); }

/* ---------------- 忽略原因 ---------------- */
.rr-drops {
  flex: none;
  border-bottom: 1px solid var(--qm-line);
  background: var(--qm-warning-soft);
}
.rr-drops-head {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  color: var(--qm-accent-strong);
  font-size: 12px;
  cursor: pointer;
}
.rr-drops-body {
  padding: 0 12px 8px 32px;
}
.rr-drop-item {
  display: flex;
  gap: 8px;
  padding: 2px 0;
  font-size: 12px;
  color: var(--qm-text-2);
}
.rr-drop-n {
  flex: none;
  min-width: 22px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: var(--qm-accent-strong);
}

/* ---------------- 三栏 ---------------- */
.rr-body {
  flex: 1;
  min-height: 0;
  display: flex;
  gap: 1px;
  background: var(--qm-line);
}
.rr-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
  background: var(--qm-bg-1);
  padding: 10px 12px;
  overflow-y: auto;
}
.rr-left { flex: 0 0 300px; }
.rr-mid { flex: 1 1 auto; }
.rr-right { flex: 0 0 320px; }

.rr-col-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
  flex: none;
}
.rr-col-title {
  font-weight: 600;
  color: var(--qm-text-1);
}
.rr-col-sub {
  font-size: 12px;
  color: var(--qm-text-3);
}

/* 左栏工具条 */
.rr-tools {
  display: flex;
  align-items: center;
  gap: 2px;
  margin-bottom: 6px;
  flex: none;
}
.rr-flex { flex: 1; }
.rr-left-list {
  flex: 1;
  min-height: 0;
}

/* 中/右栏区块 */
.rr-block {
  margin-bottom: 14px;
}
.rr-alert { margin-bottom: 12px; }
.rr-lb {
  margin-bottom: 5px;
  color: var(--qm-text-2);
  font-size: 12px;
}
.rr-lb-hint {
  margin-left: 4px;
  color: var(--qm-text-3);
}
.rr-inline-empty {
  padding: 8px 10px;
  border: 1px dashed var(--qm-line-strong);
  border-radius: 8px;
  color: var(--qm-text-3);
  font-size: 12px;
}
.rr-note {
  padding: 4px 0;
  color: var(--qm-accent-strong);
  font-size: 12px;
  line-height: 1.5;
}

/* 参数行 */
.rr-arg {
  padding: 7px 10px;
  margin-bottom: 6px;
  border: 1px solid var(--qm-line);
  border-radius: 8px;
  background: var(--qm-bg-2);
}
.rr-arg-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.rr-arg-key {
  font-family: ui-monospace, Consolas, monospace;
  font-weight: 600;
  color: var(--qm-text-1);
}
.rr-arg-body { margin-top: 6px; }

.rr-divider { margin: 12px 0 10px; }

/* ---------------- 底栏 ---------------- */
.rr-foot {
  flex: none;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-top: 1px solid var(--qm-line);
  background: var(--qm-bg-2);
}
.rr-foot-left {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
  color: var(--qm-text-3);
  font-size: 12px;
}
.rr-foot-icon { color: var(--qm-accent-strong); flex: none; }
.rr-foot-right { display: flex; gap: 8px; flex: none; }

/* ---------------- 落库结果 ---------------- */
.rr-result-line {
  display: flex;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  line-height: 1.6;
}
.rr-result-lb {
  flex: none;
  min-width: 68px;
  color: var(--qm-text-3);
}
.rr-result-vv {
  color: var(--qm-text-1);
  word-break: break-all;
}
.rr-var-tag { margin-right: 4px; }
.rr-skip {
  color: var(--qm-text-2);
  font-size: 12px;
  line-height: 1.5;
}
</style>
