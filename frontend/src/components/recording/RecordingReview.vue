<template>
  <div class="rec-review">
    <!-- ===================== 顶栏：会话身份 ===================== -->
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
        <el-tag v-if="saveState === 'saving'" size="small" type="warning" effect="plain">保存中…</el-tag>
        <el-tag v-else-if="saveState === 'error'" size="small" type="danger" effect="plain">保存失败</el-tag>
        <el-tag v-else-if="saveState === 'dirty'" size="small" type="info" effect="plain">有未保存修改</el-tag>
        <el-tag v-else size="small" type="success" effect="plain">已同步</el-tag>
        <el-button link size="small" @click="reload">重新加载</el-button>
      </div>
    </div>

    <!-- ===================== 统一审阅台骨架（P4a） =====================
         统计条 / 「被自动忽略」透明化 / 底栏 / 落库结果回执，
         与 HAR 导入审阅用的是同一个组件 —— 换入口不用重新认一遍界面。
         那些真正不同的部分（动作卡片、定位器编辑、断言、AI 补短板）走 default slot。 -->
    <ImportReviewBoard
      class="rr-board"
      :stats="boardStats"
      :drops="dropEntries"
      drop-title="解析时自动忽略"
      drop-hint="被忽略的动作不会生成步骤。若某条其实需要，回到录制里改用能映射关键字的操作，或手工在用例里补一步。"
      footer-tip="编辑只写入录制会话，不产生任何用例数据；点「生成步骤用例」才真正落库。"
      :loading="loading"
      :result="boardResult"
      v-model:result-visible="resultVisible"
      @result-primary="goToCase"
    >

    <!-- ===================== AI 补短板（P2） =====================
         ★ 三个按钮**都不自动触发**（设计方案 §05 的硬要求）。
           AI 是按量计费的，自动跑就等于「每次打开审阅台都在花钱」，
           而且用户往往只是想看一眼录制结果。
         ★ 建议一律**只建议不落库**：勾选后走与手工编辑完全相同的 patch 通道，
           所以「不采纳 ⇒ 元素库/IR 零改动」是结构上成立的，不靠自觉。 -->
    <div class="rr-ai">
      <div class="rr-ai-head">
        <el-icon class="rr-ai-ico"><MagicStick /></el-icon>
        <span class="rr-ai-title">AI 补短板</span>
        <span class="rr-ai-sub">
          <template v-if="aiTouched">
            规则层已覆盖 <b>{{ aiReport.counts.covered }}</b>/{{ aiReport.total }} 步
            · 待补 <b>{{ aiReport.counts.uncovered }}</b> 步
          </template>
          <template v-else>
            规则优先：只把规则覆盖不到的步骤交给模型 · 不会自动运行
          </template>
        </span>
        <span class="rr-flex"></span>
        <el-button
          size="small"
          :loading="aiLoading === 'locator'"
          :disabled="!!aiLoading"
          @click="runAi('locator')"
        >定位器优化<template v-if="aiSuggestions.locator.length">（{{ aiSuggestions.locator.length }}）</template></el-button>
        <el-button
          size="small"
          :loading="aiLoading === 'assertion'"
          :disabled="!!aiLoading"
          @click="runAi('assertion')"
        >断言补全<template v-if="aiSuggestions.assertion.length">（{{ aiSuggestions.assertion.length }}）</template></el-button>
        <el-button
          size="small"
          :loading="aiLoading === 'naming'"
          :disabled="!!aiLoading"
          @click="runAi('naming')"
        >用例命名<template v-if="aiSuggestions.naming.length">（{{ aiSuggestions.naming.length }}）</template></el-button>
        <el-button v-if="aiTouched" link size="small" @click="aiOpen = !aiOpen">
          {{ aiOpen ? '收起建议' : '查看建议' }}
        </el-button>
      </div>

      <!-- ★ AI 失败也要明明白白显示出来。降级成 200 + ai_error 是后端的设计，
           但前端如果只把 ai_error 吞掉，用户会以为「点了没反应」。 -->
      <div v-if="aiError" class="rr-ai-warn">
        <el-icon><WarningFilled /></el-icon>
        <span>{{ aiError }}</span>
      </div>

      <div v-if="aiTouched" class="rr-ai-meta">
        本会话已调用 <b>{{ aiMeta.used_calls }}</b>/{{ aiMeta.limit }} 次
        <span v-for="(c, i) in aiMeta.calls" :key="'c' + i" class="rr-ai-call">
          · {{ scopeLabel(c.scope) }}<template v-if="c.ok">：{{ c.elapsed_ms }}ms<template v-if="c.total_tokens">／{{ c.total_tokens }} tok</template>／{{ c.suggestions }} 条</template><template v-else>：失败（{{ (c.error || '').slice(0, 60) }}）</template>
        </span>
      </div>

      <div v-if="aiOpen" class="rr-ai-body">
        <!-- ---- 规则推导（零 token，默认全选） ---- -->
        <div v-if="aiRuleAdded.length" class="rr-ai-group is-rule">
          <div class="rr-ai-g-head">
            <span class="rr-ai-g-title">规则推导的新断言 · {{ aiRuleAdded.length }} 条</span>
            <span class="rr-ai-g-tag">零 token</span>
            <span class="rr-flex"></span>
            <el-button size="small" type="primary" :disabled="!aiPickCount.rule" @click="adoptRules">
              采纳选中
            </el-button>
          </div>
          <div class="rr-ai-hint">
            规则能推的先推 —— 这里不会花一分钱。规则推导的断言不落库，
            同样要你点「采纳」才进 IR。
          </div>
          <label v-for="(r, i) in aiRuleAdded" :key="'r' + i" class="rr-ai-row">
            <el-checkbox v-model="aiPick.rule[i]" />
            <span class="rr-ai-seq">seq={{ r.seq }}</span>
            <span class="rr-ai-txt">{{ ruleNote(r) }}</span>
          </label>
        </div>

        <!-- ---- A1 定位器优化 ---- -->
        <div v-if="aiSuggestions.locator.length" class="rr-ai-group">
          <div class="rr-ai-g-head">
            <span class="rr-ai-g-title">定位器建议 · {{ aiSuggestions.locator.length }} 条</span>
            <span class="rr-flex"></span>
            <el-button size="small" type="primary" :disabled="!aiPickCount.locator" @click="adoptLocators">
              采纳选中
            </el-button>
          </div>
          <div class="rr-ai-hint">
            只对<b>规则打分偏低</b>的元素调模型（不为全量元素花钱）。
            采纳后只改「用哪个定位器找它」，元素身份（element_ref）保持不变。
          </div>
          <label v-for="(s, i) in aiSuggestions.locator" :key="'l' + i" class="rr-ai-row">
            <el-checkbox v-model="aiPick.locator[i]" />
            <span class="rr-ai-seq">seq={{ s.seq }}</span>
            <span class="rr-ai-code">{{ s.by }}={{ s.value }}</span>
            <span class="rr-ai-conf">{{ fmtConf(s.confidence) }}</span>
            <span class="rr-ai-txt">{{ s.reason }}</span>
          </label>
        </div>

        <!-- ---- A2 断言补全 ---- -->
        <div v-if="aiSuggestions.assertion.length" class="rr-ai-group">
          <div class="rr-ai-g-head">
            <span class="rr-ai-g-title">断言建议 · {{ aiSuggestions.assertion.length }} 条</span>
            <span class="rr-flex"></span>
            <el-button size="small" type="primary" :disabled="!aiPickCount.assertion" @click="adoptAssertions">
              采纳选中
            </el-button>
          </div>
          <div class="rr-ai-hint">
            只把<b>规则覆盖不到的步骤</b>交给模型。期望值为空的需要你在断言面板里补。
          </div>
          <label v-for="(s, i) in aiSuggestions.assertion" :key="'a' + i" class="rr-ai-row">
            <el-checkbox v-model="aiPick.assertion[i]" />
            <span class="rr-ai-seq">seq={{ s.seq }}</span>
            <span class="rr-ai-badge">{{ s.method }}</span>
            <span v-if="s.extract_keyword" class="rr-ai-badge is-soft">{{ s.extract_keyword }}</span>
            <span class="rr-ai-txt">
              {{ s.expect === null || s.expect === undefined ? '（期望值待人工补）' : ('期望：' + s.expect) }}
              <i v-if="s.reason">— {{ s.reason }}</i>
            </span>
          </label>
        </div>

        <!-- ---- A3 用例命名 ---- -->
        <div v-if="aiSuggestions.naming.length" class="rr-ai-group">
          <div class="rr-ai-g-head">
            <span class="rr-ai-g-title">用例命名建议</span>
          </div>
          <div class="rr-ai-hint">采纳会写入「会话名称」，落库时作为默认用例名。</div>
          <div v-for="(s, i) in aiSuggestions.naming" :key="'n' + i" class="rr-ai-row is-plain">
            <el-button size="small" @click="adoptName(s.name)">用这个名字</el-button>
            <span class="rr-ai-name">{{ s.name }}</span>
            <span class="rr-ai-txt">{{ s.reason }}</span>
          </div>
        </div>

        <!-- ---- 被丢弃的非法建议（透明化） ---- -->
        <div v-if="aiDropped.length" class="rr-ai-group is-drop">
          <div class="rr-ai-g-head">
            <span class="rr-ai-g-title">已丢弃的非法建议 · {{ aiDropped.length }} 条</span>
          </div>
          <div class="rr-ai-hint">
            模型的输出会经过取值白名单校验（`by` / `method` / `extract_keyword`）。
            不合法的**直接丢弃并说明原因**，绝不「猜一个差不多的」——
            静默降级会让错误定位器悄悄进元素库。
          </div>
          <div v-for="(s, i) in aiDropped" :key="'d' + i" class="rr-ai-row is-plain">
            <span class="rr-ai-badge is-warn">{{ scopeLabel(s.scope) }}</span>
            <span class="rr-ai-txt">{{ s.why }}：{{ s.item }}</span>
          </div>
        </div>

        <div v-if="!aiRuleAdded.length && !aiSuggestions.locator.length
          && !aiSuggestions.assertion.length && !aiSuggestions.naming.length && !aiDropped.length"
          class="rr-ai-empty">
          这次没有可采纳的建议{{ aiError ? '' : '（可能规则层已覆盖全部步骤，无需调用模型）' }}。
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

    <template #actions>
      <el-button size="small" :loading="discarding" @click="discardSession">丢弃本次录制</el-button>
      <el-button size="small" :loading="saveState === 'saving'" @click="flushPatch({})">保存审阅</el-button>
      <el-button type="primary" size="small" :loading="importing" @click="doImport">
        生成步骤用例
      </el-button>
    </template>
    </ImportReviewBoard>
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
import { ArrowRight, ArrowDown, InfoFilled, MagicStick, WarningFilled } from '@element-plus/icons-vue'

