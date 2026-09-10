<template>
  <div class="project-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">项目列表筛选</h3>
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
					size='large'
                	filterable
					popper-class='select-dropdown-rounded'
                	class="select"
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
            <h3 class="content-title">项目列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ project_list.count || 0 }}</span>
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
            label="项目名称" 
            min-width="180" 
            align="center"
            class-name="project-column"
          >
            <template #default="scope">
              <div class="project-cell">
                <div class="project-name-section">
                  <span class="project-name-text">{{ scope.row.name }}</span>
                  <div class="project-tags">
                    <el-tag 
                      v-if="scope.row.create_by === userInfo.user_id" 
                      effect="dark" 
                      round 
                      size="small"
                      class="tag-badge my-tag"
                    >
                      我的
                    </el-tag>
                    <el-tag 
                      v-else-if="scope.row.user.includes(userInfo.user_id)" 
                      effect="dark" 
                      round 
                      size="small" 
                      type="success"
                      class="tag-badge joined-tag"
                    >
                      已加入
                    </el-tag>
                    <el-tag 
                      v-else-if="scope.row.has_appeal === false" 
                      effect="dark" 
                      round 
                      size="small" 
                      type="warning"
                      class="tag-badge applied-tag"
                    >
                      已申请
                    </el-tag>
                    <el-tag 
                      v-else 
                      effect="dark" 
                      round 
                      size="small" 
                      type="info"
                      class="tag-badge not-joined-tag"
                    >
                      未加入
                    </el-tag>
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="项目描述" 
            prop="desc" 
            min-width="200" 
            align="center"
            class-name="desc-column"
          >
            <template #default="scope">
              <div class="desc-cell">
                {{ scope.row.desc || '-' }}
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
            width="120" 
            align="center"
            class-name="creator-column"
          />
          
          <el-table-column 
            label="更新人" 
            prop="update_by_name" 
            width="120" 
            align="center"
            class-name="updater-column"
          />
          
          <el-table-column 
            label="创建时间" 
            prop="create_time" 
            sortable 
            width="170" 
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
            width="170" 
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
			width='220'
            label="操作"
            class-name="action-column"
            fixed="right"
          >
            <template #default="scope">
              <div class="action-buttons">
                <el-tooltip 
                  content="申请加入" 
                  placement="top" 
                  effect="dark"
                  v-if="(!scope.row.user.includes(userInfo.user_id)  && scope.row.has_appeal !== false) && userInfo.user_id !== scope.row.create_by && !userInfo.is_superuser"
                >
                  <el-button 
                    type="primary"
                    class="action-btn join-btn"
                    @click.stop="joinProject(scope.row)"
                    circle
                  >
                    <el-icon><Message /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="进入项目" 
                  placement="top" 
                  effect="dark"
                  v-if="scope.row.user.includes(userInfo.user_id) || userInfo.user_id === scope.row.create_by || userInfo.is_superuser"
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
                  v-if="scope.row.user.includes(userInfo.user_id) || userInfo.user_id === scope.row.create_by || userInfo.is_superuser"
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
                  v-if="userInfo.user_id === scope.row.create_by || userInfo.is_superuser"
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
                  v-if="userInfo.user_id === scope.row.create_by || userInfo.is_superuser"
                >
                  <el-button 
                    type="danger" 
                    @click.stop="deleteProject(scope.row.id)" 
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
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="projectSave" 
		  :rules="projectRules"
          ref="projectRef"
          label-position="top" 
          :disabled="projectView"
          class="dialog-form"
        >
          <el-form-item  prop="name" class="dialog-form-item" >
            <label class="dialog-label">
              <i class="icon-project-dialog"></i>
              项目名称
            </label>
            <el-input 
              v-model="projectSave.name" 
              autocomplete="off" 
              placeholder="请输入项目名称"
              class="input"
			  size='large'
              :maxlength="50"
              show-word-limit
            />
          </el-form-item>
          
          <el-form-item prop="desc" class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-desc-dialog"></i>
              项目描述
            </label>
            <el-input 
              v-model="projectSave.desc" 
              autocomplete="off" 
              placeholder="请输入项目描述" 
              type="textarea"
              :rows="2"
              class="text"
              :maxlength="200"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
      	<span class="dialog-footer" v-if="!projectView">
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
import { mapState, mapActions, mapMutations } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Search,
  Plus,
  View,
  Delete,
  EditPen,
  Message,
  Pointer
} from '@element-plus/icons-vue'

