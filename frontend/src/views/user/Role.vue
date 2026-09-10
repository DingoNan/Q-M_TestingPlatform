<template>
  <div class="role-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">角色筛选</h3>
          <el-tag size="small" type="info" effect="plain">精准查询</el-tag>
        </div>
        <div class="header-action-section">
          <el-button class="reset-btn" @click="reset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
          <el-button type="primary" @click="search" class="search-btn">
            <el-icon><Search /></el-icon>查询
          </el-button>
        </div>
      </div>
      
      <div class="filter-form-wrapper">
        <el-form :model="roleSearch" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-user"></i>
                  <span class='label-text'>角色名称</span>
                </div>
                <el-input 
                  v-model="roleSearch.name" 
                  placeholder="请输入角色名称" 
                  clearable
				  size='large'
                  class="input"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-creator"></i>
                  <span class='label-text'>创建人</span>
                </div>
                <el-select 
                  v-model="roleSearch.create_by" 
                  placeholder="请选择创建人" 
                  clearable
                  filterable
				  size='large'
				  popper-class='select-dropdown-rounded'
                  class="select"
                >
                  <el-option 
                    v-for="user_obj in user_list" 
                    :key="user_obj.id"
                    :label="user_obj.username" 
                    :value="user_obj.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-updater"></i>
                  <span class='label-text'>更新人</span>
                </div>
                <el-select 
                  v-model="roleSearch.update_by" 
                  placeholder="请选择更新人" 
                  clearable
                  filterable
                  class="select"
				  popper-class='select-dropdown-rounded'
				  size='large'
                >
                  <el-option 
                    v-for="user_obj in user_list" 
                    :key="user_obj.id"
                    :label="user_obj.username" 
                    :value="user_obj.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
    </el-card>

    <!-- 主内容区域 -->
    <el-card class="content-card elegant-shadow">
      <div class="content-header">
        <div class="content-title-section">
          <div class="title-with-stats">
            <h3 class="content-title">角色列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ roles_list.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ page_size_params.page }}</span>
              </div>
            </div>
          </div>
          <el-button 
            @click="addRole"
            type="primary" 
            class="add-btn"
          >
            <el-icon><Plus /></el-icon>新增角色
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table 
          :data="roles_list.results" 
          :max-height="'calc(100vh - 485px)'" 
          class="elegant-table"
		  @sort-change='handleSortChange'
          :header-row-style="headerRowStyle"
        >
          <el-table-column 
            label="序号" 
            width="70" 
            type="index" 
            align="center"
            class-name="index-column"
          >
            <template #default="scope">
              <div class="index-cell">
                {{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="角色名称" 
            prop="name" 
            min-width="120" 
            align="center"
            class-name="role-column"
          >
            <template #default="scope">
              <div class="role-cell">
                <div class="role-avatar">
                  {{ scope.row.name ? scope.row.name.charAt(0).toUpperCase() : '' }}
                </div>
                <div class="role-info">
                  <span class="role-name">{{ scope.row.name }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="关联项目数"
            prop="link_num" 
            min-width="120" 
            align="center"
            class-name="count-column"
          >
            <template #default="scope">
              <el-popover
                placement="bottom"
                trigger="hover"
                width="auto"
                popper-class="project-popover"
                v-if="Object.keys(scope.row.link_num || {}).length > 0"
              >
                <template #reference>
                  <el-tag 
                    size="small" 
                    type="success" 
                    effect="light"
                    class="count-tag"
                  >
                    {{ Object.keys(scope.row.link_num || {}).length || 0 }} 个
                  </el-tag>
                </template>
                <el-table 
                  :data="Object.entries(scope.row.link_num).map(([name, count]) => ({ name, count }))" 
                  size="small" 
                  border 
                  style="width: 100%; font-size: 13px;"
                  :header-cell-style="{ 'background-color': '#f8f9fa', 'font-weight': '500', 'font-size': '12px', 'color': '#67C23A', 'text-align': 'center' }"
                  :cell-style="{ 'padding': '8px 10px', 'font-size': '13px', 'color': '#67C23A', 'text-align': 'center' }"
                  :row-style="{ 'hover': { 'background-color': '#f0f9ff' } }"
                >
                  <el-table-column prop="name" label="项目名称" min-width="150" align="center">
                    <template #default="scope">
                      <el-tag 
                        size="small" 
                        type="success" 
                        effect="light"
                        class="count-tag"
                      >
                        {{ scope.row.name }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column prop="count" label="关联用户数" width="80" align="center">
                    <template #default="scope">
                      <el-tag 
                        size="small" 
                        type="success" 
                        effect="light"
                        class="count-tag"
                      >
                        {{ scope.row.count }}个
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </el-popover>
              <el-tag 
                v-else 
                size="small" 
                type="success" 
                effect="light"
                class="count-tag"
              >
                0 个
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="关联权限数" 
            prop="permissions" 
            min-width="120" 
            align="center"
            class-name="count-column"
          >
            <template #default="scope">
              <el-tag 
                size="small" 
                type="success" 
                effect="light"
                class="count-tag"
              >
                {{ scope.row.permissions || 0 }} 项
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="创建人" 
            prop="create_by_name" 
            width="150" 
            align="center"
            class-name="creator-column"
          />
          
          <el-table-column 
            label="更新人" 
            prop="update_by_name" 
            width="150" 
            align="center"
            class-name="updater-column"
          />
          
          <el-table-column 
            label="创建时间" 
            prop="create_time" 
            sortable="custom" 
            width="180" 
            align="center"
            class-name="time-column"
          >
            <template #default="scope">
              <div class="time-cell">
                <i class="icon-time"></i>
                <span>{{ formatTime(scope.row.create_time) }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="更新时间" 
            prop="update_time" 
            sortable="custom" 
            width="180" 
            align="center"
            class-name="time-column"
          >
            <template #default="scope">
              <div class="time-cell">
                <i class="icon-time"></i>
                <span>{{ formatTime(scope.row.update_time) }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            align="center" 
            :width="calcMinWidth" 
            label="操作"
            class-name="action-column"
            fixed="right"
          >
            <template #default="scope">
              <div class="action-buttons">
                <el-tooltip 
                  content="查看角色" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="success" 
                    class="action-btn view-btn"
                    @click.stop="viewRole(scope.row)"
                    circle
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="编辑角色" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="warning"
                    class="action-btn edit-btn"
                    @click.stop="editRole(scope.row)"
                    circle
                  >
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="删除角色" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="danger"
                    @click.stop="deleteRole(scope.row.id)" 
                    class="action-btn delete-btn"
                    circle
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页组件 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page_size_params.page"
          v-model:page-size="page_size_params.size"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="roles_list.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
          :background="true"
        />
      </div>
    </el-card>

    <!-- 角色编辑抽屉 -->
    <el-dialog 
      v-model="CreateRoleVisible" 
      direction="rtl" 
      fullscreen
      :title="roleTitle" 
      destroy-on-close
    >
      <div class="drawer-content">
        <el-form class="role-form" :disabled="roleView">
          <el-form-item  class="role-form-item">
            <label class="dialog-label">
              <i class="icon-role-dialog"></i>
              角色名
            </label>
            <el-input 
              v-model="name" 
              placeholder="请输入角色名"
			  size='large'
			  maxlength="20"
			  show-word-limit
              class="input"
            />
          </el-form-item>
          
          <el-divider class="elegant-divider" />
          
          <div class="permissions-container">
            <div v-for="(permission_obj, index) in permissions" :key="index" class="permission-group">
              <div class="permission-header">
                <el-checkbox 
                  @change="handleParentChange(permission_obj)" 
                  v-model="permission_obj.has_permission" 
                  size="large"
                  class="permission-checkbox"
                >
                  <span class="permission-name">{{ permission_obj.name }}</span>
                </el-checkbox>
              </div>
              
              <div class="permission-children">
                <div 
                  v-for="(children_permission_obj, childIndex) in permission_obj.children" 
                  :key="childIndex"
                  class="permission-child"
                >
                  <div class="child-header">
                    <el-checkbox 
                      @change="handleChange(permission_obj, children_permission_obj)" 
                      v-model="permission_obj.children[childIndex].has_permission" 
                      size="large"
                      class="child-checkbox"
                    >
                      <span class="child-name">{{ children_permission_obj.name }}</span>
                    </el-checkbox>
                  </div>
                  
                  <div class="permission-options">
                    <el-checkbox 
                      @change="handleReadChange(children_permission_obj, permission_obj)" 
                      v-model="permission_obj.children[childIndex].has_read_permission" 
                      class="option-checkbox"
                    >
                      查看权限
                    </el-checkbox>
                    
                    <el-checkbox 
                      @change="handleEditChange(permission_obj.children[childIndex].has_edit_permission, children_permission_obj, permission_obj)" 
                      v-model="permission_obj.children[childIndex].has_edit_permission" 
                      class="option-checkbox"
                    >
                      编辑权限
                    </el-checkbox>
                    
                    <el-checkbox 
                      @change="handleEditChange(permission_obj.children[childIndex].has_add_permission, children_permission_obj, permission_obj)" 
                      v-model="permission_obj.children[childIndex].has_add_permission" 
                      class="option-checkbox"
                    >
                      新增权限
                    </el-checkbox>
                    
                    <el-checkbox 
                      @change="handleEditChange(permission_obj.children[childIndex].has_delete_permission, children_permission_obj, permission_obj)" 
                      v-model="permission_obj.children[childIndex].has_delete_permission" 
                      class="option-checkbox"
                    >
                      删除权限
                    </el-checkbox>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-form>
      </div>
      
      <template #footer>
        <div v-if="!roleView">
          <el-button @click="CreateRoleVisible = false" class="dialog-cancel-btn">返回</el-button>
          <el-button
            type="primary" 
            @click="save"
            class="dialog-confirm-btn"
          >
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Search,
  Plus,
  View,
  Delete,
  EditPen
} from '@element-plus/icons-vue'

export default {
  name: 'RoleManagement',
  computed: {
    ...mapState(['pathPermission', 'userInfo']),
    calcMinWidth() {
      let visibleButtons = 3
      return Math.max(10, visibleButtons * 48)
    },
    drawerSize() {
      return '100%'
    }
  },
  data() {
    return {
      name: '',
      role_id: '',
      roleView: false,
      permissions: [],
      is_add: false,
      CreateRoleVisible: false,
      roleTitle: '新增角色',
      permission: {},
      user_list: [],
      roleSearch: {
        name: '',
        create_by: '',
        update_by: ''
      },
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      page_size_params: {
        page: 1,
        size: 10,
      },
      roles_list: {
        count: 0,
        results: []
      },
    }
  },
  components: {
    Refresh,
    Search,
    Plus,
    View,
    Delete,
    EditPen
  },
  methods: {
    ...mapActions(['getRolePermission']),
    
    handleCurrentChange(page) {
      this.page_size_params.page = page
      this.getRoles()
    },
    
    handleSizeChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getRoles()
    },
    
	handleSortChange(column) {
	  const { prop, order } = column
	  if (order === 'ascending') {
	    this.sort_params.ordering = prop
	  } else if (order === 'descending') {
	    this.sort_params.ordering = `-${prop}`
	  } else {
	    // 如果取消排序，则清空排序参数
	    this.sort_params.ordering = ''
	  }
	  // 重置到第一页并获取数据
	  this.page_size_params.page = 1
	  this.getRoles()
	},
	
    setValue(obj, value) {
      obj.has_permission = value
      obj.has_read_permission = value
      obj.has_edit_permission = value
      obj.has_delete_permission = value
      obj.has_add_permission = value
    },
    
    handleReadChange(obj, parent_obj) {
      if (obj.has_read_permission === true) {
        obj.has_permission = true
        parent_obj.has_permission = true
      } else {
        this.setValue(obj, false)
      }
    },
    
    handleEditChange(value, obj, parent_obj) {
      if (value) {
        parent_obj.has_permission = true
        obj.has_permission = true
        obj.has_read_permission = true
      }
    },
    
    handleChange(parent_obj, obj) {
      if (obj.has_permission === true) {
        parent_obj.has_permission = true
        this.setValue(obj, true)
      } else {
        this.setValue(obj, false)
      }
    },
    
    handleParentChange(permission_obj) {
      if (permission_obj.has_permission === true) {
        for (const children_obj of permission_obj.children) {
          this.setValue(children_obj, true)
        }
      } else {
        for (const children_obj of permission_obj.children) {
          this.setValue(children_obj, false)
        }
      }
    },
    
    headerRowStyle() {
      return {
        'font-weight': '600',
        'color': '#1a1a1a',
        'background-color': '#f8fafc',
        'border-bottom': '1px solid #e2e8f0',
        'height': '56px'
      }
    },
	
	async handleAutoView() {
	   if (this.$route.query.autoView === 'true') {
	     
	     // 调用查看方法
	     this.viewRole({id: this.$route.query.role_id})
	     
	     // 清除查询参数
	     this.$router.replace({
	       path: this.$route.path,
	       query: {}
	     })
	   }
	},
    
    formatTime(time) {
      if (!time) return '-'
      return new Date(time).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }).replace(/\//g, '-')
    },
    
    search() {
      this.page_size_params.page = 1
      this.getRoles()
    },
    
    reset() {
      for (let key in this.roleSearch) {
        this.roleSearch[key] = ''
      }
    },
    
    editRole(row_data) {
      this.CreateRoleVisible = true
      this.is_add = false
      this.roleTitle = '编辑角色'
      this.role_id = row_data.id
      this.roleView = false
      this.getRole(row_data.id)
    },
    
    viewRole(row_data) {
      this.CreateRoleVisible = true
      this.is_add = false
      this.getRole(row_data.id)
      this.role_id = row_data.id
      this.roleView = true
      this.roleTitle = '查看角色'
    },
    
    addRole() {
      this.roleTitle = '新增角色'
      this.is_add = true
      this.roleView = false
      this.CreateRoleVisible = true
      this.getPermissions()
    },
    
    save() {
      if (this.is_add) {
        this.createRolePermission()
      } else {
        this.updateRolePermission(this.role_id)
      }
    },
    
    async deleteRole(id) {
      ElMessageBox.confirm(
        '确定删除此角色？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteRole(id)
        if (response.status === 204) {
          this.getRoles()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
    async getRoles() {
      const params = Object.assign(this.page_size_params, this.sort_params)
      
      if (this.roleSearch.name) params.name = this.roleSearch.name
      if (this.roleSearch.create_by) params.create_by = this.roleSearch.create_by
      if (this.roleSearch.update_by) params.update_by = this.roleSearch.update_by
      
      try {
        const response = await this.$api.getRoles(params)
        if (response.status === 200) {
          this.roles_list = { ...response.data }
        }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		}
      } catch (error) {
        console.error('获取角色列表失败:', error)
      }
    },
    
    async getRole(id) {
      const response = await this.$api.getRole(id)
      if (response.status === 200) {
        this.permissions = response.data.result.role_permissions
        this.name = response.data.result.name
      }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
	  }
    },
    
    async getPermissions() {
      const response = await this.$api.getPermissions()
      if (response.status === 200) {
        this.permissions = response.data.result
      }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
	  }
    },
    
    async createRolePermission() {
      const response = await this.$api.createRolePermission({ role_name: this.name, items: this.permissions })
      if (response.status === 201) {
        ElMessage({
          type: 'success',
          message: '保存成功',
        })
		this.CreateRoleVisible = false
		this.getRoles()
      }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
	  }
    },
    
    async updateRolePermission(id) {
      const response = await this.$api.updateRolePermission(id, { role_name: this.name, items: this.permissions })
      if (response.status === 201) {
        ElMessage({
          type: 'success',
          message: '保存成功',
        })
		this.CreateRoleVisible = false
		this.getRoles()
      }else if(response.status != 400){
	   	   ElMessage({ message: "系统内部异常", type: 'error' })
	  }
    },
    
    getProjectUsersTooltip(projects) {
      if (!projects || Object.keys(projects).length === 0) {
        return '暂无关联项目'
      }
      let tooltip = ''
      for (const [project, count] of Object.entries(projects)) {
        tooltip += `${project}: ${count}个用户<br>`
      }
      return tooltip
    }
  },
  created() {
    if (!this.userInfo.is_superuser){
        // 重定向到权限页面，并传递from参数
        this.$router.push({name: 'noPermission', query: {from: this.$route.fullPath}})
    } else {
       this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
       this.getRoles()
	   this.handleAutoView()
    }
  }
}
</script>

<style scoped>
.role-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 75px);
  max-height: calc(100vh - 75px);
  height: calc(100vh - 75px);
}

