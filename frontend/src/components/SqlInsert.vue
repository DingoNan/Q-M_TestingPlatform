<template>
  <el-dialog v-model="exportApiVisible" title="导入列数据" width="800" append-to-body='append_to_body' :show-close='show_close'>
  	<span>导入格式为 value1 换行 value2</span>
      <v-ace-editor v-model:value='exportJson' lang='json' theme='chrome' style="height: 400px" :options='editOption'/>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="exportApiVisible = false">取消</el-button>
          <el-button @click="exportParamsFunc">确定</el-button>
        </div>
      </template>
  </el-dialog>
  <el-dialog v-model="explainVisible" title="变量名称" width="500" append-to-body='append_to_body' :show-close='show_close'>
      <el-input
          v-model="edit_params_name"
          autosize
		  @input="handleInput"
          placeholder="只能输入英文、数字和下划线"
        />
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="saveExplainValue">确定</el-button>
        </div>
      </template>
  </el-dialog>
  <div>
     <vxe-table
		  style="margin-top: 15px;"
		  border
		  header-align="center"
		  height="800"
		  :column-config="{resizable: true}"
		  :row-config="{height: 45, drag:true, keyField: 'id'}"
		  :edit-config="{trigger: 'click', mode: 'cell', showIcon: false, autoClear: false}"
		  :scroll-y="{enabled: true, gt: 0, mode: 'wheel', oSize: 30, threshold: 0}"
		  :checkbox-config="{checkField: 'is_required'}"
          show-overflow
          :data="tableData">
		  <vxe-column type='seq' width="70" align="center"/>
          <vxe-column v-for='(column_name, index) in params_columns' header-align="left" :field="column_name" min-width="250" :edit-render="{autofocus: true, placeholder: '请输入变量值'}">
			 <template #header>
				 <span>{{ column_name }}</span>
				 <el-dropdown style="float: right; margin-top: 4px;" @command="(command) => handleCommand(command, index)">
				    <el-icon class="el-icon--right">
					 <MoreFilled />
				    </el-icon>
				     <template #dropdown>
				       <el-dropdown-menu>
				         <el-dropdown-item command="1">编辑</el-dropdown-item>
				         <el-dropdown-item command="2">向左插入列</el-dropdown-item>
				         <el-dropdown-item command="3">向右插入列</el-dropdown-item>
						 <el-dropdown-item command="4">删除列</el-dropdown-item>
				         <el-dropdown-item command="5">导入数据</el-dropdown-item>
				       </el-dropdown-menu>
				     </template>
				   </el-dropdown>
			 </template>
            <template #edit="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row[column_name]' :row='row' :is_case_data="true" :is_case_params="true" :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateValue(row, column_name,$event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column title="操作" width="110" header-align="left" fixed="right">
			  <template #header>
				  <el-tooltip content="新增行">
				  	<el-button :icon="Plus" size="small" @click="pushJsonParams"></el-button>
				  </el-tooltip>
				  <el-tooltip content="删除全部">
				  	<el-button :icon="Delete" @click="delAllJsonParams" size="small"></el-button>
				  </el-tooltip>
			  </template>
			  <template #default="{ row, rowIndex }">
				<el-tooltip content="新增">
					<el-button :icon="Plus" size="small" @click="addJsonParams(row)"></el-button>
				</el-tooltip>
				<el-tooltip content="删除">
					<el-button :icon="Delete" @click="delJsonParams(row)" size="small"></el-button>
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
import { Delete, Plus, EditPen, CopyDocument, Menu, UploadFilled} from '@element-plus/icons-vue'
ace.config.set('basePath', 'https://cdn.jsdelivr.net./npm/ace-builds@' + require('ace-builds').version + '/src-noconflict/');
export default {
  computed:{
  	...mapState(['projectInfo']),
  },
  components: {
  	FuncAndParams,
	VAceEditor
  },
  props: {
  	'tableData': {
  		type: Array
  	},
	'params_columns':{
		type: Array
	},
	'bind_case_data':{
		type: Array
	},
  	'isApi':{
  		default: true
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
  		EditPen,
  		UploadFilled,
		Menu
  	}
  },
  data () {
    return {
	  exampleVisible: false,
	  loadApiVisible: false,
	  explainVisible: false,
	  funcVisible: false,
	  exportVisible: false,
	  exportApiVisible: false,
	  show_close: false,
	  //编辑参数说明和参数示例的临时变量
	  commond_data: '',
	  is_add_params: false,
	  edit_params_name: '',
	  func_values: [],
	  //设置动态函数时的临时变量
	  exportApiVisible: false,
	  show_close: false,
	  boolean_list: [true, false],
	  column_index: -1,
	  json_params:{
	  	// _id_: 0,
	  	_name_: '' ,//参数名称
	  },
    }
  },
  methods: {
	handleInput(value){
	  // 使用正则表达式替换非英文、数字、下划线的字符
	  this.edit_params_name = value.replace(/[^a-zA-Z0-9_]/g, '');
	},
	handleCommand(command, index){
		if (command === '1'){
			this.is_add_params = false
			this.explainVisible = true
			this.column_index = index
			this.edit_params_name = this.params_columns[index]
		}else if(command === '2'){
			this.commond_data = '2'
			this.is_add_params = true
			this.explainVisible = true
			this.column_index = index
			this.edit_params_name = ''
		}else if(command === '3'){
			this.commond_data = '3'
			this.is_add_params = true
			this.explainVisible = true
			this.column_index = index
			this.edit_params_name = ''
		}else if(command === '4'){
			if (this.params_columns.length === 1){
				ElMessage({
				  type: 'error',
				  message: '至少保留一列',
				})
			}else{
				this.params_columns.splice(index, 1);
			}
		}else if(command ==='5'){
			this.exportApiVisible = true
			this.column_index = index
			this.edit_params_name = this.params_columns[index]
		}
	},
	handleUpdateValue(row, column_name, newValue) {
	      row[column_name] = newValue; // 更新父组件的数据
	},
	handleUpdateName(row, newValue) {
	      row._name_ = newValue; // 更新父组件的数据
	},
	typeChange(row){
		if (row.type === "object" || row.type === "array"){
			row.value = ''
		}
	},
	pushJsonParams(){
		// this.json_params._id = uuidv4()
		// this.json_params.parentId = null
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
	delAllJsonParams(){
		ElMessageBox.confirm(
		    '确定删除全部数据?',
		    '提示',
		    {
		      confirmButtonText: '确认',
		      cancelButtonText: '取消',
		      type: 'warning',
		    }
		  ).then(async() => {
			  this.tableData.splice(0, this.tableData.length)
			  
		    }).catch(() => {})
	},
	addJsonParams(row){
		// this.json_params.id = uuidv4()
		// this.json_params.parentId = row.parentId
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
	exportParamsFunc(){
		try{
			const params = this.exportJson.split('\r\n');
			const org_length = this.tableData.length
			// this.tableData.splice(0, this.tableData.length)
			params.forEach((value, index) =>{
				if (index < org_length){
					this.tableData[index][this.edit_params_name] = value
				}else{
					const data = {...this.json_params}
					data[this.edit_params_name] = value
					this.tableData.push(data)
				}
			});
			this.exportApiVisible = false
		}catch (e){
			ElMessage({
			  type: 'error',
			  message: '导入数据格式错误',
			})
		}
	},
	setExplainValue(row){
		this.explainVisible = true
		this.edit_row = row
	},
	saveExplainValue(){
		if (this.edit_params_name === ''){
			ElMessage({
			  type: 'error',
			  message: '请输入变量名称',
			})
			return
		}
		const findIndex = this.params_columns.indexOf(this.edit_params_name)
		if (this.is_add_params){
			if(findIndex === -1){
				if (this.commond_data === '2'){
					this.params_columns.splice(this.column_index, 0, this.edit_params_name)
				}else{
					this.params_columns.splice(this.column_index + 1, 0, this.edit_params_name)
				}
				this.explainVisible = false
			}else{
				ElMessage({
				  type: 'error',
				  message: '变量名称已存在',
				})
			}
		}else{
			if (findIndex === -1 || findIndex === this.column_index){
				this.params_columns[this.column_index] = this.edit_params_name
				this.explainVisible = false
			}else{
				ElMessage({
				  type: 'error',
				  message: '变量名称已存在',
				})
			}
		}
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
  	if(this.params_columns.length === 0){
		this.params_columns.push('column_one')
	}
  }
}
</script>
<style scoped>
	:deep(.el-textarea__inner){
	  border: none;
	  box-shadow: none;
	}

</style>