export default {
  name: 'ProjectManagement',
  computed: {
    ...mapState(['projectInfo', 'userInfo']),
    calcMinWidth() {
      let visibleButtons = 0
      if (this.project_list.results && this.project_list.results.length > 0) {
        const row = this.project_list.results[0]
        if (row.has_appeal === '未申请' && this.userInfo.user_id !== row.create_by) visibleButtons += 1
        if (row.user.includes(this.userInfo.user_id)) visibleButtons += 2
        if (this.userInfo.user_id === row.create_by) visibleButtons += 2
      }
      return Math.max(10, visibleButtons * 100)
    }
  },
  data() {
    return {
      projectView: false,
      projectSearch: {
        name: '',
        desc: ''
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
      title: '新增项目',
      isAdd: true,
      editDialogVisible: false,
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
    Message,
    Pointer
  },
  methods: {
    ...mapActions(['getRolePermission']),
    ...mapMutations(['saveRoleId']),
    handleCurrentChange(page) {
      this.page_size_params.page = page
      this.getProjects()
    },
    
    headerRowStyle() {
      return {
        'font-weight': '600',
        'color': 'var(--qm-text-1)',
        'background-color': 'var(--qm-bg-1)',
        'border-bottom': '1px solid var(--qm-line-strong)',
        'height': '56px'
      }
    },
    
    handleSizeChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getProjects()
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
      this.getProjects()
    },
    
    reset() {
      for (let key in this.projectSearch) {
        this.projectSearch[key] = ''
      }
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
      this.projectView = true
      this.title = '查看项目'
      this.getProject(row_data.id)
      this.editDialogVisible = true
    },
    
    async joinProject(row_data) {
      try {
        const response = await this.$api.createProjectAppeal({ 
          project: row_data.id, 
          user: this.userInfo.user_id 
        })
        if (response.status === 201) {
          this.editDialogVisible = false
          this.getProjects()
          ElMessage({
            message: "申请已发送",
            type: 'success'
          })
        }
      } catch (error) {
        console.error('申请加入失败:', error)
      }
    },
    
    enterProject(project_info) {
      const role_id = project_info.role_id
      this.saveRoleId(role_id)
      this.$store.commit('saveProjectInfo', project_info)
      this.$store.commit('addTags', { path: '/project/index', name: '项目首页' })
      this.$router.push({ name: 'index' })
    },
    
    addProject() {
      this.projectSave.create_by = this.userInfo.user_id
      this.projectView = false
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
        '项目删除后不可恢复，确定删除该项目吗？',
        '确认删除',
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
      try {
        const params = {
          ...this.projectSearch,
        }
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
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
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
  background: var(--qm-bg-2);
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
  border-bottom: 1px solid var(--qm-bg-3);
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
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
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
  background: var(--qm-bg-2);
  transform: rotate(45deg);
}

.filter-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--qm-text-1);
  background: linear-gradient(135deg, var(--qm-text-1) 0%, var(--qm-text-2) 100%);
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
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.reset-btn:hover {
  background: var(--qm-bg-1);
  border-color: var(--qm-line-strong);
  transform: translateY(-1px);
}

.reset-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.search-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
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
  color: var(--qm-text-2);
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
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 4px;
}

.icon-role {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
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
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border-radius: 4px;
}

/* 内容卡片 */
.content-card {
  flex: 1;
  background: var(--qm-bg-2);
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.content-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--qm-bg-3);
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
  color: var(--qm-text-1);
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
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
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
  background: var(--qm-bg-1);
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
}

.stat-label {
  font-size: 12px;
  color: var(--qm-text-2);
  font-weight: 500;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-1);
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
  background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  font-weight: 600;
  color: var(--qm-text-1);
  border-bottom: 1px solid var(--qm-line-strong);
  padding: 16px 0;
}

.elegant-table >>> .el-table__header-wrapper .cell {
  padding: 0 16px;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row {
  transition: all 0.3s ease;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row:nth-child(even) {
  background: var(--qm-bg-1);
}

.elegant-table >>> .el-table__body-wrapper .el-table__row:hover {
  background: var(--qm-warning-soft);
  transform: translateX(4px);
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row {
  background: var(--qm-warning-soft);
  position: relative;
}

.elegant-table >>> .el-table__body-wrapper .el-table__row.active-row::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
}

.elegant-table >>> .el-table__body-wrapper td {
  border-bottom: 1px solid var(--qm-bg-3);
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
  background: linear-gradient(135deg, var(--qm-bg-3) 0%, var(--qm-line-strong) 100%);
  border-radius: 8px;
  font-weight: 600;
  color: var(--qm-text-2);
  margin: 0 auto;
}

.project-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.project-name-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.project-name-text {
  font-weight: 600;
  color: var(--qm-text-1);
}

.project-tags {
  display: flex;
  gap: 4px;
}

.tag-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 12px;
  transition: all 0.3s ease;
}

.tag-badge:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.my-tag {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
}

.joined-tag {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
}

.applied-tag {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
}

.not-joined-tag {
  background: linear-gradient(135deg, var(--qm-text-3) 0%, var(--qm-text-2) 100%);
  border: none;
}

.desc-cell {
  color: var(--qm-text-2);
  font-size: 14px;
  line-height: 1.5;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.members-cell {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 10px 0;
}

.member-tag {
  padding: 3px 8px;
  font-size: 11px;
}

.members-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
}

.members-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.member-tag:hover {
  background: var(--qm-bg-3);
  transform: translateY(-1px);
}

.time-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--qm-text-2);
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