/* 优雅阴影效果 */
.elegant-shadow {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06),
              0 1px 4px rgba(0, 0, 0, 0.08);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.elegant-shadow:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1),
              0 2px 8px rgba(0, 0, 0, 0.12);
}

/* 筛选卡片 */
.filter-card {
  background: white;
  border: none;
  border-radius: 16px;
  overflow: hidden;
  flex-shrink: 0;
}

.filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 24px 10px 24px;
  border-bottom: 1px solid #f1f5f9;
}

.header-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-search {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  position: relative;
}

.icon-search::before {
  content: '';
  position: absolute;
  top: 7px;
  left: 7px;
  width: 8px;
  height: 8px;
  border: 2px solid white;
  border-radius: 50%;
}

.icon-search::after {
  content: '';
  position: absolute;
  top: 15px;
  left: 15px;
  width: 6px;
  height: 2px;
  background: white;
  transform: rotate(45deg);
}

.filter-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  background: linear-gradient(135deg, #1a1a1a 0%, #4a5568 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-action-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reset-btn {
  padding: 10px 20px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reset-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.reset-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.search-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.search-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 20px 20px 0 20px;
}

.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
}

.filter-form {
  margin-bottom: 0;
}

.inline-form {
  margin-bottom: 0;
}

/* 水平布局的表单项 */
/* 关键修改：标签和输入框在一行显示 */
.form-item-inline {
  margin-bottom: 25px;
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 40px;
}

