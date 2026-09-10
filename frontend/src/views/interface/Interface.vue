<template>
	<div class="common-layout" style="width: 100%;">
		<el-container>
		      <el-header class='header' style="margin: 10px 20px; background-color: var(--qm-bg-2); padding-top: 15px">
				<el-form :inline="true" :model="interfaceSerarch" label-width="70px" style="min-width: 1200px;"> 
				  <el-form-item label="接口名称">
					<el-input v-model="interfaceSerarch.name" placeholder="请输入接口名称" clearable/>
				  </el-form-item>
				  <el-form-item label="请求方法">
					<el-select
							v-model="interfaceSerarch.method"
							placeholder="请选择请求方法"
							clearable
						  >
							<el-option v-for="http_method in methods" :label='method' :value="http_method" />
					</el-select>
				  </el-form-item>
				  <el-form-item label="接口地址">
						<el-input v-model="interfaceSerarch.url" placeholder="请输入接口地址" clearable />
				  </el-form-item>
				  <el-form-item label="接口类型">
						<el-select
								v-model="interfaceSerarch.type"
								placeholder="请选择接口类型"
								clearable
							  >
								<el-option label="项目接口" value="1" />
								<el-option label="外部接口" value="2" />
						</el-select>
				  </el-form-item>
				  <el-form-item>
					<el-button type="primary" @click="reset">重置</el-button>
					<el-button type="primary" @click="search">搜索</el-button>
				  </el-form-item>
				</el-form>
			  </el-header>
		      <el-main style="background-color: var(--qm-bg-2); margin: 0 20px 20px 20px;">
				<el-dialog v-model="addDialogVisible" :title="interfaceFormTitle" style="width: 500px;">
				    <el-form :model="interfaceForm" class='form'>
						 <el-form-item label="接口类型" label-width="80px">
						   <el-select v-model="interfaceForm.type" placeholder="请选择接口类型" clearable>
								<el-option v-for="(value, key) in typeEnum" :label='value' :value='parseInt(key)' />
						   </el-select>
						 </el-form-item>
						  <el-form-item label="接口名称" label-width="80px">
							<el-input v-model="interfaceForm.name" autocomplete="off" placeholder="请输入接口名称"/>
						  </el-form-item>
						  <el-form-item label="请求方法" label-width="80px">
							<el-select v-model="interfaceForm.method" placeholder="请选择请求方法" clearable>
								<el-option v-for="http_method in methods" :label='method' :value="http_method" />
							</el-select>
						  </el-form-item>
						  <el-form-item label="接口地址" label-width="80px">
							<el-input v-model="interfaceForm.url" autocomplete="off" placeholder="请输入接口地址"/>
						  </el-form-item>
				    </el-form>
				    <template #footer>
				      <span class="dialog-footer">
				        <el-button @click="addDialogVisible = false">取消</el-button>
				        <el-button type="primary" @click="submitForm">
				          确认
				        </el-button>
				      </span>
				    </template>
				</el-dialog>
				<el-table :data="interfaces.results" style="width: 100%; height: calc(100vh - 282px);">
					<el-table-column label="序号" width="70" type="index"/>
					<el-table-column label="接口名称" prop="name" min-width="100"/>
					<el-table-column label="请求方法" prop="method" min-width="100"/>
					<el-table-column label="接口地址" prop="url" min-width="100"/>
					<el-table-column label="接口类型" prop="type" :formatter="formatterType" min-width="100"/>
					<el-table-column label="创建时间" prop="create_time" sortable min-width="150"/>
					<el-table-column label="更新时间" prop="update_time" sortable min-width="150"/>
					<el-table-column align="center" min-width="150">
						<template #header>
						<el-button type='primary' @click="addDialogVisible = true">新增</el-button>
						</template>
						<template #default="scope">
						  <el-button :icon="Edit" size="small" @click="editInterface(scope.row)">编辑</el-button
						  >
						  <el-button
						    @click="deleteInterface(scope.row.id)"
							size="small"
							type="danger"
						  :icon="Delete"
							>删除</el-button
						  >
						</template>
					</el-table-column>
				</el-table>
				<div style="float: right; padding-top: 10px;">
					<el-pagination
					  v-model:current-page="page_size_params.page"
					  v-model:page-size="page_size_params.size"
					  :page-sizes="[10, 20, 30, 50]"
					  :small="small"
					  :disabled="disabled"
					  :background="background"
					  :hide-on-single-page="false"
					  layout="total, sizes, prev, pager, next, jumper"
					  :total="interfaces.count"
					  @size-change="handleSizeChange"
					  @current-change="handleCurrentChange"
					/>
				</div>
				
			</el-main>
		</el-container>
	</div>
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus} from '@element-plus/icons-vue'

