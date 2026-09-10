<template>
  <el-dialog v-model="explainVisible" title="编辑参数说明" width="500" append-to-body='append_to_body' :show-close='show_close'>
      <el-input
          v-model="edit_row.explain"
          autosize
          type="textarea"
		  class='text'
		  size='large'
		  style='width: 380px'
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
		  header-align="center"
		  max-height="600"
		  :row-drag-config="{trigger: 'cell', isCrossDrag: true}"
		  :row-config="{drag: true, keyField: 'id', height: 60}"
          show-overflow
          :data="tableData">
          <vxe-column field="name" title="参数名称" min-width="300" v-if='!is_com_step'>
            <template #default="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.name' :row='row'  :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateName(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column field="name" title="参数名称" min-width="300" v-if='is_com_step'>
		    <template #default="{ row, rowIndex }">
		       <FuncAndParams  :bind_case_data='bind_case_data' :value='row.name' :row='row'  :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateName(row, $event)"></FuncAndParams>
		    </template>
		  </vxe-column>
          <vxe-column field="value" title="参数值" min-width="300" >
            <template #default="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.value' :row='row' :step_index='step_index' :steps='steps' :index='rowIndex' :func_list='func_list'  :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params' :case_table_data='case_params_data' @update:value="handleUpdateValue(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column field="explain" title="参数说明" min-width="300">
		    <template #default="{ row }">
		       <el-input style="width: 100%; box-sizing: border-box;" v-model="row.explain" placeholder="参数说明" class='input' size='large'>
					 <template #suffix>
						<el-icon  @click="setExplainValue(row)"><EditPen /></el-icon>
					 </template>
		       </el-input>
		    </template>
		  </vxe-column>
		  <vxe-column title="操作" width="100" header-align="left">
			  <template #header>
				  <el-tooltip content="新增">
				  	<el-button :icon="Plus" circle @click="pushJsonParams"></el-button>
				  </el-tooltip>
			  </template>
			  <template #default="{ row, rowIndex }">
				<el-tooltip content="新增">
					<el-button :icon="Plus" circle @click="addJsonParams(row)"></el-button>
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
	'func_list':{
		type: Array
	},
	'bind_env_params':{
		type: Array
	},
	'bind_global_params':{
		type: Array
	},
	'bind_case_data':{
		type: Array
	},
	'case_params_data':{
		type: Array
	},
	'steps':{
		type: Array,
	},
	'step_index':{
		type: Number
	},
	'is_com_step':{
		type: Boolean,
		default: false,
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
	  josn_root_type: ['object', 'array'],
	  json_type: 'object',
	  controls: false,
	  getDynamicData: 'args',
	  showOverflow: true,
	  loadApiVisible: false,
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
	  type_list: ['string', 'boolean', 'number'],
	  treeConfig: {
		transform: true,
		rowField: 'id',
		parentField: 'parentId',
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
	  	value: '',//参数值
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
