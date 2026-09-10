<template>
	<el-dialog v-model="editCaseVisible" :title="title" width="600" :close-on-click-modal='false'>
		<el-form :model="caseForm" label-position='top' :disabled='caseView' :rules="caseRules" ref='caseRef'>
			<el-form-item label="用例名称" prop="name">
				<el-input v-model="caseForm.name" autocomplete="off" placeholder="请输入用例名称" style="width: 960px;"/>
			</el-form-item>
			<el-form-item label="所属模块" prop='module'>
				<el-cascader placeholder='请选择或输入模块名称' collapse-tags v-model="caseForm.module" :options="plant_module_list" :props="moduleEditProps" clearable  style="width: 100%;" filterable/>
			</el-form-item>
			<el-form-item label="用例类型" prop='type'>
				<el-select v-model="caseForm.type" placeholder="请选择用例类型" clearable multiple @change='selectTypeChange' @visible-change='visible_change'>
					<el-option :disabled='ApiSelectVisible' v-for="case_type in caseType.slice(0, 1)" :label='case_type' :value="case_type" />
					<el-option :disabled='UiSelectVisible' v-for="case_type in caseType.slice(1)" :label='case_type' :value="case_type" />
				</el-select>
			</el-form-item>
			<!-- <el-form-item label="是否设为数据工厂数据">
				<el-switch v-model="caseForm.is_data_factory" />
				<el-tooltip placement="right" effect="light">
					<template #content>
						建议需要用来测试数据构造的用例可开启开关
					</template>
					<el-icon color='green'><InfoFilled /></el-icon>
				</el-tooltip>
				<span>开启后会在造数列表显示</span>
			</el-form-item> -->
			<el-form-item label="用例标签:" prop="tag">
				<el-select v-model="caseForm.tag" placeholder="请选择用例标签" clearable multiple>
					<el-option v-for="tag in tag_list" :label='tag.name' :value="tag.id" />
				</el-select>
			</el-form-item>
		</el-form>
		<template #footer>
			<span class="dialog-footer" v-if='!caseView'>
				<el-button @click="editCaseVisible = false">取消</el-button>
				<el-button type="primary" v-if='title === "新增用例"' @click="createCase">确认</el-button>
				<el-button type="primary" v-if='title === "编辑用例"' @click="updateCase">确认</el-button>
			</span>
		</template>
	</el-dialog>
	<div class="case" v-if='case_model==="tree"' >
		<el-container>
		  <el-card style='margin-bottom: 10px;'>
		  	<el-aside style=" height: 740px; background-color: var(--qm-bg-2); margin-top: 10px; margin-left: 10px;" :style="{ width: `${asideWidth}px` }">
			   <vxe-tree
					 ref="treeRef"
					 :show-line="false"
					 @current-change='moduleSelect'
					 :node-config="{isHover: true, isCurrent: true}"
					 transform
					 title-field="name"
					 key-field="id"
					 parent-field="parent_id"
					 :data="moduleTree">
					 <template #title="{ node }">
						 <vxe-icon v-if='node.hasOwnProperty("params")' status="primary" name="dot"></vxe-icon>
						 <vxe-icon v-else status="primary" name="folder"></vxe-icon>
						 <span>{{ "  " + node.name }}</span>
					 </template>
				</vxe-tree>
		  	</el-aside>	  
		  </el-card>
		  
		  <el-main style="padding-top: 0px; padding-left: 10px; padding-right: 0px;">
			  <div class="case_tree case">
				 <el-card style='margin-bottom: 10px;'>
				 	<el-form  :model="caseSearch" label-width="100px"  class='searchForm'>
				 		<el-row :gutter="20">
				 			<el-col :span='6'>
				 				<el-form-item label="用例名称">
				 					<el-input v-model="caseSearch.name" placeholder="请输入用例名称" clearable/>
				 				</el-form-item>
				 			</el-col>
				 			<el-col :span='6'>
				 				<el-form-item label="用例类型">
				 					<el-select v-model="caseSearch.type" placeholder="请选择用例类型" clearable>
				 						<el-option v-for="case_type in caseType" :label='case_type' :value="case_type" />
				 					</el-select>
				 				</el-form-item>
				 			</el-col>
				 			<el-col :span='6'>
				 				<el-form-item label="用例标签">
				 					<el-select v-model="caseSearch.tag" placeholder="请选择用例标签" clearable>
				 						<el-option v-for="tag in tag_list" :label='tag.name' :value="tag.id" />
				 					</el-select>
				 				</el-form-item>
				 			</el-col>
				 			<el-col :span='6'>
				 				<el-form-item label="最近测试结果">
				 					<el-select v-model="caseSearch.recent_test_result" placeholder="请选择最近测试结果" clearable>
				 						<el-option v-for="result in result_list" :label='result.label' :value="result.value" />
				 					</el-select>
				 				</el-form-item>
				 			</el-col>
				 		</el-row>
				 		<el-row :gutter='20'>
				 			<el-col :span='6'>
				 				<el-form-item label="创建人">
				 					<el-select v-model="caseSearch.create_by" placeholder="请选择创建人" clearable filterable>
				 						<el-option v-for="user_obj in user_list" :label='user_obj.username' :value="user_obj.id" />
				 					</el-select>
				 				</el-form-item>
				 			</el-col>
				 			<el-col :span='6'>
				 				<el-form-item label="更新人">
				 					<el-select v-model="caseSearch.update_by" placeholder="请选择更新人" clearable filterable>
				 						<el-option v-for="user_obj in user_list" :label='user_obj.username' :value="user_obj.id" />
				 					</el-select>
				 				</el-form-item>
				 			</el-col>
				 			<div style="margin-left: auto; margin-right: 20px; margin-bottom: 20px;">
				 				<el-button @click="reset">重置</el-button>
				 				<el-button type="primary" @click="search">查询</el-button>
				 			</div>	
				 		</el-row>
				 	</el-form>	  
				 </el-card>
				 <el-card style='margin-bottom: 10px;'>
				 	<div style="background-color: var(--qm-bg-2); padding-bottom: 10px;">
						 <div style="padding-top: 10px; padding-right: 25px; padding-bottom: 10px; background-color: var(--qm-bg-2); display: flex; justify-content: flex-end" class='btn_right'>
							<el-tooltip content="切换模式">
								<el-button  @click="changeMode" :icon="Switch"></el-button>
							</el-tooltip>
							<el-button v-if='permission.has_add_permission' @click="addCase" type="primary" >新增</el-button>
						 </div>
						 <el-table :max-height='550' :data="case_list.results" class='table' @row-dblclick='editStep' :show-overflow-tooltip='true'  :header-row-style="headerRowStyle">
						 <!-- <el-table-column label="ID" width="70" prop="id" align="center"/> -->
						 <el-table-column label="用例名称" prop="name" min-width="100" align="center">
							<template #default='scope'>
								<el-link type="primary" @click='editStepTwo(scope.row)'>{{ scope.row.name }}</el-link>
							</template>
						 </el-table-column>
						 <el-table-column label="最近测试结果" prop="recent_test_result_name" width="150" align="center" >
							<template #default="scope">
								  <el-tag v-if='scope.row.recent_test_result_name ==="成功"' effect="dark" type="success" round>{{ scope.row.recent_test_result_name }}</el-tag>
								  <el-tag v-if='scope.row.recent_test_result_name ==="失败"' effect="dark" type="danger" round>{{ scope.row.recent_test_result_name }}</el-tag>
								  <el-tag v-if='scope.row.recent_test_result_name ==="错误"' effect="dark" type="danger" round>{{ scope.row.recent_test_result_name }}</el-tag>
								  <el-tag v-if='scope.row.recent_test_result_name ==="未执行"' effect="dark"  round>{{ scope.row.recent_test_result_name }}</el-tag>
							</template>
						 </el-table-column>
						 <el-table-column label="用例类型" prop="type" width="150" align="center" />
						 <el-table-column label="用例标签" prop="tag_name" width="100" :formatter="formatter_tag" align="center"/>
						 <el-table-column label="创建人" prop="create_by_name"  width="100" align="center"/>
						 <el-table-column label="更新人" prop="update_by_name"  width="100" align="center"/>
						 <el-table-column label="创建时间" prop="create_time" sortable width="180" align="center"/>
						 <el-table-column label="更新时间" prop="update_time" sortable width="180" align="center"/>
						 <el-table-column align="center" :width='calcMinWidth' label="操作">
							<template #default="scope">
							  <el-tooltip content="查看用例" >
								 <el-button v-if="permission.has_read_permission" :icon="View" @click="viewCase(scope.row)" style="width: 36px; height: 24px;"></el-button>
							  </el-tooltip>
							  <el-tooltip content="编辑用例">
								 <el-button v-if="permission.has_edit_permission" :icon="EditPen" @click="editCase(scope.row)" style="width: 36px; height: 24px;"></el-button>
							  </el-tooltip>
							  <el-tooltip content="复制用例">
								 <el-button v-if="permission.has_add_permission" size='small' @click="copy(scope.row)" :icon="CopyDocument" style="width: 36px; height: 24px;"></el-button>
							  </el-tooltip>
							  <el-tooltip content="删除用例">
								  <el-button v-if="permission.has_delete_permission" @click="deleteCase(scope.row.id)" size="small" :icon="Delete" style="width: 36px; height: 24px;"></el-button>
							  </el-tooltip>
							</template>
						 </el-table-column>
						 </el-table>
						 <div style="margin: 10px; float: right; padding-top: 10px;">
						 <el-pagination
						   v-model:current-page="page_size_params.page"
						   v-model:page-size="page_size_params.size"
						   :page-sizes="[10, 20, 30, 50]"
						   :hide-on-single-page="false"
						   layout="total, sizes, prev, pager, next, jumper"
						   :total="case_list.count"
						   @size-change="handleSizeChange"
						   @current-change="handleCurrentChange"
						 />
						 </div>
				 	</div>	  
				 </el-card>
			  </div>
		  </el-main>
		</el-container>
	</div>
	<div class="case" v-if='case_model==="list"'>
		<el-card style='margin-bottom: 10px;'>
			<el-form  :model="caseSearch" label-width="100px"  class='searchForm'>
					<el-row :gutter="20">
						<el-col :span='6'>
							<el-form-item label="用例名称">
								<el-input v-model="caseSearch.name" placeholder="请输入用例名称" clearable/>
							</el-form-item>
						</el-col>
						<el-col :span='6'>
							<el-form-item label="用例类型">
								<el-select v-model="caseSearch.type" placeholder="请选择用例类型" clearable>
									<el-option v-for="case_type in caseType" :label='case_type' :value="case_type" />
								</el-select>
							</el-form-item>
						</el-col>
						<el-col :span='6'>
							<el-form-item label="所属模块" >
								<el-cascader collapse-tags :show-all-levels="false" v-model='caseSearch.module_list' :options="plant_module_list" :props="props" clearable style="width: 100%;" />
							</el-form-item>
						</el-col>
						<el-col :span='6'>
							<el-form-item label="用例标签">
								<el-select v-model="caseSearch.tag" placeholder="请选择用例标签" clearable>
									<el-option v-for="tag in tag_list" :label='tag.name' :value="tag.id" />
								</el-select>
							</el-form-item>
						</el-col>
						<el-col :span='6'>
							<el-form-item label="最近测试结果">
								<el-select v-model="caseSearch.recent_test_result" placeholder="请选择最近测试结果" clearable>
									<el-option v-for="result in result_list" :label='result.label' :value="result.value" />
								</el-select>
							</el-form-item>
						</el-col>
						<el-col :span='6'>
							<el-form-item label="创建人">
								<el-select v-model="caseSearch.create_by" placeholder="请选择创建人" clearable filterable>
									<el-option v-for="user_obj in user_list" :label='user_obj.username' :value="user_obj.id" />
								</el-select>
							</el-form-item>
						</el-col>
						<el-col :span='6'>
							<el-form-item label="更新人">
								<el-select v-model="caseSearch.update_by" placeholder="请选择更新人" clearable filterable>
									<el-option v-for="user_obj in user_list" :label='user_obj.username' :value="user_obj.id" />
								</el-select>
							</el-form-item>
						</el-col>
						<div style="margin-left: auto; margin-right: 20px; margin-bottom: 20px;">
							<el-button @click="reset">重置</el-button>
							<el-button type="primary" @click="search">查询</el-button>
						</div>
					</el-row>
			</el-form>	  
		</el-card>
		<el-card style='margin-bottom: 10px;'>
			<div style="background-color: var(--qm-bg-2); padding-bottom: 10px;">
					   <div style="padding-top: 10px; padding-right: 24px; padding-bottom: 10px; background-color: var(--qm-bg-2); display: flex; justify-content: flex-end" class='btn_right'>
					   		<el-tooltip content="切换模式">
					   			<el-button  @click="changeMode" :icon="Switch"></el-button>
					   		</el-tooltip>
					   	<el-button v-if='permission.has_add_permission' @click="addCase" type="primary" >新增</el-button>
					   </div>
					   <el-table :max-height='550' :data="case_list.results" class='table' @row-dblclick='editStep' :show-overflow-tooltip='true' :header-row-style="headerRowStyle">
					   		<!-- <el-table-column label="ID" width="70" prop="id" align="center"/> -->
					   		<el-table-column label="用例名称" prop="name" min-width="100" align="center">
					   			<template #default='scope'>
					   				<el-link type="primary" @click='editStepTwo(scope.row)'>{{ scope.row.name }}</el-link>
					   			</template>
					   		</el-table-column>
					   		<el-table-column label="最近测试结果" prop="recent_test_result_name" width="150" align="center" >
					   			<template #default="scope">
					   			      <el-tag v-if='scope.row.recent_test_result_name ==="成功"' effect="dark" type="success" round>{{ scope.row.recent_test_result_name }}</el-tag>
					   				  <el-tag v-if='scope.row.recent_test_result_name ==="失败"' effect="dark" type="danger" round>{{ scope.row.recent_test_result_name }}</el-tag>
					   				  <el-tag v-if='scope.row.recent_test_result_name ==="错误"' effect="dark" type="danger" round>{{ scope.row.recent_test_result_name }}</el-tag>
					   				  <el-tag v-if='scope.row.recent_test_result_name ==="未执行"' effect="dark"  round>{{ scope.row.recent_test_result_name }}</el-tag>
					   			</template>
					   		</el-table-column>
					   		<el-table-column label="用例类型" prop="type" width="150" align="center" />
					   		<el-table-column label="用例标签" prop="tag_name" width="100" :formatter="formatter_tag" align="center"/>
					   		<el-table-column label="所属平台" prop="plant_name" min-width="100" align="center"/>
					   		<el-table-column label="所属模块" prop="module_name" min-width="100" align="center"/>
					   		<el-table-column label="创建人" prop="create_by_name"  width="100" align="center"/>
					   		<el-table-column label="更新人" prop="update_by_name"  width="100" align="center"/>
					   		<el-table-column label="创建时间" prop="create_time" sortable width="180" align="center"/>
					   		<el-table-column label="更新时间" prop="update_time" sortable width="180" align="center"/>
					   		<el-table-column align="center" :width='calcMinWidth' label="操作">
					   			<template #default="scope">
					   			  <el-tooltip content="查看用例" >
					   			  	 <el-button v-if="permission.has_read_permission" :icon="View" @click="viewCase(scope.row)" style="width: 36px; height: 24px;"></el-button>
					   			  </el-tooltip>
					   			  <el-tooltip content="编辑用例" >
					   			  	 <el-button v-if="permission.has_edit_permission" :icon="EditPen" @click="editCase(scope.row)" style="width: 36px; height: 24px;"></el-button>
					   			  </el-tooltip>
					   			  <el-tooltip content="复制用例">
					   				 <el-button v-if="permission.has_add_permission" size='small' @click="copy(scope.row)" :icon="CopyDocument" style="width: 36px; height: 24px;"></el-button>
					   			  </el-tooltip>
					   			  <el-tooltip content="删除用例">
					   				  <el-button v-if="permission.has_delete_permission" @click="deleteCase(scope.row.id)" size="small" :icon="Delete" style="width: 36px; height: 24px;"></el-button>
					   			  </el-tooltip>
					   			</template>
					   		</el-table-column>
					   </el-table>
					   <div style="margin: 10px; float: right; padding-top: 10px;">
					   		<el-pagination
					   		  v-model:current-page="page_size_params.page"
					   		  v-model:page-size="page_size_params.size"
					   		  :page-sizes="[10, 20, 30, 50]"
					   		  :hide-on-single-page="false"
					   		  layout="total, sizes, prev, pager, next, jumper"
					   		  :total="case_list.count"
					   		  @size-change="handleSizeChange"
					   		  @current-change="handleCurrentChange"
					   		/>
					   </div>
			</div>
				  	  
		</el-card>
	 
	   
	</div>
	
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen, CopyDocument, Switch} from '@element-plus/icons-vue'

