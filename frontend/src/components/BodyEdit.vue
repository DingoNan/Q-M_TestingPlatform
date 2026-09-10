<template>
	
  <!-- 关联脚本用例弹窗 -->
  <el-drawer v-model="chooseCaseVisible" :with-header="false" direction="ttb" show-close :z-index="1001" fullscreen="true" destroy-on-close :size="'calc(100vh - 30px)'">
    <CaseList :isCanChoose="true" v-model:chooseCaseVisible="chooseCaseVisible" @setCaseData="setCaseData"></CaseList>
  </el-drawer>
  
  <div class="code-editor-container">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <el-button type='success'  @click="copy" class="dialog-confirm-btn" >
          <!-- <el-icon  @click="copy">
            <CopyDocument />
          </el-icon> -->
		  <span class="button-text">复制</span>
        </el-button>
		
		<el-button type='success'  @click="formatJson" v-if='lang === "json"' class="dialog-confirm-btn">
		 <!-- <el-icon  @click="copy">
		    <Switch />
		  </el-icon> -->
		  <span class="button-text">格式化</span>
		</el-button>
		
		<el-button type='success'  @click="setEnvParams" v-if='isShowEnv' class="dialog-confirm-btn">
		 <!-- <el-icon  @click="copy">
		    <Switch />
		  </el-icon> -->
		  <span class="button-text">设置环境变量</span>
		</el-button>
		
		<el-button type='success'  @click="setResult" v-if="isShowBtn" class="dialog-confirm-btn">
		  <!-- <el-icon><Check /></el-icon> -->
		  <span class="button-text">设置用例结果</span>
		  
		</el-button>
		<el-button   @click="pushLog" v-if="isShowBtn"  class="dialog-confirm-btn">
		  <!-- <el-icon><DocumentAdd /></el-icon> -->
		  <span class="button-text">追加用例日志</span>
		  
		</el-button>
		<el-button type='success' @click="run_request" v-if="isShowBtn" class="dialog-confirm-btn">
		  <!-- <el-icon><Promotion /></el-icon> -->
		  
		  <span class="button-text">执行接口请求</span>
		</el-button>
		
		<el-button type='success' @click="run_case" v-if="isShowBtn" class="dialog-confirm-btn">
		  <!-- <el-icon><Promotion /></el-icon> -->
		  <span class="button-text">引用脚本用例</span>
		</el-button>
		
		<!-- ScriptAndParams 组件 -->
		<ScriptAndParams v-if="isShowBtn"
		  :bind_case_data='bind_case_data' 
		  :value='script_text' 
		  :step_index='step_index' 
		  :steps='steps' 
		  :bind_env_params='bind_env_params'
						 :bind_global_params='bind_global_params'
		  :case_table_data='case_params_data' 
		  :func_list='func_list' 
		  @update:value="handleUpdateValue($event)"
		  class="script-params"
		/>
		
		
      </div>
	  <el-alert
        v-if="isShowBtn || isShowEnv"
		title='可以在下面编辑器编写Python代码动态去设置参数值，复杂逻辑判断'
		type="info"
		:closable="false"
		show-icon
		style='width: 500px;'
	   />
	   <el-alert
	      v-if="lang === 'sql'"
	   	  title='在下面编辑器输入SQL,支持变量引用'
	   	  type="info"
	   	  :closable="false"
	   	  show-icon
	   	  style='width: 300px;'
	   />
	  
    </div>
    
    <!-- 编辑器区域 -->
    <div class="editor-area">
      <el-row v-if="isShowBtn" :gutter="20" class="editor-row">
        <el-col :span="24" class="editor-col">
          <v-ace-editor 
            :readOnly='readOnly' 
            :options='editOption' 
            v-model:value='dataEdit' 
            :lang='lang' 
            theme='chrome' 
            class="ace-editor"
            :style="{height: height}"
          />
        </el-col>
      </el-row>
      
      <v-ace-editor 
        v-else 
        :readOnly='readOnly' 
        :options='editOption' 
        v-model:value='dataEdit' 
        :lang='lang' 
        theme='chrome' 
        class="ace-editor-full"
        :style="{height: height}"
      />
    </div>
  </div>
</template>

