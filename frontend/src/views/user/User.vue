<template>
  <div class="user-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">用户筛选</h3>
          <el-tag size="small" type="info" effect="plain">模糊查询</el-tag>
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
        <el-form :model="userSearch" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-user"></i>
                  <span class="label-text">用户名称</span>
                </div>
                <el-input 
                  v-model="userSearch.username" 
                  placeholder="请输入用户名称" 
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
                  <span class="label-text">创建人</span>
                </div>
                <el-select 
                  v-model="userSearch.create_by" 
                  placeholder="请选择创建人" 
                  clearable 
                  filterable
				  size='large'
                  class="select"
				  popper-class='select-dropdown-rounded'
                >
                  <el-option 
                    v-for="user_obj in search_user_list" 
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
                  <span class="label-text">更新人</span>
                </div>
                <el-select 
                  v-model="userSearch.update_by" 
                  placeholder="请选择更新人" 
                  clearable 
				  size='large'
                  filterable
                  class="select"
				  popper-class='select-dropdown-rounded'
                >
                  <el-option 
                    v-for="user_obj in search_user_list" 
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
            <h3 class="content-title">用户列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ user_list.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ page_size_params.page }}</span>
              </div>
            </div>
          </div>
         <el-button 
           @click="addUser" 
           type="primary" 
           class="add-btn"
         >
           新增用户
         </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table 
          :data="user_list.results" 
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
            label="用户名称" 
            prop="username" 
            min-width="120" 
            align="center"
            class-name="user-column"
          >
            <template #default="scope">
              <div class="user-cell">
                <div class="user-avatar">
                  {{ scope.row.username ? scope.row.username.charAt(0).toUpperCase() : '' }}
                </div>
                <div class="user-info">
                  <span class="username">{{ scope.row.username }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="邮箱" 
            prop="email" 
            min-width="150" 
            align="center"
            class-name="email-column"
          >
            <template #default="scope">
              <div class="email-cell">
                <i class="icon-email-small"></i>
                <span class="email-text">{{ scope.row.email || '-' }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="创建人" 
            prop="create_by_name" 
            width="100" 
            align="center"
            class-name="creator-column"
          />
          
          <el-table-column 
            label="更新人" 
            prop="update_by_name" 
            width="100" 
            align="center"
            class-name="updater-column"
          />
          
          <el-table-column 
            label="最后登录时间" 
            prop="last_login" 
            width="180" 
			sortable="custom"
            align="center"
            class-name="time-column"
          >
            <template #default="scope">
              <div class="time-cell">
                <i class="icon-time"></i>
                <span>{{ formatTime(scope.row.last_login) }}</span>
              </div>
            </template>
          </el-table-column>
          
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
                  content="查看用户" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                        type="success" 
                        class="action-btn view-btn"
                        @click.stop="ViewUser(scope.row)"
                        circle
                  >
                    <el-icon><ViewIcon /></el-icon>
                 </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="编辑用户" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
					type="warning" 
					class="action-btn edit-btn"
					@click.stop="editUser(scope.row)"
					circle
                      >
                    <el-icon><EditPen /></el-icon>
                 </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="删除用户" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
					type="danger" 
					@click.stop="deleteUser(scope.row.id)" 
					class="action-btn delete-btn"
					circle
                      >
                        <el-icon><DeleteIcon /></el-icon>
                    </el-button>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页组件 - 确保始终显示 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page_size_params.page"
          v-model:page-size="page_size_params.size"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="user_list.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
		  popper-class='select-dropdown-rounded'
          :background="true"
        />
      </div>
    </el-card>

    <!-- 用户表单对话框（保持原逻辑） -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="500"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="userSave" 
          label-position="top" 
          label-width="70px" 
		  :rules="userRules"
		  ref='userRef'
          :disabled="readView"
          class="dialog-form"
        >
          <el-form-item  class="dialog-form-item" prop='username'>
            <label class="dialog-label">
              <i class="icon-user-dialog"></i>
              用户名
            </label>
            <el-input 
              v-model="userSave.username" 
              autocomplete="off" 
              placeholder="请输入用户名"
			  maxlength="25"
			  show-word-limit
			  size='large'
              class="input"
            />
          </el-form-item>
          
          <el-form-item  class="dialog-form-item" prop='email'>
            <label class="dialog-label">
              <i class="icon-email-dialog"></i>
              邮箱
            </label>
            <el-input 
              v-model="userSave.email" 
              autocomplete="off" 
			  size='large'
			  maxlength="50"
			  show-word-limit
              placeholder="请输入邮箱"
              class="input"
            />
          </el-form-item>
          
          <el-form-item  class="dialog-form-item" v-if="!readView" prop='password'>
            <label class="dialog-label">
              <i class="icon-password"></i>
              密码
            </label>
            <el-input 
              v-model="userSave.password" 
              autocomplete="off" 
              placeholder="请输入密码" 
              type="password" 
			  size='large'
			  maxlength="25"
			  show-word-limit
              show-password
              class="input"
            />
          </el-form-item>
          
          <el-form-item  class="dialog-form-item" v-if="!readView" prop='password_confirm'>
            <label class="dialog-label">
              <i class="icon-password-confirm"></i>
              确认密码
            </label>
            <el-input 
              v-model="userSave.password_confirm" 
              autocomplete="off" 
              placeholder="请输入确认密码" 
              type="password" 
			  size='large'
			  maxlength="25"
			  show-word-limit
              show-password
              class="input"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
      	<span class="dialog-footer" v-if="!readView">
      		<el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
      		<el-button 
      		  type="primary"
      		  @click="save" 
      		  class="dialog-confirm-btn"
      		>
      		  保存
      		</el-button>
      	</span>
      </template>
      
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  View as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Plus,
  Refresh,
  Search,
  User,
  Edit,
  Delete,
  Message,
  Setting
} from '@element-plus/icons-vue'
export default {
  name: 'UserManagement',
  components: {
      ViewIcon,
      EditIcon,
      DeleteIcon
	},
  computed: {
    ...mapState(['pathPermission', 'userInfo', 'projectInfo']),
    calcMinWidth() {
      let visibleButtons = 3
      return Math.max(10, visibleButtons * 48)
    },
  },
  data() {
    return {
      search_user_list: [],
      readView: false,
      permission: {},
      userSearch: {
        username: '',
        email: '',
        create_by: '',
        update_by: ''
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
      sort_params: {
        ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
      },
      title: '新增用户',
      isAdd: true,
      editDialogVisible: false,
      user_list: {
        count: 0,
        results: []
      },
	  userRules: {
	    username: [{
	      required: true,
	      message: '用户名不能为空',
	      trigger: 'blur',
	    }],
		password: [{
		  required: true,
		  message: '密码不能为空',
		  trigger: 'blur',
		}],
		password_confirm: [{
		  required: true,
		  message: '确认密码不能为空',
		  trigger: 'blur',
		}],
	    email: [{
	      required: true,
	      message: '邮箱不能为空',
	      trigger: 'change',
	    }],
	  },
      ViewVisible: false,
      userSave: {
        id: '',
        username: '',
        email: '',
        password_confirm: '',
        password: '',
		    is_superuser: false,
      },
    }
  },
  methods: {
    handleCurrentChange() {
      this.getUsers()
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
      this.getUsers()
    },
    
    handleSizeChange() {
      this.getUsers()
    },
    
    search() {
      this.getUsers()
    },
    
    reset() {
      for (let key in this.userSearch) {
        this.userSearch[key] = ''
      }
    },
    
    editUser(row_data) {
      this.isAdd = false
      this.title = '编辑用户'
      this.userSave = { ...row_data }
      this.readView = false
      this.userSave.password = ''
      this.editDialogVisible = true
	  this.$refs.userRef.resetFields();
    },
    
    ViewUser(row_data) {
      this.isAdd = false
      this.title = '查看用户'
      this.userSave = { ...row_data }
      this.readView = true
      this.userSave.password = ''
      this.editDialogVisible = true
    },
    
    addUser() {
      this.userSave = {}
      this.title = '新增用户'
      this.readView = false
      this.editDialogVisible = true
      this.isAdd = true
	  this.$refs.userRef.resetFields();
    },
    
    save() {
      if (this.isAdd) {
        this.createUser()
      } else {
        this.updateUser()
      }
    },
    
    async createUser() {
	  this.$refs['userRef'].validate(async (valid, fields)=>{
	    if(valid){
	     const response = await this.$api.createUser(this.userSave)
	     if (response.status === 201) {
	       this.editDialogVisible = false
	       this.getUsers()
	       ElMessage({ message: "保存成功", type: 'success' })
	     }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
	    }
	  })
    },
    
    async updateUser() {
	  this.$refs['userRef'].validate(async (valid, fields)=>{
	    if(valid){
	      const response = await this.$api.updateUser(this.userSave.id, this.userSave)
	      if (response.status === 200) {
	        this.editDialogVisible = false
	        this.getUsers()
	        ElMessage({ message: "保存成功", type: 'success' })
	      }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		 }
	    }
	  })
     
    },
    
    async deleteUser(id) {
      ElMessageBox.confirm(
        '确定删除此用户？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteUser(id)
        if (response.status === 204) {
          this.getUsers()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		}
		
      }).catch(() => {})
    },
    
    async getUsers() {
      const params = Object.assign({}, this.userSearch, this.page_size_params, this.sort_params)
      const response = await this.$api.getUsers(params)
      if (response.status === 200) {
        this.user_list = { ...response.data }
      }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
	  }
    },
    
    handleResize() {
      // 强制更新表格高度
      this.$nextTick(() => {
        // 触发重新计算
        this.$forceUpdate()
      })
    }
  },
  
  created() {
    if (!this.userInfo.is_superuser){
        // 重定向到权限页面，并传递from参数
        this.$router.push({name: 'noPermission', query: {from: this.$route.fullPath}})
    } else {
        this.search_user_list = JSON.parse(localStorage.getItem('user_list')) || []
        this.getUsers()
    }
  },
  
  mounted() {
    // 监听窗口大小变化，重新计算表格高度
    window.addEventListener('resize', this.handleResize)
    
    // 初始计算
    this.$nextTick(() => {
      this.handleResize()
    })
  },
  
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize)
  }
}
</script>

