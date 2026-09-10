<template>
   <div>
    <vxe-table
		  header-align="center"
		  :row-drag-config="{trigger: 'cell', isCrossDrag: true}"
		  :row-config="{drag: true, keyField: 'id', height: 60}"
          show-overflow
          :data="tableData">
          <vxe-column field="loop_times" title="循环控制器" min-width="300" >
            <template #default="{ row, rowIndex }">
               <FuncAndParams :bind_case_data='bind_case_data' :value='row.loop_times' :row='row' :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params'  :case_table_data='case_params_data'  :func_list='func_list' @update:value="handleUpdateValue(row, $event)"></FuncAndParams>
            </template>
          </vxe-column>
		  <vxe-column title="操作" width="60"  header-align="left">
			  <template #header>
				  <el-tooltip content="新增">
				  	 <el-button v-if='tableData.length === 0' :icon="Plus" circle @click="pushJsonParams"></el-button>
				  </el-tooltip>
			  </template>
			  <template #default="{ row, rowIndex }">
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
import {Delete, Plus, Menu} from '@element-plus/icons-vue'
export default {
	computed:{
		...mapState(['projectInfo']),
	},
	components: {
		FuncAndParams,
	},
	props: {
		'tableData': {
			type: Array,
			default: []
		},
		'height':{
			default: 500,
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
		  funcVisible: false,
		  //编辑参数说明和参数示例的临时变量
		  edit_row: {},
		  func_values: [],
		  //设置动态函数时的临时变量
		  json_params:{
			id: 0,
			loop_times: '',//参数类型
		  },
		}
	},
	methods: {
		handleUpdateValue(row, newValue) {
		      row.loop_times = newValue; // 更新父组件的数据
		},
		pushJsonParams(){
			this.json_params.id = uuidv4()
			this.tableData.push({...this.json_params})
		},
		delJsonParams(row){
			const parentIndex = this.findIndexById(this.tableData, row.id)
			this.tableData.splice(parentIndex, 1)
		},
		findIndexById(items, id) {
		  return items.findIndex(item => item.id === id);
		},
	},
}
</script>
<style scoped>
	:deep(.el-textarea__inner){
	  border: none;
	  box-shadow: none;
	}

</style>
