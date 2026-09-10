<template>
  <div>
     <vxe-table
		  header-align="center"
		  :height="height"
		  :row-config="{height: 45, drag:true, keyField: 'id'}"
		  :edit-config="{trigger: 'click', mode: 'cell', showIcon: false, autoClear: false}"
		  :checkbox-config="{checkField: 'is_required'}"
          show-overflow
          :data="tableData">
		  <vxe-column width="60" align="center" drag-sort/>
          <vxe-column field="rule" title="匹配规则" min-width="300"  align="left" :edit-render="{name: 'input', autofocus: true, placeholder: '匹配规则'}">
			  <template #edit="{ row, rowIndex }">
			  		<el-input v-model="row.rule" class='input' size='large'></el-input>
			  </template>
          </vxe-column>
		  <vxe-column field="method" title="匹配规则" min-width="200"  align="left" :edit-render="{ autofocus: true, placeholder: '匹配规则'}">
			  <template #edit="{ row, rowIndex }">
					<el-select v-model="row.method" size='large'class="select" popper-class='select-dropdown-rounded'>
						<el-option v-for='obj in method_list' :label="obj.lable" :value="obj.value" ></el-option>
					</el-select>
			  </template>
		  </vxe-column>
          <vxe-column field="host" title="域名地址" min-width="300" :edit-render="{name: 'input', placeholder: '域名地址', autofocus: true}">
			  <template #edit="{ row, rowIndex }">
				  <el-input v-model="row.host" class='input' size='large' ></el-input>
			  </template>
          </vxe-column>
		  <vxe-column title="操作" width="110" header-align="left">
			  <template #header>
				  <el-tooltip content="新增">
				  	<el-button :icon="Plus"  @click="pushJsonParams" circle></el-button>
				  </el-tooltip>
			  </template>
			  <template #default="{ row, rowIndex }">
				<el-tooltip content="新增">
					<el-button :icon="Plus"  @click="addJsonParams(row)" circle></el-button>
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
		default: 200,
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
	  method_list:[
		  {lable: '任意匹配', value: '任意匹配'},
		  {lable: '精准匹配', value: '精准匹配'},
		  {lable: '前缀匹配', value: '前缀匹配'},
	  ],
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
	  	rule: '' ,//参数名称
	  	host: '',//参数值
		method: '任意匹配',
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
  },
  created() {
  	if(this.tableData.length === 0 ){
		this.json_params.id = uuidv4()
		this.json_params.rule = '**'
		this.json_params.parentId = null
		this.tableData.push({...this.json_params})
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
