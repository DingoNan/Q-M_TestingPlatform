<template>
  <div class="project-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">我的项目筛选</h3>
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
        <el-form :model="projectSearch" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-user"></i>
                  <span class="label-text">项目名称</span>
                </div>
                <el-select
                  v-model="projectSearch.name"
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
                	v-model="projectSearch.create_by" 
                	placeholder="请选择创建人" 
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
            <h3 class="content-title">我的项目列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ project_list.count || 0 }}</span>
              </div>
             <!-- <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ project_list.results ? project_list.results.length : 0 }}</span>
              </div> -->
              <div class="stat-item">
                <span class="stat-label">我创建的项目</span>
                <span class="stat-value success">{{ myProjectCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">我加入的项目</span>
                <span class="stat-value info">{{ joinedCount }}</span>
              </div>
            </div>
          </div>
          <el-button 
            @click="addProject" 
            type="primary" 
            class="add-btn"
          >
            <el-icon><Plus /></el-icon>新增项目
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table 
          :data="project_list.results" 
           :max-height="'calc(100vh - 440px)'" 
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
            label="项目信息" 
            min-width="220" 
            align="center"
            class-name="project-info-column"
          >
            <template #default="scope">
              <div class="project-info-cell">
                <div class="project-main-info">
                  <div class="project-name-section">
                    <i class="icon-folder-large"></i>
                    <span class="project-name-text">{{ scope.row.name }}</span>
                  </div>
                  <div class="project-status-section">
                    <el-tag 
                      :type="getProjectTagType(scope.row)"
                      :effect="scope.row.create_by === userInfo.user_id ? 'dark' : 'light'"
                      size="small"
                      class="project-status-tag"
                    >
                      <i :class="getProjectTagIcon(scope.row)"></i>
                      {{ getProjectTagText(scope.row) }}
                    </el-tag>
                  </div>
                </div>
                <div class="project-desc-section" v-if="scope.row.desc">
                  <i class="icon-description-small"></i>
                  <span class="project-desc-text">{{ scope.row.desc }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="项目成员" 
            min-width="180" 
            align="center"
            class-name="members-column"
          >
            <template #default="scope">
              <div class="members-cell">
                <div class="members-header">
                  <i class="icon-team"></i>
                  <span class="members-count">{{ scope.row.user_names ? scope.row.user_names.length : 0 }}人</span>
                </div>
                <div class="members-tags">
                  <el-tag 
                    v-for="item in scope.row.user_names.slice(0, 3)" 
                    :key="item.id"
                    size="small" 
                    effect="plain"
                    class="member-tag"
                  >
                    {{ item.username }}
                  </el-tag>
                  <el-tag 
                    v-if="scope.row.user_names && scope.row.user_names.length > 3"
                    size="small" 
                    type="info"
                    effect="plain"
                  >
                    +{{ scope.row.user_names.length - 3 }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="创建人" 
            prop="create_by_name" 
            min-width="100" 
            align="center"
            class-name="creator-column"
          >
            <template #default="scope">
              <div class="creator-cell">
                <el-tag 
                  v-if="scope.row.create_by === userInfo.user_id"
                  type="success" 
                  size="small"
                  effect="light"
                >
                  我
                </el-tag>
                <span v-else class="creator-name">{{ scope.row.create_by_name }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="更新人" 
            prop="update_by_name" 
            min-width="100" 
            align="center"
            class-name="updater-column"
          >
            <template #default="scope">
              <div class="updater-cell">
                <span class="updater-name">{{ scope.row.update_by_name }}</span>
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
                <div class="time-info">
                  <i class="icon-calendar"></i>
                  <span>{{ formatTime(scope.row.create_time) }}</span>
                </div>
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
                <div class="time-info">
                  <i class="icon-update"></i>
                  <span>{{ formatTime(scope.row.update_time) }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            align="center" 
            width="200" 
            label="操作"
            class-name="action-column"
            fixed="right"
          >
            <template #default="scope">
              <div class="action-buttons">
                <el-tooltip 
                  content="进入项目" 
                  placement="top" 
                  effect="dark"
                  v-if="isInter(scope.row)"
                >
                  <el-button 
                    type="primary" 
                    class="action-btn enter-btn"
                    @click.stop="enterProject(scope.row)"
                    circle
                    
                  >
                    <el-icon><Pointer /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="查看项目" 
                  placement="top" 
                  effect="dark"
                  v-if="isInter(scope.row)"
                >
                  <el-button 
                    type="success" 
                    class="action-btn view-btn"
                    @click.stop="viewProject(scope.row)"
                    circle
                    
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="编辑项目" 
                  placement="top" 
                  effect="dark"
                  v-if="isOwner(scope.row)"
                >
                  <el-button 
                    type="warning" 
                    class="action-btn edit-btn"
                    @click.stop="editProject(scope.row)"
                    circle
                    
                  >
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="删除项目" 
                  placement="top" 
                  effect="dark"
                  v-if="isOwner(scope.row)"
                >
                  <el-button 
                    type="danger" 
                    class="action-btn delete-btn"
                    @click.stop="deleteProject(scope.row.id)"
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
      <!-- <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page_size_params.page"
          v-model:page-size="page_size_params.size"
          :page-sizes="[10, 20, 30, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="project_list.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="elegant-pagination"
          :background="true"
        />
      </div> -->
    </el-card>

    <!-- 项目表单对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="600"
	  class='elegant-dialog'
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="projectSave" 
          ref="projectRef"
          label-position="top" 
		  :rules="projectRules"
          :disabled="projectView"
          class="dialog-form"
        >
          <el-form-item  class="dialog-form-item" prop='name'>
            <label class="dialog-label">
              <i class="icon-project-dialog"></i>
              项目名称
            </label>
            <el-input 
              v-model="projectSave.name" 
              autocomplete="off" 
              placeholder="请输入项目名称"
			  size='large'
			  maxlength="50"
			  show-word-limit
              class="input"
            />
          </el-form-item>
          
          <el-form-item  class="dialog-form-item" prop='desc'>
            <label class="dialog-label">
              <i class="icon-description-dialog"></i>
              项目描述
            </label>
            <el-input 
              v-model="projectSave.desc" 
              autocomplete="off" 
              placeholder="请输入项目描述"
			  maxlength="200"
			  show-word-limit
              type="textarea"
			  size='large'
              class="text"
            />
          </el-form-item>
        
        </el-form>
      </div>
      <template #footer>
      	<span class="dialog-footer" v-if="!projectView">
      		<el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
      		<el-button type="primary" @click="save" class="dialog-confirm-btn">保存</el-button>
      	</span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { mapState, mapMutations } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Search,
  Plus,
  View,
  Delete,
  EditPen,
  Pointer
} from '@element-plus/icons-vue'

export default {
  name: 'ProjectManagement',
  computed: {
    ...mapState(['projectInfo', 'userInfo']),
    myProjectCount() {
      if (!this.project_list.results) return 0
      return this.project_list.results.filter(item => item.create_by === this.userInfo.user_id).length
    },
    joinedCount() {
      if (!this.project_list.results) return 0
      return this.project_list.results.filter(item => 
        item.user.includes(this.userInfo.user_id) && item.create_by !== this.userInfo.user_id
      ).length
    }
  },
  data() {
    return {
      actionWidth: 0,
      projectSearch: {
        user: '',
        name: '',
        desc: '',
		create_by: '',
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
      count: 1,
      title: '新增项目',
      isAdd: true,
      editDialogVisible: false,
      projectView: false,
      project_list: {
        count: 0,
        results: []
      },
      projectSave: {
        id: '',
        name: '',
        desc: '',
        user: [],
        user_names: [],
        create_by: '',
      },
	  projectRules: {
	    name: [{
	      required: true,
	      message: '项目名称不能为空',
	      trigger: 'blur',
	    }],
		desc: [{
		  required: true,
		  message: '项目描述不能为空',
		  trigger: 'blur',
		}],
	    user: [{
	      required: true,
	      message: '请选择项目成员',
	      trigger: 'change',
	    }],
	  },
      user_list: [],
      projectOptions: [],
    }
  },
  components: {
    Refresh,
    Search,
    Plus,
    View,
    Delete,
    EditPen,
    Pointer
  },
  methods: {
    ...mapMutations(['saveRoleId']),
    handleCurrentChange() {
      this.getProjects()
    },
    handleSizeChange() {
      this.page_size_params.size = this.page_size_params.size
      this.page_size_params.page = 1
      this.getProjects()
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

    isInter(row) {
      return row.user.includes(this.userInfo.user_id) || this.userInfo.is_superuser || row.create_by === this.userInfo.user_id
    },
    isOwner(row) {
      return this.userInfo.user_id === row.create_by || this.userInfo.is_superuser
    },
    search() {
      this.page_size_params.page = 1
      this.getProjects()
    },
    reset() {
      for (let key in this.projectSearch) {
        this.projectSearch[key] = ''
      }
    },
    enterProject(project_info) {
      const role_id = project_info.role_id
	  this.saveRoleId(role_id)
      this.$store.commit('saveProjectInfo', project_info)
      this.$router.push({ name: 'index' })
    },
    editProject(row_data) {
      this.isAdd = false
      this.title = '编辑项目'
      this.projectView = false
      this.getProject(row_data.id)
      this.editDialogVisible = true
	  this.$refs.projectRef.resetFields();
    },
    viewProject(row_data) {
      this.isAdd = false
      this.title = '查看项目'
      this.projectView = true
      this.getProject(row_data.id)
      this.editDialogVisible = true
    },
    addProject() {
      this.projectSave = {}
      this.projectView = false
      this.projectSave.create_by = this.userInfo.user_id
      this.title = '新增项目'
      this.editDialogVisible = true
      this.isAdd = true
	    this.$refs.projectRef.resetFields();
    },
    save() {
      if (this.isAdd) {
        this.createProject()
      } else {
        this.updateProject()
      }
    },
    getProjectTagType(row) {
      if (row.create_by === this.userInfo.user_id) return 'success'
      if (row.user.includes(this.userInfo.user_id)) return ''
      return 'info'
    },
    getProjectTagIcon(row) {
      if (row.create_by === this.userInfo.user_id) return 'icon-my-project'
      if (row.user.includes(this.userInfo.user_id)) return 'icon-joined'
      return 'icon-not-joined'
    },
    getProjectTagText(row) {
      if (row.create_by === this.userInfo.user_id) return '我的'
      if (row.user.includes(this.userInfo.user_id)) return '已加入'
      return '未加入'
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
    async createProject() {
	  this.$refs['projectRef'].validate(async (valid, fields)=>{
	    if(valid){
	     const response = await this.$api.createProject(this.projectSave)
	     if (response.status === 201) {
	       this.editDialogVisible = false
	       this.getProjects()
	       ElMessage({ message: "保存成功", type: 'success' })
	     }else{
	  		   ElMessage({ message: "保存失败", type: 'error' })
	  		 }
	    }
	  })
    },
    async updateProject() {
	  this.$refs['projectRef'].validate(async (valid, fields)=>{
	    if(valid){
	     const response = await this.$api.updateProject(this.projectSave.id, this.projectSave)
	       if (response.status === 200) {
	         this.editDialogVisible = false
	         this.getProjects()
	         ElMessage({ message: "保存成功", type: 'success' })
	       }else{
	  		   ElMessage({ message: "保存失败", type: 'error' })
	  		 }
	    }
	  })
    },
    async deleteProject(id) {
      ElMessageBox.confirm(
        '项目删除后不可恢复，确定删除该项目吗?',
        '提示',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteProject(id)
        if (response.status === 204) {
          this.getProjects()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    async getProjects() {
      this.projectSearch.user = this.userInfo.user_id
      const params = {
        ...this.projectSearch,
      }
      try {
        const response = await this.$api.getProjects(params)
        if (response.status === 200) {
          this.project_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取项目列表失败:', error)
      }
    },
    async getProject(id) {
      try {
        const response = await this.$api.getProject(id)
        if (response.status === 200) {
          this.projectSave = response.data.result
        }
      } catch (error) {
        console.error('获取项目详情失败:', error)
      }
    },
    async getUserNames() {
      try {
        const response = await this.$api.getUserNames()
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
    this.getProjects()
    this.getUserNames()
    this.getProjectOptions()
  }
}
</script>

<style scoped>
.project-management-container {
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

/* 输入框样式 */
.input-inline {
  flex: 1;
  margin-left: 12px;
}

.input-inline >>> .el-input__inner {
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
  width: 100%;
}

.input-inline >>> .el-input__inner:hover {
  border-color: #cbd5e1;
  background: white;
}

.input-inline >>> .el-input__inner:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
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

.stat-item .success {
  color: #10b981;
  font-weight: 700;
}

.stat-item .info {
  color: #3b82f6;
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

/* 项目信息单元格 */
.project-info-cell {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px 0;
}

.project-main-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.project-name-section {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.icon-folder-large {
  width: 20px;
  height: 20px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.project-name-text {
  font-weight: 600;
  color: #1a1a1a;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.project-status-section {
  flex-shrink: 0;
}

.project-status-tag {
  padding: 4px 10px;
  font-size: 12px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.icon-my-project,
.icon-joined,
.icon-not-joined {
  width: 12px;
  height: 12px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-my-project {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-joined {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E");
}

.icon-not-joined {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z'/%3E%3C/svg%3E");
}

.project-desc-section {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #f8fafc;
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
}

.icon-description-small {
  width: 14px;
  height: 14px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  margin-top: 2px;
  flex-shrink: 0;
}

.project-desc-text {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 项目成员单元格 */
.members-cell {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px 0;
}

.members-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.icon-team {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.members-count {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.members-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
}

.member-tag {
  padding: 3px 8px;
  font-size: 11px;
}

/* 创建人和更新人单元格 */
.creator-cell,
.updater-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
}

.creator-name,
.updater-name {
  font-weight: 500;
  color: #475569;
}

/* 时间单元格 */
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
  justify-content: center;
}

.icon-calendar,
.icon-update {
  width: 14px;
  height: 14px;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-calendar {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7z'/%3E%3C/svg%3E");
}

.icon-update {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M21 10.12h-6.78l2.74-2.82c-2.73-2.7-7.15-2.8-9.88-.1-2.73 2.71-2.73 7.08 0 9.79s7.15 2.71 9.88 0C18.32 15.65 19 14.08 19 12.1h2c0 1.98-.88 4.55-2.64 6.29-3.51 3.48-9.21 3.48-12.72 0-3.5-3.47-3.53-9.11-.02-12.58s9.14-3.47 12.65 0L21 3v7.12zM12.5 8v4.25l3.5 2.08-.72 1.21L11 13V8h1.5z'/%3E%3C/svg%3E");
}

/* 操作按钮 */
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

.action-btn.enter-btn:hover {
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
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

.action-btn.enter-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
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
  padding: 20px 24px;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
  display: block !important;
  min-height: 60px;
  background: white;
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
}

.elegant-pagination {
  display: flex;
  justify-content: flex-end;
  visibility: visible !important;
  opacity: 1 !important;
}

.elegant-pagination >>> .el-pagination {
  display: flex;
  align-items: center;
}

.elegant-pagination >>> .el-pagination__total {
  color: #64748b;
  font-weight: 500;
  margin-right: 20px;
}

.elegant-pagination >>> .el-pagination__sizes {
  margin-right: 20px;
}

.elegant-pagination >>> .el-pagination__sizes .el-input .el-input__inner {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  box-shadow: none;
  height: 32px;
  line-height: 32px;
}

.elegant-pagination >>> .el-pagination__sizes .el-input .el-input__inner:hover {
  border-color: #cbd5e1;
}

.elegant-pagination >>> .el-pager li {
  border-radius: 8px;
  margin: 0 4px;
  border: 1px solid transparent;
  transition: all 0.3s ease;
  font-weight: 500;
  min-width: 36px;
  height: 36px;
  line-height: 36px;
}

.elegant-pagination >>> .el-pager li:not(.disabled):hover {
  color: #3b82f6;
  border-color: #3b82f6;
  background: white;
}

.elegant-pagination >>> .el-pager li.active {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border-color: transparent;
}

.elegant-pagination >>> .btn-prev,
.elegant-pagination >>> .btn-next {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  transition: all 0.3s ease;
  min-width: 36px;
  height: 36px;
  line-height: 36px;
}

.elegant-pagination >>> .btn-prev:hover:not(.disabled),
.elegant-pagination >>> .btn-next:hover:not(.disabled) {
  border-color: #3b82f6;
  color: #3b82f6;
}

.elegant-pagination >>> .el-pagination__jump {
  margin-left: 20px;
}

.elegant-pagination >>> .el-pagination__jump .el-input .el-input__inner {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  box-shadow: none;
  height: 32px;
  line-height: 32px;
}

.elegant-pagination >>> .el-pagination__jump .el-input .el-input__inner:hover {
  border-color: #cbd5e1;
}

/* 对话框样式 */

.dialog-label {
  display: flex;
  align-items: center;
  gap: 8px;
  
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.icon-project-dialog,
.icon-description-dialog,
.icon-notification,
.icon-url,
.icon-team-dialog,
.icon-creator-dialog {
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-project-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
}

.icon-description-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-notification {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M18 8c0-3.31-2.69-6-6-6S6 4.69 6 8c0 4.5 6 11 6 11s6-6.5 6-11zm-8 0c0-1.1.9-2 2-2s2 .9 2 2-.89 2-2 2c-1.1 0-2-.9-2-2zM4 20v-2h16v2H4z'/%3E%3C/svg%3E");
}

.icon-url {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
}

.icon-team-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z'/%3E%3C/svg%3E");
}

.icon-creator-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

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
  .project-management-container {
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
  .project-management-container {
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
  
  .add-btn {
    width: 100%;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
  
  .elegant-table {
    min-width: 900px;
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
  
  /* 对话框响应式调整 */
  .elegant-dialog >>> .el-dialog {
    width: 95% !important;
    max-width: 500px;
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