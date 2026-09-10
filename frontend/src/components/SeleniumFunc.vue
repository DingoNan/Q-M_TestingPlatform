<template>
	<el-drawer :size="'calc(100vh - 30px)'" v-model="chooseElementVisible"  width='1300'  :z-index='9998' fullscreen='true'  destroy-on-close :with-header="false" direction='ttb'>
	    <ElementList :parentPermission="permission" :isCanChoose='isCanChoose' v-model:chooseElementVisible='chooseElementVisible' @setElementData='setElementData' :obj='func_params[index]'></ElementList>
	</el-drawer>
	<el-dialog v-model="viewSeleniumVisiable" title='查看函数体' style='width: 1250px;'>
		<BodyEdit :bind_case_data='[]' v-model='script' lang='python' height="600px" ></BodyEdit>
	</el-dialog>
	<div class="selenium-func-container">
		<div class="section-divider" >
		  <el-button type='success'  class='search-btn'   @click="viewSelenium(seleniumFuncData)" style="margin-top: -5px; width: 110px; float: right;">查看函数体</el-button>
		</div>
		<vxe-table
			ref="tableRef"
			header-align="center"
			height="300"
			empty-text="该函数没有入参"
			:row-config="{height: 55, drag:true, keyField: 'id', isHover: true}"
			:edit-config="{trigger: 'click', mode: 'cell', showIcon: false, autoClear: false}"
			:scroll-y="{enabled: true, gt: 0, mode: 'wheel', oSize: 30, threshold: 0}"
			:checkbox-config="{checkField: 'is_required'}"
			show-overflow
			:tree-config="treeConfig"
			:data="func_params"
			class="custom-table"
			style="width: 100%;">
			<vxe-column field="name" title="参数名称" width="280" tree-node align="left" :edit-render="{autofocus: true, placeholder: '参数名称'}">
			  <template #edit="{ row, rowIndex }">
				  <FuncAndParams v-if="row.parentId === undefined" :disabled='true' :bind_case_data='bind_case_data' :value='row.name' :row='row'  :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateName(row, $event)"></FuncAndParams>
				   <FuncAndParams v-else :bind_case_data='bind_case_data' :value='row.name' :row='row'  :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateName(row, $event)"></FuncAndParams>
			  </template>
			</vxe-column>
			<vxe-column field="type" title="参数类型" width="120" :edit-render="{autofocus: true, placeholder: '参数类型'}">
			  <template #edit="{ row }">
				<el-select v-if="row.parentId === undefined" v-model="row.type" @change='typeChange(row)' disabled class='select' size='large'>
				  <el-option v-for="value in type_list" :label="value" :value="value" ></el-option>
				</el-select>
				<el-select v-else v-model="row.type" @change='typeChange(row)' class='select' size='large'>
				  <el-option v-for="value in type_list" :label="value" :value="value" ></el-option>
				</el-select>
			  </template>
			</vxe-column>
			  <vxe-column  field='explain' title="参数说明" min-width="380" :edit-render="{autofocus: true, placeholder: '参数说明'}">
				  <template #default="{ row, rowIndex }">
					  <el-tooltip :content="row.explain">
						  <span>{{ row.explain }}</span>
					  </el-tooltip>
				  </template>
				<template #edit="{ row, rowIndex }">
				   <el-input size='large' class='input' v-if="row.parentId === undefined" style="width: 100%; box-sizing: border-box;" v-model="row.explain" placeholder="参数说明" disabled></el-input>
				   <el-input size='large' class='input' v-else style="width: 100%; box-sizing: border-box;" v-model="row.explain" placeholder="参数说明" ></el-input>
				</template>
			  </vxe-column>
			  <vxe-column field="value" title="参数值" width="480" :edit-render="{autofocus: true, placeholder: '参数值'}">
				<template #edit="{ row, rowIndex }">
					<el-input v-if="row.type ==='EleObject'" size='large' class='input' style="width: 100%; box-sizing: border-box;" v-model="row.value" readonly="true" placeholder="点击按钮可从元素库选择元素对象" @focus="handleFocus(rowIndex)">
						<template #append>
							<el-button v-if='row.value'  @click="choose(rowIndex)"  class='search-btn' size='large'>查看</el-button>
							<el-button v-else  @click="choose(rowIndex)"   class='search-btn' size='large'>选择</el-button>
						</template>
					</el-input>
				   <FuncAndParams v-else :bind_case_data='bind_case_data' :value='row.value' :row='row'  :step_index='step_index' :steps='steps' :index='rowIndex' :bind_env_params='bind_env_params'  :bind_global_params='bind_global_params' :case_table_data='case_params_data' :func_list='func_list' @update:value="handleUpdateValue(row, $event)"></FuncAndParams>
				</template>
			  </vxe-column>
			  <vxe-column title="操作" width="140" header-align="center">
				  <template #default="{ row, rowIndex }">
					<el-tooltip content="新增">
						<el-button v-if="row.parentId === undefined"   :icon="Plus" size="small" @click="addJsonParams(row)" style='width: 32px; height: 32px;' disabled></el-button>
						<el-button v-else   :icon="Plus" size="small" @click="addJsonParams(row)" style='width: 32px; height: 32px;' ></el-button>
					</el-tooltip>
					<el-tooltip content="新增子字段">
						<el-button v-if="row.type === 'Dict' || row.type === 'List'" :icon="Connection" size="small" @click="addSubJsonParams(row)" style='width: 32px; height: 32px;' ></el-button>
						<el-button v-else :icon="Connection" size="small" @click="addSubJsonParams(row)" style='width: 32px; height: 32px;' disabled></el-button>
					</el-tooltip>
					<el-tooltip content="删除">
						<el-button v-if="row.parentId === undefined" :icon="Delete" @click="delJsonParams(row)" size="small" style='width: 32px; height: 32px;' disabled></el-button>
						<el-button v-else :icon="Delete" @click="delJsonParams(row)" size="small" style='width: 32px; height: 32px;'></el-button>
					</el-tooltip>
				  </template>
			  </vxe-column>
	   </vxe-table>
	</div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import {mapState, mapActions, mapGetters} from 'vuex'
