<template>
  <div class="tag-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">标签筛选</h3>
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
        <el-form :model="tagSearch" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-user"></i>
                  <span class="label-text">标签名称</span>
                </div>
                <el-input 
                  v-model="tagSearch.name" 
                  placeholder="请输入标签名称" 
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
                  v-model="tagSearch.create_by" 
                  placeholder="请选择创建人" 
                  clearable
                  filterable
				  size='large'
                  class="select"
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
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-updater"></i>
                  <span class="label-text">更新人</span>
                </div>
                <el-select 
                  v-model="tagSearch.update_by" 
                  placeholder="请选择更新人" 
                  clearable
                  filterable
                  size='large'
                  class="select"
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
            <h3 class="content-title">标签列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ tag_list.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ page_size_params.page }}</span>
              </div>
            </div>
          </div>
          <el-button 
            v-if="permission.has_add_permission" 
            @click="addTag" 
            type="primary" 
            class="add-btn"
          >
            <el-icon><Plus /></el-icon>新增标签
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table 
          :data="tag_list.results" 
          :max-height="'calc(100vh - 485px)'" 
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
            label="标签名称" 
            prop="name" 
            min-width="150" 
            align="center"
            class-name="tag-column"
          >
            <template #default="scope">
              <div class="tag-cell">
                <el-tag 
                  :type="getTagType(scope.row.name)"
                  effect="light"
                  class="tag-badge"
                >
                  <span class="tag-icon">#</span>
                  {{ scope.row.name }}
                </el-tag>
              </div>
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
                  content="查看标签" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="success" 
                    v-if="permission.has_read_permission" 
                    class="action-btn view-btn"
                    @click.stop="viewTag(scope.row)"
                    circle
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="编辑标签" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="warning" 
                    v-if="permission.has_edit_permission" 
                    class="action-btn edit-btn"
                    @click.stop="editTag(scope.row)"
                    circle
                  >
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="删除标签" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="danger" 
                    v-if="permission.has_delete_permission" 
                    @click.stop="deleteTag(scope.row.id)" 
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
          :total="tag_list.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
          :background="true"
        />
      </div>
    </el-card>

    <!-- 标签表单对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="450"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
	  <template #title={}>
		  <label class="dialog-title">
		    {{ title }}
		  </label>
	  </template>
      <div class="dialog-content">
        <el-form 
          :model="tagSave" 
          :rules="tagRules" 
          ref="tagRef"
          label-position="right" 
          :disabled="tagView"
          class="dialog-form"
        >
          <el-form-item  prop="name" class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-tag-dialog"></i>
              标签名称
            </label>
            <el-input 
              v-model="tagSave.name" 
              autocomplete="off" 
              placeholder="请输入标签名称"
              class="input"
			  size='large'
              :maxlength="20"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      
      <div slot="footer" class="dialog-footer" v-if="!tagView">
        <el-button @click="editDialogVisible = false" class="dialog-cancel-btn">
          <span class="button-text">取消</span>
        </el-button>
        <el-button 
          v-if="permission.has_add_permission || permission.has_edit_permission" 
          type="primary" 
          @click="save" 
          class="dialog-confirm-btn"
        >
          <span class="button-text">保存</span>
        </el-button>
      </div>
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
  name: 'TagManagement',
  computed: {
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),
    calcMinWidth() {
      let visibleButtons = 0
      if (this.permission.has_read_permission) visibleButtons += 1
      if (this.permission.has_edit_permission) visibleButtons += 1
      if (this.permission.has_delete_permission) visibleButtons += 1
      return Math.max(10, visibleButtons * 60)
    }
  },
  data() {
    return {
      tagView: false,
      permission: {},
      tagSearch: {
        name: '',
        project: '',
        create_by: '',
        update_by: '',
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      title: '新增标签',
      isAdd: true,
      editDialogVisible: false,
      tag_list: {
        count: 0,
        results: []
      },
      tagSave: {
        project: '',
        name: ''
      },
      user_list: [],
      tagRules: {
        name: [{
          required: true,
          message: '标签名称不能为空',
          trigger: 'blur',
        }, {
          min: 1,
          max: 20,
          message: '标签名称长度在 1 到 20 个字符',
          trigger: 'blur'
        }],
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
      this.getTags()
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
    
    handleRowClick(row, column, event) {
      const rows = document.querySelectorAll('.elegant-table .el-table__row')
      rows.forEach(r => r.classList.remove('active-row'))
      event.currentTarget.classList.add('active-row')
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
	  this.getTags()
	},
    
    handleSizeChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getTags()
    },
    
    getTagType(tagName) {
      if (!tagName) return ''
      
      const colors = ['', 'success', 'info', 'warning', 'danger']
      const hash = tagName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
      return colors[hash % colors.length]
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
      this.getTags()
    },
    
    reset() {
      for (let key in this.tagSearch) {
        if (key === 'module_list') {
          this.tagSearch[key] = []
        } else {
          this.tagSearch[key] = ''
        }
      }
    },
    
    editTag(row_data) {
      this.isAdd = false
      this.title = '编辑标签'
      this.tagView = false
      this.tagSave = { ...row_data }
      this.editDialogVisible = true
      this.$nextTick(() => {
        if (this.$refs.tagRef) {
          this.$refs.tagRef.clearValidate()
        }
      })
    },
    
    viewTag(row_data) {
      this.isAdd = false
      this.tagView = true
      this.title = '查看标签'
      this.tagSave = { ...row_data }
      this.editDialogVisible = true
    },
    
    addTag() {
      this.title = '新增标签'
      this.tagView = false
      this.editDialogVisible = true
      this.isAdd = true
      this.tagSave = {
        project: this.projectInfo.id,
        name: ''
      }
      this.$nextTick(() => {
        if (this.$refs.tagRef) {
          this.$refs.tagRef.resetFields()
        }
      })
    },
    
    save() {
      this.$refs.tagRef.validate(async (valid) => {
        if (valid) {
          if (this.isAdd) {
            await this.createTag()
          } else {
            await this.updateTag()
          }
        }
      })
    },
    
    async createTag() {
      try {
        const response = await this.$api.createTag(this.tagSave)
        if (response.status === 201) {
          this.getTags()
          ElMessage({
            message: "保存成功",
            type: 'success'
          })
          this.editDialogVisible = false
        }
      } catch (error) {
        console.error('创建标签失败:', error)
      }
    },
    
    async updateTag() {
      try {
        const response = await this.$api.updateTag(this.tagSave.id, this.tagSave)
        if (response.status === 200) {
          this.getTags()
          ElMessage({
            message: "保存成功",
            type: 'success'
          })
          this.editDialogVisible = false
        }
      } catch (error) {
        console.error('更新标签失败:', error)
      }
    },
    
    async deleteTag(id) {
      ElMessageBox.confirm(
        '确定删除此标签？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deleteTag(id)
        if (response.status === 204) {
          this.getTags()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
    async check_permission(){
      const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path]}
      const response = await this.$api.check_permission(params)
      if (response.status === 200){
        this.permission = { ...response.data.result }
      }
    },

    async getTags() {
      const par = {
        page: this.page_size_params.page,
        size: this.page_size_params.size,
        project: this.projectInfo.id
      }
      const params = Object.assign(par, this.sort_params)
      if (this.tagSearch.name) params.name = this.tagSearch.name
      if (this.tagSearch.create_by) params.create_by = this.tagSearch.create_by
      if (this.tagSearch.update_by) params.update_by = this.tagSearch.update_by
      
      try {
        const response = await this.$api.getTags(params)
        if (response.status === 200) {
          this.tag_list = { ...response.data }
        }
      } catch (error) {
        console.error('获取标签列表失败:', error)
      }
    }
  },
  created() {
    this.check_permission()
    this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
    this.getTags()
  }
}
</script>

<style scoped>
.tag-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 15px 15px 15px;
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

.filter-card :deep(.el-card__body) {
  padding: 20px 20px 0 20px;
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

.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
}

.inline-form {
  margin-bottom: 0;
}

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

.tag-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.tag-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 500;
  font-size: 13px;
  transition: all 0.3s ease;
  border-width: 2px;
}

.tag-badge:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.tag-icon {
  font-weight: bold;
  margin-right: 4px;
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

/* 对话框样式 - 优化部分 */
.elegant-dialog >>> .el-dialog {
  border-radius: 20px !important;
  overflow: hidden !important;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4) !important;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(10px) !important;
}

.elegant-dialog >>> .el-dialog__header {
  padding: 24px 24px 0 !important;
  margin: 0 !important;
}

.elegant-dialog >>> .el-dialog__title {
  font-size: 20px !important;
  font-weight: 700 !important;
  color: #1a1a1a !important;
  letter-spacing: 0.5px !important;
  position: relative !important;
  padding-left: 32px !important; /* 为图标留出空间 */
}

/* 添加对话框标题图标 - 使用标签图标 */
.elegant-dialog >>> .el-dialog__title::before {
  content: '🏷️' !important; /* 标签图标 */
  position: absolute !important;
  left: 0 !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  font-size: 18px !important;
}

.elegant-dialog >>> .el-dialog__headerbtn {
  top: 24px !important;
  right: 24px !important;
  width: 32px !important;
  height: 32px !important;
  border-radius: 50% !important;
  background: rgba(0, 0, 0, 0.05) !important;
  transition: all 0.3s ease !important;
}

.elegant-dialog >>> .el-dialog__headerbtn:hover {
  background: rgba(99, 102, 241, 0.1) !important;
  transform: rotate(90deg) !important;
}

.elegant-dialog >>> .el-dialog__headerbtn .el-dialog__close {
  color: #666 !important;
  font-size: 18px !important;
}

.elegant-dialog >>> .el-dialog__body {
  padding: 24px !important;
  background: rgba(255, 255, 255, 0.7) !important;
}

.dialog-content {
  padding: 0;
}

.dialog-form {
  margin: 0;
}

.dialog-form-item {
  margin-bottom: 0;
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

.dialog-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #334155;
}

.icon-tag-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z'/%3E%3C/svg%3E");
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

.dialog-input >>> .el-input__count {
  color: #94a3b8;
}

.elegant-dialog >>> .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid #f1f5f9;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 12px;
}

