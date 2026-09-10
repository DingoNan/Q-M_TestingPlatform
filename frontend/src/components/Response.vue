<template>
  <el-dialog v-model="exportApiVisible" title="导入Json" width="800" append-to-body='append_to_body' :show-close='show_close'>
  	<span>导入格式为{"key1": "value1", "key2": "value2"}</span>
      <v-ace-editor v-model:value='exportJson' lang='json' theme='chrome' style="height: 400px" :options='editOption'/>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="exportApiVisible = false">取消</el-button>
          <el-button @click="exportJsonFuncTwo" v-if='isApi===true'>确定</el-button>
          <el-button @click="exportJsonFunc" v-if='isApi===false'>确定</el-button>
        </div>
      </template>
  </el-dialog>
  <el-dialog v-model="loadApiVisible" title="从接口加载Json" width="500" append-to-body='append_to_body'>
      <span>从接口导入Json会覆盖已经设置好的参数值，确认执行该操作？</span>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="loadApiVisible = false">取消</el-button>
          <el-button @click="loadApi()">确定</el-button>
        </div>
      </template>
  </el-dialog>
  <el-dialog v-model="explainVisible" title="编辑参数说明" width="500" append-to-body='append_to_body' :show-close='show_close'>
      <el-input
          v-model="edit_row.explain"
          autosize
          type="textarea"
          placeholder="请输入参数说明"
		  class='text'
		  size='large'
		  style='width: 380px'
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
		  :loading="false"
		  :checkbox-config="{checkField: 'is_required'}"
		  :row-config="{height: 60, drag:true, keyField: 'id'}"
		  :edit-config="{trigger: 'click', mode: 'cell', showIcon: false, autoClear: false}"
		  :scroll-y="{enabled: true, gt: 0, mode: 'wheel', oSize: 30, threshold: 0}"
		  show-overflow
		  :tree-config="treeConfig"
          :data="tableData">
          <vxe-column field="name" title="参数名称" width="400" tree-node :edit-render="{autofocus: true, placeholder: '参数名称'}" class-name="custom-cell">
            <template #edit="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.name' :row='row' :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params' :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateName(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
          <vxe-column title="必含" width="70" type='checkbox'>
          </vxe-column>
		  <vxe-column title="校验类型" width="110" field='check_type' v-if='!isApi'>
			  <template #header>
			  	<vxe-checkbox v-model="check_type_all" @change='headCheck' style='font-size: 1.1em' :class="{'not-fully-selected': false}"></vxe-checkbox>
				校验类型
			  </template>
			  <template #default="{ row }">
			    <vxe-checkbox v-model="row.check_type" @change='rowCheck(row)' style='font-size: 1.1em'></vxe-checkbox>
			  </template>
		  </vxe-column>
          <vxe-column field="type" title="参数类型" width="120" :edit-render="{autofocus: true, placeholder: 'string'}">
            <template #edit="{ row }">
              <el-select v-model="row.type" @change='typeChange(row)' size='large'class="select" popper-class='select-dropdown-rounded'>
                <el-option v-for="value in type_list" :label="value" :value="value" ></el-option>
              </el-select>
            </template>
          </vxe-column>
		  <vxe-column field="check_method" title="校验方式" width="150" :edit-render="{autofocus: true, placeholder: 'no_check'}"  v-if='!isApi'>
		    <template #edit="{ row, rowIndex }">
		       <el-select v-model="row.check_method" size='large'class="select" popper-class='select-dropdown-rounded'>
		         <el-option v-for="value in check_method" :label="value" :value="value" ></el-option>
		       </el-select>
		    </template>
		  </vxe-column>
          <vxe-column field="value" :title="expTitle" width="400" :edit-render="{autofocus: true, placeholder: '预期结果'}" class-name="custom-cell">
            <template #edit="{ row, rowIndex }">
			   <FuncAndParams :bind_case_data='bind_case_data' :value='row.value' :row='row'  :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params' :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateValue(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column field="explain" title="参数说明" min-width="250" :edit-render="{autofocus: true, placeholder: '参数说明'}">
		    <template #edit="{ row }">
		       <el-input style="width: 100%; box-sizing: border-box;" v-model="row.explain" placeholder="参数说明" class='input' size='large'>
					 <template #suffix>
						<el-icon @click="setExplainValue(row)" ><EditPen /></el-icon>
					 </template>
		       </el-input>
		    </template>
		  </vxe-column>
		  <vxe-column title="操作" width="188" header-align="left">
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
				<el-tooltip content="新增子字段">
				<el-button :icon="Connection" circle @click="addSubJsonParams(row)"></el-button>
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
	VAceEditor
  },
  props: {
  	'tableData': {
  		type: Array
  	},
	'bind_case_data':{
		type: Array
	},
  	'isApi':{
  		default: true
  	},
	'func_list': {
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
		default: [],
	},
	'check_method':{
		type: Array,
	},
	'steps':{
		type: Array,
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
	  expTitle: '预期结果',
	  check_type_all: false,
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
	  keyName: '',
	  show_close: false,
	  boolean_list: [true, false],
	  type_list: ['string', 'boolean', 'array', 'object', 'number', 'null'],
	  treeConfig: {
		transform: true,
		accordion: true,
		rowField: 'id',
		parentField: 'parentId',
		expandAll: true,
		iconOpen: 'vxe-icon-square-minus',
		iconClose: 'vxe-icon-square-plus',
	  },
	  editProps:{
	   	emitPath: true,
	   	value: 'id',
	   	label: 'name',
	  },
	  json_params:{
	  	id: 0,
	  	is_required: true, //是否必返回
		check_type: true, //是否校验类型
	  	name: '' ,//参数名称
	  	explain: '', //参数说明
	  	type: 'string',//参数类型
		check_method: 'no_check',//校验方式
	  	value: '',//预期值
		parentId: null,
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
	headCheck(obj){
		if(obj.checked){
			for (let index = 0; index < this.tableData.length; index++) {
				this.tableData[index].check_type = true
			}
		}else{
			for (let index = 0; index < this.tableData.length; index++) {
				this.tableData[index].check_type = false
			}
		}
	},
	rowCheck(row){
		const chirlrenIndexs = this.findAllChildrenIndexes(this.tableData, row.id)
		if(row.check_type){
			for (let index = chirlrenIndexs.length - 1; index >= 0; index--) {
				this.tableData[chirlrenIndexs[index]].check_type = true
			}
		}else{
			for (let index = chirlrenIndexs.length - 1; index >= 0; index--) {
				this.tableData[chirlrenIndexs[index]].check_type = false
			}
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
	async addSubJsonParams(row){
		if (row.type !=='array'){
			row.type = 'object'
		}
		const $table = this.$refs.tableRef
		this.json_params.id  = uuidv4()
		this.json_params.parentId = row.id
		const index = this.findIndexById(this.tableData, row.id)
		await this.tableData.splice(index + 1, 0, {...this.json_params})
		if ($table) {
			await $table.setTreeExpand(row, true)
		}
		
	},
	_exportJsonFunc(parentId, dataObj) {
	  for (const key in dataObj) {
	      const value = dataObj[key];
	      const dataType = typeof value;
		  const data = {...this.json_params}
		  data.id = uuidv4()
		  data.parentId = parentId
		  data.name = key
		  data.type = dataType
	      if (dataType === 'object' && value !== null) {
	        data.type = Array.isArray(value) ? 'array' : 'object';
			this.tableData.push(data)
	        this._exportJsonFunc(data.id, value); // 递归处理子对象
	      } else{
			  if (value === null){
			  	data.type = 'null'
			  }
	          data.value = value;
			  this.tableData.push(data)
	      }
	      
	  }
	},
	_exportJsonFuncTwo(parentId, dataObj) {
	  for (const key in dataObj) {
	      const value = dataObj[key];
	      const dataType = typeof value;
		  const data = {...this.json_params}
		  data.id = uuidv4()
		  data.parentId = parentId
		  data.name = key
		  data.type = dataType
	      if (dataType === 'object' && value !== null) {
	        data.type = Array.isArray(value) ? 'array' : 'object';
			this.tableData.push(data)
			if (data.type ==='array'){
				this._exportJsonFuncTwo(data.id, value.slice(0, 1)); // 递归处理子对象
			}else{
				this._exportJsonFuncTwo(data.id, value); // 递归处理子对象
			}
	      } else{
			  if (value === null){
			  	data.type = 'null'
			  }
	          data.value = value;
			  this.tableData.push(data)
	      }
	      
	  }
	},
	_exportJsonFuncDoc(parentId, dataObj) {
	  for (const key in dataObj) {
	      const value = dataObj[key];
	      const dataType = typeof value;
		  const data = {...this.json_params}
		  data.id = uuidv4()
		  data.parentId = parentId
		  data.name = key
		  data.type = dataType
	      if (dataType === 'object' && value !== null) {
	        data.type = Array.isArray(value) ? 'array' : 'object';
			if (Array.isArray(dataObj) && data.type==='object'){
				this._exportJsonFuncDoc(parentId, value); // 递归处理子对象
			}else{
				this.tableData.push(data)
				this._exportJsonFuncDoc(data.id, value); // 递归处理子对象
			}
	      } else{
			  if (value === null){
			  	data.type = 'null'
			  }
	          data.value = value;
			  this.tableData.push(data)
	      }
		  if(Array.isArray(dataObj)){
			  break
		  }
	      
	  }
	},
	exportJsonFunc(){
		try{
			const jsonData = JSON.parse(this.exportJson)
			this.tableData.splice(0, this.tableData.length)
			this._exportJsonFunc(null, jsonData)
			this.expandAllEvent()
			this.exportApiVisible = false
		}catch (e){
			ElMessage({
			  type: 'error',
			  message: 'JSON格式错误',
			})
		}
	},
	exportJsonFuncTwo(){
		try{
			const jsonData = JSON.parse(this.exportJson)
			this.tableData.splice(0, this.tableData.length)
			this._exportJsonFuncTwo(null, jsonData)
			this.expandAllEvent()
			this.exportApiVisible = false
		}catch (e){
			ElMessage({
			  type: 'error',
			  message: 'JSON格式错误',
			})
		}
	},
	exportJsonFuncDoc(){
		try{
			const jsonData = JSON.parse(this.exportJson)
			this.tableData.splice(0, this.tableData.length)
			this._exportJsonFuncDoc(null, jsonData)
			this.exportApiVisible = false
		}catch (e){
			ElMessage({
			  type: 'error',
			  message: 'JSON格式错误',
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
  	if(this.isApi){
		this.expTitle = 'Mock'
	}else{
		this.expTitle = '预期结果'
	}
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