<script>
import {VAceEditor} from 'vue3-ace-editor';
import { ElMessage } from 'element-plus';
import 'ace-builds/src-noconflict/snippets/json';
import 'ace-builds/src-noconflict/mode-json';
import 'ace-builds/src-noconflict/snippets/python';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-chrome';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/ext-language_tools';
import { VxeUI } from 'vxe-pc-ui';
import ScriptAndParams from './ScriptAndParams.vue';
import ace from 'ace-builds';
import { 
  CopyDocument, Switch, Check, DocumentAdd, Promotion, 
  Download, Upload
} from '@element-plus/icons-vue'

ace.config.set('basePath', 'https://cdn.jsdelivr.net./npm/ace-builds@' + require('ace-builds').version + '/src-noconflict/');
import CaseList from '../views/case/CaseList.vue'

export default{
  components: {
    VAceEditor,
    ScriptAndParams,
	CaseList
  },
  data() {
    return {
      isCanJson: true,
	  chooseCaseVisible: false,
      script_text: '',
      size: '18px',
      color: '#f59e0b'
    }
  },
  methods: {
    handleUpdateValue(newValue) {
      if(this.is_function){
        this.dataEdit = this.dataEdit + '\n' + '\t'  + newValue;
      }else{
        this.dataEdit = this.dataEdit + '\n' + newValue
      }
    },
	setCaseData(caseData) {
		if (caseData.type ===1){
			this.insertCode(`run_one_case(${caseData.id})`);
			this.chooseCaseVisible = false
		}else{
			ElMessage({type: 'error', message: '只能引用API用例'})
		}
		
	},
    get_step_params(){
      this.insertCode('params_name = case_params.stepResponse[0].apiResponseBody');
    },
    get_case_params(){
      this.insertCode('params_name = case_params.caseParams["这里输入变量名"]');
    },
    set_case_params(){
      this.insertCode('case_params.caseParams["这里输入变量名"] = param_value');
    },
    get_env_params(){
      this.insertCode('params_name = case_params.envParams["这里输入变量名"]');
    },
    insertCode(code) {
      const prefix = this.is_function ? '\n\t' : '\n';
      this.dataEdit = this.dataEdit + prefix + code;
    },
    setResult(){
      this.insertCode('case.result = 1' + ' # 1->成功 2->失败 3->错误');
    },
	setEnvParams(){
	  this.insertCode('update_env_params_info("环境变量名", "环境变量值")');
	},
    pushLog(){
      this.insertCode('case_log.append({"title": formatter_log("INFO", "这里输入日志标题"), "value": "这里输入日志内容"})');
    },
    run_request(){
      this.insertCode('session[host].request(method=method, url=url, data=data, json=json, params=params, headers=headers)');
    },
	run_case(){
		this.chooseCaseVisible = true
	},
    copy() {
      if (VxeUI.clipboard.copy(this.dataEdit)) {
        ElMessage({type: 'success', message: '复制成功'})
      }
    },
    expressJson(){
      try{
        const jsobj = JSON.parse(this.dataEdit)
        this.dataEdit = JSON.stringify(jsobj)
        this.isCanJson = true
      }catch (e){
        ElMessage({type: 'error', message: 'JSON格式错误'})
      }
    },
    formatJson(){
      if(this.isCanJson){
        try{
          const jsobj = JSON.parse(this.dataEdit)
          this.dataEdit = JSON.stringify(jsobj,null,4)
          this.isCanJson = false
        }catch (e){
          ElMessage({
            type: 'error',
            message: 'JSON格式错误',
          })
        }
      }else{
        this.expressJson()
      }
    }
  },
  emits: ['update:modelValue',],
  props: {
    loadBody:{},
    apiId:{
      default: -1
    },
    modelValue:{
      type: String
    },
    readOnly: {
      default: false
    },
    isShowLoadBtn: {
      default: false
    },
	isShowEnv: {
	  default: false
	},
    isShowBtn: {
      default: false
    },
    theme:{
      default: 'chrome'
    },
    height:{
      default: '500px'
    },
    width:{
      default: '100%'
    },
    lang: {
      default: 'json'
    },
    is_function: {
      default: true
    },
    'func_list':{
      type: Array,
      default: []
    },
    'bind_env_params':{
      type: Array,
      default: []
    },
    'bind_global_params':{
      type: Array,
      default: []
    },
    'case_params_data':{
      type: Array,
      default: []
    },
    'bind_case_data':{
      type: Array
    },
    'steps':{
      type: Array,
      default: []
    },
    'step_index':{
      type: Number
    }
  },
  created() {
    if (typeof this.dataEdit === "number"){
      this.dataEdit = this.dataEdit.toString()
    }else if (this.dataEdit === null){
      this.dataEdit = ''
    }
  },
  computed:{
    editOption(){
      return {
        enablesBasicAutocompletion: true,
        enableSnippets: true,
        enableLiveAutocompletion: true,
        tabSize: 4,
        fontSize: 16,
        useworker: true,
        ShowPrintMargin: false,
        enableMultiselect: true,
        showFoldwidgets: true,
        fadeFoldwidgets: true,
        wrap:true,
      }
    },
    dataEdit: {
      get(){
        return this.modelValue
      },
      set(value){
        this.$emit('update:modelValue', value)
      }
    }
  }
}
</script>