export default{
	computed:{
		...mapState(['pathPermission', 'projectInfo']),
		calcMinWidth() {
		  let visibleButtons = 0;
		  if (this.permission.has_add_permission) visibleButtons += 1;  // header中的新增按钮
		  if (this.permission.has_read_permission) visibleButtons += 1;
		  if (this.permission.has_edit_permission) visibleButtons += 1;
		  if (this.permission.has_delete_permission) visibleButtons += 1;
		  
		  return Math.max(10, visibleButtons * 65);
		}
	},
	data() {
		return {
			caseView: false,
			caseType:['API'],
			result_list: [
				{label: '成功', value: 1},
				{label: '失败', value: 2},
				{label: '错误', value: 3},
				{label: '未执行', value: 4},
			],
			asideWidth: 300,
			tag_list: '',
			caseForm:{
				project: '',
				id: '',
				module: '',
				name: '',
				type: ['API'],
				tag: '',
				params: [],//用例局部变量
				is_data_factory: false,
				is_performance: true,
			},
			caseRules: {
				name: [{
					required: true,
					message: '用例名称不能为空',
					trigger: 'blur',
				}],
				module: [{
					required: true,
					message: '请选择所属模块',
					trigger: 'change',
				}],
				type: [{
					required: true,
					message: '请选择用例类型',
					trigger: 'change',
				}],
				tag: [{
					required: true,
					message: '请选择用例标签',
					trigger: 'change',
				}],
			},
			caseFormTmp:{
				project: '',
				id: '',
				module: '',
				name: '',
				type: ['API'],
				tag: '',
				params: [],//用例局部变量
				is_data_factory: false,
				is_performance: true,
			},
			editCaseVisible: false,
			props: {
				multiple: true,
				emitPath: true,
				value: 'id',
				label: 'name',
			},
			moduleEditProps:{
				emitPath: false,
				value: 'id',
				label: 'name',
				checkStrictly: true,
			},
			case_model: 'tree',
			permission: {},
			caseSearch:{
				name: '',
				service: '',
				method: '',
				url: '',
				project: '',
				type: '',
				tag: '',
				module_list: [],
				is_data_factory: false,
				is_performance: true,
				result: '',
				create_by: '',
				update_by: '',
			},
			moduleTree: [],
			page_size_params: {
				page: 1,
				size: 10,
			},
			count: 1,
			title: '新增用例',
			case_list: [],
			user_list: [],
			service_list: [],
			ViewVisible: false,
			ApiSelectVisible: false,
			UiSelectVisible: false,
			plant_module_list: [],
			moduleSave:{
				project: '',
				name: '',
				plant: '',
				module: '',
			},
			role_names: [],
		}
	},
	setup() {
		return {
			Edit,
			Delete,
			Plus,
			View,
			EditPen,
			CopyDocument,
			Switch
		}
	},
	methods:{
		...mapActions(['getRolePermission']),
		handleCurrentChange(){
			this.getCases()
		},
		changeMode(){
			if (this.case_model === 'tree'){
				this.case_model = 'list'
				this.caseSearch.module_list = []
			}else{
				this.case_model = 'tree'
				this.setTree()
			}
			localStorage.setItem('case_model', this.case_model)
		},
		headerRowStyle() {
		    return {
		      'font-weight': 'bold',
		      'color': '#606266',
		      'background-color': '#f5f7fa' // 可选背景色
		    }
		},
		async getPlantModuleCase(){
			const response = await this.$api.getAllPlantModuleCase({project: this.projectInfo.id})
			if (response.status === 200){
				this.moduleTree = response.data.results
			}
		},
		moduleSelect({ node, checked, $event }){
			localStorage.setItem('case_node', JSON.stringify(node))
			this.caseSearch.module_list = this.getAllIds(node)
			this.getCases(false)
		},
		getAllIds(node) {
		  // 如果节点为空，返回空数组
		  if (!node) return [];
		  
		  // 初始化结果数组（包含当前节点ID）
		  const ids = [node.id];
		  
		  // 递归处理子节点
		  if (node.children && Array.isArray(node.children)) {
		    node.children.forEach(child => {
		      // 递归获取子节点的ID并合并到结果数组
		      ids.push(...this.getAllIds(child));
		    });
		  }
		  
		  return ids;
		},
		handleSizeChange(){
			this.getCases()
		},
		search(){
			this.getCases()
		},
		selectTypeChange(value){
			if(value.includes('API')){
				this.UiSelectVisible = true
				this.ApiSelectVisible = false
			}else if(value.includes('WEB_UI') || value.includes('APP_UI')){
				this.ApiSelectVisible = true
				this.UiSelectVisible = false
			}else{
				this.ApiSelectVisible = false
				this.UiSelectVisible = false
			}
		},
		visible_change(){
			if (this.caseForm.type.includes('API')){
				this.UiSelectVisible = true
				this.ApiSelectVisible = false
			}else if(this.caseForm.type.includes('WEB_UI') || this.caseForm.type.includes('APP_UI')){
				this.UiSelectVisible = false
				this.ApiSelectVisible = true
			}else{
				this.ApiSelectVisible = false
				this.UiSelectVisible = false
			}
		},
		async copyCase(id){
			const response = await this.$api.copyCase({case_id: id})
			if (response.status === 200){
				this.getCases()
				ElMessage({message: "复制成功", type: 'success'})
			}
		},
		copy(row_data){
			this.caseForm = {...row_data}
			this.caseForm.name = this.caseForm.name + '副本'
			this.createCase()
		},
		formatter_tag(row, column, cellValue, index){
			if (row.tag_name.length !=0){
				var tags = []
				for (var i = 0; i < row.tag_name.length; i++) {  
				  tags[i] = row.tag_name[i].name
				}
				return tags.join('/')
			}else{
				return '-'
			}
			
		},
		formatter_type(row, column, cellValue, index){
			if (row.type.length !=0){
				var types = []
				for (var i = 0; i < row.type.length; i++) {  
				  types[i] = row.type[i].name
				}
				return tags.join('/')
			}else{
				return '-'
			}
			
		},
		reset(){
			for(let key in this.caseSearch){
				if(key === 'module_list'){
					this.caseSearch[key] = []
				}else{
					this.caseSearch[key] = ''
				}
			}
			this.caseSearch['is_data_factory'] = false
			this.caseSearch['is_performance'] = true
		},
		editCase(row_data){
			this.editCaseVisible = true
			this.caseView = false
			this.title = '编辑用例'
			this.caseForm = {...row_data}
			this.$refs.caseRef.resetFields();
		},
		viewCase(row_data){
			this.editCaseVisible = true
			this.title = '查看用例'
			this.caseView = true
			this.caseForm = {...row_data}
		},
		addCase(){
			this.title = '新增用例'
			this.caseView = false
			this.caseForm = {...this.caseFormTmp}
			this.editCaseVisible = true
			if ( this.$refs.treeRef.getCurrentNodeId() > 0){
				this.caseForm.module = Number(this.$refs.treeRef.getCurrentNodeId())
			}
			this.$refs.caseRef.resetFields();
		},
		async createCase(){
			if(this.caseForm.module < 0){
				ElMessage({message: "所属模块不能选择根节点", type: 'error'})
				return 
			}
			this.$refs['caseRef'].validate(async (valid, fields)=>{
				if(valid){
					this.caseForm.project = this.projectInfo.id
					const response = await this.$api.createCase(this.caseForm)
					if (response.status === 201){
						this.editCaseVisible = false
						this.getCases()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		async updateCase(){
			if(this.caseForm.module < 0){
				ElMessage({message: "所属模块不能选择根节点", type: 'error'})
				return 
			}
			this.$refs['caseRef'].validate(async (valid, fields)=>{
				if(valid){
					const response = await this.$api.updateCase(this.caseForm.id, this.caseForm)
					if (response.status === 200){
						this.editCaseVisible = false
						this.getCases()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		async deleteCase(id){
			ElMessageBox.confirm(
			    '确定删除?',
			    '提示',
			    {
			      confirmButtonText: '确认',
			      cancelButtonText: '取消',
			      type: 'warning',
			    }
			  ).then(async() => {
				  const response = await this.$api.deleteCase(id)
				  if (response.status === 204){
					  this.getCases()
					  ElMessage({
					    type: 'success',
					    message: '删除成功',
					  })
				  }
				  
			    }).catch(() => {})
		},
		async getPlantModule(){
			const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
			if (response.status === 200){
				this.plant_module_list = response.data.results
			}
		},
		async getCases(){
			this.caseSearch.project = this.projectInfo.id
			const data = Object.assign(this.caseSearch, this.page_size_params)
			this.caseSearch.module = (this.caseSearch.module_list || []).join(',')
			const response = await this.$api.getCases(data)
			if (response.status === 200){
				this.case_list = {...response.data}
			}
		},
		async getTags(){
			const response = await this.$api.getTags({project: this.projectInfo.id})
			if (response.status === 200){
				this.tag_list = response.data.results
			}
		},
		editStep(row, column, event){
			localStorage.setItem('case_model', this.case_model)
			this.$router.push({name: 'caseStepEdit', query: {id: row.id}})
		},
		editStepTwo(row){
			localStorage.setItem('case_model', this.case_model)
			this.$router.push({name: 'caseStepEdit', query: {id: row.id}})
		},
		async setTree() {
		  try {
		    await Promise.race([
		      new Promise(resolve => {
		        const checkRef = () => {
		          if (this.$refs.treeRef) {
		            resolve();
		          } else if (Date.now() - startTime < 5000) {
		            setTimeout(checkRef, 500);
		          } else {
		            throw new Error('treeRef未在3秒内加载完成');
		          }
		        };
		        const startTime = Date.now();
		        checkRef();
		      }),
		      new Promise((_, reject) => 
		        setTimeout(() => reject('操作超时'), 5000)
		      )
		    ]);
		
		    // 执行树操作
		    await this.$refs.treeRef.setAllExpandNode(true);
		    const node =  JSON.parse(localStorage.getItem('case_node'));
		    if (node) {
		      this.$refs.treeRef.setCurrentNodeId(node.id);
			  this.caseSearch.module_list = this.getAllIds(node)
		    }
		  } catch (error) {
		    console.error('树操作失败:', error);
		  }
		  this.getCases(false)
		}
	},
	created() {
		this.case_model = localStorage.getItem('case_model') || 'tree'
		this.user_list =  JSON.parse(localStorage.getItem('user_list'))
		this.getRolePermission(this.pathPermission[this.$route.path]).then(res =>{
			this.permission = {...res.result}
			localStorage.setItem('caseListPermission', JSON.stringify(this.permission))
		})
		this.getPlantModuleCase()
		this.getPlantModule()
		this.getPlantModule()
		this.getTags()
		if (this.case_model === 'tree'){
			this.setTree()
		}else{
			this.getCases()
		}
	}
}
</script>

<style scoped>
	.case{
		width: 100%;
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}
	.case .searchForm{
		
		background-color: var(--qm-bg-2);
		padding: 15px 15px 0 15px;
		
	}
	.case .el-form--inline .el-form-item{
		margin-bottom: 15px;
	}
	.case .table{
		background-color: var(--qm-bg-2);
		flex: 1;
		margin-right: 10px;
		margin-left: 10px;
	}
	
	.form .el-select{
		width: 300px;
	}
	.el-button{
		width: 70px;
	}
	.el-icon{
		margin-left: 10px;
	}
	::v-deep .el-card__body{
			padding: 0px;
	}
	
</style>