export default{
	data() {
		return {
			typeEnum:{
				1: '项目接口',
				2: '外部接口'
			},
			interfaceFormTitle: '新增接口',
			page_size_params: {

				page: 1,

				size: 10,

			},
			interfaces: '',
			interfaceSerarch: {
				name: '',
				url: '',
				method: '',
				
			},
			count: 1,
			addDialogVisible: false,
			interfaceForm: {
				name: '',
				method: '',
				url: '',
				type: '',
			},
			methods: [
				'GET',
				'POST',
				'PUT',
				'DELETE',
			],
		}
	},
	setup() {
		return {
			Edit,
			Delete,
			Plus
		}
	},
	computed:{
		...mapState(['projectInfo']),
	},
	methods:{
		search(){
			this.getInterfaces(Object.assign(this.interfaceSerarch, this.page_size_params))
		},
		reset(){
			for(let key in this.interfaceSerarch){
				this.interfaceSerarch[key] = ''
			}
		},
		handleCurrentChange(){
			this.getInterfaces(Object.assign(this.interfaceSerarch, this.page_size_params))
		},
		handleSizeChange(){
			this.getInterfaces(Object.assign(this.interfaceSerarch, this.page_size_params))
		},
		submitForm(){
			this.addDialogVisible = false
			if(this.interfaceFormTitle === '新增接口'){
				this.createInterface()
			}else{
				this.updateInterface()
			}
			this.interfaceForm = {}
		},
		formatterType(row, column, cellValue, index){
			return this.typeEnum[row.type]
		},
		editInterface(row_data){
			this.addDialogVisible = true
			this.interfaceFormTitle = '编辑接口'
			this.interfaceForm = {...row_data}
			
		},
		async updateInterface(){
			this.interfaceForm.project = this.projectInfo.id
			const response = await this.$api.updateInterface(this.interfaceForm.id, this.interfaceForm)
			if(response.status === 200){
				this.getInterfaces(this.page_size_params)
				ElMessage({message: "保存成功", type: 'success'})
			}
		},
		async createInterface(){
			this.interfaceForm.project = this.projectInfo.id
			const response = await this.$api.createInterface(this.interfaceForm)
			if(response.status === 201){
				this.getInterfaces(this.page_size_params)
				ElMessage({message: "保存成功", type: 'success'})
			}
		},
		async deleteInterface(id){
			const response = await this.$api.deleteInterface(id)
			if (response.status === 204){
				this.getInterfaces(this.page_size_params)
				ElMessage({
				  type: 'success',
				  message: '删除成功',
				})
			}
		},
		async getInterfaces(params){
				params.project = this.projectInfo.id
				const response = await this.$api.getInterfaces(params)
			    if (response.status === 200){
					this.interfaces = response.data
			    }
		}
	},
	created() {
		this.getInterfaces(this.page_size_params)
	}
}
</script>

<style scoped>
	.header .el-input{
		width: 150px;
	}
	.form .el-input{
		width: 300px;
	}
	.form .el-select{
		width: 300px;
	}
	.el-button{
		width: 70px;
	}
	
</style>
