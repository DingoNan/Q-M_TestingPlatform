<template>
  <div class="assert-panel">
    <div class="assert-head">
      <span class="assert-title">断言</span>
      <span class="assert-seq">挂在动作 seq={{ seq }} 上</span>
    </div>

    <div v-if="!list.length" class="assert-empty">
      这一步没有断言。录制能自动推导的（导航后 URL、输入框回填值、显式断言）
      已经尽量推了，剩下的需要你按业务判断补 —— 点下面的「新增断言」。
    </div>

    <div v-else class="assert-list">
      <div v-for="(a, i) in list" :key="i" class="assert-item" :class="{ 'is-manual': a.manual }">
        <div class="assert-row1">
          <span class="assert-method">{{ methodText(a.method) }}</span>
          <el-tag v-if="a.manual" size="small" type="success" effect="plain">人工</el-tag>
          <el-tag v-else-if="a.auto" size="small" type="primary" effect="plain">自动推导</el-tag>
          <el-tag v-else size="small" type="warning" effect="plain">待确认</el-tag>
          <el-tag v-if="a.brittle" size="small" type="danger" effect="plain">易碎</el-tag>
          <span class="assert-flex"></span>
          <el-button link size="small" @click="$emit('remove', i)">移除</el-button>
        </div>
        <div class="assert-row2">
          <span class="assert-lb">取值来源</span>
          <span>{{ a.extract_keyword || '（本步骤返回值）' }}</span>
        </div>
        <div class="assert-row3">
          <span class="assert-lb">期望值</span>
          <span class="assert-exp">{{
            (a.expect === null || a.expect === undefined || a.expect === '') ? '（空 · 需人工填写）' : a.expect
          }}</span>
        </div>
        <div v-if="a.rule" class="assert-rule">推导规则：{{ a.rule }}</div>
      </div>
    </div>

    <div class="assert-add">
      <div class="assert-add-head" @click="formOpen = !formOpen">
        <el-icon><Plus /></el-icon>
        新增断言
        <span class="assert-add-tip">（选「取值来源」决定断言什么，选「校验方式」决定怎么比）</span>
      </div>
      <div v-if="formOpen" class="assert-form">
        <el-select v-model="form.extract_keyword" size="small" style="width: 100%" placeholder="取值来源">
          <el-option v-for="k in extractOptions" :key="k.value" :label="k.label" :value="k.value" />
        </el-select>
        <el-select v-model="form.method" size="small" style="width: 100%; margin-top: 6px">
          <el-option v-for="m in methodOptions" :key="m.value" :label="m.label" :value="m.value" />
        </el-select>
        <el-input
          v-model="form.expect"
          size="small"
          style="margin-top: 6px"
          placeholder="期望值（例如 /project 或 登录成功）"
        />
        <el-button type="primary" size="small" style="margin-top: 6px" @click="submit">
          加到这一步
        </el-button>
        <div class="assert-form-note">
          断言的实际值来自该步骤的返回值；如果这一步本身不产生返回值，
          落库时平台会自动补一条同名的提取步骤来承载它。
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 断言面板（P1 审阅台）
 *
 * ★ 两个清单必须与后端对齐，改一处就要改两处：
 *   · 取值来源（extract_keyword）取自 `apps/recording/importer.py::_VERIFY_DESC`
 *     —— 它同时是「底座里真实存在的 Playwright 关键字」的清单，
 *     写了不在表里的值 ⇒ 落库时 `_build_func_params` 会抛错、这一步被跳过。
 *   · 校验方式（method）取自 `core/com/check.py::CHECK_TEXT`
 *     —— 不在表里的 method 在执行期 `CHECK_FUNC_MAP[method]` 会 KeyError。
 */
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

// 9 个「取值来源」= 底座里能返回值的提取关键字
const EXTRACT_OPTIONS = [
  { value: 'url', label: '页面 URL（url）' },
  { value: 'title', label: '页面标题（title）' },
  { value: 'text_content', label: '元素文本（text_content）' },
  { value: 'get_attribute', label: '元素属性（get_attribute）' },
  { value: 'is_visible', label: '元素是否可见（is_visible）' },
  { value: 'is_enabled', label: '元素是否可用（is_enabled）' },
  { value: 'is_checked', label: '元素是否勾选（is_checked）' },
  { value: 'tag_name', label: '元素标签名（tag_name）' },
  { value: 'css_property', label: '元素样式（css_property）' }
]