import RecActionCard from './ActionCard.vue'
import RecLocatorPicker from './LocatorPicker.vue'
import RecAssertionPanel from './AssertionPanel.vue'
// ★ P4a：与 HAR 导入共用同一套「导入审阅台」骨架
import ImportReviewBoard from '../common/ImportReviewBoard.vue'

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
  components: {
    RecActionCard, RecLocatorPicker, RecAssertionPanel, ImportReviewBoard,
    ArrowRight, ArrowDown, InfoFilled, MagicStick, WarningFilled
  },
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
      mismatchGuard: 0,

      // ---- AI 补短板（P2）----
      // ★ 三个 scope 都是 null 表示「没跑过」；同一时刻只允许跑一个（aiLoading）。
      aiLoading: null,
      aiOpen: false,
      aiTouched: false,          // 是否跑过或采纳过（决定面板是否显示）
      aiError: '',
      aiMeta: { used_calls: null, limit: 20, calls: [] },
      aiSuggestions: { locator: [], assertion: [], naming: [] },
      aiRuleAdded: [],           // 规则层新补的断言（带完整 spec，可被 patch 直接吃）
      aiDropped: [],
      // ★ 规则覆盖率**只能由后端算** —— 前端自己复算一遍必然与后端漂移
      //   （这和 P1 的 elements_unique 是同一类陷阱）。
      //   代价是「跑过 AI 之后才知道覆盖率」，但那也比两个数字对不上强。
      aiReport: { total: 0, counts: { covered: 0, manual_only: 0, uncovered: 0 } },
      // 勾选状态：按 group + 下标。默认全选（降低操作成本），
      // 但每条都带 confidence/reason 供人复核。
      aiPick: { rule: {}, locator: {}, assertion: {} }
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
    // ---- P4a：喂给统一审阅台骨架的输入 ----
    // ★ 统计条原本是本组件自己用 rr-stat 文本渲染的；现在与 HAR 导入共用
    //   同一份实现 —— 换到接口自动化那边，长得一模一样。
    boardStats() {
      const s = this.stat || {}
      return [
        { label: '条保留', value: s.kept != null ? s.kept : 0 },
        { label: '条已取消', value: s.off != null ? s.off : 0, tone: s.off ? 'warn' : 'plain' },
        { label: '个元素', value: s.elems != null ? s.elems : 0 },
        { label: '条断言', value: s.asserts != null ? s.asserts : 0 },
      ]
    },
    // ★ 结果回执也走统一组件：把本组件自己的 result 翻译成骨架认识的形状。
    //   「跳过 / 待补断言」这些**最容易让用户以为工具吞了数据**的信息必须在。
    boardResult() {
      const r = this.result
      if (!r) return null
      const lines = [
        {
          label: '用例', value: r.case_name,
          tags: [{ text: r.case_created ? '新建' : '追加', type: r.case_created ? 'success' : 'info' }],
        },
        { label: '模块', value: r.module_name },
        {
          label: '步骤',
          value: `共 ${r.step_count} 条（动作 ${r.action_step_count} / 校验 ${r.verify_step_count}）`,
        },
        { label: '断言', value: `${r.assertion_count} 条` },
        {
          label: '元素',
          value: `新增 ${(r.elements || {}).created || 0} / 复用 ${(r.elements || {}).reused || 0}`,
        },
      ]
      if ((r.deferred_assertions || []).length) {
        lines.push({
          label: '待补断言',
          value: `${r.deferred_assertions.length} 条（期望值需要人工填写）`,
        })
      }
      return {
        title: '落库结果',
        lines,
        variables: (r.variables || []).map((v) => (v && v.name) ? v.name : v),
        skips: r.skipped_actions || [],
        primaryText: '打开用例',
      }
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
    },
    /**
     * 已勾选的建议条数（按 group）。用于「采纳选中」按钮的禁用态。
     * ★ 用 `=== true` 判断而不是真值判断：`el-checkbox` 的 `v-model` 在
     *   未初始化时是 `undefined`，真值判断会把它当成未勾选 —— 行为上没错，
     *   但一旦以后有人把默认值改成 'indeterminate' 字符串就会静默出问题。
     * ★★ 必须留在**同一个 `computed` 块内**。本文件曾经出现两个 `computed:` 键：
     *   对象字面量的后键会覆盖前键 ⇒ 整个原有 computed（actions / activeAction /
     *   localStat / flatModules…）被**静默丢弃**，三栏联动与统计全废，
     *   而 `@vue/compiler-sfc` 一句错都不报。这是「追加式编辑插错位置」的典型后果，
     *   只能靠闸门的「顶层选项键唯一性」检查拦住。
     */
    aiPickCount() {
      const count = (group) => Object.keys(this.aiPick[group] || {})
        .filter((k) => this.aiPick[group][k] === true).length
      return {
        rule: count('rule'),
        locator: count('locator'),
        assertion: count('assertion')
      }
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
      // ★ AI 建议必须跟着一起清：它们是基于**某一份具体的 IR** 算出来的，
      //   重载后 IR 变了，旧建议里的 seq / 定位器可能已经不存在。
      //   留着会让人「采纳成功但什么都没发生」，比不显示更糟。
      this._aiClear()
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
    // AI 补短板（P2）
    // ---------------------------------------------------------------
    scopeLabel(s) {
      return { locator: '定位器优化', assertion: '断言补全', naming: '用例命名' }[s] || s || ''
    },
    fmtConf(c) {
      const n = Number(c)
      return Number.isFinite(n) ? n.toFixed(2) : '—'
    },
    ruleNote(r) {
      const spec = r.spec || {}
      const note = spec.note || r.rule || ''
      return spec.method ? `${note}（${spec.method}）` : note
    },
    /** 默认全选（降低操作成本），但每条都带依据供人复核。 */
    _aiResetPicks(group, n) {
      const next = {}
      for (let i = 0; i < n; i += 1) next[i] = true
      this.aiPick[group] = next
    },
    _aiClear() {
      this.aiTouched = false
      this.aiOpen = false
      this.aiError = ''
      this.aiMeta = { used_calls: null, limit: 20, calls: [] }
      this.aiSuggestions = { locator: [], assertion: [], naming: [] }
      this.aiRuleAdded = []
      this.aiDropped = []
      this.aiPick = { rule: {}, locator: {}, assertion: {} }
    },
    /**
     * 跑一个 scope 的 AI 增强。
     * ★ 三个按钮都不自动触发；且一次只允许跑一个（`aiLoading` 兼作互斥锁）——
     *   并发跑两个 scope 会让 `ai_meta` 的记账互相覆盖。
     */
    async runAi(scope) {
      if (this.aiLoading) return
      if (!this.sessionId) return
      // ★ 必须先 flush：AI 是**基于服务端 IR** 算的。本地若有未保存改动，
      //   算出来的建议会对应一份用户已经改过的旧 IR —— 这是错位建议的头号来源。
      const flushed = await this.flushPatch({ silent: true })
      if (!flushed) {
        ElMessage.warning('还有修改没有保存成功，已中止（避免 AI 基于旧 IR 给建议）')
        return
      }
      this.aiLoading = scope
      this.aiError = ''
      try {
        const resp = await this.$api.recordingSessionAiEnhance(this.sessionId, { scopes: [scope] })
        const rb = resp.data || {}
        const d = rb.result || rb
        this.aiTouched = true
        this.aiOpen = true
        if (resp.status !== 200) {
          this.aiError = d.detail || 'AI 增强请求失败'
          return
        }
        // ★ 后端的设计是「AI 失败也返 200 + ai_error」，所以这里不能按状态码判断
        //   成败，必须把 ai_error 显式呈现出来，否则用户会以为「点了没反应」。
        this.aiError = d.ai_error || ''
        this.aiMeta = d.ai_meta || this.aiMeta

        const rule = d.rule || {}
        this.aiReport = (rule.report && rule.report.counts)
          ? rule.report
          : { total: 0, counts: { covered: 0, manual_only: 0, uncovered: 0 } }

        // ★ 用 concat 而不是覆盖：用户可以「先跑定位器、再跑断言」，
        //   覆盖会把上一轮的建议与勾选全清掉，等于白花钱。
        const added = Array.isArray(rule.added) ? rule.added : []
        if (added.length) {
          const base = this.aiRuleAdded.length
          this.aiRuleAdded = this.aiRuleAdded.concat(added)
          added.forEach((_, i) => { this.aiPick.rule[base + i] = true })
        }
        const adds = {
          locator: Array.isArray(d.locator) ? d.locator : [],
          assertion: Array.isArray(d.assertion) ? d.assertion : [],
          naming: Array.isArray(d.naming) ? d.naming : []
        }
        Object.keys(adds).forEach((g) => {
          if (!adds[g].length) return
          const base = this.aiSuggestions[g].length
          this.aiSuggestions[g] = this.aiSuggestions[g].concat(adds[g])
          adds[g].forEach((_, i) => { this.aiPick[g][base + i] = true })
        })
        if (Array.isArray(d.dropped) && d.dropped.length) {
          this.aiDropped = this.aiDropped.concat(d.dropped)
        }

        const total = added.length + adds.locator.length
          + adds.assertion.length + adds.naming.length
        if (this.aiError) {
          ElMessage({ type: 'warning', duration: 8000, showClose: true, message: this.aiError })
        } else {
          ElMessage.success(`${this.scopeLabel(scope)}完成，得到 ${total} 条建议（尚未写入，需你勾选采纳）`)
        }
      } catch (e) {
        this.aiTouched = true
        this.aiOpen = true
        this.aiError = 'AI 增强请求失败：' + (e && e.message ? e.message : e)
      } finally {
        this.aiLoading = null
      }
    },
    /**
     * 采纳选中的规则断言。
     * ★ 走的是与手工「加断言」**完全相同**的通道（pendingAssertions → patch），
     *   不新开写路径 —— 这样「不采纳 ⇒ 零改动」是结构保证。
     * ★ 采纳后从列表里移除：`patch/assertions` 是**追加**语义，留在列表里
     *   再点一次就会变成两条。
     */
    async adoptRules() {
      const picked = this.aiRuleAdded.filter((r, i) => this.aiPick.rule[i] === true)
      if (!picked.length) return
      const spent = []
      picked.forEach((r) => {
        const spec = r.spec || {}
        if (!Number.isInteger(r.seq)) return
        this.pendingAssertions.push({
          seq: r.seq,
          method: spec.method,
          expect: spec.expect,
          extract_keyword: spec.extract_keyword,
          extract_args: spec.extract_args || {}
        })
        spent.push(r)
      })
      if (!spent.length) {
        ElMessage.warning('这些建议缺少 seq，无法采纳')
        return
      }
      this.aiRuleAdded = this.aiRuleAdded.filter((r) => spent.indexOf(r) < 0)
      this._aiResetPicks('rule', this.aiRuleAdded.length)
      const ok = await this.flushPatch({ silent: false })
      if (ok) ElMessage.success(`已采纳 ${spent.length} 条规则断言`)
    },
    async adoptAssertions() {
      const picked = this.aiSuggestions.assertion.filter((s, i) => this.aiPick.assertion[i] === true)
      if (!picked.length) return
      const spent = []
      picked.forEach((s) => {
        if (!Number.isInteger(s.seq)) return
        this.pendingAssertions.push({
          seq: s.seq,
          method: s.method,
          expect: s.expect,
          extract_keyword: s.extract_keyword,
          extract_args: s.extract_args || {}
        })
        spent.push(s)
      })
      if (!spent.length) {
        ElMessage.warning('这些建议缺少 seq，无法采纳')
        return
      }
      this.aiSuggestions.assertion = this.aiSuggestions.assertion.filter((s) => spent.indexOf(s) < 0)
      this._aiResetPicks('assertion', this.aiSuggestions.assertion.length)
      const ok = await this.flushPatch({ silent: false })
      if (ok) ElMessage.success(`已采纳 ${spent.length} 条断言建议`)
    },
    async adoptLocators() {
      const picked = this.aiSuggestions.locator.filter((s, i) => this.aiPick.locator[i] === true)
      if (!picked.length) return
      const done = []
      picked.forEach((s) => {
        const a = this.actions.find((x) => x.seq === s.seq)
        if (!a) return
        // 本地乐观更新 —— 必须与 `onPickLocator` **完全同形**，
        // 否则用户会看到「采纳了但琥珀色标记没消失」，以为没生效。
        const el = a.element || (a.element = {})
        const locs = Array.isArray(el.locators) ? el.locators : []
        const head = {
          by: s.by, value: s.value, opts: s.opts || {},
          source: 'ai', pinned: true, score: 0.99
        }
        el.locators = [head].concat(locs.filter((c) => !(
          String(c.by || '').toLowerCase() === String(s.by || '').toLowerCase()
          && String(c.value || '') === String(s.value || ''))))
        a.confidence = 1.0
        a.needs_review = false
        const pe = this._pe(s.seq)
        if (pe) pe.locator = { by: s.by, value: s.value, opts: s.opts || {} }
        done.push(s)
      })
      if (!done.length) {
        ElMessage.warning('这些建议对应的动作已不在当前 IR 里，无法采纳')
        return
      }
      this.aiSuggestions.locator = this.aiSuggestions.locator.filter((s) => done.indexOf(s) < 0)
      this._aiResetPicks('locator', this.aiSuggestions.locator.length)
      const ok = await this.flushPatch({ silent: false })
      if (ok) ElMessage.success(`已采纳 ${done.length} 条定位器建议`)
    },
    async adoptName(name) {
      if (!name) return
      this.sessionName = name
      this.caseName = name
      const ok = await this.flushPatch({ silent: false })
      if (ok) ElMessage.success(`已把会话名与用例名改为「${name}」`)
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

/* P4a：统一审阅台骨架要撑满剩余高度，否则三栏会塌成 0 高 */
.rr-board {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding: 10px 12px 0;
}
/* ★ 骨架的 default slot 里装的是「AI 面板 + 三栏主体」，得让它把剩余高度吃满 */
.rr-board ::v-deep .irb-body {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
/* AI 面板高度随内容，别跟着抢三栏的空间 */
.rr-board ::v-deep .rr-ai {
  flex: none;
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

/* ---------------- AI 补短板（P2） ----------------
   配色只用 theme.css 里已存在的变量，不新造颜色：
   --qm-accent-strong（浅色 #b45309 / 深色 #fbbf24）做强调，
   --qm-warning-soft / --qm-warning-soft-2 做提示底色。 */
.rr-ai {
  flex: none;
  border-bottom: 1px solid var(--qm-line);
  background: var(--qm-bg-3);
}
.rr-ai-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
}
.rr-ai-ico { color: var(--qm-accent-strong); }
.rr-ai-title { font-weight: 600; color: var(--qm-text-1); }
.rr-ai-sub { color: var(--qm-text-3); font-size: 12px; }
.rr-ai-sub b { color: var(--qm-accent-strong); }
.rr-ai-warn {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin: 0 12px 8px;
  padding: 6px 10px;
  border-radius: var(--qm-radius);
  background: var(--qm-warning-soft);
  color: var(--qm-text-1);
  font-size: 12px;
  line-height: 1.6;
}
.rr-ai-meta {
  padding: 0 12px 8px;
  color: var(--qm-text-3);
  font-size: 12px;
  line-height: 1.7;
}
.rr-ai-meta b { color: var(--qm-text-1); }
.rr-ai-call { margin-left: 2px; }

.rr-ai-body {
  max-height: 320px;
  overflow: auto;
  padding: 0 12px 10px;
}
.rr-ai-group {
  border: 1px solid var(--qm-line);
  border-radius: var(--qm-radius);
  background: var(--qm-bg-2);
  padding: 8px 10px;
  margin-bottom: 8px;
}
.rr-ai-group.is-rule { border-left: 3px solid var(--qm-green); }
.rr-ai-group.is-drop { border-left: 3px solid var(--qm-red); }
.rr-ai-g-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.rr-ai-g-title { font-weight: 600; color: var(--qm-text-1); }
.rr-ai-g-tag {
  font-size: 11px;
  padding: 0 6px;
  border-radius: 8px;
  background: var(--qm-warning-soft-2);
  color: var(--qm-accent-strong);
}
.rr-ai-hint {
  color: var(--qm-text-3);
  font-size: 12px;
  line-height: 1.6;
  margin-bottom: 4px;
}
.rr-ai-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 3px 0;
  cursor: pointer;
}
.rr-ai-row.is-plain { cursor: default; }
.rr-ai-seq {
  flex: none;
  color: var(--qm-text-3);
  font-family: Consolas, Monaco, monospace;
  font-size: 12px;
}
.rr-ai-code {
  flex: none;
  max-width: 320px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: Consolas, Monaco, monospace;
  font-size: 12px;
  color: var(--qm-accent-strong);
}
.rr-ai-conf { flex: none; color: var(--qm-text-3); font-size: 12px; }
.rr-ai-badge {
  flex: none;
  font-size: 11px;
  padding: 0 6px;
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
  color: var(--qm-text-2);
}
.rr-ai-badge.is-soft { border-style: dashed; }
.rr-ai-badge.is-warn {
  border-color: var(--qm-red);
  color: var(--qm-red);
}
.rr-ai-name { font-weight: 600; color: var(--qm-text-1); }
.rr-ai-txt {
  color: var(--qm-text-2);
  font-size: 12px;
  line-height: 1.6;
  min-width: 0;
}
.rr-ai-txt i { color: var(--qm-text-3); font-style: normal; }
.rr-ai-empty {
  color: var(--qm-text-3);
  font-size: 12px;
  padding: 4px 2px 8px;
}
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
