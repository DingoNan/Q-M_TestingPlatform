<template>
  <el-scrollbar height="calc(100vh - 70px)">
	<div class='create_test'>
		  <el-form :model="apiForm">
			<div class='action'>
				<el-form-item>
				      <el-button type="primary" @click="()=>{this.$router.push({name: 'test'})}">返回</el-button>
				      <el-button type="primary" @click='createTestCase'>保存</el-button>
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
					<el-form-item label="请求方法">
						<el-select v-model="apiForm.method" clearable>
							<el-option v-for="http_method in methods" :label='http_method' :value="http_method" />
						</el-select>
					</el-form-item>
					<el-form-item label="接口地址">
						<el-input v-model="apiForm.url" placeholder="请以/开头"/>
					</el-form-item>
				</el-form>
				
			</div>
			<el-divider content-position="left">接口请求信息</el-divider>
			<el-radio-group v-model="position">
				<el-radio-button label="top">top</el-radio-button>
				<el-radio-button label="right">right</el-radio-button>
				<el-radio-button label="bottom">bottom</el-radio-button>
				<el-radio-button label="left">left</el-radio-button>
			</el-radio-group>
			<el-tabs :tab-position="position" class="demo-tabs">
				<el-tab-pane label="请求头(Headers)">
					<BodyEdit v-model='testCaseForm.headers'></BodyEdit>
				</el-tab-pane>
				<el-tab-pane label="查询参数(Params)">
					<BodyEdit v-model='testCaseForm.request'></BodyEdit>
				</el-tab-pane>
				<el-tab-pane label="请求体(Body)">
					<el-radio-group v-model="bodyType">
						<el-radio label="json">application/json</el-radio>
						<el-radio label="url-data">x-www-for-urlencoded</el-radio>
						<el-radio label="form-data">form-data</el-radio>
					</el-radio-group>
					<BodyEdit v-if="bodyType==='json' " v-model='testCaseForm.request'></BodyEdit>
				</el-tab-pane>
				<el-tab-pane label="前置脚本">
					 <el-row>
						 <el-col :span="20">
							<BodyEdit lang='python' v-model='testCaseForm.setup_script'></BodyEdit>
						 </el-col>
						 <el-col :span="4">
							 <el-divider>脚本模板</el-divider>
							 <div class='script'>
								 <div style="margin: 20px auto;"><el-button type="primary">预设全局变量</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">预设局部变量</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">调用全局函数</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">执行SQL查询</el-button></div>
							 </div>
						 </el-col>
					  </el-row>
				</el-tab-pane>
				<el-tab-pane label="后置脚本">
					<el-row>
						<el-col :span="20">
							<BodyEdit lang='python' v-model='testCaseForm.teardown_script'></BodyEdit>
						</el-col>
						<el-col :span="4">
							 <el-divider>脚本模板</el-divider>
							 <div class='script'>
								 <div style="margin: 20px auto;"><el-button type="primary">获取响应体</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">json数据提取</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">预设全局变量</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">预设局部变量</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">调用全局函数</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">执行SQL查询</el-button></div>
								 <div style="margin: 20px auto;"><el-button type="primary">断言状态码</el-button></div>
							 </div>
						</el-col>
					</el-row>
				</el-tab-pane>
			</el-tabs>
		  </el-form>
	</div>
  </el-scrollbar>
  
  
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen} from '@element-plus/icons-vue'
import BodyEdit from '../../components/BodyEdit.vue'

export default{
	components: {
		BodyEdit
	},
	data() {
		return {
			methods: [
				'GET',
				'POST',
				'PUT',
				'DELETE',
			],
			bodyType: 'json',
			showEdit: false,
			position: 'top',
			service_list: [],
			apiForm:{
				name: '',
				url: '',
				method: '',
				service: '',
				headers: '',
				json: '',
				data: '',
				params: '',
			},
			testCaseForm: {
				id:'',
				title: '',
				interface: '',
				request: '',
				headers: '',
				setup_script: '',
				teardown_script: '',
				file: '',
			},
			interfaces: [],
			selectInterface: {
				method: '',
				type: '',
				url: '',
				create_time: '',
				update_time: '',
				steps: '',
				count: '',
				name: '',
			},
		}
	},
	computed:{
		...mapState(['projectInfo']),
	},
	methods: {
		async getTestCase(){
				const response = await this.$api.getTestCase(this.$route.query.id)
			    if (response.status === 200){
					this.testCaseForm = {...response.data}
					this.selectInterface = JSON.parse(JSON.stringify(this.testCaseForm.interface))
					this.selectInterface.count = this.selectInterface.steps.length
					this.testCaseForm.interface = this.testCaseForm.interface.id
					this.testCaseForm.headers = JSON.stringify(this.testCaseForm.headers, null, 4)
					this.testCaseForm.request = JSON.stringify(this.testCaseForm.request, null, 4)
			    }
		},
		async createTestCase(){
			if (this.$route.query.id){
				try{
					this.testCaseForm.headers = JSON.stringify(JSON.parse(this.testCaseForm.headers))
					this.testCaseForm.request = JSON.stringify(JSON.parse(this.testCaseForm.request))
				}catch(e){
					ElMessage({
					  type: 'error',
					  message: 'JSON格式错误',
					})
					return
				}
				
				const response = await this.$api.updateTestCase(this.$route.query.id, this.testCaseForm)
				if (response.status === 200){
					ElMessage({
					  type: 'success',
					  message: '更新成功',
					})
					this.$router.push({name: 'test'})
				}
			}else{
				const response = await this.$api.createTestCase(this.testCaseForm)
				if(response.status === 201){
					ElMessage({
					  type: 'success',
					  message: '添加成功',
					})
					this.$router.push({name: 'test'})
				}
			}
			
		},
		parserType(value){
			if(value === '1'){
				return '项目接口'
			}else if(value === '2'){
				return '外部接口'
			}else{
				return ''
			}
		},
		setInterfaceValues(id){
			if(id){
				const index = this.interfaces.results.findIndex(item =>{
					return item.id === id
				})
				this.selectInterface = this.interfaces.results[index]
				this.selectInterface.count = this.selectInterface.steps.length
			}else{
				for(let key in this.selectInterface){
					this.selectInterface[key] = ''
				}
			}
		},
		async getServices(){
				const response = await this.$api.getServices({project: this.projectInfo.id})
			    if (response.status === 200){
					this.service_list = response.data.results
			    }
		}
	},
	created() {
		this.getServices()
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
</style>