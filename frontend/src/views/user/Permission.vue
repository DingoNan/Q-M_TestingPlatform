<template>
  <div class="permission-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow" >
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">菜单权限筛选</h3>
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
        <el-form :model="menuSearch" class="filter-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-menu"></i>
                  <span class="label-text">菜单名称</span>
                </div>
                <el-input 
                  v-model="menuSearch.name" 
                  placeholder="请输入菜单名称" 
                  clearable
				  size='large'
                  class="input"
                />
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-level"></i>
                  <span class="label-text">菜单等级</span>
                </div>
                <el-select 
                  v-model="menuSearch.level" 
                  placeholder="请选择菜单等级" 
                  clearable
				  size='large'
                  class="select"
				  popper-class='select-dropdown-rounded'
                >
                  <el-option 
                    v-for="menu_obj in menu_level" 
                    :key="menu_obj.id"
                    :label="menu_obj.name" 
                    :value="menu_obj.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-parent"></i>
                  <span class="label-text">父菜单</span>
                </div>
                <el-select 
                  v-model="menuSearch.parent" 
                  placeholder="请选择父菜单" 
                  clearable
                  filterable
                  class="select"
				  size='large'
				  popper-class='select-dropdown-rounded'
                >
                  <el-option 
                    v-for="main_menu in mainMenu" 
                    :key="main_menu.id"
                    :label="main_menu.name" 
                    :value="main_menu.id" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-icon"></i>
                  <span class="label-text">菜单图标</span>
                </div>
                <el-input 
                  v-model="menuSearch.icon" 
                  placeholder="请输入菜单图标" 
                  clearable
                  class="input"
				  size='large'
                />
              </el-form-item>
            </el-col>
            
          </el-row>
		  
		  <el-row :gutter="24">
			  <el-col :xs="24" :sm="12" :md="8" :lg="6">
				  <el-form-item class="form-item-inline">
					<div class="label-with-icon">
					  <i class="icon-path"></i>
					  <span class="label-text">菜单路径</span>
					</div>
					<el-input 
					  v-model="menuSearch.path" 
					  placeholder="请输入菜单路径" 
					  clearable
					  class="input"
							  size='large'
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
					  v-model="menuSearch.create_by" 
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
				  <el-form-item class="form-item-inline">
					<div class="label-with-icon">
					  <i class="icon-updater"></i>
					  <span class="label-text">更新人</span>
					</div>
					<el-select 
					  v-model="menuSearch.update_by" 
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
            <h3 class="content-title">菜单权限列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ menu_list.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ page_size_params.page }}</span>
              </div>
            </div>
          </div>
          <el-button 
            @click="addMenu"
            type="primary" 
            class="add-btn"
          >
            <el-icon><Plus /></el-icon>新增菜单权限
          </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table 
          :data="menu_list.results" 
          :max-height="'calc(100vh - 540px)'" 
          class="elegant-table"
		  @sort-change='handleSortChange'
          :header-row-style="headerRowStyle"
          :show-overflow-tooltip="true"
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
            label="菜单名称" 
            prop="name" 
            min-width="120" 
            align="center"
            class-name="menu-column"
          >
            <template #default="scope">
              <div class="menu-cell">
                <div class="menu-icon">
                  <el-icon v-if="scope.row.icon">
                    <component :is="scope.row.icon" />
                  </el-icon>
                  <el-icon v-else>
                    <Menu />
                  </el-icon>
                </div>
                <div class="menu-info">
                  <span class="menu-name">{{ scope.row.name }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="菜单路径" 
            prop="path" 
            min-width="150" 
            align="center"
            class-name="path-column"
          >
            <template #default="scope">
              <div class="path-cell">
                <i class="icon-path-small"></i>
                <span class="path-text">{{ scope.row.path || '-' }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="菜单图标" 
            prop="icon" 
            min-width="100" 
            align="center"
            class-name="icon-column"
          >
            <template #default="scope">
              <div class="icon-cell">
                <el-tag v-if="scope.row.icon" size="small" effect="light">
                  {{ scope.row.icon }}
                </el-tag>
                <span v-else class="no-icon">-</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="菜单等级" 
            prop="level" 
            min-width="100" 
            align="center"
            class-name="level-column"
          >
            <template #default="scope">
              <el-tag 
                :type="scope.row.level === 1 ? 'primary' : 'success'" 
                effect="light"
                class="level-tag"
              >
                {{ formatterLevel(scope.row) }}
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
                  content="查看权限" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="success" 
                    class="action-btn view-btn"
                    @click.stop="viewMenu(scope.row)"
                    circle
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="编辑权限" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="warning"
                    class="action-btn edit-btn"
                    @click.stop="editMenu(scope.row)"
                    circle
                  >
                    <el-icon><EditPen /></el-icon>
                  </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="删除权限" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="danger"
                    @click.stop="deletePermission(scope.row.id)" 
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
          :total="menu_list.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
          :background="true"
        />
      </div>
    </el-card>

    <!-- 菜单权限表单对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="500"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <div class="dialog-content">
        <el-form 
          :model="menuSave" 
          label-position="top" 
          label-width="70px" 
		  :rules="permissionRules"
		  ref='permissionRef'
          :disabled="permissionView"
          class="dialog-form"
        >
          <el-form-item  class="dialog-form-item" prop='name'>
            <label class="dialog-label">
              <i class="icon-menu-dialog"></i>
              菜单名称
            </label>
            <el-input 
              v-model="menuSave.name" 
              autocomplete="off" 
			  size='large'
              placeholder="请输入菜单名称"
              class="input"
			  maxlength="20"
			  show-word-limit
            />
          </el-form-item>
          
          <el-form-item  class="dialog-form-item" prop='level'>
            <label class="dialog-label">
              <i class="icon-level-dialog"></i>
              菜单等级
            </label>
            <el-select
              v-model="menuSave.level"
              placeholder="请选择菜单等级"
              clearable
              class="select"
			  size='large'
              @change="handleLevelChange"
			  popper-class='select-dropdown-rounded'
            >
              <el-option 
                v-for="menu_obj in menu_level" 
                :key="menu_obj.id"
                :label="menu_obj.name" 
                :value="menu_obj.id" 
                class="dialog-option"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item  class="dialog-form-item" prop='icon'>
            <label class="dialog-label">
              <i class="icon-icon-dialog"></i>
              菜单图标
            </label>
            <el-input 
              v-model="menuSave.icon" 
              autocomplete="off" 
              placeholder="请输入菜单图标"
			  size='large'
			  maxlength="20"
			  show-word-limit
              class="input"
            />
          </el-form-item>
          
          <el-form-item  class="dialog-form-item" prop='path'>
            <label class="dialog-label">
              <i class="icon-path-dialog"></i>
              菜单路径
            </label>
            <el-input 
              v-model="menuSave.path" 
              autocomplete="off" 
              placeholder="请输入菜单路径"
              class="input"
			  maxlength="50"
			  show-word-limit
			  size='large'
            />
          </el-form-item>
          
          <el-form-item 
            class="dialog-form-item" 
			prop='parent'
            v-if="menuSave.level && menuSave.level != 1"
          >
            <label class="dialog-label">
              <i class="icon-parent-dialog"></i>
              父菜单
            </label>
            <el-select
              v-model="menuSave.parent"
              placeholder="请选择父菜单"
              filterable
              clearable
              class="select"
			  popper-class='select-dropdown-rounded'
			  size='large'
            >
              <el-option 
                v-for="main_menu in mainMenu" 
                :key="main_menu.id"
                :label="main_menu.name" 
                :value="main_menu.id" 
                class="dialog-option"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
	  
	  <template #footer>
	  	<span class="dialog-footer" v-if="!permissionView">
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
  Refresh,
  Search,
  Plus,
  View,
  Delete,
  EditPen,
  Menu
} from '@element-plus/icons-vue'

export default {
  name: 'PermissionManagement',
  computed: {
    ...mapState(['pathPermission', 'userInfo']),
    calcMinWidth() {
      let visibleButtons = 3
      return Math.max(10, visibleButtons * 48)
    }
  },
  data() {
    return {
      user_list: [],
      permissionView: false,
      permission: {},
      mainMenu: [],
      title: '编辑菜单权限',
      editDialogVisible: false,
      menu_level: [
        { name: '主菜单', id: 1 },
        { name: '子菜单', id: 2 }
      ],
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      page_size_params: {
        page: 1,
        size: 10,
      },
      menu_list: {
        count: 0,
        results: []
      },
      menuSearch: {
        name: '',
        path: '',
        icon: '',
        parent: '',
        level: '',
        create_by: '',
        update_by: ''
      },
      menuSave: {
        id: '',
        name: '',
        path: '',
        icon: '',
        parent: '',
        level: ''
      },
	  permissionRules: {
	    name: [{
	      required: true,
	      message: '菜单名称不能为空',
	      trigger: 'blur',
	    }],
		path: [{
		  required: true,
		  message: '菜单路径不能为空',
		  trigger: 'blur',
		}],
		icon: [{
		  required: true,
		  message: '菜单图标不能为空',
		  trigger: 'blur',
		}],
	    parent: [{
	      required: true,
	      message: '请选择父菜单',
	      trigger: 'change',
	    }],
	    level: [{
	      required: true,
	      message: '请选择菜单等级',
	      trigger: 'change',
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
    EditPen,
    Menu
  },
  methods: {
    ...mapActions(['getRolePermission']),
    
    formatterLevel(row) {
      return row.level === 1 ? '主菜单' : '子菜单'
    },
    
    handleCurrentChange(page) {
      this.page_size_params.page = page
      this.getPermssions()
    },
    
    handleSizeChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getPermssions()
    },
    
    search() {
      this.page_size_params.page = 1
      this.getPermssions()
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
    
    reset() {
      for (let key in this.menuSearch) {
        this.menuSearch[key] = ''
      }
    },
    
    editMenu(row_data) {
      this.editDialogVisible = true
      this.permissionView = false
      this.title = '编辑菜单权限'
      this.menuSave = { ...row_data }
	  this.$refs.permissionRef.resetFields();
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
	  this.getPermssions()
	},
    
    viewMenu(row_data) {
      this.title = '查看菜单权限'
      this.permissionView = true
      this.editDialogVisible = true
      this.menuSave = { ...row_data }
    },
    
    addMenu() {
      this.title = '新增菜单权限'
      this.permissionView = false
      this.editDialogVisible = true
      this.menuSave = {}
	  this.$refs.permissionRef.resetFields();
    },
    
    save() {
      if (this.menuSave.id) {
        this.updatePermission()
      } else {
        this.createPermission()
      }
    },
    
    handleLevelChange(value) {
      if (value === 1) {
        this.menuSave.parent = ''
      }
    },
    
    async createPermission() {
	  this.$refs['permissionRef'].validate(async (valid, fields)=>{
	    if(valid){
			 const response = await this.$api.createPermission(this.menuSave)
			 if (response.status === 201) {
			   this.editDialogVisible = false
			   this.getPermssions()
			   ElMessage({ message: "保存成功", type: 'success' })
			 }else if(response.status != 400){
				ElMessage({ message: "系统内部异常", type: 'error' })
			 }
	    }
	  })
    },
    
    async updatePermission() {
	  this.$refs['permissionRef'].validate(async (valid, fields)=>{
	    if(valid){
			 const response = await this.$api.updatePermission(this.menuSave.id, this.menuSave)
			 if (response.status === 200) {
			   this.editDialogVisible = false
			   this.menuSave = {}
			   this.getPermssions()
			   ElMessage({ message: "保存成功", type: 'success' })
			 }else if(response.status != 400){
				ElMessage({ message: "系统内部异常", type: 'error' })
			 }
	    }
	  })
      
    },
    
    async deletePermission(id) {
      ElMessageBox.confirm(
        '确定删除此菜单权限？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        const response = await this.$api.deletePermission(id)
        if (response.status === 204) {
          this.getPermssions()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }else if(response.status != 400){
			ElMessage({ message: "系统内部异常", type: 'error' })
		}
      }).catch(() => {})
    },
    
    async getPermssions() {
      const par = {
        page: this.page_size_params.page,
        size: this.page_size_params.size,
        back_list: true
      }
      const params =  Object.assign({}, par, this.sort_params)
      if (this.menuSearch.name) params.name = this.menuSearch.name
      if (this.menuSearch.level) params.level = this.menuSearch.level
      if (this.menuSearch.parent) params.parent = this.menuSearch.parent
      if (this.menuSearch.icon) params.icon = this.menuSearch.icon
      if (this.menuSearch.path) params.path = this.menuSearch.path
      if (this.menuSearch.create_by) params.create_by = this.menuSearch.create_by
      if (this.menuSearch.update_by) params.update_by = this.menuSearch.update_by
      
      try {
        const response = await this.$api.getPermissions(params)
        if (response.status === 200) {
          this.menu_list = { ...response.data }
        }else if(response.status != 400){
		   ElMessage({ message: "系统内部异常", type: 'error' })
		}
      } catch (error) {
        console.error('获取菜单权限失败:', error)
      }
    },
    
    async getMainPermssions() {
      const response = await this.$api.getPermissions({ back_list: true, level: 1 })
      if (response.status === 200) {
        this.mainMenu = [...response.data.results]
      }else if(response.status != 400){
		ElMessage({ message: "系统内部异常", type: 'error' })
	  }
    }
  },
  created() {
    if (!this.userInfo.is_superuser){
        // 重定向到权限页面，并传递from参数
        this.$router.push({name: 'noPermission', query: {from: this.$route.fullPath}})
    } else {
       this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
       this.getPermssions()
       this.getMainPermssions()
    }
  }
}
</script>

<style scoped>
.permission-management-container {
  width: 100%;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
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
  background: var(--qm-bg-2);
  border: none;
  padding: 0px;
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

/* 修改筛选区域的表单样式 */
.filter-card :deep(.el-card__body) {
  padding: 20px 20px 0 20px;
}

.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
}

.filter-form {
  margin-bottom: 0;
}

.form-item-enhanced {
  margin-bottom: 0;
  display: flex;
  align-items: center;
  min-height: 56px;
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
  color: var(--qm-text-2);
  width: 90px;
  margin-right: 10px;
  flex-shrink: 0;
  white-space: nowrap;
}

.label-text {
  white-space: nowrap;
}

.icon-menu,
.icon-level,
.icon-parent,
.icon-icon,
.icon-path,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.icon-menu { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
.icon-level { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-parent { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-icon { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); }
.icon-path { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.icon-updater { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }

/* 调整 el-form-item 的内部布局 */
.filter-form >>> .el-form-item__content {
  display: flex;
  align-items: center;
  flex: 1;
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

.menu-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
}

.menu-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.menu-icon .el-icon {
  font-size: 20px;
}

.menu-info {
  text-align: left;
}

.menu-name {
  font-weight: 500;
  color: var(--qm-text-1);
}

.path-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.icon-path-small {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.path-text {
  color: var(--qm-text-2);
  word-break: break-all;
}

.icon-cell {
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-icon {
  color: var(--qm-text-3);
}

.level-tag {
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
  float: right;
  min-height: 40px;
  background: var(--qm-bg-2);
  z-index: 10;
  position: relative;
  opacity: 1 !important;
  visibility: visible !important;
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
  color: var(--qm-text-2);
}

/* 对话框图标样式 */
.icon-menu-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-level-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8z'/%3E%3Cpath fill='%2394a3b8' d='M12.5 7H11v6l5.25 3.15.75-1.23-4.5-2.67z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-icon-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-path-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-parent-dialog {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2394a3b8' d='M16.5 13c-1.2 0-3.07.34-4.5 1-1.43-.67-3.3-1-4.5-1C5.33 13 1 14.08 1 16.25V19h22v-2.75c0-2.17-4.33-3.25-6.5-3.25zm-4 4.5h-10v-1.25c0-.54 2.56-1.75 5-1.75s5 1.21 5 1.75v1.25zm9 0H14v-1.25c0-.46-.2-.86-.52-1.22.88-.3 1.96-.53 3.02-.53 2.44 0 5 1.21 5 1.75v1.25zM7.5 12c1.93 0 3.5-1.57 3.5-3.5S9.43 5 7.5 5 4 6.57 4 8.5 5.57 12 7.5 12zm0-5.5c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm9 5.5c1.93 0 3.5-1.57 3.5-3.5S18.43 5 16.5 5 13 6.57 13 8.5s1.57 3.5 3.5 3.5zm0-5.5c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.elegant-dialog >>> .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid var(--qm-bg-3);
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
  .permission-management-container {
    padding: 16px;
  }
  
  .filter-card .filter-header,
  .content-card .content-header,
  .content-card .table-wrapper {
    padding: 16px 20px;
  }
}

@media screen and (max-width: 768px) {
  .permission-management-container {
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
  
  .filter-form >>> .el-form-item__content {
    width: 100%;
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