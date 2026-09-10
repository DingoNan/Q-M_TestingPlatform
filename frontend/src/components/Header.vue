<template>
  <el-dialog v-model="exportApiVisible" title="导入Header" width="800" append-to-body='append_to_body' :show-close='show_close'>
  	<!-- 提示文案 -->
  	 <el-alert
  			title='导入格式为 key:value，多条之间使用换行间隔'
  			type="info"
  			:closable="false"
  			show-icon
  			class="tip-alert"
  	 />
	
      <v-ace-editor v-model:value='exportJson' lang='json' theme='chrome' style="height: 400px" :options='editOption'/>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="exportApiVisible = false">取消</el-button>
          <el-button @click="exportHeaderFunc">确定</el-button>
        </div>
      </template>
  </el-dialog>
  <el-dialog v-model="loadApiVisible" title="从接口加载Headers" width="500" append-to-body='append_to_body'>
      <span>从接口导入Headers会覆盖已经设置好的参数值，确认执行该操作？</span>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="loadApiVisible = false">取消</el-button>
          <el-button @click="loadApi()">确定</el-button>
        </div>
      </template>
  </el-dialog>
  <FuncDynamic v-model:funcVisible='funcVisible' :edit_row='edit_row' @updateEditRow='updateEditRow' :func_list='func_list'></FuncDynamic>
  <el-dialog v-model="explainVisible" title="编辑参数说明" width="500" append-to-body='append_to_body' :show-close='show_close'>
      <el-input
          v-model="edit_row.explain"
          autosize
          type="textarea"
		  class='text'
		  style='width: 380px'
          placeholder="请输入参数说明"
        />
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="saveExplainValue">确定</el-button>
        </div>
      </template>
  </el-dialog>
  <el-dialog v-model="advancedSettingVisible" title="高级设置" width="650" append-to-body='append_to_body'>
      <div class="setting-section-title">基础信息</div>
      <div class="param-info-section">
        <div class="param-info-grid">
          <div class="param-info-item">
            <span class="param-info-label">参数名称</span>
            <span class="param-info-value">{{ advancedSettingRow.name || '-' }}</span>
          </div>
          <div class="param-info-item">
            <span class="param-info-label">类型</span>
            <span class="param-info-value">{{ advancedSettingRow.type || '-' }}</span>
          </div>
          <div class="param-info-item">
            <span class="param-info-label">必填</span>
            <span class="param-info-value">{{ advancedSettingRow.is_required ? '是' : '否' }}</span>
          </div>
          <div class="param-info-item">
            <span class="param-info-label">说明</span>
            <span class="param-info-value">{{ advancedSettingRow.explain || '-' }}</span>
          </div>
        </div>
      </div>
      <el-form label-width="80px" class="advanced-setting-form">
        <div class="setting-section">
          <div class="setting-section-title">长度值设置</div>
          <div class="setting-row">
            <el-form-item label="最小长度">
              <el-input v-model="advancedSettingRow.min_length" type="number" :min="0" step="1" class="input" style="width: 100%" placeholder="最小长度" @input="advancedSettingRow.min_length = Math.floor(Number(advancedSettingRow.min_length)) || ''" />
            </el-form-item>
            <el-form-item label="最大长度">
              <el-input v-model="advancedSettingRow.max_length" type="number" :min="0" step="1" class="input" style="width: 100%" placeholder="最大长度" @input="advancedSettingRow.max_length = Math.floor(Number(advancedSettingRow.max_length)) || ''" />
            </el-form-item>
          </div>
        </div>
        <div class="setting-section">
          <div class="setting-section-title">大小值设置<span class="setting-tip" v-if="advancedSettingRow.type !== 'number'">（仅number类型可设置）</span></div>
          <div class="setting-row">
            <el-form-item label="最小值">
              <el-input v-model="advancedSettingRow.min_value" type="number" :disabled="advancedSettingRow.type !== 'number'" class="input" style="width: 100%" placeholder="最小值" />
            </el-form-item>
            <el-form-item label="最大值">
              <el-input v-model="advancedSettingRow.max_value" type="number" :disabled="advancedSettingRow.type !== 'number'" class="input" style="width: 100%" placeholder="最大值" />
            </el-form-item>
          </div>
        </div>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="advancedSettingVisible = false">取消</el-button>
          <el-button type="primary" @click="saveAdvancedSetting">确定</el-button>
        </div>
      </template>
  </el-dialog>

  <div>
     <vxe-table
		  ref="tableRef"
		  header-align="center"
		  max-height="600"
		  :row-config="{height: 60, drag:true, keyField: 'id'}"
		  :edit-config="{trigger: 'click', mode: 'cell', showIcon: false, autoClear: false}"
		  :checkbox-config="{checkField: 'is_required'}"
          show-overflow
		  :tree-config="treeConfig"
          :data="tableData">
		  <vxe-column field="is_required"  width="35" type='checkbox' v-if='isTest'></vxe-column>
          <vxe-column field="name" title="参数名称" width="400" tree-node align="left" :edit-render="{autofocus: true, placeholder: '参数名称'}">
            <template #edit="{ row, rowIndex }">
				<el-select
				    v-model="row.name"
				    filterable
				    allow-create
				    default-first-option
				    :reserve-keyword="false"
				    placeholder="请选择或输入"
					size='large'class="select" popper-class='select-dropdown-rounded'
				  >
				    <el-option
				      v-for="item in options"
				      :key="item"
				      :label="item"
				      :value="item"
				    />
				  </el-select>
            </template>
          </vxe-column>
          <vxe-column field="is_required" title="必填" width="70" type='checkbox' v-if='!isTest'></vxe-column>
          <vxe-column field="type" title="参数类型" width="150" :edit-render="{autofocus: true, placeholder: '参数类型'}">
            <template #edit="{ row }">
              <el-select v-model="row.type" @change='typeChange(row)' size='large'class="select" popper-class='select-dropdown-rounded'>
                <el-option v-for="value in type_list" :label="value" :value="value" ></el-option>
              </el-select>
            </template>
          </vxe-column>
          <vxe-column field="value" title="参数值" width="400" :edit-render="{autofocus: true, placeholder: '参数值'}">
            <template #edit="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.value' :row='row'  :index='rowIndex' :step_index='step_index' :steps='steps' :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateValue(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column field="explain" title="参数说明" min-width="285" :edit-render="{autofocus: true, placeholder: '参数说明'}">
		    <template #edit="{ row }">
		       <el-input style="width: 100%; box-sizing: border-box;" v-model="row.explain" placeholder="参数说明" size='large' class='input'>
		    	 <template #suffix>
		    		<el-icon @click="setExplainValue(row)" ><EditPen /></el-icon>
		    	 </template>
		       </el-input>
		    </template>
		  </vxe-column>
		  <vxe-column title="操作" width="153" header-align="left">
			  <template #header>
				  <el-tooltip content="新增">
				  	<el-button :icon="Plus" circle @click="pushJsonParams"></el-button>
				  </el-tooltip>
				  <el-tooltip content="导入">
				  	 <el-button :icon="UploadFilled" circle  @click="exportApiVisible = true; this.exportJson =''"></el-button>
				  </el-tooltip>
			  </template>
			  <template #default="{ row, rowIndex }">
				<el-tooltip content="新增">
					<el-button :icon="Plus" circle @click="addJsonParams(row)"></el-button>
				</el-tooltip>
				<el-tooltip content="高级设置">
					<el-button :icon="Setting" circle @click="setAdvancedSetting(row)"></el-button>
				</el-tooltip>
				<el-tooltip content="删除">
					<el-button :icon="Delete" @click="delJsonParams(row)" circle></el-button>
				</el-tooltip>
			  </template>
		  </vxe-column>
        </vxe-table>
  </div>