.form-item-inline :deep(.el-form-item__content) {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
  margin-left: 0 !important;
  width: 100%;
}

.label-with-icon {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  width: 90px;
  margin-right: 10px;
  flex-shrink: 0;
  white-space: nowrap;
}

.label-text {
  white-space: nowrap;
}

.icon-user,
.icon-role,
.icon-email,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
}

/* 为图标添加背景颜色 */
.icon-user {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 4px;
}

.icon-creator {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 4px;
}

.icon-updater {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border-radius: 4px;
}


/* 内容卡片 */
.content-card {
  flex: 1;
  background: white;
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.content-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  flex-shrink: 0;
}

.content-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-with-stats {
  display: flex;
  align-items: center;
  gap: 20px;
}

.content-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  position: relative;
  padding-left: 16px;
}

.content-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 2px;
}

.stats-info {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
}

.add-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

.add-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

/* 表格区域 */
.table-wrapper {
  flex: 1;
  padding: 0px;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.elegant-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: transparent;
  border-radius: 12px;
  overflow: hidden;
}

.elegant-table >>> .el-table__header-wrapper th {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  font-weight: 600;
  color: #1a1a1a;
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 0;
}

.elegant-table >>> .el-table__header-wrapper .cell {
  padding: 0 16px;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row {
  transition: all 0.3s ease;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row:nth-child(even) {
  background: #f8fafc;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row:hover {
  background: #f1f8ff;
  transform: translateX(4px);
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row {
  background: #ebf5ff;
  position: relative;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
}

.elegant-table >>> .el-table__body-wrapper td {
  border-bottom: 1px solid #f1f5f9;
  padding: 16px 0;
  transition: all 0.3s ease;
}

.elegant-table >>> .el-table__body-wrapper .cell {
  padding: 0 16px;
}

.index-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  border-radius: 8px;
  font-weight: 600;
  color: #475569;
  margin: 0 auto;
}

.role-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
}

.role-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.role-info {
  text-align: left;
}

.role-name {
  font-weight: 500;
  color: #1a1a1a;
}

.count-tag {
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 20px;
}

.time-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #64748b;
  font-size: 13px;
}

