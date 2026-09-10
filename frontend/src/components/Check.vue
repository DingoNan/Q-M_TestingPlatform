<template>
  <div>
     <vxe-table
		  header-align="center"
		  :row-drag-config="{trigger: 'cell', isCrossDrag: true}"
		  :row-config="{drag: true, keyField: 'id', height: 60}"
          show-overflow
          :data="tableData">
		  <vxe-column width="70" align="center" drag-sort/>
          <vxe-column field="act_value" title="实际值" min-width="300" >
            <template #default="{ row, rowIndex}">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.act_value' :row='row' :index='rowIndex' :step_index='step_index' :steps='steps'  :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params' :case_table_data='case_params_data'  :func_list='func_list' @update:value="handleUpdateActValue(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column title="断言方式" field="method" align="center" width="300">
		  	<template #default="{ row }">
		  		<el-select v-model="row.method" style="width: 100%;" size='large'class="select" popper-class='select-dropdown-rounded'>
		  			<el-option v-for="value in method" :label="value" :value="value" ></el-option>
		  		</el-select>
		  	</template>
		  </vxe-column>
          <vxe-column field="exp_value" title="预期值" min-width="300" >
            <template #default="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.exp_value' :row='row'  :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params' :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateExpValue(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column title="操作" width="100"  header-align="left">
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
import { ElMessage, ElMessageBox } from 'element-plus'
import {v4 as uuidv4} from 'uuid'
import {mapState, mapActions, mapGetters} from 'vuex'
import FuncAndParams from './FuncAndParams.vue'
import {Plus, Delete, Menu} from '@element-plus/icons-vue'
export default {
  computed:{
  	...mapState(['projectInfo']),
  },
  components: {
  	FuncAndParams,
  },
  props: {
  	'tableData': {
  		type: Array
  	},
  	'height':{
  		default: 500,
  	},
	'method': {
		type: Array
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
		type: Array
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
		Menu
  	}
  },
  data () {
    return {
	  exampleVisible: false,
	  explainVisible: false,
	  funcVisible: false,
	  exportVisible: false,
	  //编辑参数说明和参数示例的临时变量
	  edit_row: {},
	  keyName: '',
	  func_values: [],
	  //设置动态函数时的临时变量
	  exportApiVisible: false,
	  and_or_list: ["And", "Or"],
	  type_list: ['string', 'boolean', 'array', 'object', 'number', 'null'],
	  editProps:{
	   	emitPath: true,
	   	value: 'id',
	   	label: 'name',
	  },
	  json_params:{
	  	id: 0,
	  	act_value: '',//实际值
		exp_value: '',//预期值
	  	method: '',//校验方式
	  },
    }
  },
  methods: {
	handleUpdateActValue(row, newValue) {
	      row.act_value = newValue; // 更新父组件的数据
	},
	handleUpdateExpValue(row, newValue) {
	      row.exp_value = newValue; // 更新父组件的数据
	},
	typeChange(row){
		if (row.type === "object" || row.type === "array"){
			row.value = ''
		}
	},
	pushJsonParams(){
		this.json_params.id = uuidv4()
		this.tableData.push({...this.json_params})
	},
	delJsonParams(row){
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
  },
  created() {
  }
}
</script>
<style scoped>
	:deep(.el-textarea__inner){
	  border: none;
	  box-shadow: none;
	}

</style>