<style scoped>
.code-editor-container {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  background: var(--qm-bg-2);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--qm-bg-1);
  border-bottom: 1px solid #ebeef5;
}

.toolbar-left {
  display: flex;
  gap: 12px;
  align-items: center;
}

.toolbar-btn {
  cursor: pointer;
  padding: 6px;
  border-radius: 4px;
  transition: all 0.3s;
}

.toolbar-btn:hover {
  background: var(--qm-bg-4);
  transform: translateY(-1px);
}

.editor-area {
  padding: 16px;
}

.editor-row {
  height: 100%;
}

.editor-col {
  height: 100%;
}

.params-col {
  height: 100%;
}

.params-panel {
  background: #f9fafc;
  border-radius: 6px;
  padding: 16px;
  height: 100%;
  border: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.params-header {
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-1);
  padding-bottom: 8px;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 8px;
}

.action-buttons-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-buttons-title,
.variable-buttons-title {
  font-size: 13px;
  color: var(--qm-text-2);
  margin-top: 8px;
  margin-bottom: 4px;
  font-weight: 500;
}

.action-buttons-title {
  margin-top: 0;
}

.action-btn,
.variable-btn {
  width: 100%;
  justify-content: flex-start;
  text-align: left;
  margin-bottom: 4px;
}

.action-btn .el-icon,
.variable-btn .el-icon {
  margin-right: 6px;
  font-size: 14px;
}

.action-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #66b1ff 100%);
  border: none;
  color: white;
}

.action-btn:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #f59e0b 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.variable-btn {
  background: #f0f2f5;
  border: 1px solid var(--qm-line);
  color: var(--qm-text-2);
}

.variable-btn:hover {
  background: var(--qm-bg-4);
  border-color: #d3d6dd;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.script-params {
  flex: 1;
  margin-top: 8px;
}

.ace-editor {
  border-radius: 4px;
  border: 1px solid var(--qm-line-strong);
  overflow: hidden;
}

.ace-editor-full {
  width: 100%;
  border-radius: 4px;
  border: 1px solid var(--qm-line-strong);
  overflow: hidden;
}

/* 按钮文字容器 */
.button-text {
  position: relative;
  display: inline-block;
  padding-bottom: 3px; /* 为下划线留出空间 */
}

/* 下划线效果 */
.button-text::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: bottom right;
  transition: transform 0.3s ease;
}

.dialog-confirm-btn {
  position: relative;
  padding: 10px 24px !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 15px !important;
  transition: all 0.3s ease !important;
  overflow: hidden;
}

.dialog-confirm-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
  border: none !important;
  color: white !important;
}

.dialog-confirm-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(245, 158, 11, 0.4) !important;
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
}

/* 确认按钮下划线颜色 */
.button-text::after {
  background: var(--qm-bg-2); /* 白色下划线 */
}


/* 响应式调整 */
@media screen and (max-width: 1200px) {
  .editor-row {
    flex-direction: column;
  }
  
  .editor-col, .params-col {
    width: 100%;
  }
  
  .params-col {
    margin-top: 16px;
  }
}

/* 滚动条样式 */
:deep(.ace_scrollbar) {
  scrollbar-width: thin;
  scrollbar-color: #c0c4cc var(--qm-bg-3);
}

:deep(.ace_scrollbar::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}

:deep(.ace_scrollbar::-webkit-scrollbar-track) {
  background: var(--qm-bg-3);
  border-radius: 3px;
}

:deep(.ace_scrollbar::-webkit-scrollbar-thumb) {
  background: #c0c4cc;
  border-radius: 3px;
}

:deep(.ace_scrollbar::-webkit-scrollbar-thumb:hover) {
  background: var(--qm-text-3);
}
</style>