import BodyEdit from './BodyEdit.vue'
import {v4 as uuidv4} from 'uuid'
import ElementList from './ElementList.vue'
import FuncAndParams from './FuncAndParams.vue'
import { View, Delete, Plus, EditPen, CopyDocument, Top, Bottom, Connection, Menu, UploadFilled, Setting, Loading} from '@element-plus/icons-vue'

export default{
	computed:{
		...mapState(['projectInfo']),
		firstDesc() {
		    return (this.seleniumFuncData.desc && this.seleniumFuncData.desc[0]) || ''
		},
	},
	components:{
		BodyEdit,
		ElementList,
		FuncAndParams,
	},
	props: {
		'seleniumFuncData': {
			type: Object,
		},
		'permission': {
            type: Object,
            default: null,
        },
		'func_params':{
			type: Array,
		},
		'value': {
			type: String,
		},
		'tag_name': {
			type: String
		},
		'isCanChoose': {
			type: Boolean,
			default: false,
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
		'bind_case_data':{
			type: Array
		},
		'case_params_data':{
			type: Array,
			default: [],
		},
		'web_keys': {
			type: Array,
		},
		'check_method':{
			type: Array,
		},
		'steps':{
			type: Array,
		},
		'step_index':{
			type: Number
		},
		'keyword': {
			type: String,
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
	data() {
			return {
				index: '',
				script: '',
				keywordValue: '',
				treeConfig: {
				transform: true,
				accordion: true,
				rowField: 'id',
				parentField: 'parentId',
				iconOpen: 'vxe-icon-square-minus',
				iconClose: 'vxe-icon-square-plus',
			},
			viewSeleniumVisiable: false,
			isCanChoose: true,
			chooseElementVisible: false,
			localValue: this.value,
			activeNames: '1',
			StepType:{
				PlatformSystemFunction: -1,   
				UserCustomizeFunction: 1,     
				Request: 1,                  
				Selenium: 2,                  
				ComStep:3,                 
				UserCustomizeScript: 4
			},
			editProps:{
			 	emitPath: true,
			 	value: 'id',
			 	label: 'name',
			},
			show_close: false,
			append_to_body: true,
			funcVisible: false,
			// func_list: [],
			func_values: [],
			func_script: "",
			func_desc: "",
			func_package: '',
			func_name: '',
			func_run_result: '',
			type_list: ['Str', 'Int', 'Float', "Dict", "List", 'Bool'],
			json_params:{
				id: 0,
				is_required: true, //是否必填
				name: '' ,//参数名称
				explain: '', //参数说明
				type: 'Str',//参数类型
				value: '',//参数值
				parentId: null,
			},
		}
	},
	methods: {
		hasParentId(row) {
		    return row?.hasOwnProperty?.('parentId')
		},
		handleUpdateValue(row, newValue) {
		      row.value = newValue; // 更新父组件的数据
		},
		handleUpdateName(row, newValue) {
		      row.name = newValue; // 更新父组件的数据
		},
		viewSelenium(row){
			this.viewSeleniumVisiable =true
			this.script = row.script
		},
		handleFocus(index) {
			this.index = index
			this.isCanChoose = true
			this.chooseElementVisible = false
		},
		choose(index) {
			this.index = index
			this.isCanChoose = true
			this.chooseElementVisible = true
		},
		setElementData(data){
			this.chooseElementVisible = false
			this.func_params[this.index]['value'] = data.id
		},
		delJsonParams(row){
			// 先找到所有子节点的索引
			const childrenIndexes = this.findAllChildrenIndexes(this.func_params, row.id)
			// 找到父节点的索引
			const parentIndex = this.findIndexById(this.func_params, row.id)
			
			// 如果父节点存在，先删除所有子节点（从后往前删除）
			if (parentIndex !== -1) {
				// 从后往前删除子节点，避免索引变化
				for (let i = childrenIndexes.length - 1; i >= 0; i--) {
					if (childrenIndexes[i] !== -1) {
						this.func_params.splice(childrenIndexes[i], 1)
					}
				}
				// 最后删除父节点
				this.func_params.splice(parentIndex, 1)
			}
		},
		addJsonParams(row){
			this.json_params.id = uuidv4()
			this.json_params.parentId = row.parentId
			const index = this.findIndexById(this.func_params, row.id)
			this.func_params.splice(index + 1, 0, {...this.json_params})
		},
		findIndexById(items, id) {
		  return items.findIndex(item => item.id === id);
		},
		
		findAllChildrenIndexes(items, parentId) {
		  const indexes = []
		  
		  // 递归查找所有子节点的索引
		  const findChildren = (items, parentId) => {
			for (let i = 0; i < items.length; i++) {
			  if (items[i].parentId === parentId) {
				indexes.push(i)
				// 递归查找子节点的子节点
				findChildren(items, items[i].id)
			  }
			}
		  }
		  
		  findChildren(items, parentId)
		  return indexes
		},
		findIndexById(items, id) {
		  return items.findIndex(item => item.id === id);
		},
		async addSubJsonParams(row){
			if (row.type !=='List'){
				row.type = 'Dict'
			}
			const $table = this.$refs.tableRef
			this.json_params.id  = uuidv4()
			this.json_params.parentId = row.id
			const index = this.findIndexById(this.func_params, row.id)
			await this.func_params.splice(index + 1, 0, {...this.json_params})
			if ($table) {
				await $table.setTreeExpand(row, true)
			}
			
		},
	},
	watch: {
		keyword: {
			handler(newVal) {
				// 当keyword变化时，同步到本地keywordValue
				if (newVal !== this.keywordValue) {
					this.keywordValue = newVal
				}
			},
			immediate: true
		},
		keywordValue: {
			handler(newVal) {
				// 当本地keywordValue变化时，同步到props的keyword
				if (newVal !== this.keyword) {
					this.$emit('update:keyword', newVal)
				}
			}
		},
		web_keys: {
			handler(newVal) {
				// 当数据加载完成后，如果keyword有值，确保选中对应项
				if (this.keyword && newVal.length > 0) {
					// 数据加载完成，el-tree-select会自动更新选中状态
				}
			},
			deep: true
		}
	},
	created() {
	    console.log(this.permission, 'test')
	}
}

</script>

<style scoped>
	:deep(.custom-table .vxe-table--body) {
	  font-size: 14px;
	  font-weight: 400;
	}
	
	:deep(.custom-table .vxe-table--header) {
	  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
	  border-bottom: 2px solid #e2e8f0;
	}
	
	:deep(.custom-table .vxe-header--column) {
	  font-weight: 600;
	  color: #374151;
	  font-size: 14px;
	  padding: 12px 16px;
	}
	
	:deep(.custom-table .vxe-body--column) {
	  padding: 6px 8px !important;
	  border-bottom: 1px solid #f1f5f9;
	  box-sizing: border-box !important;
	  overflow: visible !important;
	}
	
	:deep(.custom-table .vxe-table--edit-cell) {
	  padding: 2px 4px !important;
	  box-sizing: border-box !important;
	  overflow: visible !important;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input) {
	  width: 100% !important;
	  box-sizing: border-box !important;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input .el-input__wrapper) {
	  width: 100% !important;
	  box-sizing: border-box !important;
	  border-radius: 6px;
	  border: 1px solid #d1d5db;
	  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	  transition: all 0.2s ease;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-select) {
	  width: 100% !important;
	  box-sizing: border-box !important;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-select .el-input__wrapper) {
	  width: 100% !important;
	  box-sizing: border-box !important;
	  border-radius: 6px;
	  border: 1px solid #d1d5db;
	  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input-group) {
	  width: 100% !important;
	  box-sizing: border-box !important;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input-group .el-input__wrapper) {
	  width: 100% !important;
	  box-sizing: border-box !important;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-button) {
	  box-sizing: border-box !important;
	  margin: 0 2px !important;
	}
	
	:deep(.custom-table .vxe-table--body) {
	  overflow: visible !important;
	}
	
	:deep(.custom-table .vxe-table--body-wrapper) {
	  overflow: visible !important;
	}
	
	:deep(.custom-table .vxe-table--body-row) {
	  transition: all 0.2s ease;
	}
	
	:deep(.custom-table .vxe-table--body-row:hover) {
	  background-color: #f8fafc !important;
	  transform: translateY(-1px);
	  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
	}
	
	:deep(.custom-table .vxe-table--body-row.row--current) {
	  background-color: #eff6ff !important;
	}
	
	:deep(.custom-table .vxe-table--empty-block) {
	  background: #f8fafc;
	  color: #64748b;
	  font-size: 14px;
	}
	
	:deep(.custom-table .vxe-table--empty-content) {
	  padding: 40px 0;
	}
	
	:deep(.custom-table .vxe-table--fixed-left-wrapper) {
	  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.08);
	}
	
	:deep(.custom-table .vxe-table--fixed-right-wrapper) {
	  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.08);
	}
	
	:deep(.custom-table .vxe-tree-cell) {
	  font-weight: 500;
	}
	
	:deep(.custom-table .vxe-tree-node--leaf) {
	  color: #4b5563;
	}
	
	:deep(.custom-table .vxe-tree-node--expanded) {
	  color: #1f2937;
	  font-weight: 600;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input .el-input__wrapper) {
	  border-radius: 8px;
	  border: 1px solid #d1d5db;
	  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	  transition: all 0.2s ease;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input .el-input__wrapper:hover) {
	  border-color: #3b82f6;
	  box-shadow: 0 2px 6px rgba(59, 130, 246, 0.2);
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input .el-input__wrapper.is-focus) {
	  border-color: #3b82f6;
	  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-select .el-input__wrapper) {
	  border-radius: 8px;
	  border: 1px solid #d1d5db;
	  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	}
	
	/* 表格操作按钮样式 - 只修改圆角 */
	:deep(.custom-table .vxe-table--body .el-button) {
	  border-radius: 8px !important;
	}
	
	:deep(.custom-table .vxe-table--body .el-button--small) {
	  border-radius: 8px !important;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-tooltip) {
	  margin-right: 8px;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-tooltip:last-child) {
	  margin-right: 0;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input-group__append) {
	  border-radius: 0 8px 8px 0;
	}
	
	:deep(.custom-table .vxe-table--edit-cell .el-input-group__append .el-button) {
	  border-radius: 0 6px 6px 0;
	}
	
	:deep(.el-textarea__inner){
	  border: none;
	  box-shadow: none;
	}
	.search-btn {
	  padding: 10px 24px;
	  border-radius: 10px;
	  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
	  border: none;
	  font-weight: 500;
	  transition: all 0.3s ease;
	  color: white !important;
	  display: flex;
	  align-items: center;
	  justify-content: center;
	}
	
	.search-btn:hover {
	  transform: translateY(-2px);
	  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
	}
	
	.search-btn .el-icon {
	  margin-right: 8px;
	  font-size: 16px;
	}
	.el-tag{
		border: none
	}
	.el-button{
		width: 70px;
	}
	.content-card {
	  flex: 1;
	  background: white;
	  margin-bottom: 20px;
	  border: none;
	  border-radius: 16px;
	  display: flex;
	  flex-direction: column;
	  min-height: 0;
	  overflow: hidden;
	}
	.section-divider {
	  display: flex;
	  align-items: center;
	  justify-content: space-between;
	  margin: 12px 0 12px 0;
	  padding: 0 8px;
	}
	
	.selenium-func-container {
	  border: 2px solid #e2e8f0;
	  border-radius: 16px;
	  padding: 20px;
	  background: white;
	  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
	  transition: all 0.3s ease;
	}
	
	.selenium-func-container:hover {
	  border-color: #cbd5e1;
	  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
	}
	
	.section-title {
	  font-size: 16px;
	  font-weight: 600;
	  color: #334155;
	}
</style>