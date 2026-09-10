<template>
	<div class='create_role'>
		<div class='action'>
			<el-button class='action_btn' type="primary" @click='save'>保存</el-button>
			<el-button class='action_btn' type="primary" @click="()=>{this.$router.go(-1)}">返回</el-button>
		</div>
		<el-form class='role_form'>
			<el-form-item label="角色名">
				<el-input v-model='name' placeholder="请输入角色名"></el-input>
			</el-form-item>
			<el-divider border-style='solid'/>
			<template v-for="permission_obj, _index in permissions">
				<el-checkbox @change='handleParentChange(permission_obj)' v-model="permissions[_index].has_permission" :label="permission_obj.name" size="large" />
				<div class='top_border'>
					<div v-for="children_permission_obj, index in permission_obj.children" class='top_border'>
						<el-checkbox @change="handleChange(permission_obj, children_permission_obj)" v-model="permissions[_index].children[index].has_permission" :label="children_permission_obj.name" size="large" />
						<el-divider border-style='solid'/> 
						<el-checkbox @change="handleReadChange(children_permission_obj, permission_obj)" v-model="permissions[_index].children[index].has_read_permission" label="查看权限" size="large" />
						<el-checkbox @change="handleEditChange(permissions[_index].children[index].has_edit_permission, children_permission_obj, permission_obj)" v-model="permissions[_index].children[index].has_edit_permission" label="编辑权限" size="large" />
						<el-checkbox @change="handleEditChange(permissions[_index].children[index].has_add_permission, children_permission_obj, permission_obj)" v-model="permissions[_index].children[index].has_add_permission" label="新增权限" size="large" />
						<el-checkbox @change="handleEditChange(permissions[_index].children[index].has_delete_permission, children_permission_obj, permission_obj)" v-model="permissions[_index].children[index].has_delete_permission" label="删除权限" size="large" />
					</div>
				</div>
			</template>
		</el-form>
	</div>
   
  
</template>

<script>
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen} from '@element-plus/icons-vue'

export default{
	data() {
		return {
			name: '',
			permissions: [],
		}
	},
	computed:{
		...mapState(['projectInfo']),
	},
	created(){
		if(this.$route.query.id){
			this.getRole()
		}else{
			this.getPermissions()
		}
	},
	methods: {
		save(){
			if(this.$route.query.id){
				this.updateRolePermission(this.$route.query.id)
			}else{
				this.createRolePermission()
			}
		},
		setValue(obj, value){
			obj.has_permission = value
			obj.has_read_permission = value
			obj.has_edit_permission = value
			obj.has_delete_permission = value
			obj.has_add_permission = value
		},
		handleReadChange(obj, parent_obj){
			if(obj.has_read_permission == true){
				obj.has_permission = true
				parent_obj.has_permission = true
			}else{
				this.setValue(obj, false)
			}
		},
		handleEditChange(value, obj, parent_obj){
			if (value){
				parent_obj.has_permission = true
				obj.has_permission = true
				obj.has_read_permission = true
			}
		},
		handleChange(parent_obj, obj){
			if(obj.has_permission === true){
				parent_obj.has_permission = true
				this.setValue(obj, true)
			}else{
				this.setValue(obj, false)
			}
			
		},
		handleParentChange(permission_obj){
			if(permission_obj.has_permission===true){
				for(const children_obj of permission_obj.children){
					this.setValue(children_obj, true)
				}
			}else{
				for(const children_obj of permission_obj.children){
					this.setValue(children_obj, false)
				}
			}
		},
		async getRole(){
			const response = await this.$api.getRole(this.$route.query.id)
			if (response.status === 200){
				this.permissions = response.data.result.role_permissions
				this.name = response.data.result.name
			}
		},
		async getPermissions(){
				const response = await this.$api.getPermissions()
			    if (response.status === 200){
					this.permissions = response.data.result
			    }
		},
		async createRolePermission(){
			const response = await this.$api.createRolePermission({role_name: this.name, items: this.permissions})
			this.$router.push({name: 'role'})
		},
		async updateRolePermission(id){
			const response = await this.$api.updateRolePermission(id ,{role_name: this.name, items: this.permissions})
			this.$router.push({name: 'role'})
		}
	},
}

</script>

<style scoped>
	.create_role{
		clear: both;
	}
	.role_form {
		clear: both;
		margin: 18px;
	}
	.role_form .el-divider{
		margin: 0px;
	}
	.top_border{
		border: 1px solid #dcdfe6;
		padding: 10px;
	}
	.action .action_btn{
		float: right;
		margin: 10px;
	}
	.create_role .el-input{
		width: 300px;
	}

</style>