/* 按钮文字下划线样式 */
.dialog-cancel-btn,
.dialog-confirm-btn {
  position: relative;
  padding: 10px 24px !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  font-size: 15px !important;
  transition: all 0.3s ease !important;
  overflow: hidden;
}

.dialog-cancel-btn {
  border: 1px solid #e2e8f0 !important;
  background: white !important;
  color: #64748b !important;
}

.dialog-cancel-btn:hover {
  background: #f8fafc !important;
  border-color: #cbd5e1 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.15) !important;
}

.dialog-confirm-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
  border: none !important;
  color: white !important;
}

.dialog-confirm-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
}

/* 按钮文字容器 */
.button-text {
  position: relative;
  display: inline-block;
  padding-bottom: 3px; /* 为下划线留出空间 */
}

/* 下划线效果 */
.button-text::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: currentColor;
  transform: scaleX(0);
  transform-origin: bottom right;
  transition: transform 0.3s ease;
}

/* 取消按钮下划线颜色 */
.dialog-cancel-btn .button-text::after {
  background: #3b82f6; /* 蓝色下划线 */
}

/* 确认按钮下划线颜色 */
.dialog-confirm-btn .button-text::after {
  background: white; /* 白色下划线 */
}

/* 鼠标悬停时显示下划线 */
.dialog-cancel-btn:hover .button-text::after,
.dialog-confirm-btn:hover .button-text::after {
  transform: scaleX(1);
  transform-origin: bottom left;
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .tag-management-container {
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
  .tag-management-container {
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
  
  .input-inline >>> .el-input__inner,
  .select-inline >>> .el-input__inner {
    margin-left: 0;
    margin-top: 4px;
  }
  
  .select-inline {
    margin-left: 0;
    margin-top: 4px;
  }
  
  /* 响应式调整对话框 */
  .elegant-dialog >>> .el-dialog {
    width: 90% !important;
    max-width: 450px;
  }
  
  .elegant-dialog >>> .el-dialog__header,
  .elegant-dialog >>> .el-dialog__body,
  .elegant-dialog >>> .el-dialog__footer {
    padding-left: 16px !important;
    padding-right: 16px !important;
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