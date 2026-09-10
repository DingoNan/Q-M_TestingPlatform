import api from '@/api'
import { createStore } from 'vuex'

export default createStore({
  state: {
	  role_id: '',
	  pathPermission: {},
	  cur_path: '',
	  projectInfo: '',
	  userInfo: '',
	  interfaces: [],
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
		  },
		  clearUserInfo(state){
			  state.userInfo = ''
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
