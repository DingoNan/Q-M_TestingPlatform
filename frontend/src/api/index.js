import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router/index.js'

// API 地址：优先使用构建期注入的 VUE_APP_API_BASE；否则按当前访问的 hostname 自动拼接后端 8000 端口，
// 这样本地开发 (127.0.0.1:8080 -> 127.0.0.1:8000) 与 Docker 部署 (任意 host:8080 -> host:8000) 都能直接工作。
export const base_url = process.env.VUE_APP_API_BASE || `${window.location.protocol}//${window.location.hostname}:8000`
const http_request = axios.create({
	baseURL: base_url,
	validateStatus: function(status){
		return true
	}
})

http_request.interceptors.request.use(function(config){
	if (config.url != '/user/login/' && config.url != '/user/navigation'){
		config.headers['Authorization'] = 'Bearer ' + JSON.parse(window.localStorage.getItem('token'))
	}
	return config
})

http_request.interceptors.response.use(function(res){
	if (res.status === 401){
		router.push({name: 'login'})
	}
	if (res.status === 403){
		router.push({name: 'noPermission'})
	}
	if(res.status === 400){
		for(let error_obj in res.data.result){
			ElMessage({
			  type: 'error',
			  duration: 5000,
			  showClose: true, 
			  message: res.data.result[error_obj][0],
			})
		}
	}else if(res.status === 500 && res.config.url !='/mock_api_run/'){
		ElMessage({ message: "系统内部异常", type: 'error' })
	}
	return res
})


