import { createRouter, createWebHashHistory } from 'vue-router'
import {mapState} from 'vuex'
import store from '../store/index.js'; // 导入 Vuex 实例
import api from '../api/index.js'

const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/user/login'
  },
  {
    path: '/no-permission',
    name: 'noPermission',
    component: () => import(/* webpackChunkName: "noPermission" */ '../views/NoPermission.vue')
  },
  {
    path: '/user/login',
    name: 'login',
    component: () => import(/* webpackChunkName: "login" */ '../views/user/Login.vue')
  },
  {
    path: '/user/register',
    name: 'register',
    component: () => import(/* webpackChunkName: "register" */ '../views/user/Register.vue')
  },
  {
    path: '/user/navigation',
    name: 'navigation',
    component: () => import(/* webpackChunkName: "about" */ '../views/Navigation.vue')
  },
  {
    path: '/user/help',
    name: 'help',
    component: () => import(/* webpackChunkName: "about" */ '../views/Help.vue')
  },
  {
    path: '/projectManager',
    name: 'projectManager',
    component: () => import(/* webpackChunkName: "projects" */ '../views/user/Projects.vue'),
	children: [
		{
			path: '/user/list',
			name: 'user',
			component: () => import(/* webpackChunkName: "user" */ '../views/user/User.vue'),
		},
		{
			path: '/user/role',
			name: 'role',
			component: () => import(/* webpackChunkName: "role" */ '../views/user/Role.vue'),
		},
		{
			path: '/user/roleCreate',
			name: 'roleCreate',
			component: () => import(/* webpackChunkName: "createEditRole" */ '../views/user/CreateEditRole.vue'),
		},
		{
			path: '/user/roleEdit',
			name: 'roleEdit',
			component: () => import(/* webpackChunkName: "createEditRole" */ '../views/user/CreateEditRole.vue'),
		},
		{
			path: '/user/permission',
			name: 'permission',
			component: () => import(/* webpackChunkName: "permission" */ '../views/user/Permission.vue'),
		},
		{
			path: '/user/auditLog',
			name: 'auditLog',
			component: () => import(/* webpackChunkName: "auditLog" */ '../views/audit/AuditLog.vue'),
		},
		{
			path: '/myProjects',
			name: 'myProject',
			component: () => import(/* webpackChunkName: "myProject" */ '../views/user/MyProject.vue'),
		},
		{
			path: '/project/list',
			name: 'projectList',
			component: () => import(/* webpackChunkName: "projectList" */ '../views/user/ProjectList.vue'),
		},
		{
			path: '/project/appeal',
			name: 'projectAppeal',
			component: () => import(/* webpackChunkName: "projectAppeal" */ '../views/user/ProjectAppeal.vue'),
		},
		{
			path: '/project/myAppeal',
			name: 'myAppeal',
			component: () => import(/* webpackChunkName: "myAppeal" */ '../views/user/ProjectMyAppeal.vue'),
		},
	]
  },
  {
	path: '/project',
	name: 'projectHome',
	component: () => import(/* webpackChunkName: "projectHome" */ '../views/ProjectHome.vue'),
	children: [
		{
			path: '/project/systemSetting',
			name: 'systemSetting',
			component: () => import(/* webpackChunkName: "systemSetting" */ '../views/user/SystemSetting.vue'),
		},
		{
			path: '/project/tools',
			name: 'Tools',
			component: () => import(/* webpackChunkName: "about" */ '../views/user/Tools.vue')
		},
		{
			path: '/project/index',
			name: 'index',
			component: () => import(/* webpackChunkName: "projectIndex" */ '../views/ProjectIndex.vue'),
		},
		{
			path: '/env/env',
			name: 'env',
			component: () => import(/* webpackChunkName: "env" */ '../views/env/Env.vue'),
		},
		{
			path: '/env/service',
			name: 'service',
			component: () => import(/* webpackChunkName: "service" */ '../views/env/Service.vue'),
		},
		{
			path: '/env/plant',
			name: 'plant',
			component: () => import(/* webpackChunkName: "plant" */ '../views/env/Plant.vue'),
		},
		{
			path: '/env/db',
			name: 'db',
			component: () => import(/* webpackChunkName: "db" */ '../views/env/Db.vue'),
		},
		{
			path: '/resource/api',
			name: 'api',
			component: () => import(/* webpackChunkName: "about" */ '../views/interface/Api.vue'),
		},
		{
			path: '/resource/apiEdit',
			name: 'apiEdit',
			component: () => import(/* webpackChunkName: "apiEdit" */ '../views/interface/ApiEdit.vue'),
		},
		{
			path: '/common/python',
			name: 'python',
			component: () => import(/* webpackChunkName: "python" */ '../views/script/Python.vue'),
		},
		{
			path: '/common/enum',
			name: 'enum',
			component: () => import(/* webpackChunkName: "enum" */ '../views/script/Enum.vue'),
		},
		{
			path: '/common/file',
			name: 'file',
			component: () => import(/* webpackChunkName: "file" */ '../views/script/File.vue'),
		},
		{
			path: '/resource/scriptCase',
			name: 'case',
			component: () => import(/* webpackChunkName: "CaseList" */ '../views/case/CaseList.vue'),
		},
		{
			path: '/resource/knowledgeBase',
			name: 'knowledgeBase',
			component: () => import(/* webpackChunkName: "VectorStore" */ '../views/case/VectorStore.vue'),
		},
		{
			path: '/resource/funcCase',
			name: 'func_case',
			component: () => import(/* webpackChunkName: "FunCaseList" */ '../views/case/FunCaseList.vue'),
		},
		{
			path: '/resource/tag',
			name: 'tag',
			component: () => import(/* webpackChunkName: "TagList" */ '../views/case/TagList.vue'),
		},
		{
			path: '/test/caseCreate',
			name: 'caseCreate',
			component: () => import(/* webpackChunkName: "caseCreate" */ '../views/case/CaseStepCreate.vue'),
		},
		{
			path: '/common/element',
			name: 'element',
			component: () => import(/* webpackChunkName: "element" */ '../views/element/Element.vue'),
		},
		{
			path: '/resource/scriptCaseEdit',
			name: 'caseStepEdit',
			component: () => import(/* webpackChunkName: "CaseStepCreate" */ '../views/case/CaseStepCreate.vue'),
		},
		{
			path: '/common/step',
			name: 'step',
			component: () => import(/* webpackChunkName: "stepList" */ '../views/case/StepList.vue'),
		},
		{
			path: '/exec/suite',
			name: 'suite',
			component: () => import(/* webpackChunkName: "suiteList" */ '../views/exec/SuiteList.vue'),
		},
		{
			path: '/exec/plan',
			name: 'plan',
			component: () => import(/* webpackChunkName: "testPlan" */ '../views/exec/TestPlan.vue'),
		},
		{
			path: '/exec/plan/detail/:id',
			name: 'TestPlanDetail',
			component: () => import(/* webpackChunkName: "testPlanDetail" */ '../views/exec/TestPlanDetail.vue'),
		},
		{
			path: '/exec/plan/overview/:id',
			name: 'TestPlanOverview',
			component: () => import(/* webpackChunkName: "testPlanOverview" */ '../views/exec/TestPlanOverview.vue'),
		},
		{
			path: '/exec/task',
			name: 'task',
			component: () => import(/* webpackChunkName: "taskPlan" */ '../views/exec/TaskPlan.vue'),
		},
		{
			path: '/report/list',
			name: 'report',
			component: () => import(/* webpackChunkName: "reportList" */ '../views/report/ReportList.vue'),
		},
		{
			path: '/report/log',
			name: 'log',
			component: () => import(/* webpackChunkName: "reportList" */ '../views/report/LogList.vue'),
		},
		{
			path: '/report/locust',
			name: 'reportlocust',
			component: () => import(/* webpackChunkName: "reportList" */ '../views/report/LocustReportList.vue'),
		},
		{
			path: '/report/listView',
			name: 'reportViewDetail',
			component: () => import(/* webpackChunkName: "reportDetail" */ '../views/report/ReportDetail.vue'),
		},
		{
			path: '/report/locust/detail',
			name: 'locustDetail',
			component: () => import(/* webpackChunkName: "reportDetail" */ '../views/report/LocustReportDetail.vue'),
		},
		{
			path: '/defect/list',
			name: 'defect',
			component: () => import(/* webpackChunkName: "defectList" */ '../views/defect/DefectList.vue'),
		},
		{
			path: '/factory/list/FactoryCaseEdit',
			name: 'FactoryCaseEdit',
			component: () => import(/* webpackChunkName: "FactoryCaseEdit" */ '../views/case/FactoryCaseEdit.vue'),
		},
	]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})


async function hasPermission(path){
	if (['/user/login', '/user/help', '/user/navigation', '/projectManager', '/project/index', '/myProjects', '/project/list', '/project/appeal', '/project/myAppeal', '/project/systemSetting', '/project/tools', '/user/auditLog'].includes(path)){
		return true
	}
	let permission_map = store.state.pathPermission
	const user_id = store.state.user_id
	const project_id = store.state.projectInfo.id
	if (!permission_map[path]) {
		return false
	}
	const response =  await check_permission({user_id: user_id, project_id: project_id, permission_id: permission_map[path]})
	if (response.data.result.has_permission){
		return true
	}
	return false
}


// 设置路由导航守卫ie，控制前端路由访问的权限
router.beforeEach((to, from, next) =>{
	const token = window.localStorage.getItem('token')
	if(token){
		next()
	}else{
		if (to.name === 'login' || to.name ==='navigation' || to.name ==='help' || to.name === 'noPermission' || to.name === 'register'){
			next()
		}else{
			next({name: 'login'})
		}
		
	}
})
export default router