.action-btn.join-btn:hover {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.action-btn.enter-btn:hover {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
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

.action-btn.join-btn,
.action-btn.enter-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.action-btn.view-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.action-btn.edit-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
}

.action-btn.delete-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
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
  border-top: 1px solid var(--qm-bg-3);
  flex-shrink: 0;
  display: block !important;
  min-height: 60px;
  background: var(--qm-bg-2);
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
  color: var(--qm-text-2);
  font-weight: 500;
  margin-right: 20px;
}

.elegant-pagination >>> .el-pagination__sizes {
  margin-right: 20px;
}

.elegant-pagination >>> .el-pagination__sizes .el-input .el-input__inner {
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  box-shadow: none;
  height: 32px;
  line-height: 32px;
}

.elegant-pagination >>> .el-pagination__sizes .el-input .el-input__inner:hover {
  border-color: var(--qm-line-strong);
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
  color: #f59e0b;
  border-color: #f59e0b;
  background: var(--qm-bg-2);
}

.elegant-pagination >>> .el-pager li.active {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
  border-color: transparent;
}

.elegant-pagination >>> .btn-prev,
.elegant-pagination >>> .btn-next {
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  transition: all 0.3s ease;
  min-width: 36px;
  height: 36px;
  line-height: 36px;
}

.elegant-pagination >>> .btn-prev:hover:not(.disabled),
.elegant-pagination >>> .btn-next:hover:not(.disabled) {
  border-color: #f59e0b;
  color: #f59e0b;
}

.elegant-pagination >>> .el-pagination__jump {
  margin-left: 20px;
}

.elegant-pagination >>> .el-pagination__jump .el-input .el-input__inner {
  border-radius: 8px;
  border: 1px solid var(--qm-line-strong);
  box-shadow: none;
  height: 32px;
  line-height: 32px;
}

.elegant-pagination >>> .el-pagination__jump .el-input .el-input__inner:hover {
  border-color: var(--qm-line-strong);
}

/* 对话框样式 */

.dialog-label {
  display: flex;
  align-items: center;
  gap: 8px;
  
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-2);
}

.icon-project-dialog,
.icon-desc-dialog,
.icon-notification-dialog,
.icon-url-dialog,
.icon-users-dialog,
.icon-creator-dialog {
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-project-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z'/%3E%3Cpath fill='%2394a3b8' d='M7 12h10v2H7zm0-4h10v2H7z'/%3E%3C/svg%3E");
}

.icon-desc-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-notification-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.07-1.63-5.64-4.5-6.32V4c0-.83-.67-1.5-1.5-1.5s-1.5.67-1.5 1.5v.68C7.64 5.36 6 7.92 6 11v5l-2 2v1h16v-1l-2-2z'/%3E%3C/svg%3E");
}

.icon-url-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
}

.icon-users-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z'/%3E%3C/svg%3E");
}

.icon-creator-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
}

.dialog-input >>> .el-input__inner,
.dialog-textarea >>> .el-textarea__inner,
.dialog-select >>> .el-input__inner {
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  width: 100%;
}

.dialog-textarea >>> .el-textarea__inner {
  padding: 12px 16px;
  resize: vertical;
  min-height: 80px;
}

.dialog-input >>> .el-input__inner:hover,
.dialog-textarea >>> .el-textarea__inner:hover,
.dialog-select >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input >>> .el-input__inner:focus,
.dialog-textarea >>> .el-textarea__inner:focus,
.dialog-select >>> .el-input__inner:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.dialog-input >>> .el-input__count,
.dialog-textarea >>> .el-input__count {
  color: var(--qm-text-3);
}

.multiple-select >>> .el-select__tags {
  max-width: calc(100% - 40px);
}

.elegant-dialog >>> .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid var(--qm-bg-3);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 12px;
}

.dialog-cancel-btn {
  padding: 10px 24px;
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-cancel-btn:hover {
  background: var(--qm-bg-1);
  border-color: var(--qm-line-strong);
  transform: translateY(-1px);
}

.dialog-confirm-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
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
  }
  
  .add-btn {
    width: 100%;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
  
  .elegant-table {
    min-width: 1000px;
  }
  
  .pagination-wrapper {
    padding: 15px 20px;
  }
  
  .elegant-dialog {
    width: 95% !important;
    max-width: 400px;
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