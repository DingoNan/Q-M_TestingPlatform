<template>
  <div class="appeal-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">我的项目申请查询</h3>
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
        <el-form :model="appealSearch" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-user"></i>
                  <span class="label-text">项目名称</span>
                </div>
                <el-select
                  v-model="appealSearch.project_name"
                  placeholder="请选择项目名称"
                  clearable
                  filterable
                  size='large'
                  class="select"
                  popper-class='select-dropdown-rounded'
                >
                  <el-option
                    v-for="p in projectOptions"
                    :key="p.id"
                    :label="p.name"
                    :value="p.name"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-creator"></i>
                  <span class="label-text">申请人</span>
                </div>
				<el-select
					v-model="appealSearch.user" 
					placeholder="请选择申请人" 
					clearable 
					filterable
					size='large'
					class="select"
					popper-class='select-dropdown-rounded'
				>
					<el-option 
						v-for="user_obj in user_list" 
						:label='user_obj.username' 
						:value="user_obj.id"
						:key="user_obj.id"
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
            <h3 class="content-title">我的项目申请列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ appeal_list.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ appeal_list.results ? appeal_list.results.length : 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">待审批</span>
                <span class="stat-value warning">{{ pendingCount }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table 
          :data="appeal_list.results" 
          :max-height="'calc(100vh - 485px)'" 
          class="elegant-table"
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
            label="项目名称" 
            prop="project_name" 
            min-width="180" 
            align="center"
            class-name="project-column"
          >
            <template #default="scope">
              <div class="project-cell">
                <el-tooltip 
                  :content="scope.row.project_name" 
                  placement="top" 
                  effect="dark"
                >
                  <div class="project-name">
                    <i class="icon-folder"></i>
                    <span class="project-text">{{ scope.row.project_name }}</span>
                  </div>
                </el-tooltip>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="项目创建人" 
            prop="project_create_by" 
            min-width="120" 
            align="center"
            class-name="creator-column"
          >
            <template #default="scope">
              <div class="creator-cell">
                <i class="icon-applicant-small"></i>
                <span>{{ scope.row.project_create_by }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="申请人" 
            prop="create_by_name" 
            min-width="120" 
            align="center"
            class-name="applicant-column"
          >
            <template #default="scope">
              <div class="applicant-cell">
                <el-tag 
                  size="small" 
                  effect="plain"
                  class="applicant-tag"
                >
                  <i class="icon-applicant-small"></i>
                  {{ scope.row.create_by_name }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="状态" 
            prop="status" 
            min-width="100" 
            align="center"
            class-name="status-column"
          >
            <template #default="scope">
              <div class="status-cell">
                <el-tag 
                  :type="scope.row.status ? 'success' : 'warning'"
                  :effect="scope.row.status ? 'light' : 'dark'"
                  class="status-tag"
                  round
                >
                  <i :class="scope.row.status ? 'icon-check' : 'icon-pending'"></i>
                  {{ scope.row.status ? '已同意' : '待审批' }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="创建时间" 
            prop="create_time" 
            sortable 
            width="160" 
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
            sortable 
            width="160" 
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
            width="80" 
            label="操作"
            class-name="action-column"
            fixed="right"
          >
            <template #default="scope">
              <div class="action-buttons">
                <el-tooltip 
                  content="同意申请" 
                  placement="top" 
                  effect="dark"
                  v-if="!scope.row.status"
                >
                  <el-button 
                    type="success" 
                    class="action-btn approve-btn"
                    @click.stop="approved(scope.row)"
                    circle
                    size="small"
                  >
                    <el-icon><Check /></el-icon>
                  </el-button>
                </el-tooltip>
                <span v-else class="action-placeholder">-</span>
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
          :total="appeal_list.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
          :background="true"
        />
      </div>
    </el-card>

    <!-- 角色选择弹窗 -->
    <el-dialog
      v-model="roleDialogVisible"
      :title="'为用户 ' + selectedUser + ' 选择角色'"
      width="450px"
      class="role-dialog"
    >
      <el-form :model="roleForm" label-width="80px">
        <el-form-item label="选择角色">
          <el-select
            v-model="roleForm.role_id"
            placeholder="请选择角色"
            class="select"
            popper-class='select-dropdown-rounded'
            size="large"
          >
            <el-option
              v-for="role in roleList"
              :label="role.name"
              :value="role.id"
              :key="role.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="roleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRoleSelection">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { ElMessage } from 'element-plus'
import { 
  Refresh, 
  Search, 
  Check,
  Message 
} from '@element-plus/icons-vue'

export default {
  name: 'AppealManagement',
  computed: {
    ...mapState(['userInfo', 'projectInfo']),
    pendingCount() {
      if (!this.appeal_list.results) return 0
      return this.appeal_list.results.filter(item => !item.status).length
    }
  },
  data() {
    return {
      appealSearch: {
        project_name: '',
        user: '',
        project_create_by_id: ''
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
      count: 1,
      title: '新增用户',
      isAdd: true,
      editDialogVisible: false,
      appeal_list: {
        count: 0,
        results: []
      },
      ViewVisible: false,
      AppealSave: {
        id: '',
        status: '',
        project: '',
        user: '',
      },
      user_list: [],
      projectOptions: [],
      // 角色选择弹窗相关
      roleDialogVisible: false,
      selectedUser: '',
      selectedAppeal: null,
      roleForm: {
        role_id: ''
      },
      roleList: []
    }
  },
  components: {
    Refresh,
    Search,
    Check,
    Message
  },
  methods: {
    handleCurrentChange() {
      this.getProjectAppeals()
    },
    handleSizeChange() {
      this.page_size_params.size = this.page_size_params.size
      this.page_size_params.page = 1
      this.getProjectAppeals()
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

    search() {
      this.page_size_params.page = 1
      this.getProjectAppeals()
    },
    reset() {
      for (let key in this.appealSearch) {
        this.appealSearch[key] = ''
      }
    },
    approved(row_data) {
      // 打开角色选择弹窗
      this.selectedAppeal = row_data
      this.selectedUser = row_data.create_by_name
      this.roleForm.role_id = ''
      this.getRoles()
      this.roleDialogVisible = true
    },
    async getRoles() {
      try {
        const response = await this.$api.getRoles()
        if (response.status === 200) {
          this.roleList = response.data.results
        }
      } catch (error) {
        console.error('获取角色列表失败:', error)
      }
    },
    async confirmRoleSelection() {
      if (!this.roleForm.role_id) {
        ElMessage.warning('请选择角色')
        return
      }
      
      // 构建参数，包含角色信息
      this.AppealSave.project = this.selectedAppeal.project
      this.AppealSave.user = this.selectedAppeal.user
      this.AppealSave.status = true
      this.AppealSave.role_id = this.roleForm.role_id
      
      await this.updaterojectAppeal(this.selectedAppeal.id, this.AppealSave)
      this.roleDialogVisible = false
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
    async getProjectAppeals() {
      this.appealSearch.project_create_by_id = this.userInfo.user_id
      const params = {
        ...this.appealSearch,
        ...this.page_size_params
      }
      try {
        const response = await this.$api.getProjectAppeals(params)
        if (response.status === 200) {
          this.appeal_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取申请列表失败:', error)
      }
    },
    async updaterojectAppeal(id, params) {
      try {
        const response = await this.$api.updateProjectAppeal(id, params)
        if (response.status === 200) {
          this.getProjectAppeals()
          ElMessage({
            message: '申请已同意',
            type: 'success'
          })
        }
      } catch (error) {
        console.error('更新申请失败:', error)
      }
    },
	async getUsers() {
	  try {
	    const response = await this.$api.getUsers()
	    if (response.status === 200) {
	      this.user_list = response.data.results
	      localStorage.setItem('user_list', JSON.stringify(this.user_list))
	    }
	  } catch (error) {
	    console.error('获取用户列表失败:', error)
	  }
	},
	async getProjectOptions() {
	  try {
	    const response = await this.$api.getProjects({ size: 1000 })
	    if (response.status === 200) {
	      this.projectOptions = response.data.results || []
	    }
	  } catch (error) {
	    console.error('获取项目列表失败:', error)
	  }
	}
  },
  created() {
    this.getProjectAppeals()
	this.getUsers()
	this.getProjectOptions()
  }
}
</script>

<style scoped>
.appeal-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 80px);
  height: calc(100vh - 80px);
  max-height: calc(100vh - 80px);
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

.inline-form {
  margin-bottom: 0;
}

/* 内联表单样式 */
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

.stat-item .warning {
  color: #f59e0b;
  font-weight: 700;
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

.project-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.project-name {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
  max-width: 200px;
  overflow: hidden;
}

.project-name:hover {
  background: #f1f5f9;
  transform: translateY(-1px);
}

.icon-folder {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.project-text {
  font-weight: 500;
  color: #334155;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.creator-cell,
.applicant-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #475569;
  font-weight: 500;
}


.applicant-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.icon-applicant-small {
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  display: inline-block;
  margin-right: 4px;
}

.status-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-tag {
  padding: 6px 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.status-tag i {
  width: 12px;
  height: 12px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-check {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E");
}

.icon-pending {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
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

.action-btn.approve-btn:hover {
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
}

.action-btn:active {
  transform: translateY(0) scale(0.95);
}

.action-btn.approve-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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

.action-placeholder {
  color: #94a3b8;
  font-size: 14px;
}

/* 分页组件样式 */
.pagination-wrapper {
  padding: 20px 24px 0px 24px;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
  display: block !important;
  float: right;
  min-height: 40px;
  background: white;
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
}



/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .appeal-management-container {
    padding: 16px;
  }
  
  .filter-card .filter-header,
  .filter-card .filter-form-wrapper,
  .content-card .content-header,
  .content-card .table-wrapper {
    padding: 16px 20px;
  }
}

@media screen and (max-width: 768px) {
  .appeal-management-container {
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
  
  .table-wrapper {
    overflow-x: auto;
  }
  
  .elegant-table {
    min-width: 800px;
  }
  
  .pagination-wrapper {
    padding: 15px 20px;
  }
  
  /* 响应式调整内联表单 */
  .inline-form-item {
    height: auto;
    flex-wrap: wrap;
    margin-bottom: 16px;
  }
  
  .inline-label-wrapper {
    min-width: 80px;
    margin-bottom: 8px;
  }
  
  .input-inline {
    margin-left: 0;
    margin-top: 4px;
    width: 100%;
  }
  
  .input-inline >>> .el-input__inner {
    margin-left: 0;
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

.content-card {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}
</style>