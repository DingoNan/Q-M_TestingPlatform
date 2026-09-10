import api from '@/api'
import { createStore } from 'vuex'

export default createStore({
  state: {
	  role_id: '',
	  pathPermission: {},
	  cur_path: '',
	  projectInfo: '',
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
  },
  modules: {
  }
})