// 12 个校验方式，与 core/com/check.py::CHECK_TEXT 一一对应
const METHOD_OPTIONS = [
  { value: 'check_equal', label: '字符串相等' },
  { value: 'check_not_equal', label: '字符串不相等' },
  { value: 'check_number_equal', label: '数字相等' },
  { value: 'check_number_not_equal', label: '数字不相等' },
  { value: 'check_number_gt', label: '数字大于' },
  { value: 'check_number_ge', label: '数字大于等于' },
  { value: 'check_number_lt', label: '数字小于' },
  { value: 'check_number_le', label: '数字小于等于' },
  { value: 'check_bool_equal', label: '布尔相等' },
  { value: 'check_bool_not_equal', label: '布尔不相等' },
  { value: 'check_object_is_empty', label: '对象为空' },
  { value: 'check_object_is_not_empty', label: '对象非空' }
]

export default {
  name: 'RecAssertionPanel',
  props: {
    assertions: { type: Array, default: () => [] },
    seq: { type: [Number, String], default: '' }
  },
  emits: ['add', 'remove'],
  data() {
    return {
      formOpen: false,
      form: { extract_keyword: 'url', method: 'check_equal', expect: '' },
      extractOptions: EXTRACT_OPTIONS,
      methodOptions: METHOD_OPTIONS
    }
  },
  computed: {
    list() {
      return Array.isArray(this.assertions) ? this.assertions : []
    }
  },
  methods: {
    methodText(m) {
      const hit = METHOD_OPTIONS.find((x) => x.value === m)
      return hit ? hit.label : (m || '未知校验方式')
    },
    submit() {
      if (!this.form.method) {
        ElMessage.warning('请选择校验方式')
        return
      }
      if (this.form.extract_keyword && this.form.expect === '') {
        // 允许空期望值（后端会落成 ''，执行期就是「和空串比」），但要提醒
        ElMessage.warning('期望值为空，这条断言等价于「校验为空」，请确认是否本意')
      }
      this.$emit('add', {
        seq: this.seq,
        method: this.form.method,
        extract_keyword: this.form.extract_keyword,
        extract_args: {},
        expect: this.form.expect
      })
      this.form.expect = ''
      this.formOpen = false
    }
  }
}
</script>

<style scoped>
.assert-panel { font-size: 13px; }
.assert-head {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-bottom: 8px;
}
.assert-title { font-weight: 600; color: var(--qm-text-1); }
.assert-seq { font-size: 12px; color: var(--qm-text-3); }
.assert-empty {
  padding: 10px 12px;
  border: 1px dashed var(--qm-line-strong);
  border-radius: 8px;
  color: var(--qm-text-3);
  font-size: 12px;
  line-height: 1.6;
}
.assert-list { display: flex; flex-direction: column; gap: 6px; }
.assert-item {
  padding: 7px 10px;
  border: 1px solid var(--qm-line);
  border-left: 3px solid var(--qm-accent);
  border-radius: 8px;
  background: var(--qm-bg-2);
}
.assert-item.is-manual { border-left-color: var(--qm-green); }
.assert-row1 { display: flex; align-items: center; gap: 6px; }
.assert-method { font-weight: 600; color: var(--qm-text-1); }
.assert-flex { flex: 1; }
.assert-row2, .assert-row3 {
  margin-top: 3px;
  display: flex;
  gap: 6px;
  color: var(--qm-text-2);
  font-size: 12px;
}
.assert-lb {
  flex: none;
  color: var(--qm-text-3);
  min-width: 52px;
}
.assert-exp {
  color: var(--qm-text-1);
  font-family: ui-monospace, Consolas, monospace;
  word-break: break-all;
}
.assert-rule { margin-top: 3px; font-size: 12px; color: var(--qm-text-3); }
.assert-add {
  margin-top: 10px;
  padding: 10px 12px;
  border: 1px dashed var(--qm-line-strong);
  border-radius: 8px;
  background: var(--qm-bg-3);
}
.assert-add-head {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: var(--qm-text-2);
  font-size: 13px;
}
.assert-add-tip { font-size: 12px; color: var(--qm-text-3); }
.assert-form { margin-top: 8px; }
.assert-form-note {
  margin-top: 6px;
  font-size: 12px;
  color: var(--qm-text-3);
  line-height: 1.5;
}
</style>
