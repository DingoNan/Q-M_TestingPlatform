<template>
  <div class="appeal-my-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">我申请的项目查询</h3>
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
                  <span class="label-text">项目创建人</span>
                </div>
				<el-select
					v-model="appealSearch.project_create_by" 
					placeholder="请选择项目创建人" 
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
            <h3 class="content-title">我申请的项目列表</h3>
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
              <div class="stat-item">
                <span class="stat-label">已加入</span>
                <span class="stat-value success">{{ joinedCount }}</span>
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
            min-width="200" 
            align="center"
            class-name="project-column"
          >
            <template #default="scope">
              <div class="project-cell">
                <div class="project-info">
                  <div class="project-name-row">
                    <i class="icon-folder"></i>
                    <span class="project-text">{{ scope.row.project_name }}</span>
                  </div>
                  <div class="project-status-row">
                    <el-tag 
                      :type="scope.row.status === true ? 'success' : 'info'"
                      size="small" 
                      effect="light"
                      class="project-status-tag"
                    >
                      <i :class="scope.row.status === true ? 'icon-check-circle' : 'icon-clock'"></i>
                      {{ scope.row.status === true ? '已加入' : '未加入' }}
                    </el-tag>
                  </div>
                </div>
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
                <el-tag 
                  size="small" 
                  effect="plain"
                  class="creator-tag"
                >
                  <i class="icon-applicant"></i>
                  {{ scope.row.project_create_by }}
                </el-tag>
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
                <div class="applicant-info">
                  <i class="icon-applicant"></i>
                  <span class="applicant-name">{{ scope.row.create_by_name }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="申请状态" 
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
            label="申请时间" 
            prop="create_time" 
            sortable 
            width="160" 
            align="center"
            class-name="time-column"
          >
            <template #default="scope">
              <div class="time-cell">
                <div class="time-info">
                  <i class="icon-clock"></i>
                  <div class="time-details">
                    <div class="time-label">申请</div>
                    <div class="time-value">{{ formatTime(scope.row.create_time) }}</div>
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="加入时间" 
            prop="update_time" 
            sortable 
            width="160" 
            align="center"
            class-name="time-column"
          >
            <template #default="scope">
              <div class="time-cell">
                <div class="time-info">
                  <i class="icon-calendar"></i>
                  <div class="time-details">
                    <div class="time-label">加入</div>
                    <div class="time-value">{{ scope.row.status ? formatTime(scope.row.update_time) : '-' }}</div>
                  </div>
                </div>
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
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { 
  Refresh, 
  Search,
  View,
  Delete,
  EditPen
} from '@element-plus/icons-vue'

export default {
  name: 'AppealMyManagement',
  computed: {
    ...mapState(['projectInfo', 'userInfo']),
    pendingCount() {
      if (!this.appeal_list.results) return 0
      return this.appeal_list.results.filter(item => !item.status).length
    },
    joinedCount() {
      if (!this.appeal_list.results) return 0
      return this.appeal_list.results.filter(item => item.status === true).length
    }
  },
  data() {
    return {
      appealSearch: {
        project_name: '',
        project_create_by: '',
        user: ''
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
      user_list: [],
      projectOptions: [],
    }
  },
  components: {
    Refresh,
    Search,
    View,
    Delete,
    EditPen
  },
  methods: {
    handleCurrentChange() {
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

    handleSizeChange() {
      this.page_size_params.size = this.page_size_params.size
      this.page_size_params.page = 1
      this.getProjectAppeals()
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
      this.appealSearch.user = this.userInfo.user_id
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
        console.error('获取我的申请列表失败:', error)
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
.appeal-my-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: calc(100vh - 75px);
  height: calc(100vh - 75px);
  max-height: calc(100vh - 75px);
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

.stat-item .success {
  color: #10b981;
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

.project-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.project-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
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
  font-weight: 600;
  color: #334155;
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-status-tag {
  padding: 4px 8px;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.icon-check-circle,
.icon-clock {
  width: 12px;
  height: 12px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-check-circle {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E");
}

.icon-clock {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
}

.creator-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.creator-tag {
  padding: 6px 10px;
  border-radius: 12px;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}


.applicant-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.applicant-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.icon-applicant {
  width: 14px;
  height: 14px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.applicant-name {
  font-weight: 500;
  color: #475569;
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
}

.time-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  min-width: 120px;
}

.time-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-label {
  font-size: 10px;
  color: #94a3b8;
  font-weight: 500;
}

.time-value {
  font-size: 12px;
  color: #475569;
  font-weight: 500;
}

.icon-clock,
.icon-calendar {
  width: 14px;
  height: 14px;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-calendar {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E");
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
  .appeal-my-management-container {
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
  .appeal-my-management-container {
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
    flex-wrap: wrap;
  }
  
  .stat-item {
    flex: 1;
    min-width: 120px;
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
  
  /* 表格内容响应式调整 */
  .project-info,
  .time-info,
  .applicant-info {
    min-width: 100px;
  }
  
  .time-details {
    min-width: 80px;
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