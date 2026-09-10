<template>
  <div class="header-management-container">
    <!-- Header搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">全局请求头筛选</h3>
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
        <el-form :model="headerSearch" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="inline-form-item">
                <div class="inline-label-wrapper">
                  <i class="icon-plant"></i>
                  <span class="inline-label-text">所属产品</span>
                </div>
                <el-select 
                  v-model="headerSearch.plant" 
                  placeholder="请选择产品" 
                  clearable
                  class="select"
                  size='large'
                  popper-class='select-dropdown-rounded'
                >
                  <el-option 
                    v-for="plant in plant_list" 
                    :key="plant.id"
                    :label="plant.name" 
                    :value="plant.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="inline-form-item">
                <div class="inline-label-wrapper">
                  <i class="icon-env"></i>
                  <span class="inline-label-text">环境名称</span>
                </div>
                <el-select 
                  v-model="headerSearch.env" 
                  placeholder="请选择环境" 
                  clearable
                  class="select"
                  size='large'
                  popper-class='select-dropdown-rounded'
                >
                  <el-option 
                    v-for="env_obj in env_list.results" 
                    :key="env_obj.id"
                    :label="env_obj.name" 
                    :value="env_obj.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="inline-form-item">
                <div class="inline-label-wrapper">
                  <i class="icon-run"></i>
                  <span class="inline-label-text">是否批跑</span>
                </div>
                <el-select 
                  v-model="headerSearch.is_all_run" 
                  placeholder="请选择" 
                  clearable
                  class="select"
                  size='large'
                  popper-class='select-dropdown-rounded'
                >
                  <el-option label="是" :value="true" />
                  <el-option label="否" :value="false" />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="inline-form-item">
                <div class="inline-label-wrapper">
                  <i class="icon-creator"></i>
                  <span class="inline-label-text">创建人</span>
                </div>
                <el-select 
                  v-model="headerSearch.create_by" 
                  placeholder="请选择创建人" 
                  clearable
                  filterable
                  class="select"
                  size='large'
                  popper-class='select-dropdown-rounded'
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
              <el-form-item class="inline-form-item">
                <div class="inline-label-wrapper">
                  <i class="icon-updater"></i>
                  <span class="inline-label-text">更新人</span>
                </div>
                <el-select 
                  v-model="headerSearch.update_by" 
                  placeholder="请选择更新人" 
                  clearable
                  filterable
                  class="select"
                  size='large'
                  popper-class='select-dropdown-rounded'
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
            <h3 class="content-title">全局请求头</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ header_list.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ page_size_params.page }}</span>
              </div>
            </div>
          </div>
          <el-button 
            v-if="permission.has_add_permission" 
            @click="addHeader" 
            type="primary" 
            class="add-btn"
          >
            <el-icon><Plus /></el-icon>新增全局请求头
          </el-button>
        </div>
        
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <!-- Header表格 -->
        <el-table 
          :data="header_list.results" 
          :max-height="'calc(100vh - 585px)'" 
          class="elegant-table"
          :header-row-style="headerRowStyle"
		  @sort-change='handleSortChange'
		  
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
            label="请求头名称" 
            prop="name" 
            min-width="150" 
            align="center"
            class-name="name-column"
          >
            <template #default="scope">
              <div class="name-cell">
                <el-tag 
                  type="info"
                  effect="light"
                  class="name-badge"
                >
                  <span class="name-icon"><i class="icon-header"></i></span>
                  {{ scope.row.name }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="是否批跑" 
            prop="is_all_run_tag" 
            width="100" 
            align="center"
            class-name="run-column"
           :show-overflow-tooltip="true">
            <template #default="scope">
              <el-tag 
                :type="scope.row.is_all_run ? 'success' : 'info'"
                effect="light"
                class="run-tag"
              >
                {{ scope.row.is_all_run_tag }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="所属产品" 
            prop="plant_name" 
            width="120" 
            align="center"
            class-name="plant-column"
          :show-overflow-tooltip="true" />
          
          <el-table-column 
            label="所属环境" 
            prop="env_name" 
            width="180" 
            align="center"
            class-name="env-column"
          />
          
          <!-- 合并列：创建信息 -->
          <el-table-column
            label="创建信息"
            width="200"
            align="center"
            sortable="custom"
            prop="create_time"
            class-name="creator-column"
          >
            <template #default="scope">
              <div class="user-time-cell">
                <div class="user-info">
                  <i class="icon-user"></i>
                  <span class="user-name">{{ scope.row.create_by_name || '-' }}</span>
                </div>
                <div class="time-info">
                  <i class="icon-time-small"></i>
                  <span class="time-text">{{ formatTime(scope.row.create_time) }}</span>
                </div>
              </div>
            </template>
          </el-table-column>

          <!-- 合并列：更新信息 -->
          <el-table-column
            label="更新信息"
            width="200"
            align="center"
            sortable="custom"
            prop="update_time"
            class-name="updater-column"
          >
            <template #default="scope">
              <div class="user-time-cell">
                <div class="user-info">
                  <i class="icon-user"></i>
                  <span class="user-name">{{ scope.row.update_by_name || '-' }}</span>
                </div>
                <div class="time-info">
                  <i class="icon-time-small"></i>
                  <span class="time-text">{{ formatTime(scope.row.update_time) }}</span>
                </div>
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
                  content="查看Header" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="success" 
                    v-if="permission.has_read_permission" 
                    class="action-btn view-btn"
                    @click.stop="viewHeader(scope.row)"
                    circle
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="编辑Header" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="warning" 
                    v-if="permission.has_edit_permission" 
                    class="action-btn edit-btn"
                    @click.stop="editHeader(scope.row)"
                    circle
                  >
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="删除Header" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="danger" 
                    v-if="permission.has_delete_permission" 
                    @click.stop="deleteHeader(scope.row.id)" 
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
          :total="header_list.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
          :background="true"
        />
      </div>
    </el-card>

    <!-- Header表单对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="title"
      width="1200"
	  height='600'
      class="elegant-dialog"
      :close-on-click-modal="false"

    >
      <div class="dialog-content">
        <el-form 
          :model="HeaderSave" 
          :rules="headerRules" 
          ref="headerRef"
          label-position="top" 
          :disabled="headerView"
          class="dialog-form"
        >
          <div class="dialog-form-row">
            <el-form-item  prop="name" class="dialog-form-item">
              <div class="dialog-label">
                <i class="icon-header-dialog"></i>
                请求头名称
              </div>
              <el-input 
                v-model="HeaderSave.name" 
                autocomplete="off" 
                placeholder="请输入请求头名称"
                size='large'
                :maxlength="50"
                show-word-limit
				class="input"
				
              />
            </el-form-item>
            
            <el-form-item  prop="plant" class="dialog-form-item">
              <div class="dialog-label">
                <i class="icon-plant-dialog"></i>
                所属产品
              </div>
              <el-select 
                v-model="HeaderSave.plant" 
                placeholder="请选择所属产品"
                
                :disabled="!isAdd"
				class="select"
				size='large'
				popper-class='select-dropdown-rounded'
              >
                <el-option 
                  v-for="plant in plant_list" 
                  :key="plant.id"
                  :label="plant.name" 
                  :value="plant.id" 
                />
              </el-select>
            </el-form-item>
            
            <el-form-item  prop="env" class="dialog-form-item">
              <div class="dialog-label">
                <i class="icon-env-dialog"></i>
                所属环境
              </div>
              <el-select 
                v-model="HeaderSave.env" 
                placeholder="请选择所属环境"
                
                :disabled="!isAdd"
				class="select"
				size='large'
				popper-class='select-dropdown-rounded'
              >
                <el-option 
                  v-for="env_obj in env_list.results" 
                  :key="env_obj.id"
                  :label="env_obj.name" 
                  :value="env_obj.id" 
                />
              </el-select>
            </el-form-item>
            
            <el-form-item  prop="is_all_run" class="dialog-form-item">
              <div class="dialog-label">
                <i class="icon-run-dialog"></i>
                是否批跑
              </div>
              <el-select 
                v-model="HeaderSave.is_all_run" 
                placeholder="请选择是否批跑"
                
                :disabled="!isAdd"
				class="select"
				size='large'
				popper-class='select-dropdown-rounded'
				
              >
                <el-option label="是" :value="true" />
                <el-option label="否" :value="false" />
              </el-select>
            </el-form-item>
          </div>
          
          <div class="header-table-section">
            <div class="section-title">
              <i class="icon-table"></i>
              <span>请求头配置</span>
              <el-tag size="small" type="warning">键值对配置</el-tag>
            </div>
            <Header 
              :bind_case_data="[]"
              :tableData="HeaderSave.value"
              class="header-editor"
            />
            <div v-if="headerTableError" class="error-tip">
              <el-icon color="#f56c6c"><Warning /></el-icon>
              <span>请完善请求头表格，所有字段都必填</span>
            </div>
          </div>
        </el-form>
      </div>
      
	  <template #footer>
	  	<span class="dialog-footer" v-if="!headerView">
	  		<el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
	  		<el-button 
	  		  v-if="permission.has_add_permission || permission.has_edit_permission" 
	  		  type="primary" 
	  		  @click="saveHeader" 
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
  Refresh,
  Search,
  Plus,
  View,
  Delete,
  EditPen,
  Warning
} from '@element-plus/icons-vue'
import Header from '../../components/Header.vue'
import * as common from '../../utils/common.js'

export default {
  name: 'HeaderManagement',
  computed: {
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),
    calcMinWidth() {
      let visibleButtons = 0
      if (this.permission.has_read_permission) visibleButtons += 1
      if (this.permission.has_edit_permission) visibleButtons += 1
      if (this.permission.has_delete_permission) visibleButtons += 1
      return Math.max(10, visibleButtons * 48)
    }
  },
  components: {
    Header,
    Refresh,
    Search,
    Plus,
    View,
    Delete,
    EditPen,
    Warning
  },
  data() {
    return {
      headerView: false,
      permission: {},
      headerSearch: {
        plant: '',
        env: '',
        project: '',
        create_by: '',
        is_all_run: '',
        update_by: ''
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      title: '新增请求头',
      plant_list: [],
      env_list: [],
      isAdd: true,
      editDialogVisible: false,
      editDialogVisibleCookie: false,
      header_list: {
        count: 0,
        results: []
      },
      user_list: [],
      HeaderSave: {
        project: '',
        env: '',
        name: '',
        is_all_run: false,
        value: [],
      },
      headerRules: {
        name: [{
          required: true,
          message: '请求头名称不能为空',
          trigger: 'blur',
        }],
        plant: [{
          required: true,
          message: '请选择所属产品',
          trigger: 'change',
        }],
        env: [{
          required: true,
          message: '请选择所属环境',
          trigger: 'change',
        }],
        is_all_run: [{
          required: true,
          message: '请选择是否批跑',
          trigger: 'change',
        }],
      },
      headerTableError: false,
      cookieTableError: false
    }
  },
  methods: {
    ...mapActions(['check_permission']),
    
    handleCurrentChange(page) {
      this.page_size_params.page = page
      this.getHeaders()
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
	  this.getHeaders()
	},
    
    handleSizeChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getHeaders()
    },
    
    handleTabChange(tabName) {
      this.page_size_params.page = 1
      this.getHeaders()
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
      this.getHeaders()
    },
    
    reset() {
      for (let key in this.headerSearch) {
        this.headerSearch[key] = ''
      }
    },
    
    editHeader(row_data) {
      this.isAdd = false
      this.title = '编辑Header'
      this.headerView = false
      this.headerTableError = false
      this.getHeader(row_data.id)
      this.editDialogVisible = true
      this.$nextTick(() => {
        if (this.$refs.headerRef) {
          this.$refs.headerRef.clearValidate()
        }
      })
    },
    
    viewHeader(row_data) {
      this.isAdd = false
      this.headerView = true
      this.title = '查看Header'
      this.headerTableError = false
      this.getHeader(row_data.id)
      this.editDialogVisible = true
    },
    
    addHeader() {
      this.title = '新增Header'
      this.headerView = false
      this.headerTableError = false
      this.editDialogVisible = true
      this.isAdd = true
      this.HeaderSave = {
        project: this.projectInfo.id,
        env: '',
        name: '',
        is_all_run: false,
        value: [],
      }
      this.$nextTick(() => {
        if (this.$refs.headerRef) {
          this.$refs.headerRef.resetFields()
        }
      })
    },
    
    async getPlants() {
      try {
        const response = await this.$api.getPlants({ project: this.projectInfo.id })
        if (response.status === 200) {
          this.plant_list = response.data.results
        }
      } catch (error) {
        console.error('获取产品列表失败:', error)
      }
    },
    
    saveHeader() {
      this.headerTableError = common.hasEmptyValues(this.HeaderSave.value, ['name', 'type', 'value'])
      
      this.$refs.headerRef.validate(async (valid) => {
        if (valid && !this.headerTableError) {
          if (this.isAdd) {
            await this.createHeader()
          } else {
            await this.updateHeader()
          }
        } else if (this.headerTableError) {
          ElMessage({
            message: "请完善请求头表格，所有字段都必填",
            type: 'error'
          })
        }
      })
    },
    
    handleDialogClose(type) {
      if (type === 'header') {
        this.headerTableError = false
      } else {
        this.cookieTableError = false
      }
    },
    
    async createHeader() {
      try {
        this.HeaderSave.project = this.projectInfo.id
        const response = await this.$api.createHeader(this.HeaderSave)
        if (response.status === 201) {
          this.editDialogVisible = false
          this.getHeaders()
          ElMessage({
            message: "保存成功",
            type: 'success'
          })
        }
      } catch (error) {
        console.error('创建Header失败:', error)
      }
    },
    
    async updateHeader() {
      try {
        this.HeaderSave.project = this.projectInfo.id
        const response = await this.$api.updateHeader(this.HeaderSave.id, this.HeaderSave)
        if (response.status === 200) {
          this.editDialogVisible = false
          this.getHeaders()
          ElMessage({
            message: "保存成功",
            type: 'success'
          })
        }
      } catch (error) {
        console.error('更新Header失败:', error)
      }
    },

    async deleteHeader(id) {
      ElMessageBox.confirm(
        '确定删除此Header？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteHeader(id)
        if (response.status === 204) {
          this.getHeaders()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
    
    async getHeader(id) {
      try {
        const response = await this.$api.getHeader(id)
        if (response.status === 200) {
          this.HeaderSave = { ...response.data.result }
        }
      } catch (error) {
        console.error('获取Header详情失败:', error)
      }
    },
    
    async getHeaders() {
      try {
        const par = {
          page: this.page_size_params.page,
          size: this.page_size_params.size,
          project: this.projectInfo.id
        }
        
		const params = Object.assign(par, this.sort_params)
        if (this.headerSearch.plant) params.plant = this.headerSearch.plant
        if (this.headerSearch.env) params.env = this.headerSearch.env
        if (this.headerSearch.is_all_run !== '') params.is_all_run = this.headerSearch.is_all_run
        if (this.headerSearch.create_by) params.create_by = this.headerSearch.create_by
        if (this.headerSearch.update_by) params.update_by = this.headerSearch.update_by
        
        const response = await this.$api.getHeaders(params)
        if (response.status === 200) {
          this.header_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取Header列表失败:', error)
      }
    },

    async  check_permission(){
        const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission['/env/env']}
		const response = await this.$api.check_permission(params)
		if (response.status === 200){
			 this.permission = { ...response.data.result }
		}
	 },
    
    
    async getEnvs() {
      try {
        const response = await this.$api.getEnvs({ project: this.projectInfo.id })
        if (response.status === 200) {
          this.env_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取环境列表失败:', error)
      }
    }
  },
  created() {
    this.check_permission()
    this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
    this.getHeaders()
    this.getPlants()
    this.getEnvs()
  },
  watch: {
    activeName() {
      this.getHeaders()
    }
  }
}
</script>

<style scoped>


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
  padding: 15px 10px 10px 5px;
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
  padding: 25px 5px 0px 5px;
}

/* 内联表单样式 */
.inline-form {
  margin-bottom: 0;
}

.inline-form-item {
  margin-bottom: 20px;
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 40px;
}

.inline-form-item :deep(.el-form-item__content) {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  flex-wrap: nowrap !important;
  margin-left: 0 !important;
  width: 100%;
}

.inline-label-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 90px;
  flex-shrink: 0;
}

.inline-label-text {
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

.icon-plant,
.icon-env,
.icon-run,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.icon-plant { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.icon-env { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-run { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }
.icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-updater { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }

/* 内联输入框样式 */
.select-inline >>> .el-input__inner {
  border-radius: 10px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-1);
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
  flex: 1;
  margin-left: 12px;
}

.select-inline >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  background: var(--qm-bg-2);
}

.select-inline >>> .el-input__inner:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.select-inline {
  flex: 1;
  margin-left: 12px;
}

/* 内容卡片 */
.content-card {
  flex: 1;
  background: var(--qm-bg-2);
  border: none;
  border-radius: 16px;
  display: flex;
  margin-top: 20px;
  flex-direction: column;
  min-height: 0;
}

.content-header {
  margin-top: 20px;
  padding: 20px 24px 0 24px;
  flex-shrink: 0;
}

.content-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

/* Tabs样式 */
.tabs-wrapper {
  margin-top: 10px;
}

.elegant-tabs {
  background: transparent;
}

.elegant-tabs >>> .el-tabs__header {
  margin: 0;
  border-bottom: 2px solid var(--qm-bg-3);
}

.elegant-tabs >>> .el-tabs__nav-wrap::after {
  display: none;
}

.elegant-tabs >>> .el-tabs__item {
  padding: 0 20px;
  height: 40px;
  line-height: 40px;
  color: var(--qm-text-2);
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
}

.elegant-tabs >>> .el-tabs__item:hover {
  color: #f59e0b;
}

.elegant-tabs >>> .el-tabs__item.is-active {
  color: #f59e0b;
  font-weight: 600;
}

.elegant-tabs >>> .el-tabs__item.is-active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
  border-radius: 3px 3px 0 0;
}

.elegant-tabs >>> .el-tabs__active-bar {
  display: none;
}

/* 表格区域 */
.table-wrapper {
  flex: 1;
  padding: 0 0;
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

.name-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.name-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 13px;
  transition: all 0.3s ease;
  border-width: 2px;
}

.name-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.name-icon {
  font-weight: bold;
  margin-right: 4px;
}

.icon-header {
  display: inline-block;
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M4 6h16v2H4zm0 4h16v2H4zm0 4h16v2H4zm0 4h16v2H4z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-cookie {
  display: inline-block;
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M21.95 11c-.04-.33-.07-.66-.1-1-.03-.35-.06-.7-.11-1.05-.05-.35-.1-.7-.16-1.04-.06-.35-.13-.7-.2-1.05-.07-.35-.15-.69-.24-1.04-.09-.35-.19-.69-.3-1.03-.1-.34-.22-.68-.34-1.01-.12-.33-.25-.66-.39-.98-.14-.32-.29-.64-.44-.95-.15-.31-.32-.61-.49-.91-.17-.3-.35-.6-.54-.89-.19-.29-.39-.57-.6-.85-.21-.28-.43-.55-.66-.82-.23-.27-.47-.53-.72-.79-.25-.26-.51-.51-.78-.75-.27-.24-.55-.47-.84-.69L4 4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-9.05c-.33.04-.66.07-1 .1-.35.03-.7.06-1.05.11-.35.05-.7.1-1.04.16-.35.06-.7.13-1.05.2-.35.07-.69.15-1.04.24-.35.09-.69.19-1.03.3-.34.1-.68.22-1.01.34-.33.12-.66.25-.98.39-.32.14-.64.29-.95.44-.31.15-.61.32-.91.49-.3.17-.6.35-.89.54-.29.19-.57.39-.85.6-.28.21-.55.43-.82.66-.27.23-.53.47-.79.72-.26.25-.51.51-.75.78-.24.27-.47.55-.69.84-.22.29-.43.59-.62.9-.19.31-.36.63-.52.95-.16.32-.31.65-.44.98-.13.33-.25.67-.35 1.01-.1.34-.19.69-.27 1.04-.08.35-.15.7-.21 1.05-.06.35-.11.7-.15 1.05-.04.35-.07.7-.09 1.05-.02.35-.03.7-.03 1.05H4v-2h2v-2H4v-2h2v-2H4v-2h2v-2H4v-2h2V8H4V6h2V4h2v2h2V4h2v2h2V4h2v2h2v2h2v2h2v2h-2v2h2v2h-2v2h2v2h-2v2h2v2h-9c0-6.62 5.38-12 12-12v-1c-.35 0-.7-.03-1.05-.05z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.run-tag,
.type-tag {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
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

.user-time-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: flex-start;
  padding: 8px 0;
}
.user-info,
.time-info {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}
.icon-user {
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}
.icon-time-small {
  width: 12px;
  height: 12px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}
.user-name {
  font-size: 13px;
  color: var(--qm-text-2);
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.time-text {
  font-size: 12px;
  color: var(--qm-text-2);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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
  padding: 20px 24px 0px 24px;
  border-top: 1px solid var(--qm-bg-3);
  flex-shrink: 0;
  display: block !important;
  min-height: 40px;
  background: var(--qm-bg-2);
  float: right;
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
.elegant-dialog >>> .el-dialog {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog >>> .el-dialog__header {
  padding: 24px 24px 0;
  margin: 0;
}

.elegant-dialog >>> .el-dialog__title {
  font-size: 20px;
  font-weight: 700;
  color: var(--qm-text-1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.elegant-dialog >>> .el-dialog__title::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  border-radius: 2px;
}

.elegant-dialog >>> .el-dialog__body {
  padding: 24px;
  max-height: 70vh;
  overflow-y: auto;
}

.dialog-content {
  padding: 24px 0 0 0;
}

.dialog-form {
  margin: 0;
}

.dialog-form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 24px;
}

.dialog-form-item {
  flex: 1;
  min-width: 200px;
  margin-bottom: 0;
}

.dialog-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-2);
}

.icon-header-dialog,
.icon-plant-dialog,
.icon-env-dialog,
.icon-run-dialog,
.icon-cookie-dialog,
.icon-type-dialog {
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-header-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M4 6h16v2H4zm0 4h16v2H4zm0 4h16v2H4zm0 4h16v2H4z'/%3E%3C/svg%3E");
}

.icon-plant-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 2a9 9 0 0 1 9 9v1h1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-1v1a9 9 0 0 1-9 9H8a9 9 0 0 1-9-9v-7a9 9 0 0 1 9-9h4zm0 2H8a7 7 0 0 0-7 7v7a7 7 0 0 0 7 7h4a7 7 0 0 0 7-7v-7a7 7 0 0 0-7-7zm-4 5a1 1 0 0 1 1 1v2a1 1 0 0 1-2 0v-2a1 1 0 0 1 1-1zm8 0a1 1 0 0 1 1 1v2a1 1 0 0 1-2 0v-2a1 1 0 0 1 1-1z'/%3E%3C/svg%3E");
}

.icon-env-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 3L4 9v12h16V9l-8-6zm0 2.5L18 9v3h-2v4h-2v-4h-2v4h-2v-4H6V9l6-3.5zM6 19v-5h12v5H6z'/%3E%3C/svg%3E");
}

.icon-run-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M8 5v14l11-7z'/%3E%3C/svg%3E");
}

.icon-cookie-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M21.95 11c-.04-.33-.07-.66-.1-1-.03-.35-.06-.7-.11-1.05-.05-.35-.1-.7-.16-1.04-.06-.35-.13-.7-.2-1.05-.07-.35-.15-.69-.24-1.04-.09-.35-.19-.69-.3-1.03-.1-.34-.22-.68-.34-1.01-.12-.33-.25-.66-.39-.98-.14-.32-.29-.64-.44-.95-.15-.31-.32-.61-.49-.91-.17-.3-.35-.6-.54-.89-.19-.29-.39-.57-.6-.85-.21-.28-.43-.55-.66-.82-.23-.27-.47-.53-.72-.79-.25-.26-.51-.51-.78-.75-.27-.24-.55-.47-.84-.69L4 4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-9.05c-.33.04-.66.07-1 .1-.35.03-.7.06-1.05.11-.35.05-.7.1-1.04.16-.35.06-.7.13-1.05.2-.35.07-.69.15-1.04.24-.35.09-.69.19-1.03.3-.34.1-.68.22-1.01.34-.33.12-.66.25-.98.39-.32.14-.64.29-.95.44-.31.15-.61.32-.91.49-.3.17-.6.35-.89.54-.29.19-.57.39-.85.6-.28.21-.55.43-.82.66-.27.23-.53.47-.79.72-.26.25-.51.51-.75.78-.24.27-.47.55-.69.84-.22.29-.43.59-.62.9-.19.31-.36.63-.52.95-.16.32-.31.65-.44.98-.13.33-.25.67-.35 1.01-.1.34-.19.69-.27 1.04-.08.35-.15.7-.21 1.05-.06.35-.11.7-.15 1.05-.04.35-.07.7-.09 1.05-.02.35-.03.7-.03 1.05H4v-2h2v-2H4v-2h2v-2H4v-2h2v-2H4v-2h2V8H4V6h2V4h2v2h2V4h2v2h2V4h2v2h2v2h2v2h2v2h-2v2h2v2h-2v2h2v2h-2v2h2v2h-9c0-6.62 5.38-12 12-12v-1c-.35 0-.7-.03-1.05-.05z'/%3E%3C/svg%3E");
}

.icon-type-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M12 3L1 9l11 6 9-4.91V17h2V9L12 3zM5 13.38v3.79l7 3.11 7-3.11v-3.79l-7 3.11-7-3.11z'/%3E%3C/svg%3E");
}