<style scoped>
.user-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  /* 关键：精确计算高度，防止滚动条 */
  height: calc(100vh - 75px); /* 减去顶部菜单高度 */
  min-height: calc(100vh - 75px);
  max-height: calc(100vh - 75px);
  overflow: hidden;
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

.reset-btn i {
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

.search-btn i {
  margin-right: 8px;
  font-size: 16px;
}

.filter-card :deep(.el-card__body) {
  padding: 20px 20px 0 20px;
}

.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
}

.inline-form {
  margin-bottom: 0;
}

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

.icon-role {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 4px;
}

.icon-email {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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
  padding-bottom: 0px;
  max-height: 100%;
  overflow: hidden;
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

.add-btn i {
  margin-right: 8px;
  font-size: 16px;
}

/* 表格区域 */
.table-wrapper {
  flex: 1;
  padding: 0 0px;
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

.elegant-table :deep(.el-table__header-wrapper th) {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  font-weight: 600;
  color: #1a1a1a;
  border-bottom: 1px solid #e2e8f0;
  padding: 16px 0;
}

.elegant-table :deep(.el-table__header-wrapper .cell) {
  padding: 0 16px;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row) {
  transition: all 0.3s ease;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row:nth-child(even)) {
  background: #f8fafc;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row:hover) {
  background: #f1f8ff;
  transform: translateX(4px);
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row.active-row) {
  background: #ebf5ff;
  position: relative;
}

.elegant-table :deep(.el-table__body-wrapper .el-table__row.active-row::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
}

.elegant-table :deep(.el-table__body-wrapper td) {
  border-bottom: 1px solid #f1f5f9;
  padding: 16px 0;
  transition: all 0.3s ease;
}

.elegant-table :deep(.el-table__body-wrapper .cell) {
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

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
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

.user-info {
  text-align: left;
}

.username {
  font-weight: 500;
  color: #1a1a1a;
}

.email-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.icon-email-small {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.email-text {
  color: #475569;
  word-break: break-all;
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

/* .action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  padding: 0;
} */

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

.action-btn i {
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
  float: right;
  flex-shrink: 0;
  display: block !important;
  min-height: 40px;
  background: white;
  z-index: 10;
}


/* 对话框样式 */
.elegant-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog :deep(.el-dialog__header) {
  padding: 24px 24px 0;
  margin: 0;
}

.elegant-dialog :deep(.el-dialog__title) {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 12px;
}

.elegant-dialog :deep(.el-dialog__title::before) {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 2px;
}

.elegant-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.dialog-content {
  padding: 0;
}

.dialog-form {
  margin: 0;
}

.dialog-form-item {
  margin-bottom: 20px;
}

.dialog-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.dialog-input :deep(.el-input__inner),
.dialog-select :deep(.el-input__inner) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.dialog-input :deep(.el-input__inner:hover),
.dialog-select :deep(.el-input__inner:hover) {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input :deep(.el-input__inner:focus),
.dialog-select :deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.dialog-select {
  width: 100%;
}

.elegant-dialog :deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  border-top: 1px solid #f1f5f9;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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
  .user-management-container {
    padding: 16px;
    height: calc(100vh - 60px);
    min-height: calc(100vh - 60px);
    max-height: calc(100vh - 60px);
  }
  
  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-card .content-header,
  .content-card .table-wrapper {
    padding: 16px 20px;
  }
  
  .label-with-icon {
    min-width: 70px;
    font-size: 13px;
  }
}

@media screen and (max-width: 768px) {
  .user-management-container {
    padding: 12px;
    height: auto;
    min-height: calc(100vh - 60px);
    max-height: none;
    overflow-y: auto;
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
  
  .form-item-inline {
    flex-direction: column;
    align-items: flex-start;
    height: auto;
  }
  
  .form-item-inline :deep(.el-form-item__content) {
    flex-direction: column !important;
    align-items: flex-start !important;
  }
  
  .label-with-icon {
    margin-bottom: 8px;
    margin-right: 0;
    min-width: auto;
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
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}



/* 多重选择器确保覆盖 */
.simple-rounded-dropdown,
.simple-rounded-dropdown.el-select-dropdown,
.simple-rounded-dropdown.el-popper,
.el-popper.simple-rounded-dropdown {
  border-radius: 8px !important;
  overflow: hidden !important;
  margin-top: 4px !important;
}

.simple-rounded-dropdown .el-select-dropdown__list,
.simple-rounded-dropdown .el-select-dropdown__wrap,
.simple-rounded-dropdown .el-select-dropdown__wrap .el-select-dropdown__list {
  border-radius: 8px !important;
}

.simple-rounded-dropdown .el-select-dropdown__item,
.simple-rounded-dropdown .el-select-dropdown__list .el-select-dropdown__item {
  height: 40px !important;
  line-height: 40px !important;
  border-radius: 6px !important;
  margin: 2px 8px !important;
}

.simple-rounded-dropdown .el-select-dropdown__item:hover,
.simple-rounded-dropdown .el-select-dropdown__list .el-select-dropdown__item:hover {
  background-color: #f3f4f6 !important;
}

</style>