export default {
	// 导航分组接口
	getGroups(params){
		return http_request.get('/user/group/', {params: params})
	},
	getGroup(id){
		return http_request.get(`/user/group/${id}`)
	},
	updateGroup(id, params){
		return http_request.put(`/user/group/${id}/`, params)
	},
	createGroup(params){
		return http_request.post('/user/group/', params)
	},
	deleteGroup(id){
		return http_request.delete(`/user/group/${id}/`)
	},
	// 导航接口
	getNavigations(params){
		return http_request.get('/user/navigation/', {params: params})
	},
	getNavigation(id){
		return http_request.get(`/user/navigation/${id}`)
	},
	updateNavigation(id, params){
		return http_request.put(`/user/navigation/${id}/`, params)
	},
	createNavigation(params){
		return http_request.post('/user/navigation/', params)
	},
	deleteNavigation(id){
		return http_request.delete(`/user/navigation/${id}/`)
	},
	// 环境管理接口
	getEnvs(params){
		return http_request.get('/env/env/', {params: params})
	},
	getEnv(id){
		return http_request.get(`/env/env/${id}`)
	},
	updateEnv(id, params){
		return http_request.put(`/env/env/${id}/`, params)
	},
	createEnv(params){
		return http_request.post('/env/env/', params)
	},
	deleteEnv(id){
		return http_request.delete(`/env/env/${id}/`)
	},
	// selenium执行机管理接口
	getWebExecutors(params){
		return http_request.get('/env/web_executor/', {params: params})
	},
	getWebExecutor(id){
		return http_request.get(`/env/web_executor/${id}`)
	},
	updateWebExecutor(id, params){
		return http_request.put(`/env/web_executor/${id}/`, params)
	},
	createWebExecutor(params){
		return http_request.post('/env/web_executor/', params)
	},
	deleteWebExecutor(id){
		return http_request.delete(`/env/web_executor/${id}/`)
	},
	// appium执行机管理接口
	getAppExecutors(params){
		return http_request.get('/env/app_executor/', {params: params})
	},
	getAppExecutor(id){
		return http_request.get(`/env/app_executor/${id}`)
	},
	updateAppExecutor(id, params){
		return http_request.put(`/env/app_executor/${id}/`, params)
	},
	createAppExecutor(params){
		return http_request.post('/env/app_executor/', params)
	},
	deleteAppExecutor(id){
		return http_request.delete(`/env/app_executor/${id}/`)
	},
	// 变量管理接口
	getPars(params){
		return http_request.get('/env/params/', {params: params})
	},
	getPar(id){
		return http_request.get(`/env/params/${id}`)
	},
	updatePar(id, params){
		return http_request.put(`/env/params/${id}/`, params)
	},
	createPar(params){
		return http_request.post('/env/params/', params)
	},
	deletePar(id){
		return http_request.delete(`/env/params/${id}/`)
	},
	// 全局变量管理接口
	getGlobalPars(params){
		return http_request.get('/env/global/', {params: params})
	},
	getGlobalPar(id){
		return http_request.get(`/env/global/${id}`)
	},
	updateGlobalPar(id, params){
		return http_request.put(`/env/global/${id}/`, params)
	},
	createGlobalPar(params){
		return http_request.post('/env/global/', params)
	},
	deleteGlobalPar(id){
		return http_request.delete(`/env/global/${id}/`)
	},
	// 服务管理接口
	getServices(params){
		return http_request.get('/env/service/', {params: params})
	},
	getService(id){
		return http_request.get(`/env/service/${id}`)
	},
	updateService(id, params){
		return http_request.put(`/env/service/${id}/`, params)
	},
	createService(params){
		return http_request.post('/env/service/', params)
	},
	deleteService(id){
		return http_request.delete(`/env/service/${id}/`)
	},
	// Db管理接口
	getDbs(params){
		return http_request.get('/env/db/', {params: params})
	},
	getDb(id){
		return http_request.get(`/env/db/${id}`)
	},
	updateDb(id, params){
		return http_request.put(`/env/db/${id}/`, params)
	},
	createDb(params){
		return http_request.post('/env/db/', params)
	},
	deleteDb(id){
		return http_request.delete(`/env/db/${id}/`)
	},
	// 环境服务管理接口
	getRequestHost(params){
		return http_request.get('/env/get_request_host/', {params: params})
	},
	getEnvServices(params){
		return http_request.get('/env/env_service/', {params: params})
	},
	getEnvService(id){
		return http_request.get(`/env/env_service/${id}`)
	},
	updateEnvService(id, params){
		return http_request.put(`/env/env_service/${id}/`, params)
	},
	createEnvService(params){
		return http_request.post('/env/env_service/', params)
	},
	deleteEnvService(id){
		return http_request.delete(`/env/env_service/${id}/`)
	},
	// DB服务管理接口
	getEnvDbs(params){
		return http_request.get('/env/env_db/', {params: params})
	},
	getEnvDb(id){
		return http_request.get(`/env/env_db/${id}`)
	},
	updateEnvDb(id, params){
		return http_request.put(`/env/env_db/${id}/`, params)
	},
	createEnvDb(params){
		return http_request.post('/env/env_db/', params)
	},
	deleteEnvDb(id){
		return http_request.delete(`/env/env_db/${id}/`)
	},
	// 平台管理接口
	getPlants(params){
		return http_request.get('/env/plant/', {params: params})
	},
	getPlant(id){
		return http_request.get(`/env/plant/${id}`)
	},
	updatePlant(id, params){
		return http_request.put(`/env/plant/${id}/`, params)
	},
	createPlant(params){
		return http_request.post('/env/plant/', params)
	},
	deletePlant(id){
		return http_request.delete(`/env/plant/${id}/`)
	},
	// 元素管理接口
	getElements(params){
		return http_request.get('/element/', {params: params})
	},
	getElement(id){
		return http_request.get(`/element/${id}`)
	},
	updateElement(id, params){
		return http_request.put(`/element/${id}/`, params)
	},
	createElement(params){
		return http_request.post('/element/', params)
	},
	deleteElement(id){
		return http_request.delete(`/element/${id}/`)
	},
	batchUpdateElements(params){
		return http_request.post('/element/batch_update/', params)
	},
	batchDeleteElements(params){
		return http_request.post('/element/batch_delete/', params)
	},
	// 环境平台理接口
	getEnvPlants(params){
		return http_request.get('/env/env_plant/', {params: params})
	},
	getEnvPlant(id){
		return http_request.get(`/env/env_plant/${id}`)
	},
	updateEnvPlant(id, params){
		return http_request.put(`/env/env_plant/${id}/`, params)
	},
	createEnvPlant(params){
		return http_request.post('/env/env_plant/', params)
	},
	deleteEnvPlant(id){
		return http_request.delete(`/env/env_plant/${id}/`)
	},
	// 模块接口
	getModules(params){
		return http_request.get('/env/module/', {params: params})
	},
	getModule(id){
		return http_request.get(`/env/module/${id}`)
	},
	updateModule(id, params){
		return http_request.put(`/env/module/${id}/`, params)
	},
	createModule(params){
		return http_request.post('/env/module/', params)
	},
	deleteModule(id){
		return http_request.delete(`/env/module/${id}/`)
	},
	// 服务模块接口
	getServiceModules(params){
		return http_request.get('/env/service_module/', {params: params})
	},
	getServiceModule(id){
		return http_request.get(`/env/service_module/${id}`)
	},
	updateServiceModule(id, params){
		return http_request.put(`/env/service_module/${id}/`, params)
	},
	createServiceModule(params){
		return http_request.post('/env/service_module/', params)
	},
	deleteServiceModule(id){
		return http_request.delete(`/env/service_module/${id}/`)
	},
	// 页面接口
	getAllPlantModule(params){
		return http_request.get('/env/allPlantModule/', {params: params})
	},
	getAllServiceModule(params){
		return http_request.get('/env/allServiceModule/', {params: params})
	},
	// 页面接口
	getAllPlantModuleTwo(params){
		return http_request.get('/env/allPlantModuleTwo/', {params: params})
	},
	getAllServiceModuleTwo(params){
		return http_request.get('/env/allServiceModuleTwo/', {params: params})
	},
	getAllPlantModuleCase(params){
		return http_request.get('/env/allPlantModuleCase/', {params: params})
	},
	getAllModulePage(params){
		return http_request.get('/env/allModulePage/', {params: params})
	},
	getAllPlantElement(params){
		return http_request.get('/env/allPlantElement/', {params: params})
	},
	getPages(params){
		return http_request.get('/env/page/', {params: params})
	},
	getPage(id){
		return http_request.get(`/env/page/${id}`)
	},
	updatePage(id, params){
		return http_request.put(`/env/page/${id}/`, params)
	},
	createPage(params){
		return http_request.post('/env/page/', params)
	},
	deletePage(id){
		return http_request.delete(`/env/page/${id}/`)
	},
	// 请求头
	getHeaders(params){
		return http_request.get('/env/header/', {params: params})
	},
	getHeader(id){
		return http_request.get(`/env/header/${id}`)
	},
	updateHeader(id, params){
		return http_request.put(`/env/header/${id}/`, params)
	},
	createHeader(params){
		return http_request.post('/env/header/', params)
	},
	deleteHeader(id){
		return http_request.delete(`/env/header/${id}/`)
	},
	// cookie
	getCookies(params){
		return http_request.get('/env/cookie/', {params: params})
	},
	getCookie(id){
		return http_request.get(`/env/cookie/${id}`)
	},
	updateCookie(id, params){
		return http_request.put(`/env/cookie/${id}/`, params)
	},
	createCookie(params){
		return http_request.post('/env/cookie/', params)
	},
	deleteCookie(id){
		return http_request.delete(`/env/cookie/${id}/`)
	},
	// 脚本接口
	getPythons(params){
		return http_request.get('/script/python/', {params: params})
	},
	getPython(id){
		return http_request.get(`/script/python/${id}`)
	},
	updatePython(id, params){
		return http_request.put(`/script/python/${id}/`, params)
	},
	createPython(params){
		return http_request.post('/script/python/', params)
	},
	deletePython(id){
		return http_request.delete(`/script/python/${id}/`)
	},
	// 枚举值接口
	getEnums(params){
		return http_request.get('/script/enum/', {params: params})
	},
	getEnum(id){
		return http_request.get(`/script/enum/${id}`)
	},
	updateEnum(id, params){
		return http_request.put(`/script/enum/${id}/`, params)
	},
	createEnum(params){
		return http_request.post('/script/enum/', params)
	},
	deleteEnum(id){
		return http_request.delete(`/script/enum/${id}/`)
	},
	// 文件管理接口
	getFiles(params){
		return http_request.get('/script/file/', {params: params})
	},
	getFile(id){
		return http_request.get(`/script/file/${id}`)
	},
	updateFile(id, params){
		return http_request.put(`/script/file/${id}/`, params)
	},
	createFile(params){
		return http_request.post('/script/file/', params)
	},
	deleteFile(id){
		return http_request.delete(`/script/file/${id}/`)
	},
	// API接口
	getApis(params){
		return http_request.get('/interface/api/', {params: params})
	},
	getApi(id){
		return http_request.get(`/interface/api/${id}`)
	},
	updateApi(id, params){
		return http_request.put(`/interface/api/${id}/`, params)
	},
	createApi(params){
		return http_request.post('/interface/api/', params)
	},
	deleteApi(id){
		return http_request.delete(`/interface/api/${id}/`)
	},
	// Mock接口
	getMocks(params){
		return http_request.get('/interface/mock/', {params: params})
	},
	getMock(id){
		return http_request.get(`/interface/mock/${id}`)
	},
	updateMock(id, params){
		return http_request.put(`/interface/mock/${id}/`, params)
	},
	createMock(params){
		return http_request.post('/interface/mock/', params)
	},
	deleteMock(id){
		return http_request.delete(`/interface/mock/${id}/`)
	},
	// 步骤接口
	getActions(params){
		return http_request.get('/test/actions/', {params: params})
	},
	// 步骤接口
	getReportFunCases(params){
		return http_request.get('/test/func_cases/', {params: params})
	},
	getSeleniumKey(params){
		return http_request.get('/test/selenium/', {params: params})
	},
	getPlaywrightKey(params){
		return http_request.get('/test/playwright/', {params: params})
	},
	getAppiumKey(params){
		return http_request.get('/test/appium/', {params: params})
	},
	getFuncs(params){
		return http_request.get('/test/funcs/', {params: params})
	},
	getSteps(params){
		return http_request.get('/test/step/', {params: params})
	},
	getStep(id){
		return http_request.get(`/test/step/${id}`)
	},
	updateStep(id, params){
		return http_request.put(`/test/step/${id}/`, params)
	},
	createStep(params){
		return http_request.post('/test/step/', params)
	},
	deleteStep(id, params){
		return http_request.delete(`/test/step/${id}/`, params)
	},
	// 用例接口
	getCheck(){
		return http_request.get('/test/check/')
	},
	addManyStep(params){
		return http_request.post('/test/add_many_step/', params)
	},
	getSystemFunctionDoc(params){
		return http_request.get('/test/system_function_doc/', {params: params})
	},
	singleRunFunction(params){
		return http_request.post('/test/run_system_function/', params)
	},
	singleRunUserFunction(params){
		return http_request.post('/test/run_user_function/', params)
	},
	caseRun(params){
		return http_request.post('/test/run/', params)
	},
	StepRun(params){
		return http_request.post('/test/step_run/', params)
	},
	locustRun(params){
		return http_request.post('/test/locust_run/', params)
	},
	downloadWindows(params){
		return http_request.post('/test/download/windows', params)
	},
	copyCase(params){
		return http_request.post('/test/copyCase/', params)
	},
	update_is_run(params){
		return http_request.post('/test/update_is_run/', params)
	},
	change_step_index(params){
		return http_request.post('/test/change_step_index/', params)
	},
	getCaseLogs(params){
		return http_request.get('/test/logs/', {params: params})
	},
	deleteCaseLog(id){
		return http_request.delete(`/test/logs/${id}/`)
	},
	getCases(params){
		return http_request.get('/test/case/', {params: params})
	},
	getCase(id){
		return http_request.get(`/test/case/${id}`)
	},
	getCaseDetail(id){
		return http_request.get(`/test/caseDetail/${id}`)
	},
	updateCase(id, params){
		return http_request.put(`/test/case/${id}/`, params)
	},
	updateCaseSteps(id, params){
		return http_request.put(`/test/casesteps/${id}/`, params)
	},
	createCase(params){
		return http_request.post('/test/case/', params)
	},
	deleteCase(id){
		return http_request.delete(`/test/case/${id}/`)
	},
	batchUpdateCases(params){
		return http_request.post('/test/case/batch_update/', params)
	},
	//标签
	getTags(params){
		return http_request.get('/test/tag/', {params: params})
	},
	getTag(id){
		return http_request.get(`/test/tag/${id}`)
	},
	updateTag(id, params){
		return http_request.put(`/test/tag/${id}/`, params)
	},
	createTag(params){
		return http_request.post('/test/tag/', params)
	},
	deleteTag(id){
		return http_request.delete(`/test/tag/${id}/`)
	},
	//功能用例
	getFCases(params){
		return http_request.get('/test/func_case/', {params: params})
	},
	getFCase(id){
		return http_request.get(`/test/func_case/${id}/`)
	},
	updateFCase(id, params){
		return http_request.put(`/test/func_case/${id}/`, params)
	},
	createFCase(params){
		return http_request.post('/test/func_case/', params)
	},
	deleteFCase(id){
		return http_request.delete(`/test/func_case/${id}/`)
	},
	batchUpdateFuncCases(params){
		return http_request.post('/test/func_case/batch_update/', params)
	},
	// 用户管理接口
	getUsers(params){
		return http_request.get('/user/users/', {params: params})
	},
	getUserNames(params){
		return http_request.get('/user/usernames/', {params: params})
	},
	getUser(id){
		return http_request.get(`/user/users/${id}`)
	},
	updateUser(id, params){
		return http_request.put(`/user/users/${id}/`, params)
	},
	modify_pwd(params){
		return http_request.post(`/user/modify_pwd/`, params)
	},
	createUser(params){
		return http_request.post('/user/users/', params)
	},
	deleteUser(id){
		return http_request.delete(`/user/users/${id}/`)
	},
	// 权限管理接口
	getPermissions(params){
		return http_request.get('/user/permission', {params: params})
	},
	updatePermission(id, params){
		return http_request.put(`/user/permission/${id}/`, params)
	},
	createPermission(params){
		return http_request.post('/user/permission/', params)
	},
	deletePermission(id){
		return http_request.delete(`/user/permission/${id}/`)
	},
	// 角色管理接口
	getRole(id, params){
		return http_request.get(`/user/role/${id}/`, {params: params})
	},
	getRoles(params){
		return http_request.get('/user/role/', {params: params})
	},
	updateRole(id, params){
		return http_request.put(`/user/role/${id}/`, params)
	},
	getRolePermission(id){
		return http_request.get(`/user/role_permission/${id}`)
	},
	createRolePermission(params){
		return http_request.post('/user/role_permission/', params)
	},
	updateRolePermission(id, params){
		return http_request.put(`/user/role_permission/${id}/`, params)
	},
	deleteRole(id){
		return http_request.delete(`/user/role/${id}/`)
	},
	// 登录接口
	loginApi(params){
		return http_request.post('/user/login/', params)
	},
	register(params){
		return http_request.post('/user/register/', params)
	},
	// 登出接口
	logout(){
		return http_request.post('/user/logout/')
	},
	// 项目管理模块中的接口
	getProject(id){
		return http_request.get(`/projects/${id}/`)
	},
	getProjects(params){
		return http_request.get('/projects/', {params: params})
	},
	createProject(params){
		return http_request.post('/projects/', params)
	},
	check_permission(params){
		return http_request.post('/check_permission/', params)
	},
	deleteProject(id){
		return http_request.delete(`/projects/${id}/`)
	},
	updateProject(id, params){
		return http_request.put(`/projects/${id}/`, params)
	},
	// ai模型接口
	getAiConfig(id){
		return http_request.get(`/ai_model_setting/${id}/`)
	},
	getAiConfigs(params){
		return http_request.get('/ai_model_setting/', {params: params})
	},
	createAiConfig(params){
		return http_request.post('/ai_model_setting/', params)
	},
	deleteAiConfig(id){
		return http_request.delete(`/ai_model_setting/${id}/`)
	},
	updateAiConfig(id, params){
            return http_request.put(`/ai_model_setting/${id}/`, params)
    },
    setDefaultAiConfig(id){
            return http_request.post(`/ai_model_setting/${id}/set_default/`)
    },
	// AI生成功能用例
	aiGenerateFuncCase(params){
		return http_request.post('/ai/conversations/generate_func_case/', params)
	},
	// AI生成接口自动化用例
	aiGenerateApiCase(params){
		const { project_id, ...rest } = params
		return http_request.post('/ai/conversations/generate_api_case/', rest, { params: { project: project_id } })
	},
	// AI从功能用例生成场景脚本用例(接口/WebUI自动化)
	aiGenerateScenarioCase(params){
		const { project_id, ...rest } = params
		return http_request.post('/ai/conversations/generate_scenario_case/', rest, { params: { project: project_id } })
	},
	aiTaskStatus(params){
		return http_request.get('/ai/conversations/task_status/', {params: params})
	},
	aiRebuildVectorstore(params){
		return http_request.post('/ai/conversations/rebuild_vectorstore/', params)
	},
	// AI对话式生成
	aiConversations(params){
		return http_request.get('/ai/conversations/', {params: params})
	},
	aiCreateConversation(params){
		return http_request.post('/ai/conversations/', params)
	},
	aiDeleteConversation(id){
		return http_request.delete(`/ai/conversations/${id}/`)
	},
	aiRenameConversation(id, params){
		return http_request.patch(`/ai/conversations/${id}/rename/`, params)
	},
	aiConversationMessages(id){
		return http_request.get(`/ai/conversations/${id}/messages/`)
	},
	aiSaveChatCases(params){
		return http_request.post('/ai/conversations/save_chat_cases/', params)
	},
	// 向量库统计
	vectorstoreStats(params){
		// 该 action 注册在 VectorStoreViewSet(basename=vectorstore) 下，正确路径是 /vectorstore/vectorstore_stats/
		return http_request.get('/vectorstore/vectorstore_stats/', {params: params})
	},
	// 向量库管理
	vectorstoreList(params){
		return http_request.get('/vectorstore/', {params: params})
	},
	vectorstoreGet(id, params){
		return http_request.get(`/vectorstore/${id}/`, {params: params})
	},
	vectorstoreCreate(params){
		return http_request.post('/vectorstore/', params)
	},
	vectorstoreUpdate(id, params){
		return http_request.put(`/vectorstore/${id}/`, params)
	},
	vectorstoreDelete(id, params){
		return http_request.delete(`/vectorstore/${id}/`, {params: params})
	},
	vectorstoreBatchDelete(params){
		return http_request.post('/vectorstore/batch_delete/', params)
	},
	vectorstoreSourceTypes(params){
		return http_request.get('/vectorstore/source_types/', {params: params})
	},
	vectorstoreParseFile(params){
		return http_request.post('/vectorstore/parse_file/', params)
	},
	// 项目管理模块中的接口
	getProjectAppeals(params){
		return http_request.get('/project_appeal/', {params: params})
	},
	updateProjectAppeal(id, params){
		return http_request.put(`/project_appeal/${id}/`, params)
	},
	createProjectAppeal(params){
		return http_request.post('/project_appeal/', params)
	},
	//接口管理模块中的接口
	getInterfaces(params){
		return http_request.get('interfaces/', {params: params})
	},
	json_to_list(params){
		return http_request.post('/json_to_list/', params)
	},
	import_api(params){
		return http_request.post('/import_api/', params)
	},
	import_api_v2(params){
		// 支持文件上传：若 params 为 FormData，需指定 multipart 头
		const config = params instanceof FormData
			? { headers: { 'Content-Type': 'multipart/form-data' } }
			: {}
		return http_request.post('/import_api_v2/', params, config)
	},
	import_element(params){
		return http_request.post('/import_element/', params)
	},
	aiGenerateElements(params){
		return http_request.post('/ai_generate_elements/', params)
	},
	api_run(params){
		return http_request.post('/api_run/', params)
	},
	mock_api_run(params){
		return http_request.post('/mock_api_run/', params)
	},
	createInterface(params){
		return http_request.post('/interfaces/', params)
	},
	updateInterface(id, params){
		return http_request.put(`/interfaces/${id}/`, params)
	},
	deleteInterface(id){
		return http_request.delete(`/interfaces/${id}/`)
	},
	//用例管理模块中的接口
	getTestCase(id){
		return http_request.get(`test_steps/${id}/`)
	},
	getTestCases(params){
		return http_request.get('test_steps/', {params: params})
	},
	createTestCase(params){
		return http_request.post('/test_steps/', params)
	},
	updateTestCase(id, params){
		return http_request.put(`/test_steps/${id}/`, params)
	},
	deleteTestCase(id){
		return http_request.delete(`/test_steps/${id}/`)
	},
	//套件管理模块中的接口
	getSuite(id){
		return http_request.get(`suite/${id}/`)
	},
	getSuites(params){
		return http_request.get('suite/', {params: params})
	},
	runSuite(params){
		return http_request.post('/suite/run/', params)
	},
	createSuite(params){
		return http_request.post('/suite/', params)
	},
	updateSuite(id, params){
		return http_request.put(`/suite/${id}/`, params)
	},
	deleteSuite(id){
		return http_request.delete(`/suite/${id}/`)
	},
	getTask(id){
		return http_request.get(`task/${id}/`)
	},
	getTasks(params){
		return http_request.get('task/', {params: params})
	},
	createTask(params){
		return http_request.post('/task/', params)
	},
	updateTask(id, params){
		return http_request.put(`/task/${id}/`, params)
	},
	deleteTask(id){
		return http_request.delete(`/task/${id}/`)
	},
	//测试计划模块接口
	getPlan(id){
		return http_request.get(`/plan/${id}/`)
	},
	getPlans(params){
		return http_request.get('/plan/', {params: params})
	},
	createPlan(params){
		return http_request.post('/plan/', params)
	},
	updatePlan(id, params){
		return http_request.put(`/plan/${id}/`, params)
	},
	deletePlan(id){
		return http_request.delete(`/plan/${id}/`)
	},
	addFuncCasesToPlan(planId, params){
		return http_request.post(`/plan/${planId}/add_func_case/`, params)
	},
	removeFuncCasesFromPlan(planId, params){
		return http_request.post(`/plan/${planId}/remove_func_case/`, params)
	},
	getPlanOverview(id){
		return http_request.get(`/plan/${id}/overview/`)
	},
	// 测试计划用例接口
	getPlanCases(params){
		return http_request.get('/plan_case/', {params: params})
	},
	getPlanCase(id){
		return http_request.get(`/plan_case/${id}/`)
	},
	updatePlanCase(id, params){
		return http_request.patch(`/plan_case/${id}/`, params)
	},
	modifyExecutedBy(ids, params){
		return http_request.post('/plan_case/modify_executed_by/', {ids, ...params})
	},
	modifyExecStatus(ids, params){
		return http_request.post('/plan_case/modify_exec_status/', {ids, ...params})
	},
	runPlanCaseAutomation(params){
		return http_request.post('/plan_case/run_automation_cases/', params)
	},
	deletePlanCase(id){
		return http_request.delete(`/plan_case/${id}/`)
	},
	getPlanCaseComments(params){
		return http_request.get('/plan_case_comment/', {params: {...params, ordering: '-create_time'}})
	},
	addPlanCaseComment(params){
		return http_request.post('/plan_case_comment/', params)
	},
	updatePlanCaseComment(id, params){
		return http_request.patch(`/plan_case_comment/${id}/`, params)
	},
	deletePlanCaseComment(id){
		return http_request.delete(`/plan_case_comment/${id}/`)
	},
	//报告管理模块中的接口
	getReport(id){
		return http_request.get(`report/func/${id}/`)
	},
	getReports(params){
		return http_request.get('report/func/', {params: params})
	},
	deleteReport(id){
		return http_request.delete(`/report/func/${id}/`)
	},
	//报告管理模块中的接口
	getLocustReport(id){
		return http_request.get(`report/locust/${id}/`)
	},
	getLocustReports(params){
		return http_request.get('report/locust/', {params: params})
	},
	// 消息推送接口
	getProjectMsgPush(params){
		return http_request.get('/project_msg_push/', {params: params})
	},
	getProjectMsgPushDetail(id){
		return http_request.get(`/project_msg_push/${id}/`)
	},
	createProjectMsgPush(params){
		return http_request.post('/project_msg_push/', params)
	},
	updateProjectMsgPush(id, params){
		return http_request.put(`/project_msg_push/${id}/`, params)
	},
	deleteProjectMsgPush(id){
		return http_request.delete(`/project_msg_push/${id}/`)
	},
	// 项目通用设置接口
	getProjectGeneralSetting(params){
		return http_request.get('/project_general_setting/', {params: params})
	},
	createProjectGeneralSetting(params){
		return http_request.post('/project_general_setting/', params)
	},
	updateProjectGeneralSetting(id, params){
		return http_request.put(`/project_general_setting/${id}/`, params)
	},
	deleteLocustReport(id){
		return http_request.delete(`/report/locust/${id}/`)
	},
	// 项目成员管理接口
	getProjectMembers(params){
		return http_request.get('/project_members/', {params: params})
	},
	updateProjectMember(id, params){
		return http_request.put(`/project_members/${id}/`, params)
	},
	deleteProjectMember(id){
		return http_request.delete(`/project_members/${id}/`)
	},
	createProjectMember(params){
		return http_request.post('/project_members/', params)
	},
	// 获取在线用户数
	getOnlineUsersCount(){
		return http_request.get('/user/online_count/')
	},
	// 消息通知接口
	getMessages(params){
		return http_request.get('/message/', {params: params})
	},
	getMessage(id){
		return http_request.get(`/message/${id}/`)
	},
	deleteMessage(id){
		return http_request.delete(`/message/${id}/`)
	},
	markMessageRead(params){
		return http_request.post('/message/mark-read/', params)
	},
	markAllMessageRead(){
		return http_request.post('/message/mark-all-read/')
	},
	getUnreadMessageCount(params){
		return http_request.get('/message/unread-count/', {params: params})
	},
	// 审计日志接口
	getAuditLogs(params){
		return http_request.get('/audit_log/', {params: params})
	},
	getAuditLog(id){
		return http_request.get(`/audit_log/${id}/`)
	},
	rollbackAuditLog(id){
		return http_request.post(`/audit_log/${id}/rollback/`)
	},
	// 缺陷管理接口
	getDefects(params){
		return http_request.get('/defect/defect/', {params: params})
	},
	getDefect(id){
		return http_request.get(`/defect/defect/${id}/`)
	},
	createDefect(data){
		return http_request.post('/defect/defect/', data)
	},
	updateDefect(id, data){
		return http_request.put(`/defect/defect/${id}/`, data)
	},
	patchDefect(id, data){
		return http_request.patch(`/defect/defect/${id}/`, data)
	},
	deleteDefect(id){
		return http_request.delete(`/defect/defect/${id}/`)
	},
	getDefectComments(params){
		return http_request.get('/defect/defect_comment/', {params: params})
	},
	createDefectComment(data){
		return http_request.post('/defect/defect_comment/', data)
	},
	deleteDefectComment(id){
		return http_request.delete(`/defect/defect_comment/${id}/`)
	},
	updateDefectComment(id, data){
		return http_request.patch(`/defect/defect_comment/${id}/`, data)
	},
	base_url,
}
