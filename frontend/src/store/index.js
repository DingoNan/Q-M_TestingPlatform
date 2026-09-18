import api from '@/api'
import { createStore } from 'vuex'

const PROJECT_KEY = 'qm-projectInfo'

// 读取项目上下文：容错版。
// 历史实现直接 JSON.parse 后取值，遇到「存进去的是字符串 null/"undefined"」或
// 「对象存在但 id 缺失」这两种脏数据时不会报错，却会让 projectInfo.id 为 undefined，
// 导致所有带 project 参数的接口全部查空（模块树空白、用例列表空白）。
// 这里统一收敛：只有解析出「带有效 id 的对象」才算命中，其余一律视为未选中项目。
function readProjectInfo() {
  try {
    const raw = localStorage.getItem(PROJECT_KEY)
    if (!raw || raw === 'null' || raw === 'undefined' || raw === '""') return ''
    const parsed = JSON.parse(raw)
    if (parsed && typeof parsed === 'object' && parsed.id) return parsed
    return ''
  } catch (e) {
    return ''
  }
}

export default createStore({
  state: {
	  role_id: '',
	  pathPermission: {},
	  cur_path: '',
	  // 当前项目上下文。**持久化到 localStorage**（键 qm-projectInfo）：
	  // 它过去只活在内存里，刷新页面/新开标签页就丢，导致所有「把 projectInfo.id 传给后端」
	  // 的接口会因缺失 project_id 而报 400（典型：性能压测执行直接 400 且不产生任何报告）。
	  // 与 userInfo 的处理方式保持一致，登出时由 clearProjectInfo 一并清理。
	  projectInfo: readProjectInfo(),
	  // 兜底标记：本次会话是否已经尝试过「自动恢复项目上下文」，
	  // 避免每个页面 created 都去拉一次 /projects/ 造成重复请求。
	  projectResolved: false,
	  // 登录后写入 localStorage（键 qm-userInfo），刷新/新标签页可恢复，
	  // 否则超管页（/user/list 等）的 userInfo.is_superuser 判空会被误判为无权限
	  userInfo: (() => {
		  try { return JSON.parse(localStorage.getItem('qm-userInfo')) || '' } catch (e) { return '' }
	  })(),
	  interfaces: [],
	  tags: [],
	  theme: localStorage.getItem('qm-theme') || 'light',
  },
  mutations: {
		  setPathPermission(state, path_permission){
			  state.pathPermission = path_permission
		  },
		  saveRoleId(state, id){
			  state.role_id = id
		  },
		  saveCurPath(state, path){
		   	state.cur_path = path
		  },
		  saveProjectInfo(state, item){
			  state.projectInfo = {...item}
			  try { localStorage.setItem('qm-projectInfo', JSON.stringify(item)) } catch (e) {}
		  },
		  clearProjectInfo(state){
			  state.projectInfo = ''
			  state.projectResolved = false
			  try { localStorage.removeItem('qm-projectInfo') } catch (e) {}
		  },
		  setProjectResolved(state, val){
			  state.projectResolved = !!val
		  },
		  saveUserInfo(state, item){
			  state.userInfo = {...item}
			  try { localStorage.setItem('qm-userInfo', JSON.stringify(item)) } catch (e) {}
		  },
		  clearUserInfo(state){
			  state.userInfo = ''
			  try { localStorage.removeItem('qm-userInfo') } catch (e) {}
		  },
		  setTheme(state, theme){
			  state.theme = theme
			  localStorage.setItem('qm-theme', theme)
			  document.documentElement.classList.toggle('dark', theme === 'dark')
		  },
		  toggleTheme(state){
			  const next = state.theme === 'dark' ? 'light' : 'dark'
			  state.theme = next
			  localStorage.setItem('qm-theme', next)
			  document.documentElement.classList.toggle('dark', next === 'dark')
		  },
	  addTags(state, obj_item){
		  const obj = state.tags.find((item)=>{
			  return item.path === obj_item.path
		  })
		  if(!obj){
			 state.tags.push(obj_item)
			 if (state.tags.length >=11){
			 	state.tags.splice(1, 1)
			 }
			 
		  }
	  },
	  delTags(state, item){
		  const index = state.tags.findIndex((to)=>{
			  return to.path === item.path
		  })
		  state.tags.splice(index, 1)
	  },
	  clearTags(state){
		  const len= state.tags.length - 1
		  for (var index=len; index>=0; index--){
				state.tags.splice(index, 1)
		  }
	  }
  },
  actions: {
	  async getInterfaces(content, params){
		  const response = await api.getInterfaces(params)
		  if (response.status === 200){
			  return response.data
		  }
	  },

	  // 项目上下文三层兜底恢复。
	  // 背景：项目内所有二级页面都依赖 projectInfo.id 作为 project 查询参数，
	  // 而该值只由「点进项目列表」这一个动作写入。用户刷新内页、新开标签页、
	  // 换账号或被清缓存后，projectInfo 即为空，后端按 project=None 过滤命中 0 条，
	  // 表现为「模块管理空白 / 用例列表空白」，且接口返回 200 不报任何错。
	  //
	  // 兜底顺序（已用到的第 1 层是内存/localStorage，这里补齐后两层）：
	  //   ① 当前已有有效 projectInfo —— 直接复用，不发请求；
	  //   ② 拉取 /projects/ —— 仅一个项目时自动采用（绝大多数私有化部署场景）；
	  //      多个项目则不下断言，交由调用方提示用户选择；
	  //   ③ 都拿不到 —— 保持为空，由调用方给出「请先选择项目」的明确提示，
	  //      而不是静默返回空列表。
	  //
	  // 返回 { ok, reason, project }：
	  //   ok=true  → project 为可用的项目对象
	  //   ok=false → reason 说明原因（'no-token' / 'multi-project' / 'empty' / 'error'）
	  async resolveProject({ state, commit }){
		  // ① 已有有效上下文
		  if (state.projectInfo && state.projectInfo.id) {
			  return { ok: true, reason: 'cached', project: state.projectInfo }
		  }
		  // 本项目只支持已登录场景，无 token 时不发请求（避免必定的 401）
		  let token = null
		  try { token = JSON.parse(localStorage.getItem('token')) } catch (e) { token = null }
		  if (!token) {
			  commit('setProjectResolved', true)
			  return { ok: false, reason: 'no-token', project: null }
		  }
		  if (state.projectResolved) {
			  // 本轮已尝试过且失败，不重复打扰后端
			  return { ok: false, reason: state.projectInfo ? 'cached' : 'empty', project: null }
		  }
		  try {
			  const res = await api.getProjects({ page: 1, size: 100 })
			  const list = (res && res.data && res.data.results) || []
			  if (list.length === 1) {
				  // ② 唯一项目 —— 自动采用，并写回缓存
				  commit('saveProjectInfo', list[0])
				  if (list[0].role_id !== undefined) commit('saveRoleId', list[0].role_id)
				  commit('setProjectResolved', true)
				  return { ok: true, reason: 'auto', project: list[0] }
			  }
			  commit('setProjectResolved', true)
			  if (list.length === 0) return { ok: false, reason: 'empty', project: null }
			  // ③ 多项目 —— 不自作主张，交由调用方提示用户选择
			  return { ok: false, reason: 'multi-project', project: null }
		  } catch (e) {
			  commit('setProjectResolved', true)
			  return { ok: false, reason: 'error', project: null }
		  }
	  },
  },
  modules: {
  }
})
