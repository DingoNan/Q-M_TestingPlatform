<template>
  <el-dialog v-model="exportApiVisible" title="导入Params" width="800" append-to-body='append_to_body' :show-close='show_close'>
  	
	<el-alert
		title='导入格式为 key=value&key=value&key=value'
		type="info"
		:closable="false"
		show-icon
		class="tip-alert"
	/>
	
      <v-ace-editor v-model:value='exportJson' lang='json' theme='chrome' style="height: 400px" :options='editOption'/>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="exportApiVisible = false">取消</el-button>
          <el-button @click="exportParamsFunc">确定</el-button>
        </div>
      </template>
  </el-dialog>
  <el-dialog v-model="loadApiVisible" title="从接口加载Params" width="500" append-to-body='append_to_body'>
      <span>从接口导入Params会覆盖已经设置好的参数值，确认执行该操作？</span>
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
		  :height="height"
		  :row-config="{height: 60, drag:true, keyField: 'id'}"
		  :edit-config="{trigger: 'click', mode: 'cell', showIcon: false, autoClear: false}"
		  :checkbox-config="{checkField: 'is_required'}"
          show-overflow
          :data="tableData">
          <vxe-column field="name" title="参数名称" min-width="300" tree-node align="left" :edit-render="{autofocus: true, placeholder: '参数名称'}">
            <template #edit="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.name' :row='row' :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params' :case_table_data='case_params_data'  :func_list='func_list' @update:value="handleUpdateName(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
          <vxe-column field="check_method" title="校验方式" width="250" :edit-render="{autofocus: true, placeholder: '参数类型'}">
            <template #edit="{ row }">
              <el-select v-model="row.check_method" @change='typeChange(row)' size='large'class="select" popper-class='select-dropdown-rounded'>
                <el-option v-for="value in check_methods" :label="value" :value="value" ></el-option>
              </el-select>
            </template>
          </vxe-column>
          <vxe-column field="value" title="参数值" min-width="300" :edit-render="{autofocus: true, placeholder: '参数值'}">
            <template #edit="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.value' :row='row' :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateValue(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column title="操作" width="150" header-align="left">
			  <template #header>
				  <el-tooltip content="新增">
				  	<el-button :icon="Plus"  @click="pushJsonParams"  circle></el-button>
				  </el-tooltip>
				  <el-tooltip content="导入">
				  	 <el-button :icon="UploadFilled"  circle   @click="exportApiVisible = true; this.exportJson =''"></el-button>
				  </el-tooltip>
				  <el-tooltip content="删除全部">
				  	<el-button :icon="Delete" @click="delJsonAllParams(row)"  circle></el-button>
				  </el-tooltip>
			  </template>
			  <template #default="{ row, rowIndex }">
				<el-tooltip content="新增">
					<el-button :icon="Plus"  @click="addJsonParams(row)"  circle></el-button>
				</el-tooltip>
				<el-tooltip content="删除">
					<el-button :icon="Delete" @click="delJsonParams(row)"  circle></el-button>
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
	'height':{
		default: 500,
	},
	'check_methods':{
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
	'bind_case_data':{
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
	  exampleVisible: false,
	  loadApiVisible: false,
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
	  	name: '' ,//参数名称
	  	check_method: 'check_equal',//参数类型
	  	value: '',//参数值
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
	loadApi(){
	  	this.loadApiVisible = false
	  	this.tableData.splice(0, this.tableData.length)
	  	for (const key in this.apiJson) {
	  		this.tableData.push({...this.apiJson[key]})
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
	delAllJsonParams(){
		this.tableData.splice(0, this.tableData.length)
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
	exportParamsFunc(){
		try{
			const params = this.exportJson.split('&');
			this.tableData.splice(0, this.tableData.length)
			params.forEach(param => {
			        // 如果参数不为空，则以'='分割得到键和值
			        if (param) {
			            const [key, value] = param.split('=');
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