.dialog-input >>> .el-input__inner,
.dialog-select >>> .el-input__inner {
  border-radius: 12px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  width: 100%;
  height: 40px;
  line-height: 40px;
}

.dialog-input >>> .el-input__inner:hover,
.dialog-select >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input >>> .el-input__inner:focus,
.dialog-select >>> .el-input__inner:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.dialog-input >>> .el-input__count {
  color: var(--qm-text-3);
}

/* 表格配置区域 */
.header-table-section,
.cookie-table-section {
  margin-top: 24px;
  border-top: 1px solid var(--qm-bg-3);
  padding-top: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.icon-table {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.header-editor,
.cookie-editor {
  border: 1px solid var(--qm-line-strong);
  border-radius: 12px;
  overflow: hidden;
  padding: 16px;
  background: var(--qm-bg-2);
}

.error-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px 16px;
  background: var(--qm-red-soft);
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 14px;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}


.dialog-footer {
  display: flex;
  
  justify-content: flex-end;
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
  .header-management-container {
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
  .header-management-container {
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
  
  .select-inline >>> .el-input__inner {
    margin-left: 0;
    margin-top: 4px;
  }
  
  .select-inline {
    margin-left: 0;
    margin-top: 4px;
  }
  
  /* 对话框响应式 */
  .dialog-form-row {
    flex-direction: column;
    gap: 16px;
  }
  
  .dialog-form-item {
    min-width: 100%;
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