</template>

<script>
import {VAceEditor} from 'vue3-ace-editor';
import 'ace-builds/src-noconflict/snippets/json';
import 'ace-builds/src-noconflict/mode-json';
import 'ace-builds/src-noconflict/snippets/python';
import 'ace-builds/src-noconflict/mode-python';
import 'ace-builds/src-noconflict/theme-chrome';
import 'ace-builds/src-noconflict/theme-monokai';
import 'ace-builds/src-noconflict/ext-language_tools';
import ace from 'ace-builds';
import { ElMessage, ElMessageBox } from 'element-plus'
import {v4 as uuidv4} from 'uuid'
import {mapState, mapActions, mapGetters} from 'vuex'
import FuncAndParams from './FuncAndParams.vue'
import { View, Delete, Plus, EditPen, CopyDocument, Top, Bottom, Connection, Menu, UploadFilled, Setting, Loading} from '@element-plus/icons-vue'
ace.config.set('basePath', 'https://cdn.jsdelivr.net./npm/ace-builds@' + require('ace-builds').version + '/src-noconflict/');
export default {
  computed:{
  	...mapState(['projectInfo']),
  	editOption(){
  		return {
  			enablesBasicAutocompletion: true,
  			enableSnippets: true,
  			enableLiveAutocompletion: true,
  			tabSize: 4,
  			fontSize: 18,
  			useworker: true,
  			ShowPrintMargin: false,
  			enableMultiselect: true,
  			showFoldwidgets: true,
  			fadeFoldwidgets: true,
  			wrap:true,
  		}
  	},
  },
  components: {
  	FuncAndParams,
  	VAceEditor,
  },
  props: {
  	'tableData': {
  		type: Array
  	},
  	'isApi':{
  		default: true
  	},
	'isTest':{
		default: false
	},
  	'height':{
  		default: 500,
  	},
	'apiJson':{
		type: Array,
	},
	'func_list':{
		type: Array
	},
	'bind_case_data':{
		type: Array
	},
	'bind_env_params':{
		type: Array
	},
	'bind_global_params':{
		type: Array
	},
	'case_params_data':{
		type: Array,
		default: []
	},
	'steps':{
		type: Array,
		default: []
	},
	'step_index':{
		type: Number
	}
  },
  setup() {
  	return {
  		Delete,
  		Plus,
  		View,
  		EditPen,
  		Connection,
  		Top,
  		Bottom,
  		CopyDocument,
  		UploadFilled,
  		Setting,
  		Loading,
		Menu
  	}
  },
  data () {
    return {
	  StepType:{
	  	PlatformSystemFunction: -1,   
	  	UserCustomizeFunction: 1,     
	  	Request: 5,                  
	  	Selenium: 2,                  
	  	ComStep:3,                 
	  	UserCustomizeScript: 4
	  },
	  options: ['Accept', 'Accept-Charset', 'Accept-Encoding', 'Accept-Language', 'Accept-Ranges', 'Date',
	   'Authorization', 'Cache-Control', 'Connection', 'Cookie', 'Content-Length', 'Content-Type', 'Expect',
	   'Content-MD5', 'User-Agent', 'Host', 'Referer', 'Origin', 'From', 'Upgrade', 'Warning', 'Range',
	   'If-Match', 'If-Modified-Since', 'If-None-Match', 'If-Range', 'If-Unmodified-Since'],
	  josn_root_type: ['object', 'array'],
	  json_type: 'object',
	  controls: false,
	  getDynamicData: 'args',
	  showOverflow: true,
	  exampleVisible: false,
	  explainVisible: false,
	  funcVisible: false,
	  exportVisible: false,
	  exportApiVisible: false,
	  show_close: false,
	  //编辑参数说明和参数示例的临时变量
	  edit_row: {},
	  advancedSettingVisible: false,
	  advancedSettingRow: {},
	  func_values: [],
	  //设置动态函数时的临时变量
	  exportApiVisible: false,
	  show_close: false,
	  boolean_list: [true, false],
	  loadApiVisible: false,
	  type_list: ['string', 'boolean', 'array', 'object', 'number', 'null'],
	  treeConfig: {
		transform: true,
		rowField: 'id',
		parentField: 'parentId',
		iconOpen: 'vxe-icon-square-minus',
		iconClose: 'vxe-icon-square-plus',
		expandAll: true,
		expandRowKeys: []
	  },
	  editProps:{
	   	emitPath: true,
	   	value: 'id',
	   	label: 'name',
	  },
	  json_params:{
	  	id: 0,
	  	is_required: true, //是否必填
	  	name: '' ,//参数名称
	  	explain: '', //参数说明
	  	example: '',//参数示例
	  	type: 'string',//参数类型
	  	value: '',//参数值
		parentId: null,
	  	//type=Dynamic 时,函数的入参
	  	params: [],
	  	//函数描述文档
	  	function_desc: []
	  },
    }
  },
  methods: {
	handleUpdateValue(row, newValue) {
	      row.value = newValue; // 更新父组件的数据
	},
	handleUpdateName(row, newValue) {
	      row.name = newValue; // 更新父组件的数据
	},
	loadApi(){
	  	this.loadApiVisible = false
	  	this.tableData.splice(0, this.tableData.length)
	  	for (const key in this.apiJson) {
	  		this.tableData.push({...this.apiJson[key]})
	  	}
	},
	updateEditRow(key, value){
		this.edit_row[key] = value
	},
	handleCommand(command){
	   if(command.type === 'func_generate'){
		   this.funcVisible = true		   
		   this.edit_row = command.row
	   }
	 },
	 getInsertEvent () {
	      const $table = this.$refs.tableRef
	      if ($table) {
	        const insertRecords = $table.getInsertRecords()
	      }
	},
	typeChange(row){
		if (row.type === "object" || row.type === "array"){
			row.value = ''
		}
	},
	pushJsonParams(){
		this.json_params.id = uuidv4()
		this.json_params.parentId = null
		this.tableData.push({...this.json_params})
	},
	findAllChildrenIndexes(data, parentId, indexes = []) {
	  data.forEach((item, index) => {
	    if (item.parentId === parentId) {
	      indexes.push(index);
	      this.findAllChildrenIndexes(data, item.id, indexes);
	    }
	  });
	  return indexes;
	},
	delJsonParams(row){
		const chirlrenIndexs = this.findAllChildrenIndexes(this.tableData, row.id)
		// chirlrenIndexs.push(parentIndex)
		// chirlrenIndexs.sort((a, b) => a - b);
		for (let index = chirlrenIndexs.length - 1; index >= 0; index--) {
			this.tableData.splice(chirlrenIndexs[index], 1)
		}
		const parentIndex = this.findIndexById(this.tableData, row.id)
		this.tableData.splice(parentIndex, 1)
	},
	addJsonParams(row){
		this.json_params.id = uuidv4()
		this.json_params.parentId = row.parentId
		const index = this.findIndexById(this.tableData, row.id)
		this.tableData.splice(index + 1, 0, {...this.json_params})
	},
	findIndexById(items, id) {
	  return items.findIndex(item => item.id === id);
	},
	exportHeaderFunc(){
		try{
			const params = this.exportJson.split('\n');
			this.tableData.splice(0, this.tableData.length)
			params.forEach(param => {
			        // 如果参数不为空，则以'='分割得到键和值
			        if (param) {
			            const [key, value] = param.split(':');
			            const data = {...this.json_params}
			            data.id = uuidv4()
			            data.name = key
			            data.type = 'string'
						data.value = value
						this.tableData.push(data)
			        }
			});
			this.exportApiVisible = false
		}catch (e){
			ElMessage({
			  type: 'error',
			  message: '格式错误',
			})
		}
	},
	setExplainValue(row){
		this.explainVisible = true
		this.edit_row = row
	},
	saveExplainValue(){
		this.explainVisible = false
		this.edit_row = {}
	},
	setAdvancedSetting(row){
		this.advancedSettingVisible = true
		this.advancedSettingRow = row
		if (this.advancedSettingRow.min_length === undefined) this.advancedSettingRow.min_length = ''
		if (this.advancedSettingRow.max_length === undefined) this.advancedSettingRow.max_length = ''
		if (this.advancedSettingRow.min_value === undefined) this.advancedSettingRow.min_value = ''
		if (this.advancedSettingRow.max_value === undefined) this.advancedSettingRow.max_value = ''
	},
	saveAdvancedSetting(){
		const row = this.advancedSettingRow
		if (row.min_length !== '' && row.max_length !== '' && row.max_length !== null && row.min_length !== null) {
			if (Number(row.max_length) < Number(row.min_length)) {
				ElMessage.error('最大长度不能小于最小长度')
				return
			}
		}
		if (row.type === 'number' && row.min_value !== '' && row.max_value !== '' && row.min_value !== null && row.max_value !== null) {
			if (Number(row.max_value) < Number(row.min_value)) {
				ElMessage.error('最大值不能小于最小值')
				return
			}
		}
		this.advancedSettingVisible = false
		ElMessage.success('高级设置已保存')
	},
	setExampleValue(row){
		this.exampleVisible = true
		this.edit_row = row
	},
	saveExampleValue(){
		this.exampleVisible = false
		this.edit_row = {}
	},
	expandAllEvent () {
	      const $table = this.$refs.tableRef
	      if ($table) {
	        $table.setAllTreeExpand(true)
	      }
	},
	async getPlantElement(){
		const response = await this.$api.getAllPlantElement({project: this.projectInfo.id})
		if (response.status === 200){
			this.loc_list = response.data.results
		}
	},
  },
  created() {
  	// this.getPlantElement()
  }
}
</script>
<style scoped>
	:deep(.el-textarea__inner){
	  border: none;
	  box-shadow: none;
	}

	.param-info-section {
		background: var(--qm-bg-1);
		border: 1px solid var(--qm-line-strong);
		border-radius: 10px;
		padding: 16px;
		margin-bottom: 20px;
	}

	.param-info-grid {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr 1fr;
		gap: 12px;
	}

	.param-info-item {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.param-info-label {
		font-size: 12px;
		color: var(--qm-text-3);
		font-weight: 500;
	}

	.param-info-value {
		font-size: 14px;
		color: var(--qm-text-1);
		font-weight: 500;
		word-break: break-all;
	}

	.advanced-setting-form .setting-section {
		margin-bottom: 24px;
	}

	.setting-section-title {
		font-size: 15px;
		font-weight: 600;
		color: var(--qm-text-1);
		margin-bottom: 16px;
		padding-left: 10px;
		border-left: 3px solid #f59e0b;
		line-height: 1.2;
	}

	.advanced-setting-form .setting-tip {
		font-size: 12px;
		color: var(--qm-text-3);
		font-weight: normal;
		margin-left: 4px;
	}

	.advanced-setting-form :deep(.el-form-item) {
		margin-bottom: 18px;
	}

	.advanced-setting-form .setting-row {
		display: flex;
		gap: 16px;
	}

	.advanced-setting-form .setting-row :deep(.el-form-item) {
		flex: 1;
		margin-bottom: 0;
	}

	.advanced-setting-form :deep(.el-input.is-disabled .el-input__wrapper) {
		background-color: var(--qm-bg-1) !important;
	}

</style>
