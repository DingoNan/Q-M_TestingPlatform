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


// ★★ 免权限校验路径（模块级常量）。
// 守卫与 hasPermission 共用同一份，避免两处硬编码各自漂移。
// ★★★ 必须包含 '/no-permission'，这是「无限重定向」死锁的止血点：
//   若它不在免校验名单里，一旦某个页面的权限判定为 false，就会
//     判定无权限 → next({name:'noPermission'}) → 落到 /no-permission
//     → 该路径同样判定无权限 → 再次 next({name:'noPermission'}) → ……
//   形成不收敛的重定向。实测：进入 /no-permission 后
//   loginFreeList.includes 在同一处被调用 20000+ 次、Object.assign 20 万次，
//   主线程被彻底占满，页面表现为「完全无响应」，连 DevTools 都连不上。
const NO_AUTH_PATHS = [
	'/user/login', '/user/help', '/user/navigation', '/projectManager',
	'/project/index', '/myProjects', '/project/list', '/project/appeal',
	'/project/myAppeal', '/project/systemSetting', '/project/tools', '/user/auditLog',
	'/no-permission'
]

async function hasPermission(path){
	if (NO_AUTH_PATHS.includes(path)){
		return true
	}
	let permission_map = store.state.pathPermission
	const user_id = store.state.user_id
	const project_id = store.state.projectInfo && store.state.projectInfo.id
	// 项目上下文缺失时不具备校验前提：
	// 原实现会带着 project_id=undefined 请求后端并大概率拿到 has_permission=false，
	// 把用户误导航到「无权限」页 —— 但那其实只是上下文没恢复，不是真的没权限。
	// 这里放行，交由页面兜底逻辑提示「请先选择项目」。
	if (!project_id) {
		return true
	}
	// ★★★ 权限表尚未就绪 ⇒ 不具备校验前提，放行。
	//   pathPermission 全项目只有一个写入点：Menu.vue 拉到角色权限后调用
	//   setPathPermission()。而守卫在「首次进入项目内页面」时就会先执行，
	//   此刻它必然是初始值 {} ⇒ 旧实现返回 false ⇒ 用户被直接推到无权限页。
	if (!permission_map || typeof permission_map !== 'object' || !Object.keys(permission_map).length) {
		return true
	}
	// ★★★ 该路径未纳入权限表 ⇒ 视为不受「页面级」管控，放行。
	//   权限表只收录 27 个列表/主页级路径（实测），编辑页、详情页等子页面
	//   不在其中（例：/resource/scriptCaseEdit 不在表内，而 /resource/scriptCase 在）。
	//   子页面权限由所属列表页负责；真正的数据级鉴权仍由后端接口保证。
	//   旧实现对「表里没有」与「真的没权限」不加区分，一律 false ⇒
	//   点开脚本用例（跳编辑页）即触发无限重定向。
	if (!permission_map[path]) {
		return true
	}
	const response =  await check_permission({user_id: user_id, project_id: project_id, permission_id: permission_map[path]})
	if (response.data.result.has_permission){
		return true
	}
	return false
}


// 设置路由导航守卫，控制前端路由访问的权限
// 改造点：原实现直接在守卫里读 store.state.projectInfo.id，
// 该值一旦为空（刷新内页/新开标签页/换账号），权限校验会带着 project_id=undefined
// 去请求后端，且依赖 project 的页面会静默查空。
// 现改为：进入「项目内页面」时先走一次 resolveProject 三层兜底，
// 恢复出项目上下文后再校验权限，避免「能进页面但内容全空」。
router.beforeEach(async (to, from, next) => {
	const token = window.localStorage.getItem('token')
	if (!token) {
		if (to.name === 'login' || to.name === 'navigation' || to.name === 'help' || to.name === 'noPermission' || to.name === 'register') {
			next()
		} else {
			next({ name: 'login' })
		}
		return
	}

	// ★★★ 最终防线：无权限页自身绝不再进入权限校验分支。
	//   否则 next({name:'noPermission'}) 会在下一轮导航里再次落进下面的
	//   权限分支 ⇒ 再次 next({name:'noPermission'}) ⇒ 无限重定向 ⇒ 页面锁死。
	//   按 to.name 判断（而非 path），避免路径尾斜杠/大小写差异绕过这道闸门。
	if (to.name === 'noPermission') {
		next()
		return
	}

	// 系统层页面与免校验页面：直接放行，不触发项目上下文恢复
	if (NO_AUTH_PATHS.includes(to.path)) {
		next()
		return
	}

	// 项目内页面：确保项目上下文可用（三层兜底），再做权限校验
	if (!store.state.projectInfo || !store.state.projectInfo.id) {
		try {
			await store.dispatch('resolveProject')
		} catch (e) {
			// 兜底失败不阻断导航，交由页面自身给出提示
		}
	}

	try {
		const allowed = await hasPermission(to.path)
		if (allowed) {
			next()
		} else {
			next({ name: 'noPermission', query: { from: to.fullPath } })
		}
	} catch (e) {
		// 权限接口异常时放行，避免因校验失败导致整站不可用
		next()
	}
})
export default router
