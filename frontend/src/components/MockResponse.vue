<template>
  <el-dialog v-model="exportApiVisible" title="导入Json" width="800" append-to-body='append_to_body' :show-close='show_close'>
	<el-alert
		title='导入格式为{"key1": "value1", "key2": "value2"}'
		type="info"
		:closable="false"
		show-icon
		class="tip-alert"
	/>
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
		  class='input'
		  size='large'
          placeholder="请输入参数说明"
        />
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="saveExplainValue">确定</el-button>
        </div>
      </template>
  </el-dialog>
  <div>
     <vxe-table
		  ref="tableRef"
		  header-align="center"
		  :height="height"
		  :loading="false"
		  :row-config="{height: 60, drag:true, keyField: 'id'}"
		  :edit-config="{trigger: 'click', mode: 'cell', showIcon: false, autoClear: false}"
		  :scroll-y="{enabled: true, gt: 0, mode: 'wheel', oSize: 30, threshold: 0}"
		  show-overflow
		  :tree-config="treeConfig"
          :data="tableData">
          <vxe-column field="name" title="参数名称" min-width="300" tree-node :edit-render="{autofocus: true, placeholder: '参数名称'}" class-name="custom-cell">
            <template #edit="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.name' :row='row' :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateName(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
          <vxe-column field="type" title="参数类型" width="120" :edit-render="{autofocus: true, placeholder: 'string'}">
            <template #edit="{ row }">
              <el-select v-model="row.type" @change='typeChange(row)' size='large'class="select" popper-class='select-dropdown-rounded'>
                <el-option v-for="value in type_list" :label="value" :value="value" ></el-option>
              </el-select>
            </template>
          </vxe-column>
          <vxe-column field="value" title="预期结果" min-width="300" :edit-render="{autofocus: true, placeholder: '预期结果'}" class-name="custom-cell">
            <template #edit="{ row, rowIndex }">
			   <FuncAndParams :bind_case_data='bind_case_data' :value='row.value' :row='row'  :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateValue(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column field="explain" title="参数说明" min-width="250" :edit-render="{autofocus: true, placeholder: '参数说明'}">
		    <template #edit="{ row }">
		       <el-input style="width: 100%; box-sizing: border-box;" v-model="row.explain" placeholder="参数说明" size='large' class='input'>
					 <template #suffix>
						<el-icon @click="setExplainValue(row)" ><EditPen /></el-icon>
					 </template>
		       </el-input>
		    </template>
		  </vxe-column>
		  <vxe-column title="操作" width="150" header-align="left">
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
				<el-tooltip content="删除">
					<el-button :icon="Delete" circle @click="delJsonParams(row)" ></el-button>
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
  	'isApi':{
  		default: true
  	},
	'func_list': {
		type: Array
	},
	'bind_case_data':{
		type: Array
	},
	'bind_env_params':{
		type: Array
	},
	'case_params_data':{
		type: Array,
		default: [],
	},
	'height':{
		default: 500,
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
	  showOverflow: true,
	  exampleVisible: false,
	  explainVisible: false,
	  funcVisible: false,
	  exportVisible: false,
	  exportApiVisible: false,
	  show_close: false,
	  //编辑参数说明和参数示例的临时变量
	  edit_row: {},
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
	  	name: '' ,//参数名称
	  	explain: '', //参数说明
	  	type: 'string',//参数类型
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
</style>
