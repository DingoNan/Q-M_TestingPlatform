<template>
  <el-scrollbar height="calc(100vh - 70px)">
	<div class='create_test'>
		  <el-form :model="apiForm">
			<div class='action'>
				<el-form-item>
				      <el-button type="primary" @click="()=>{this.$router.push({name: 'api'})}">返回</el-button>
					  <el-button type="primary" @click="()=>{this.$router.push({name: 'api'})}">复制</el-button>
				      <el-button type="primary" @click='saveApi'>保存</el-button>
				</el-form-item>
			</div>
			<div class='interface_info'>
				<el-divider content-position="left">接口基本信息</el-divider>
				<el-form :inline="true">
					<el-form-item label="接口名称">
						<el-input v-model="apiForm.name"></el-input>
					</el-form-item>
					<el-form-item label="所属服务">
						<el-select v-model="apiForm.service" clearable>
							<el-option v-for="service in service_list" :label='service.name' :value="service.id" />
						</el-select>
					</el-form-item>
					<el-form-item label="所属模块">
						<el-cascader collapse-tags v-model='apiForm.module' :options="plant_module_list" :props="editProps" clearable  style="width: 100%;"/>
					</el-form-item>
					<el-form-item label="请求方法">
						<el-select v-model="apiForm.method" clearable>
							<el-option v-for="http_method in methods" :label='http_method' :value="http_method" />
						</el-select>
					</el-form-item>
					<el-form-item label="接口地址">
						<el-input v-model="apiForm.url" placeholder="url请以'/'开头" style="width: 250px;"/>
					</el-form-item>
					<el-form-item label="请求头">
						<el-select v-model="apiForm.headers" @change='setHeaderValue'>
							<el-option v-for="header_obj in header_list" :label='header_obj.name' :value="header_obj.id" />
						</el-select>
					</el-form-item>
				</el-form>
			</div>
			<el-divider content-position="left">接口请求信息</el-divider>
			<el-tabs :tab-position="position" class="demo-tabs">
				<el-tab-pane label="请求头(Headers)">
					<KeyTable :keyData='headerValue' :readOnly='true'></KeyTable>
				</el-tab-pane>
				<el-tab-pane label="查询参数(Params)">
					<KeyTable :keyData='apiForm.params' :readOnly='false'></KeyTable>
				</el-tab-pane>
				<el-tab-pane label="请求体(Body)">
					<el-radio-group v-model="bodyType">
						<el-radio label="json">json</el-radio>
						<el-radio label="data">data</el-radio>
					</el-radio-group>
					<BodyEdit v-model='apiForm.body'></BodyEdit>
				</el-tab-pane>
				<el-tab-pane label="数据提取(Extract)">
					<Extract :keyData='apiForm.extract' :readOnly='false'></Extract>
				</el-tab-pane>
				<el-tab-pane label="断言(Check)">
					<Check :keyData='apiForm.check' :readOnly='false'></Check>
				</el-tab-pane>
			</el-tabs>
		  </el-form>
	</div>
  </el-scrollbar>
  
  
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen, CopyDocument, Top, Bottom} from '@element-plus/icons-vue'
import BodyEdit from '../../components/BodyEdit.vue'
import KeyTable from '../../components/KeyTable.vue'
import Extract from '../../components/Extract.vue'
import Check from '../../components/Check.vue'

export default{
	setup() {
		return {
			Edit,
			Delete,
			Plus,
			View,
			EditPen,
			CopyDocument,
			Top,
			Bottom,
		}
	},
	components: {
		BodyEdit,
		KeyTable,
		Extract,
		Check,
	},
	data() {
		return {
			editProps:{
				emitPath: false,
				value: 'id',
				label: 'name',
			},
			headersData: [],
			paramsData: [],
			methods: [
				'GET',
				'POST',
				'PUT',
				'DELETE',
			],
			plant_module_list: [],
			key_type: ['Str', 'Number', 'Bool'],
			data: [],
			json_row_data: {
				key: '',
				// 0 固定值， 1 Faker
				generate: 0,
				type: 'Str',
				value: '',
				
			},
			bodyType: 'json',
			showEdit: false,
			position: 'top',
			service_list: [],
			header_list: [],
			headerValue: [],
			apiForm:{
				id: '',
				module: '',
				name: '',
				url: '',
				method: '',
				service: '',
				headers: '',
				json: '',
				data: '',
				body: '',
				params: [],
				extract: [],
				check: [],
			},
		}
	},
	computed:{
		...mapState(['projectInfo']),
	},
	methods: {
		setHeaderValue(value){
			const index = this.header_list.findIndex(item=>{
				return item.id === value
			})
			if(index != -1){
				this.headerValue = this.header_list[index].value
			}			
		},
		saveApi(){
			if(this.bodyType === 'json'){
				this.apiForm.json = this.apiForm.body
				this.apiForm.data = ''
			}else{
				this.apiForm.data = this.apiForm.body
				this.apiForm.json = ''
			}
			if(this.$route.query.id){
				this.updateApi()
			}else{
				this.createApi()
			}
		},
		async getPlantModule(){
			const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
			if (response.status === 200){
				this.plant_module_list = response.data.results
			}
		},
		async createApi(){
			const response = await this.$api.createApi(this.apiForm)
			if (response.status === 201){
				this.$router.push({name: 'api'})
			}
		},
		async updateApi(){
			const response = await this.$api.updateApi(this.apiForm.id, this.apiForm)
			if (response.status === 200){
				this.$router.push({name: 'api'})
			}
		},
		async getApi(id){
			const response = await this.$api.getApi(id)
			if (response.status === 200){
				this.apiForm = response.data.result
				this.setBody()
				this.setHeaderValue(this.apiForm.headers)
			}
		},
		setBody(){
			if(this.apiForm.json){
				this.apiForm.body = this.apiForm.json
			}else{
				this.bodyType = 'data'
				this.apiForm.body = this.apiForm.data
			}
		},
		async getServices(){
			const response = await this.$api.getServices({project: this.projectInfo.id})
			if (response.status === 200){
				this.service_list = response.data.results
			}
		},
		async getHeaders(){
			const response = await this.$api.getHeaders({project: this.projectInfo.id})
			if (response.status === 200){
				this.header_list = response.data.results
				if(this.$route.query.id){
					this.getApi(this.$route.query.id)
				}
			}
		}
	},
	created() {
		this.getPlantModule()
		this.getServices()
		this.getHeaders()
	}
}

</script>

<style scoped>
	.action{
		float: right;
	}
	.create_test{
		margin: 20px 20px;
	}
	.interface_info{
		clear: both;
		/* margin-bottom: 40px; */
	}
	.create_test .el-input-group__append{
		background-color: white;
		box-shadow: none;
		border: none;
		/* padding: 0px; */
	}
	.script{
		text-align: center;
	}
	.script .el-button{
		width: 100px;
	}
	.json{
		overflow-x: hidden;
	}
</style>