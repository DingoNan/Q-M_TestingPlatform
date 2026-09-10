<template>
  <div>
     <vxe-table
		  ref="tableRef"
		  :height="250"
		  header-align="center"
		  :row-config="{height: 60, drag:true, keyField: 'id'}"
		  :checkbox-config="{checkField: 'is_required'}"
		  :edit-config="{trigger: 'click', mode: 'cell', showIcon: false, autoClear: false}"
          show-overflow
		  :tree-config="treeConfig"
          :data="tableData">
          <vxe-column field="name" title="类属性" min-width="200" tree-node align="left"  :edit-render="{autofocus: true, placeholder: '参数名称'}">
			  <template #edit="{ row, rowIndex }">
				  <el-input 
				    v-model="row.name" 
					placeholder="请输入类属性 如: PersonUser"
					maxlength="20"
					show-word-limit
					class="input"
					size='large'
				    @input="(value) => filterEnglishAndUnderscore(value, row)"
				  ></el-input>
			  </template>
          </vxe-column>
          <vxe-column field="value" title="类属性值" min-width="200" :edit-render="{autofocus: true, placeholder: '参数值'}">
            <template #edit="{ row, rowIndex }">
			  <el-input 
				v-model="row.value" 
				placeholder="请输入类属性值"
				maxlength="20"
				show-word-limit
				class="input"
				size='large'
			  ></el-input>
            </template>
          </vxe-column>
		  <vxe-column field="explain" title="类属性描述" min-width="200" :edit-render="{autofocus: true, placeholder: '参数描述'}">
		    <template #edit="{ row, rowIndex }">
		      <el-input 
		    	v-model="row.explain" 
				placeholder="请输入类属性描述"
				maxlength="200"
				show-word-limit
				class="input"
				size='large'
		      ></el-input>
		    </template>
		  </vxe-column>
		  <vxe-column title="操作" width="100"  header-align="left">
			  <template #header>
				  <el-tooltip content="新增">
				  	<el-button :icon="Plus" circle @click="pushJsonParams"></el-button>
				  </el-tooltip>
				 <!-- <el-tooltip content="导入">
				  	 <el-button :icon="UploadFilled" circle  @click="exportApiVisible = true; this.exportJson =''"></el-button>
				  </el-tooltip> -->
			  </template>
			  <template #default="{ row, rowIndex }">
				<el-tooltip content="新增">
					<el-button :icon="Plus" circle @click="addJsonParams(row)"></el-button>
				</el-tooltip>
				<el-tooltip content="删除">
					<el-button type="danger" :icon="Delete" @click="delJsonParams(row)" circle></el-button>
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
  	'height':{
  		default: 250,
  	},
	'apiJson':{
		type: Array,
	},
	'func_list':{
		type: Array
	},
	'bind_env_params':{
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
	  controls: false,
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
	  show_close: false,
	  boolean_list: [true, false],
	  loadApiVisible: false,
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
	  	name: '' ,//参数名称
	  	explain: '', //参数说明
	  	value: '',//参数值
		parentId: null,
	  },
    }
  },
  methods: {
	filterEnglishAndUnderscore(value, row) {
	      row.name = value.replace(/[^a-zA-Z_]/g, '');
	},
	handleUpdateValue(row, newValue) {
	      row.value = newValue; // 更新父组件的数据
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
