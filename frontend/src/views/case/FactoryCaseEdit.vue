<template>
	<el-drawer v-model="lookLogVisible" direction="rtl" :show-close='false' :size="1400">
		<template #header="{ close, titleId, titleClass }">
			  <h4>测试历史</h4>
		      <el-text style="margin-left: 50px;">总执行次数 : {{ caseForm.all_run_times }}</el-text>
		      <el-text style="margin-left: 20px;" type="success">执行成功次数 : {{ caseForm.all_success_times }}</el-text>
		      <el-text style="margin-left: 20px;" type="danger">执行失败数 : {{ caseForm.all_fail_times }}</el-text>
		      <el-text style="margin-right: 20px; margin-left: 20px;" type="danger">执行错误数 : {{ caseForm.all_error_times }}</el-text>
			  <el-select v-model="run_result" placeholder="请选择执行结果" @change='resultChange' clearable style="width: 160px;">
			  	<el-option label='成功' :value="1" />
				<el-option label='失败' :value="2" />
				<el-option label='错误' :value="3" />
			  </el-select>
		</template>
		<div>
			<div style="margin-left: 45px; margin-bottom: 25px">
				<el-pagination
				  v-model:current-page="page_size_params.page"
				  v-model:page-size="page_size_params.size"
				  :page-sizes="[1, 3, 6, 9, 12]"
				  layout="total, sizes, prev, pager, next, jumper"
				  :total="case_logs.count"
				  @size-change="handleSizeChange"
				  @current-change="handleCurrentChange"
				/>
			</div>
			<el-timeline v-for="(case_log, case_index) in case_logs.results" :key='case_log.id'>
			    <el-timeline-item center :timestamp="case_log.create_time" placement="top">
					<el-collapse v-model="caseActive" accordion>
			           <el-collapse-item :name='case_index'>
						   <template #title>
						       <el-text v-if="case_log.result_value === '成功'" type="success">【用例执行人: {{ case_log.create_by_name }}】【用例执行环境: {{ case_log.env_name }}】【用例花费时间: {{case_log.time.toFixed(2)}}秒】【用例执行结果: {{case_log.result_value}}】</el-text>
						       <el-text v-if="case_log.result_value === '失败'" type="danger">【用例执行人: {{ case_log.create_by_name }}】 【用例执行环境: {{ case_log.env_name }}】【用例花费时间: {{case_log.time.toFixed(2)}}秒】【用例执行结果: {{case_log.result_value}}】</el-text>
						       <el-text v-if="case_log.result_value === '错误'" type="danger">【用例执行人: {{ case_log.create_by_name }}】 【用例执行环境: {{ case_log.env_name }}】【用例花费时间: {{case_log.time.toFixed(2)}}秒】【用例执行结果: {{case_log.result_value}}】</el-text>
						   </template>
						   <template v-for="(step_log, step_index) in case_log.logs" :key='step_index'>
							   <el-collapse v-model="stepActive" accordion>
							        <el-collapse-item :name='step_index'>
									   <template #title>
										   <el-text v-if='step_index===0' type="success"> 【env】</el-text>
										   <el-text v-if='step_index===1' type="success"> 【case】</el-text>
										   <el-text v-if='step_index > 1' type="success"> 【step{{ step_index - 1 }}】</el-text>
									   </template>
									   <template v-for="(log_info, log_index) in step_log" :key='log_index'>
										   <el-collapse v-model="logActive" accordion>
											  <el-collapse-item :title="log_info.title" :name='log_info.title'>
												  <template #title>
													   <el-text v-if="log_info.title.includes('【INFO】')" type="success">{{ log_info.title }}</el-text>
													   <el-text v-if="log_info.title.includes('【ERROR】')" type="danger">{{ log_info.title }}</el-text>
												  </template>
												  <BodyEdit v-model='case_logs.results[case_index].logs[step_index][log_index].value'></BodyEdit>
											  </el-collapse-item>
										   </el-collapse>
									   </template>
									</el-collapse-item>
								</el-collapse>
							</template>
			           </el-collapse-item>
					</el-collapse>
			    </el-timeline-item>
			</el-timeline>
		</div>
	</el-drawer>
	<el-dialog v-model="loadApiVisible" title="从接口同步请求数据" width="550">
	    <el-checkbox-group v-model="loadTypeList">
	        <el-checkbox label="Headers" />
	        <el-checkbox label="Params" />
	        <el-checkbox label="Json" />
	        <el-checkbox label="Data"/>
			<el-select v-model="loadResponseIndex" placeholder="Response" style="width: 130px; margin-left: 25px; margin-bottom: 15px;" size="small" clearable>
				<el-option v-for="(item, index) in this.caseForm.step[this.step_index].api_all.response" :label="`Response[${item.response_status}]`" :value="index" />
			</el-select>
	      </el-checkbox-group>
	    <template #footer>
	      <div class="dialog-footer">
	        <el-button @click="loadApiVisible = false">取消</el-button>
	        <el-button @click="loadApi()">确定</el-button>
	      </div>
	    </template>
	</el-dialog>
	<el-dialog v-model="chooseApiVisible" title="请选择接口" width='1300' :show-close='show_close'>
	    <ApiList :isCanChoose='true' v-model:chooseApiVisible='chooseApiVisible' @setApiData='setApiData'></ApiList>
	</el-dialog>
	<el-dialog v-model="chooseStepVisible" title="请选择步骤" width='1500' :show-close='show_close'>
	    <StepList :isCanChoose='true' v-model:chooseStepVisible='chooseStepVisible' @setStepData='setStepData'></StepList>
	</el-dialog>
	<div>
		<el-page-header @back="()=>{this.$router.go(-1)}" style='min-width: 400px'>
			  <template #content>
			    <div>
				  <span>{{ caseForm.name }}</span>
			    </div>
			  </template>
			  <template #extra>
			    <div class="flex items-center">
				  <el-button v-if="$route.name === 'FactoryCaseEdit'" type="primary" @click="look_logs">造数历史</el-button>
				  <el-button v-if="$route.name === 'FactoryCaseEdit'" type="primary" @click="run" style='margin-right: 10px;'>执行造数</el-button>
			    </div>
			  </template>
			  <el-form :model="caseForm" style='margin:0'>
			  	<el-tabs v-model="active_tab" type="card" style='background-color: white, margin: 0'>
					<el-tab-pane label="用例基础信息" name="case_info" lazy='true'>
			  			   <el-form :inline="false">
			  			   	<el-row :gutter="20">
			  			   	    <el-col :span="12">
			  			   			<el-form-item label="用例名称:">
			  			   				<el-input v-model="caseForm.name"></el-input>
			  			   			</el-form-item>
			  			   		</el-col>
			  			   	    <el-col :span="12">
			  			   			<el-form-item label="所属模块:">
			  			   				<el-cascader placeholder='请选择或输入模块名称' collapse-tags v-model='caseForm.module' :options="plant_module_list" :props="moduleEditProps" clearable  style="width: 100%;" filterable/>
			  			   			</el-form-item>
			  			   		</el-col>
			  			   	</el-row>
			  			   	<el-row :gutter="20">
			  			   		<el-col :span="8">
			  			   			<el-form-item label="用例类型:">
			  			   				<el-select v-model="caseForm.type" placeholder="请选择用例类型" clearable>
			  			   					<el-option v-for="case_type in caseType" :label='case_type.label' :value="case_type.value" />
			  			   				</el-select>
			  			   			</el-form-item>
			  			   		</el-col>
			  			   		<el-col :span="8">
			  			   			<el-form-item label="用例标签:">
			  			   				<el-select v-model="caseForm.tag" placeholder="请选择用例标签" clearable multiple>
			  			   					<el-option v-for="tag in tag_list" :label='tag.name' :value="tag.id" />
			  			   				</el-select>
			  			   			</el-form-item>
			  			   		</el-col>
			  			   		<el-col :span="8">
			  			   			<el-form-item label="是否可作为造数用例:">
			  			   				<el-tooltip placement="right" effect="light">
			  			   				    <template #content>
												建议正常场景的用例可开启开关用来测试数据构造
											</template>
			  			   				    <el-icon color='green'><InfoFilled /></el-icon>
			  			   				</el-tooltip>
			  			   				<el-switch v-model="caseForm.is_data_factory" />
			  			   			</el-form-item>
			  			   		</el-col>
			  			   		<el-col :span="8">
			  			   		</el-col>
			  			   	</el-row>
			  			   </el-form>
			  		   </el-tab-pane>
				    <el-tab-pane label="用例局部变量" name="local_params_info" lazy='true'>
					   <CaseParams :tableData='caseForm.params' :isApi="false" :func_list='func_list'></CaseParams>
				   </el-tab-pane>
			  	    <el-tab-pane label="用例测试步骤" name="step_info" lazy='true'>
						<div style="margin-bottom: 20px">
							<el-button type="primary" @click="addStepTab" style='margin-left:20px'>新增</el-button>
							<el-button type="primary" @click="addStep(step_active_tab)" style='margin-left:20px'>插入</el-button>
							<el-button type="primary" @click="topStep(step_active_tab)" style='margin-left:20px'>上移</el-button>
							<el-button type="primary" @click="bomStep(step_active_tab)" style='margin-left:20px'>下移</el-button>
							<el-button type="primary" @click="copyStep(step_active_tab)" style='margin-left:20px'>复制</el-button>
							<el-button type="primary" @click="delStep(step_active_tab)" style='margin-left:20px'>删除</el-button>
						</div>
						<el-tabs tab-position="left" class="demo-tabs" style='height:calc(100vh - 200px)' v-model="step_active_tab">
							<el-tab-pane v-for="step, index in caseForm.step" :key="index" :label="step.desc" :name="index" lazy='true'>
								  <el-tabs v-model='single_step_tab'>
									<el-tab-pane label="步骤局部变量" name="step_params_info" lazy='true'>
										<CaseParams :tableData='step.step_params' :isApi="false" :func_list='func_list'></CaseParams>
									</el-tab-pane>
								  	<el-tab-pane label="步骤基础信息" name='step_base_info' lazy='true'>
								  		<el-form :inline="false">
								  			<el-row :gutter="20">
								  			    <el-col :span="10">
								  					<el-form-item label="步骤名称:">
								  						<el-input v-model="step.desc"></el-input>
								  					</el-form-item>
								  				</el-col>
								  			    <el-col :span="6">
								  					<el-form-item label="步骤关键字:">
														<el-select v-model="step.type" placeholder="请选择步骤类型" @change='actionChange(index, step.type)' clearable>
															<el-option v-for="(value, type, index) in StepType" :label='type' :value="value" />
														</el-select>
								  					</el-form-item>
								  				</el-col>
												<el-col :span="3">
													<el-form-item label="步骤是否执行:">
														<el-switch v-model="step.is_run" />
													</el-form-item>
												</el-col>
												<el-col :span="5">
													<el-form-item label="步骤执行失败重试次数:">
														<el-input-number v-model="step.fail_is_rerun" :precision="0" :step="1" :min='0' :max="10" />
													</el-form-item>
												</el-col>
								  			</el-row>
											<el-row :gutter="20" v-if='step.type === StepType.Request || step.com_step_type === StepType.Request'>
												<el-col :span="8">
													<el-form-item label="所属服务:">
														<el-select v-model="step.api_service" disabled>
															<el-option v-for="service in service_list" :label='service.name' :value="service.id" />
														</el-select>
														<!-- <el-input v-model="step.api_service" disabled></el-input> -->
													</el-form-item>
												</el-col>
												<el-col :span="14">
													<el-input v-model="step.api_uri" disabled>
													      <template #prepend>
													        <el-select v-model="step.api_method" disabled style="width: 100px;">
													        	<el-option v-for="http_method in methods" :label='http_method' :value="http_method" />
													        </el-select>
													      </template>
													</el-input>
												</el-col>
												<el-col :span="2">
													<el-button type="primary" @click='setApiVisible(step.keyword, index)'>从接口同步</el-button>
												</el-col>
											</el-row>
								  		</el-form>
										<el-tabs class="demo-tabs" v-model='step.step_active_tab'>
											<!-- <el-tab-pane name='args'
											 v-if='step.type === StepType.PlatformSystemFunction 
											 || step.type === StepType.Selenium
											 || step.type ===StepType.UserCustomizeFunction'>
												<template #label>
													<span class="custom-tabs-label">
													  <el-tooltip effect="light">
														  <template #content>
															  <el-row v-for='params_txt in step.function_desc'>
															  	 <el-text type='primary'>{{ params_txt }}</el-text>
															  </el-row>
														  </template>
														  <span>{{ step.key[step.key.length - 1] }}</span>
														  <el-icon style="top: 2.3px; left: 2px"><Warning /></el-icon>
													  </el-tooltip>
													</span>
												</template>
												<Args :keyData='step.params' :step_type='step.type' :function_name='step.key[step.key.length - 1]'></Args>
											</el-tab-pane> -->
											<el-tab-pane  lazy='true' v-if='step.type === StepType.UserCustomizeScript || step.com_step_type === StepType.UserCustomizeScript' label="Python脚本" name='python_script' >
												<BodyEdit v-model='step.script' lang='python' :is_function='false' height="800px"></BodyEdit>
											</el-tab-pane>
											<el-tab-pane v-if='step.type === StepType.Request || step.com_step_type === StepType.Request' label="Headers" name='headers' lazy='true'>
												<Header :tableData='step.api_headers' :isApi="false" :func_list='func_list'></Header>
											</el-tab-pane>
											<el-tab-pane v-if='step.type === StepType.Request || step.com_step_type === StepType.Request' label="Params" name='params' lazy='true'>
												<Params :tableData='step.api_params' :isApi="false" :func_list='func_list'></Params>
											</el-tab-pane>
											<el-tab-pane label="Json" name='json' v-if="step.type === StepType.Request || step.com_step_type === StepType.Request" lazy='true'>
												<el-form-item label="JSON 根类型:" style="margin-left: 15px;">
													<el-select v-model="step.api_json_type" style='width: 200px;'>
													   <el-option v-for="value in josn_root_type" :label="value" :value="value" ></el-option>
													</el-select>
												</el-form-item>
												<Json :tableData='step.api_json' :isApi="false" :func_list='func_list'></Json>
											</el-tab-pane>
											<el-tab-pane label="Data" name='data' v-if="step.type === StepType.Request || step.com_step_type === StepType.Request" lazy='true'>
												<el-form-item label="JSON 根类型:" style="margin-left: 15px;">
													<el-select v-model="step.api_data_type" style='width: 200px;'>
													   <el-option v-for="value in josn_root_type" :label="value" :value="value" ></el-option>
													</el-select>
												</el-form-item>
												<Json :tableData='step.api_data' :isApi="false" :func_list='func_list'></Json>
											</el-tab-pane>
											<el-tab-pane label="Response" name='response' v-if='step.type === StepType.Request || step.com_step_type === StepType.Request' lazy='true'>
												<el-form-item label="JSON 根类型:" style="margin-left: 15px;">
													<el-select v-model="step.api_response_type" style='width: 200px;'>
													   <el-option v-for="value in josn_root_type" :label="value" :value="value" ></el-option>
													</el-select>
												</el-form-item>
												<Response :check_method='method' :tableData='step.api_response' :isApi="false" :func_list='func_list'></Response>
											</el-tab-pane>
										</el-tabs>
								  	</el-tab-pane>
								  	<el-tab-pane label="步骤执行条件设置" name='Condition' lazy='true'>
								  		<el-tabs :tab-position="position" class="demo-tabs" v-model='condition_tab'>
								  			<el-tab-pane name='If' label="执行条件(If)" lazy='true'>
								  				<IfRun :tableData='step.run_params' :func_list='func_list' :method='method'></IfRun>
								  			</el-tab-pane>
								  			<el-tab-pane name='For' label="循环执行(For)"  lazy='true'>
								  				<Loop :tableData='step.loop' :func_list='func_list'></Loop>
								  			</el-tab-pane>
								  			<el-tab-pane name='While' label="一直执行(While)"  lazy='true'>
								  				<Until :tableData='step.until' :func_list='func_list' :method='method' ></Until>
								  			</el-tab-pane>
								  		</el-tabs>
								  	</el-tab-pane>
									<el-tab-pane name='check' label="步骤断言设置" lazy='true'>
										<Check :tableData='step.check' :func_list='func_list' :method='method'></Check>
									</el-tab-pane>
								  </el-tabs>
								  <template #label>
									  <span style='text-align: left'>
										<span>
											<span style='margin-right: 10px'>{{ index + 1}}.</span>
											<el-tooltip v-if='step.desc.length <= 5' effect="dark" :content="step.desc" placement="top-start">
												<span>{{ step.desc }}</span>
											</el-tooltip>
											<el-tooltip v-if='step.desc.length > 5' effect="dark" :content="step.desc" placement="top-start">
												<span>{{ step.desc.slice(0, 5) }}...</span>
											</el-tooltip>
										</span>
										<el-dropdown @command="stepCommand">
											<el-icon style='margin:3px 3px'><arrow-down /></el-icon>
											<template #dropdown>
											  <el-dropdown-menu>													
												<el-dropdown-item :command="{type: 1, index: index}">插入</el-dropdown-item>
												<el-dropdown-item :command="{type: 2, index: index}">复制</el-dropdown-item>
												<el-dropdown-item :command="{type: 3, index: index}">上移</el-dropdown-item>
												<el-dropdown-item :command="{type: 4, index: index}">下移</el-dropdown-item>
												<el-dropdown-item :command="{type: 5, index: index}">删除</el-dropdown-item>
											  </el-dropdown-menu>
											</template>
										  </el-dropdown>
									  </span>
								  </template>
							</el-tab-pane>
						</el-tabs>
					</el-tab-pane>
			  	</el-tabs>
			  </el-form>
			</el-page-header>
	</div>
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage } from 'element-plus'
import ApiList from '../../components/ApiList.vue'
import StepList from '../../components/StepList.vue'
import BodyEdit from '../../components/BodyEdit.vue'
import Header from '../../components/Header.vue'
import Params from '../../components/Params.vue'
import Json from '../../components/Json.vue'
import CaseParams from '../../components/CaseParams.vue'
import Check from '../../components/Check.vue'
import Args from '../../components/Args.vue'
import IfRun from '../../components/IfRun.vue'
import Loop from '../../components/Loop.vue'
import Until from '../../components/Until.vue'
import Response from '../../components/Response.vue'
export default{
	components: {
		BodyEdit,
		Header,
		Params,
		Json,
		CaseParams,
		Check,
		Args,
		IfRun,
		Loop,
		Until,
		Response,
		ApiList,
		StepList,
	},
	data() {
		return {
			methods: [
				'GET',
				'POST',
				'PUT',
				'DELETE',
			],
			apiData: '',
			run_result: '',
			title: '新增测试用例',
			loadResponseIndex: '',
			show_close: false,
			loadTypeList: [],
			loadApiVisible: false,
			chooseApiVisible: false,
			chooseStepVisible: false,
			loadApiId: '',
			logActive: '',
			stepActive: '',
			caseActive: '',
			josn_root_type: ['object', 'array'],
			StepType:{
				UserCustomizeFunction: 1,     
				Request: 5,                  
				Selenium: 2,                  
				ComStep:3,                 
				UserCustomizeScript: 4
			},
			page_size_params: {
				page: 1,
				size: 1,
			},
			active_tab: 'step_info',
			step_active_tab: 0, //步骤Tab默认的Tab名称
			condition_tab: 'If',
			single_step_tab: 'step_base_info',
			case_logs: [],
			lookLogVisible: false,
			caseType:[
				{
					value: 1,
					label: 'API',
				},
				{
					value: 2,
					label: 'WEB UI',
				},
				{
					value: 3,
					label: 'ANDROID UI',
				},
				{
					value: 4,
					label: 'IOS UI',
				},
			],
			editProps:{
				emitPath: true,
				value: 'id',
				label: 'name',
			},
			moduleEditProps:{
				emitPath: false,
				value: 'id',
				label: 'name',
			},
			method: [],
			service_list: [],
			paramsData: [],
			tag_list: [],
			func_list: [],
			plant_module_list: [],
			data: [],
			showEdit: false,
			position: 'top',
			actions: [],
			caseRunForm:{
				env_id: '',
				case_id: '',
				is_data_factory: true
			},
			// 步骤参数
			step: {
				id: 0,
				step_index: '',
				step_active_tab: 'json',
				project: '',//所属项目
				desc: '您好呀！请输入测试步骤的描述', //步骤名称
				type: '', //步骤类型
				com_step_type: '',//步骤类型
				keyword: '',//步骤关键字
				is_run: true, //步骤是否执行
				fail_is_rerun: 0, //步骤失败是否重复执行
				api_all: '',//返回的api总数据
				api_service: '', //api所属服务
				api_method: '', //api请求方法
				api_uri: '',//api请求网址
				api_headers: [], //api 请求头
				api_json: [], //api 请求体
				api_json_tree: [],
				api_json_type: 'object',
				api_data: [],//api 请求体 form-data
				api_data_tree: [],
				api_data_type: 'object',
				api_response: [], //api返回体
				api_response_tree: [],
				api_response_type: 'object',
				api_params: [],//api查询参数
				step_after: false,
				extract: [],//数据提取参数
				check: [],//断言参数
				run_params: [],//是否执行条件参数
				step_params: [],//步骤变量参数
				loop: [],//循环执行参数
				until: [],
				func_params: [],//函数入参
				script: '',
				// function_name: '', //函数名称
				// function_desc: '', //函数说明文档
			},
			caseForm:{
				project: '',
				id: '',
				module: '',
				name: '',
				type: '',
				tag: '',
				step: [],
				params: [],//用例局部变量
				is_data_factory: false
			},
		}
	},
	computed:{
		...mapState(['projectInfo', 'env_id']),
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
	methods: {
		copyFromApi(){
			console.log(112233)
		},
		async getCheck(){
			const response = await this.$api.getCheck()
			if (response.status === 200){
				this.method = response.data.results
			}
		},
		async getServices(){
			const response = await this.$api.getServices({project: this.projectInfo.id})
			if (response.status === 200){
				this.service_list = response.data.results
			}
		},
		setApiData(apiData){
			this.apiData = apiData
			this.caseForm.step[this.step_index].keyword = apiData.id
			this.caseForm.step[this.step_index].api_all = JSON.parse(JSON.stringify(apiData))
			this.caseForm.step[this.step_index].api_method = apiData.method
			this.caseForm.step[this.step_index].api_uri = apiData.url
			this.caseForm.step[this.step_index].api_service = apiData.service
			this.loadApiVisible = true
		},
		setStepData(apiData){
			this.loadStepVisible = true
			this.caseForm.step[this.step_index] = {...apiData}
			this.caseForm.step[this.step_index].com_step_type = apiData.type
			this.caseForm.step[this.step_index].type = this.StepType.ComStep
			console.log(this.caseForm.step[this.step_index], '2223')
			
		},
		loadApi(){
			if (this.loadTypeList.includes('Headers')){
				this.caseForm.step[this.step_index].api_headers = this.caseForm.step[this.step_index].api_all.headers
			}
			if (this.loadTypeList.includes('Params')){
				this.caseForm.step[this.step_index].api_params = this.caseForm.step[this.step_index].api_all.params
			}
			if (this.loadTypeList.includes('Json')){
				this.caseForm.step[this.step_index].api_json = this.caseForm.step[this.step_index].api_all.json
			}
			if (this.loadTypeList.includes('Data')){
				this.caseForm.step[this.step_index].api_data = this.caseForm.step[this.step_index].api_all.data
			}
			if (this.loadResponseIndex !== ''){
				this.caseForm.step[this.step_index].api_response = this.caseForm.step[this.step_index].api_all.response[this.loadResponseIndex].response_data
			}
			this.loadApiVisible = false
		},
		setApiVisible(api_id, index){
			this.step_index = index
			this.getApi(api_id, index)
		},
		async getApi(id, index){
			const response = await this.$api.getApi(id)
			if (response.status === 200){
				console.log(response.data.result, 'result')
				this.setApiData(response.data.result)
			}
		},
		//关键字步骤值改变时回调函数
		actionChange(index, step_type){
			if (step_type === this.StepType.Request){
				this.chooseApiVisible = true
				this.caseForm.step[index].step_active_tab = 'json'
				this.caseForm.step[index].com_step_type = this.StepType.Request
				this.step_index = index
				// this.getApi(step_key, index)
			}else if(step_type === this.StepType.ComStep){
				this.chooseStepVisible = true
				this.caseForm.step[index].step_active_tab = 'python_script'
				this.caseForm.step[index].com_step_type = this.StepType.UserCustomizeScript
				this.step_index = index
			}else if(step_type === this.StepType.UserCustomizeScript){
				this.caseForm.step[index].step_active_tab = 'python_script'
				this.caseForm.step[index].com_step_type = this.StepType.UserCustomizeScript
				this.step_index = index
			}
			// if (!this.keyData[index].step_after){
			// 	this.keyData[index].step_after = true
			// }
			// this.edit_row_data = JSON.parse(JSON.stringify(this.keyData[index]))
			// this.edit_row_data.function_name = step_key
		},
		async getSystemFunctionDoc(index, step_key){
			const response = await this.$api.getSystemFunctionDoc({step_key: step_key})
			if (response.status === 200){
				this.caseForm.step[index].function_desc = response.data.result.doc
				this.caseForm.step[index].params = response.data.result.params
			}
		},
		//增加一个步骤
		addStepTab(){
			this.caseForm.step.push(JSON.parse(JSON.stringify(this.step)))
			this.step_active_tab = this.caseForm.step.length - 1
		},
		addStep(index){
			this.caseForm.step.splice(index + 1, 0, JSON.parse(JSON.stringify(this.step_params)))
			this.step_active_tab = index + 1
		},
		copyStep(index){
			const data = JSON.parse(JSON.stringify(this.caseForm.step[index]))
			data.id = 0
			this.caseForm.step.splice(index + 1, 0, data)
			this.step_active_tab = index + 1
		},
		topStep(index){
			if(index != 0){
				const row_data = this.caseForm.step[index - 1]
				this.caseForm.step[index - 1] = this.caseForm.step[index]
				this.caseForm.step[index] = row_data
				this.step_active_tab = index - 1
				
			}
		},
		botStep(index){
			if(index != this.caseForm.step.length - 1){
				const row_data = this.caseForm.step[index + 1]
				this.caseForm.step[index + 1] = this.caseForm.step[index]
				this.caseForm.step[index] = row_data
				this.step_active_tab = index + 1
			}
		},
		delStep(index){
			this.caseForm.step.splice(index, 1)
			this.step_active_tab = index - 1
		},
		stepCommand(command){
			if(command.type === 1){
				this.addStep(command.index)
			}else if(command.type ===2){
				this.copyStep(command.index)
			}else if(command.type === 3){
				this.topStep(command.index)
			}else if (command.type === 4){
				this.botStep(command.index)
			}else{
				this.delStep(command.index)
			}
		},
		delExtraInfo(data){
		  console.log(data, 'data')
		  for (let index = 0; index < data.length; index++) {
			delete data[index]._X_ROW_CHILD
			delete data[index]._X_ROW_KEY
			if (data[index].hasOwnProperty('children')) {
			  this.delExtraInfo(data[index].children);
			}else{
			  delete data[index].children
			}
		  }
		},
		look_logs(){
			this.lookLogVisible = true
			this.caseActive = ''
			this.stepActive = ''
			this.logActive = ''
			this.getCaseLogs()
		},
		async getCaseLogs(){
			const query_data  = {case: this.$route.query.id, is_data_factory: true, result: this.run_result}
			const response = await this.$api.getCaseLogs(Object.assign(query_data, this.page_size_params))
			if (response.status === 200){
				this.case_logs = {...response.data}
			}
		},
		run(){
			if(!this.env_id){
				ElMessage({message: '请选择执行环境', type: 'error'})
			}else{
				this.caseRun()
			}
		},
		saveCase(){
			console.log(this.caseForm.step, 'step')
			for (const key in this.caseForm.step) {
				this.caseForm.step[key].project = this.projectInfo.id
				this.caseForm.step[key].api_json_tree = JSON.parse(JSON.stringify(this.caseForm.step[key].api_json))
				this.caseForm.step[key].api_data_tree = JSON.parse(JSON.stringify(this.caseForm.step[key].api_data))
				this.caseForm.step[key].api_response_tree = JSON.parse(JSON.stringify(this.caseForm.step[key].api_response))
				for (let index = this.caseForm.step[key].api_json.length - 1; index >= 0; index--) {
				  delete this.caseForm.step[key].api_json[index].children
				  delete this.caseForm.step[key].api_json[index]._X_ROW_CHILD
				  delete this.caseForm.step[key].api_json[index]._X_ROW_KEY
				  if(this.caseForm.step[key].api_json_tree[index].parentId !== null){
					  this.caseForm.step[key].api_json_tree.splice(index, 1)
				  }
				}
				this.delExtraInfo(this.caseForm.step[key].api_json_tree)
				for (let index = this.caseForm.step[key].api_data.length - 1; index >= 0; index--) {
				  delete this.caseForm.step[key].api_data[index].children
				  delete this.caseForm.step[key].api_data[index]._X_ROW_CHILD
				  delete this.caseForm.step[key].api_data[index]._X_ROW_KEY
				  if(this.caseForm.step[key].api_data_tree[index].parentId !== null){
					  this.caseForm.step[key].api_data_tree.splice(index, 1)
				  }
				}
				this.delExtraInfo(this.caseForm.step[key].api_data_tree)
				for (const index in this.caseForm.step[key].api_headers){
					delete this.caseForm.step[key].api_headers[index].children
					delete this.caseForm.step[key].api_headers[index]._X_ROW_CHILD
					delete this.caseForm.step[key].api_headers[index]._X_ROW_KEY
				}
				for (const index in this.caseForm.step[key].api_params){
					delete this.caseForm.step[key].api_params[index].children
					delete this.caseForm.step[key].api_params[index]._X_ROW_CHILD
					delete this.caseForm.step[key].api_params[index]._X_ROW_KEY
				}
				for (let index = this.caseForm.step[key].api_response.length - 1; index >= 0; index--) {
				  delete this.caseForm.step[key].api_response[index].children
				  delete this.caseForm.step[key].api_response[index]._X_ROW_CHILD
				  delete this.caseForm.step[key].api_response[index]._X_ROW_KEY
				  if(this.caseForm.step[key].api_response_tree[index].parentId !== null){
					  this.caseForm.step[key].api_response_tree.splice(index, 1)
				  }
				}
				this.delExtraInfo(this.caseForm.step[key].api_response_tree)
			}
			if(this.$route.query.id && this.$route.name === 'caseEdit'){
				this.updateCase()
			}else{
				this.createCase()
			}
		},
		async getPlantModule(){
			const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
			if (response.status === 200){
				this.plant_module_list = response.data.results
			}
		},
		resultChange(){
			this.getCaseLogs()
		},
		handleCurrentChange(){
			this.getCaseLogs()
		},
		handleSizeChange(){
			this.getCaseLogs()
		},
		async createCase(){
			this.caseForm.project = this.projectInfo.id
			const response = await this.$api.createCase(this.caseForm)
			if (response.status === 201){
				this.$router.push({name: 'case'})
				ElMessage({message: "保存成功", type: 'success'})
			}
		},
		async caseRun(){
			this.caseRunForm.env_id = this.env_id
			this.caseRunForm.case_id = this.$route.query.id
			const response = await this.$api.caseRun(this.caseRunForm)
			if (response.status === 200){
				ElMessage({message: "【" + this.caseForm.name + '】' + '用例执行中，请稍后在测试历史中查看执行结果', type: 'success'})
			}
		},
		async updateCase(){
			const response = await this.$api.updateCase(this.caseForm.id, this.caseForm)
			if (response.status === 200){
				ElMessage({message: "保存成功", type: 'success'})
			}
		},
		async getCase(id){
			const response = await this.$api.getCaseDetail(id)
			if (response.status === 200){
				this.caseForm = response.data.result
			}
		},
		async getActions(){
			const response = await this.$api.getActions({project: this.projectInfo.id, isCase: true})
			if (response.status === 200){
				this.actions = response.data.results
			}
		},
		async getTags(){
			const response = await this.$api.getTags({project: this.projectInfo.id})
			if (response.status === 200){
				this.tag_list = response.data.results
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
		this.getPlantModule()
		this.getServices()
		this.getTags()
		// this.getActions()
		this.getfuncs()
		this.getCheck()
		if(this.$route.query.id){
			this.getCase(this.$route.query.id)
		}else{
			this.addStepTab()
		}
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
		color: #409eff
	}
	.create_case .el-input-group__append{
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