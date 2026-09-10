<template>
	<div>
		<el-dialog v-model="responseStatusVisible" title="新增响应返回体" width="300" append-to-body='append_to_body' :show-close='show_close'>
		    <el-select
		        :disabled='disabled'
		        v-model="response_status"
		        filterable
		        allow-create
		        default-first-option
		        :reserve-keyword="false"
		        placeholder="请选择或输入响应状态码"
		      >
		        <el-option
		          v-for="item in http_status"
		          :key="item"
		          :label="item"
		          :value="item"
		        />
		      </el-select>
		    <template #footer>
		      <div class="dialog-footer">
		        <el-button @click="responseStatusVisible = false">取消</el-button>
		        <el-button @click="saveResponse">确定</el-button>
		      </div>
		    </template>
		</el-dialog>
		<div style='float: right'>
		  <el-button type="primary" @click='saveApi' style='margin-right:15px' >保存</el-button>
		</div>
		<div style="float: right;">
		  <el-button type="primary" @click="()=>{this.$router.push({name: 'api'})}" style='margin-right:10px' >返回</el-button>
		</div>
		<div style="clear: both;">
			<el-form :model="caseForm" style='margin:0'>
				<el-row :gutter="20">
					<el-col :span="8">
						<el-form-item label="接口名称:">
							<el-input v-model="apiForm.name"></el-input>
						</el-form-item>
					</el-col>
					<el-col :span="16">
						<el-form-item label="所属模块:">
							<el-cascader collapse-tags v-model='apiForm.module' :options="plant_module_list" :props="moduleProps" clearable  style="width: 100%;"/>
						</el-form-item>
					</el-col>
				</el-row>
				<el-row :gutter="20">
					<el-col :span="4">
						<el-form-item label="所属服务:">
							<el-select v-model="apiForm.service" clearable>
								<el-option v-for="service in service_list" :label='service.name' :value="service.id" />
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :span="4">
						<el-form-item label="请求方法:">
							<el-select v-model="apiForm.method" clearable>
								<el-option v-for="http_method in methods" :label='http_method' :value="http_method" />
							</el-select>
						</el-form-item>
					</el-col>
					<el-col :span="16">
						<el-form-item label="接口地址:">
							<el-input v-model="apiForm.url" placeholder="url请以'/'开头"/>
						</el-form-item>
					</el-col>
					<!-- <el-col :span="4">
						<el-form-item label="请求头:">
							<el-select v-model="apiForm.headers" @change='setHeaderValue'>
								<el-option v-for="header_obj in header_list" :label='header_obj.name' :value="header_obj.id" />
							</el-select>
						</el-form-item>
					</el-col> -->
				</el-row>
				<div class='api_request_info'>
					<el-tabs v-model="active_request_tab" type="card" @tab-click="handleClick" style='background-color: var(--qm-bg-2), margin: 0'>
						<el-tab-pane label="Headers" name="headers">
							<Header :tableData='apiForm.headers' :func_list='func_list'></Header>
						</el-tab-pane>
						<el-tab-pane label="Params" name="params">
							<Params :tableData='apiForm.params' :func_list='func_list'></Params>
						</el-tab-pane>
						<el-tab-pane label="Json" name="json">
							<Json :tableData='apiForm.json' :func_list='func_list'></Json>
						</el-tab-pane>
						<el-tab-pane label="Data" name="data">
							<Json :tableData='apiForm.data' :func_list='func_list'></Json>
						</el-tab-pane>
						<el-tab-pane label="Response" name="response">
							<el-tabs v-model="response_tab_active" type="card" editable @edit="addResponseTab">
							    <el-tab-pane v-for="(item, index) in apiForm.response" :key="index" :label="`Response[${item.response_status}]`" :name="index">
							       <Response :tableData='item.response_data' :func_list='func_list'></Response>
							    </el-tab-pane>
							</el-tabs>
						</el-tab-pane>
					</el-tabs>
				</div>
			</el-form>
		</div>
	</div>
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen, CopyDocument, Top, Bottom} from '@element-plus/icons-vue'
import ApiList from '../../components/ApiList.vue'
import BodyEdit from '../../components/BodyEdit.vue'
import KeyTable from '../../components/KeyTable.vue'
import Params from '../../components/Params.vue'
import Header from '../../components/Header.vue'
import Extract from '../../components/Extract.vue'
import Check from '../../components/Check.vue'
import Args from '../../components/Args.vue'
import Loop from '../../components/Loop.vue'
import Until from '../../components/Until.vue'
import Json from '../../components/Json.vue'
import Response from '../../components/Response.vue'

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
		Params,
		Extract,
		Header,
		Check,
		Extract,
		Args,
		Loop,
		Until,
		Json,
		Response,
		ApiList
	},
	data() {
		return {
			title: '新增接口',
			methods: [
				'GET',
				'POST',
				'PUT',
				'DELETE',
				'HEAD',
				'OPTIONS',
				'PATCH'
			],
			active_tab: 'api_base_info',
			responseStatusVisible: false,
			active_request_tab: 'json',
			response_tab_active: 0,
			func_list: [],
			moduleProps:{
				emitPath: false,
				value: 'id',
				label: 'name',
			},
			editProps:{
				emitPath: true,
				value: 'id',
				label: 'name',
			},
			header_list: [],
			headerValue: [],
			service_list: [],
			paramsData: [],
			tag_list: [],
			plant_module_list: [],
			response_status: '',
			http_status: [200, 403, 404, 410, 422, 500, 502, 503, 504],
			data: [],
			position: 'top',			
			apiForm:{
				id: '',
				module: '',
				name: '',
				url: '',
				method: '',
				service: '',
				headers: [],
				json: [],
				data: [],
				body: '',
				params: [],
				extract: [],
				check: [],
				response: [{
					'response_status': 200,
					'response_data': [],
				},]
			},
		}
	},
	computed:{
		...mapState(['projectInfo', 'env_id']),
	},
	methods: {
		addResponseTab(index, action){
			if (action==='remove'){
				this.apiForm.response.splice(index, 1)
			}else{
				this.responseStatusVisible = true
				
			}
		},
		saveResponse(){
			this.apiForm.response.push({
				'response_status': this.response_status,
				'response_data': [],
			},)
			this.responseStatusVisible = false
		},
		setHeaderValue(value){
			const index = this.header_list.findIndex(item=>{
				return item.id === value
			})
			if(index != -1){
				this.headerValue = this.header_list[index].value
			}			
		},
		async getPlantModule(){
			const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
			if (response.status === 200){
				this.plant_module_list = response.data.results
			}
		},
		async getServices(){
			const response = await this.$api.getServices({project: this.projectInfo.id})
			if (response.status === 200){
				this.service_list = response.data.results
			}
		},
		async createApi(){
			const response = await this.$api.createApi(this.apiForm)
			if (response.status === 201){
				this.$router.push({name: 'api'})
				ElMessage({message: "保存成功", type: 'success'})
			}
		},
		async updateApi(){
			const response = await this.$api.updateApi(this.apiForm.id, this.apiForm)
			if (response.status === 200){
				this.$router.push({name: 'api'})
				ElMessage({message: "保存成功", type: 'success'})
			}
		},
		saveApi(){
			for (const index in this.apiForm.json){
				delete this.apiForm.json[index].children
				delete this.apiForm.json[index]._X_ROW_CHILD
				delete this.apiForm.json[index]._X_ROW_KEY
			}
			for (const index in this.apiForm.data){
				delete this.apiForm.data[index].children
				delete this.apiForm.data[index]._X_ROW_CHILD
				delete this.apiForm.data[index]._X_ROW_KEY
			}
			for (const index in this.apiForm.headers){
				delete this.apiForm.headers[index].children
				delete this.apiForm.headers[index]._X_ROW_CHILD
				delete this.apiForm.headers[index]._X_ROW_KEY
			}
			for (const index in this.apiForm.params){
				delete this.apiForm.params[index].children
				delete this.apiForm.params[index]._X_ROW_CHILD
				delete this.apiForm.params[index]._X_ROW_KEY
			}
			for (const key in this.apiForm.response) {
				for (const index in this.apiForm.response[key].response_data){
					delete this.apiForm.response[key].response_data[index].children
					delete this.apiForm.response[key].response_data[index]._X_ROW_CHILD
					delete this.apiForm.response[key].response_data[index]._X_ROW_KEY
				}
			}
			if(this.$route.query.id){
				this.updateApi()
			}else{
				this.createApi()
			}
		},
		async getApi(id){
			const response = await this.$api.getApi(id)
			if (response.status === 200){
				this.apiForm = response.data.result
				this.setHeaderValue(this.apiForm.headers)
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
		},
		async getfuncs(){
			const response = await this.$api.getFuncs({project: this.projectInfo.id})
			if (response.status === 200){
				this.func_list = [...response.data.results]
			}
		},
	},
	created() {
		if(this.$route.query.id){
			this.title = '编辑接口'
			this.getApi(this.$route.query.id)
		}
		this.getServices()
		this.getHeaders()
		this.getfuncs()
		this.getPlantModule()
	}
}

</script>

<style scoped>
	/deep/.el-tabs--left .el-tabs__item.is-left{
		justify-content: flex-start;
	}
	/deep/.el-page-header.is-contentful .el-page-header__main {
		margin: 4px
	}
	.demo-tabs > .el-tabs__content {
	  padding: 32px;
	  color: #6b778c;
	  font-size: 32px;
	  font-weight: 600;
	}

	/deep/ .el-page-header__content{
		color: #f59e0b
	}
	.create_case .el-input-group__append{
		background-color: var(--qm-bg-2);
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