.icon-time {
  width: 14px;
  height: 14px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.action-btn:hover {
  transform: translateY(-2px) scale(1.1);
}

.action-btn:hover::before {
  width: 100%;
  height: 100%;
}

.action-btn.view-btn:hover {
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
}

.action-btn.edit-btn:hover {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.action-btn.delete-btn:hover {
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.action-btn:active {
  transform: translateY(0) scale(0.95);
}

.action-btn.view-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.action-btn.edit-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.action-btn.delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.action-btn .el-icon {
  color: white;
  font-size: 16px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 分页组件样式 */
.pagination-wrapper {
  padding: 20px 24px 0px 24px;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
  float: right;
  display: block !important;
  min-height: 40px;
  background: white;
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
}

.icon-role-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.dialog-input >>> .el-input__inner {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.dialog-input >>> .el-input__inner:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input >>> .el-input__inner:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.elegant-divider {
  margin: 20px 0 !important;
}

.permissions-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.permission-group {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.permission-group:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.permission-header {
  padding: 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.permission-checkbox {
  width: 100%;
}

.permission-name {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.permission-children {
  padding: 0;
}

.permission-child {
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.permission-child:last-child {
  border-bottom: none;
}

.child-header {
  margin-bottom: 12px;
}

.child-checkbox {
  margin-bottom: 8px;
}

.child-name {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.permission-options {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  padding-left: 28px;
}

.option-checkbox {
  font-size: 14px;
  color: #64748b;
}

.dialog-cancel-btn {
  padding: 10px 24px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-cancel-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.dialog-confirm-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .role-management-container {
    padding: 16px;
  }
  
  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-card .content-header,
  .content-card .table-wrapper {
    padding: 16px 20px;
  }
  
  .permission-options {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media screen and (max-width: 768px) {
  .role-management-container {
    padding: 12px;
  }
  
  .filter-card .filter-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-title-section,
  .header-action-section {
    justify-content: center;
  }
  
  .filter-form .el-row .el-col {
    width: 100%;
    margin-bottom: 16px;
  }
  
  /* 在移动端将水平布局改回垂直布局 */
  .form-item-horizontal {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .horizontal-label {
    width: 100%;
    margin-right: 0;
    margin-bottom: 8px;
  }
  
  .content-card .content-header .content-title-section {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .title-with-stats {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .stats-info {
    justify-content: center;
  }
  
  .add-btn {
    width: 100%;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
  
  .elegant-table {
    min-width: 800px;
  }
  
  .pagination-wrapper {
    padding: 15px 20px;
  }
  
  .permission-options {
    grid-template-columns: 1fr;
  }
}

/* 项目关联popover样式 */
.project-count-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.project-count-tag:hover {
  background-color: #ecf5ff;
}

/* 项目关联popover样式 */
.el-popover.project-popover {
  padding: 5px;
}

.el-popover.project-popover .el-table {
  font-size: 13px !important;
  border: 1px solid #e2e8f0 !important;
}

.el-popover.project-popover .el-table th {
  background-color: #f8f9fa !important;
  font-weight: 500 !important;
  font-size: 12px !important;
  color: #67C23A !important;
  border-bottom: 1px solid #e2e8f0 !important;
}

.el-popover.project-popover .el-table td {
  padding: 8px 10px !important;
  font-size: 13px !important;
  color: #303133 !important;
  border-bottom: 1px solid #f0f0f0 !important;
}

.el-popover.project-popover .el-table tr:hover {
  background-color: #f0f9ff !important;
}

.el-popover.project-popover .el-table--border {
  border: 1px solid #e2e8f0 !important;
}

.el-popover.project-popover .el-table--border th,
.el-popover.project-popover .el-table--border td {
  border-right: 1px solid #e2e8f0 !important;
}

.project-empty {
  color: #909399;
  font-size: 14px;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0, 0.2, 1);
}

.content-card {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.elegant-drawer >>> .el-drawer {
  animation: slideInRight 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
</style>