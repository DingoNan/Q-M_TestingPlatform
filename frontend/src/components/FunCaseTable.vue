<template>
  <div>
     <vxe-table
		  ref="tableRef"
		  header-align="center"
		  min-height="250"
		  :row-config="{height: 90, drag:!readonly, keyField: 'id'}"
		  :checkbox-config="{checkField: 'is_required'}"
          show-overflow
          :data="tableData">
		  <vxe-column v-if="!readonly" width="60" align="center" drag-sort/>
		  <vxe-column type="seq" width="60" align="center"></vxe-column>
          <vxe-column field="name" title="步骤描述" min-width="400" tree-node align="left" >
            <template #default="{ row, rowIndex }">
			<el-input v-model="row.step_desc"  size='large' type='textarea' :autosize="{ minRows: 1, maxRows: 3 }"  maxlength='120' :readonly="readonly"></el-input>
            </template>
          </vxe-column>
          <vxe-column field="value" title="预期结果" min-width="400">
            <template #default="{ row, rowIndex }">
			<el-input v-model="row.step_exp"  size='large'  type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" maxlength='120' :readonly="readonly"></el-input>
            </template>
          </vxe-column>
		  <vxe-column title="操作" width="110"  header-align="left" v-if="!readonly">
		  <template #header>
			  <el-tooltip content="新增">
			  	<el-button :icon="Plus" circle @click="pushJsonParams"></el-button>
			  </el-tooltip>
		  </template>
		  <template #default="{ row, rowIndex }">
			<el-tooltip content="新增">
				<el-button :icon="Plus" circle @click="addJsonParams(row, rowIndex)"></el-button>
			</el-tooltip>
			<el-tooltip content="删除">
				<el-button :icon="Delete" @click="delJsonParams(row, rowIndex)" circle></el-button>
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
		default: 500,
	},
	'readonly':{
		type: Boolean,
		default: false
	},
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
	  getDynamicData: 'args',
	  showOverflow: true,
	  exampleVisible: false,
	  explainVisible: false,
	  funcVisible: false,
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
	  	step_exp: '',//参数类型
	  	step_desc: '',//用例步骤描述
	  },
    }
  },
  methods: {
	handleUpdateValue(row, newValue) {
	      row.value = newValue; // 更新父组件的数据
	},
	updateEditRow(key, value){
		this.edit_row[key] = value
	},
	 getInsertEvent () {
	      const $table = this.$refs.tableRef
	      if ($table) {
	        const insertRecords = $table.getInsertRecords()
	      }
	},
	pushJsonParams(){
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
	addJsonParams(row, index){
		console.log(row, index ,'111')
		// this.json_params.id = uuidv4()
		// this.json_params.parentId = row.parentId
		// const index = this.findIndexById(this.tableData, row.id)
		this.tableData.splice(index + 1, 0, {...this.json_params})
	},
	findIndexById(items, id) {
	  return items.findIndex(item => item.id === id);
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
