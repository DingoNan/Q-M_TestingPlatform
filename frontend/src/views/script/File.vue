<template>
  <div class="file-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">文件筛选</h3>
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
        <el-form :model="fileSearch" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-file"></i>
                  <span class="label-text">文件名称</span>
                </div>
                <el-input 
                  v-model="fileSearch.name" 
                  placeholder="请输入文件名称" 
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
                  v-model="fileSearch.create_by" 
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
                  v-model="fileSearch.update_by" 
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
            <h3 class="content-title">文件列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总计</span>
                <span class="stat-value">{{ file_list.count || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ page_size_params.page }}</span>
              </div>
            </div>
          </div>
         <el-button 
           v-if="permission.has_add_permission" 
           @click="addFile" 
           type="primary" 
           class="add-btn"
         >
           新增文件
         </el-button>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table 
          :data="file_list.results" 
          :max-height="'calc(100vh - 490px)'" 
          class="elegant-table"
		   @sort-change='handleSortChange'
          :header-row-style="headerRowStyle"
          :show-overflow-tooltip='true'
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
            label="文件名称" 
            prop="name" 
            min-width="150" 
            align="center"
            class-name="file-column"
          >
            <template #default="scope">
              <div class="file-cell">
                <div class="file-icon">
                  <i class="icon-file-small"></i>
                </div>
                <div class="file-info">
                  <span class="filename">{{ scope.row.name }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="文件描述" 
            prop="desc" 
            min-width="200" 
            align="center"
            class-name="desc-column"
          >
            <template #default="scope">
              <div class="desc-cell">
                <i class="icon-desc"></i>
                <span class="desc-text">{{ scope.row.desc || '-' }}</span>
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
                  content="查看文件" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                        type="success" 
                        v-if="permission.has_read_permission" 
                        class="action-btn view-btn"
                        @click.stop="viewFile(scope.row)"
                        circle
                  >
                    <el-icon><View /></el-icon>
                 </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="编辑文件" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
					type="warning" 
					v-if="permission.has_edit_permission" 
					class="action-btn edit-btn"
					@click.stop="editFile(scope.row)"
					circle
                      >
                    <el-icon><EditPen /></el-icon>
                 </el-button>
                </el-tooltip>
                
                <el-tooltip 
                  content="删除文件" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
					type="danger" 
					v-if="permission.has_delete_permission" 
					@click.stop="deleteFile(scope.row.id)" 
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
          :hide-on-single-page="false"
          layout="total, sizes, prev, pager, next, jumper"
          :total="file_list.count"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="input select"
          :background="true"
        />
      </div>
    </el-card>

    <!-- 文件表单对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      :title="title" 
      width="500"
      class="elegant-dialog"
      :close-on-click-modal="false"
      append-to-body
      :show-close='show_close'
    >
      <div class="dialog-content">
        <el-form 
          :model="FileSave" 
          :disabled='fileView' 
          class="dialog-form"
          :rules="fileRules" 
          ref='fileRef' 
          label-position='top'
        >
          <el-form-item class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-desc-dialog"></i>
              文件描述
            </label>
            <el-input 
              v-model="FileSave.desc" 
              type='textarea'
              placeholder="请输入文件描述"
              class="text"
              size='large'
			  :maxlength="100"
			  show-word-limit
              :rows="3"
            />
          </el-form-item>
          
          <el-form-item class="dialog-form-item" v-if='isAdd'>
            <label class="dialog-label">
              <i class="icon-upload"></i>
              上传文件
            </label>
            <div class="upload-wrapper">
              <el-upload
                class="upload-elegant"
                :limit='1'
                :on-remove="handleRemove"
                :auto-upload="false"
                :show-file-list="true"
                :on-change="handleChange"
              >
                <el-button class="upload-btn">请选择文件</el-button>
              </el-upload>
            </div>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
      	<span class="dialog-footer" v-if="!fileView">
      		<el-button @click="editDialogVisible = false" class="dialog-cancel-btn">取消</el-button>
      		<el-button 
      		  type="primary" 
      		  @click="save" 
      		  v-if='permission.has_add_permission || permission.has_edit_permission'
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
import {mapState, mapActions, mapGetters} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { View, Delete, Edit, Plus, EditPen, Refresh, Search } from '@element-plus/icons-vue'

export default{
  name: 'FileManagement',
  components: {
    View,
    Delete,
    Edit,
    Plus,
    EditPen
  },
	computed:{
		...mapState(['pathPermission', 'projectInfo', 'userInfo']),
		calcMinWidth() {
		  let visibleButtons = 0;
		  if (this.permission.has_read_permission) visibleButtons += 1;
		  if (this.permission.has_edit_permission) visibleButtons += 1;
		  if (this.permission.has_delete_permission) visibleButtons += 1;
		  return Math.max(10, visibleButtons * 60);
		}
	},
	data() {
		return {
			user_list: [],
			fileView: false,
			show_close: false,
			permission: {},
			fileSearch:{
				name: '',
				project: '',
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
			title: '新增文件',
			file_list: [],
			isAdd: true,
			editDialogVisible: false,
			ViewVisible: false,
			FileSaveTmp:{
				project: '',
				name: '',
				desc: '',
				raw: ''
			},
			FileSave:{
				project: '',
				name: '',
				desc: '',
				raw: ''
			},
			fileRules: {
				desc: [{
					required: true,
					message: '请输入文件描述',
					trigger: 'blur',
				}],
			},
			role_names: [],
		}
	},
	setup() {
		return {
			Edit,
			Delete,
			Plus,
			View,
			EditPen,
      Refresh,
      Search
		}
	},
	methods:{
		...mapActions(['getRolePermission']),
		
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
    
    headerRowStyle() {
      return {
        'font-weight': '600',
        'color': '#1a1a1a',
        'background-color': '#f8fafc',
        'border-bottom': '1px solid #e2e8f0',
        'height': '56px'
      }
    },
		
		handleCurrentChange(){
			this.getFiles()
		},
		
		async handleChange(file) {
		   this.FileSave.name = file.name
		   const f = file.raw;
		   const buffer = await f.arrayBuffer();
		   const base64 = btoa(
		       new Uint8Array(buffer)
		         .reduce((data, byte) => data + String.fromCharCode(byte), '')
		     );
		   this.FileSave.name = file.name
		   this.FileSave.raw = base64
		   console.log(this.FileSave, '111')
		},
		
		handleRemove(file) {
		   this.FileSave.name = ''
		   this.FileSave.type = ''
		},
		
		handleSizeChange(){
			this.getFiles()
		},
		
		search(){
			this.getFiles()
		},
		
		reset(){
			for(let key in this.fileSearch){
				this.fileSearch[key] = ''
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
		  this.getFiles()
		},
		
		editFile(row_data){
			this.isAdd = false
			this.title = '编辑文件'
			this.fileView = false
			this.getFile(row_data.id)
			this.editDialogVisible = true
			this.$refs.fileRef.resetFields();
		},
		
		viewFile(row_data){
			this.isAdd = false
			this.title = '查看文件'
			this.fileView = true
			this.getFile(row_data.id)
			this.editDialogVisible = true
			this.$refs.fileRef.resetFields();
		},
		
		addFile(){
			this.FileSave = {...this.FileSaveTmp}
			this.fileView = false
			this.title = '新增文件'
			this.editDialogVisible = true
			this.isAdd = true
			this.$refs.fileRef.resetFields();
		},
		
		save(){
			if(this.FileSave.name === ''){
				ElMessage({message: "请上传文件", type: 'error'})
			}else if (this.isAdd){
				this.createFile()
			}else{
				this.updateFile()
			}
		},
		
		async createFile(){
			this.$refs['fileRef'].validate(async (valid, fields)=>{
				if(valid){
					this.FileSave.project = this.projectInfo.id
					const response = await this.$api.createFile(this.FileSave)
					if(response.status === 201){
						this.editDialogVisible = false
						this.getFiles()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		
		async updateFile(){
			this.$refs['fileRef'].validate(async (valid, fields)=>{
				if(valid){
					this.FileSave.project = this.projectInfo.id
					const response = await this.$api.updateFile(this.FileSave.id, this.FileSave)
					if(response.status === 200){
						this.editDialogVisible = false
						this.getFiles()
						ElMessage({message: "保存成功", type: 'success'})
					}
				}
			})
		},
		
		async deleteFile(id){
			ElMessageBox.confirm(
			    '确定删除此文件？删除后数据将无法恢复。',
			    '确认删除',
			    {
			      confirmButtonText: '确认删除',
			      cancelButtonText: '取消',
			      type: 'warning',
			      confirmButtonClass: 'el-button--danger',
			      customClass: 'confirm-dialog'
			    }
			  ).then(async() => {
				  const response = await this.$api.deleteFile(id)
				  if (response.status === 204){
					  this.getFiles()
					  ElMessage({
					    type: 'success',
					    message: '删除成功',
					  })
				  }
				  
			    }).catch(() => {})
		},
		
		async getFile(id){
			const response = await this.$api.getFile(id)
			if (response.status === 200){
				this.FileSave = {...response.data.result}
			}
		},

     async  check_permission(){
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path]}
			const response = await this.$api.check_permission(params)
			if (response.status === 200){
				this.permission = { ...response.data.result }
			}
	 	},
		
		async getFiles(){
			this.fileSearch.project = this.projectInfo.id
			this.FileSave.project = this.projectInfo.id
			const response = await this.$api.getFiles(Object.assign(this.fileSearch, this.page_size_params, this.sort_params))
			if (response.status === 200){
				this.file_list = {...response.data}
			}
		},
	},
	created() {
    this.check_permission()
		this.user_list =  JSON.parse(localStorage.getItem('user_list'))
		this.getFiles()
		
	}
}
</script>

<style scoped>
.file-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: calc(100vh - 75px);
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

.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
}

.inline-form {
  margin-bottom: 0;
}

/* 标签和输入框在一行显示 */
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
  margin-right: 10px;
  color: #475569;
  width: 90px;
  flex-shrink: 0;
  white-space: nowrap;
}

.label-text {
  white-space: nowrap;
}

.icon-file,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
}

/* 为图标添加背景颜色 */
.icon-file {
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

.input-elegant,
.select-elegant {
  flex: 1;
  margin-left: 10px;
}

.input-elegant :deep(.el-input__inner),
.select-elegant :deep(.el-input__inner) {
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 0 12px;
  height: 36px;
  line-height: 36px;
  box-shadow: none;
  transition: all 0.3s ease;
}

.input-elegant :deep(.el-input__inner:hover),
.select-elegant :deep(.el-input__inner:hover) {
  border-color: #cbd5e1;
}

.input-elegant :deep(.el-input__inner:focus),
.select-elegant :deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
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

.file-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.icon-file-small {
  width: 20px;
  height: 20px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='white' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.file-info {
  text-align: left;
}

.filename {
  font-weight: 500;
  color: #1a1a1a;
}

.desc-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.icon-desc {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}

.desc-text {
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

.action-btn {
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
  border-top: 1px solid #f1f5f9;
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

.icon-desc-dialog {
  width: 16px;
  height: 16px;
  display: inline-block;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 4px;
}

.icon-upload {
  width: 16px;
  height: 16px;
  display: inline-block;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 4px;
}

.dialog-input :deep(.el-input__inner),
.dialog-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 12px 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.dialog-input :deep(.el-input__inner:hover),
.dialog-input :deep(.el-textarea__inner:hover) {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input :deep(.el-input__inner:focus),
.dialog-input :deep(.el-textarea__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.upload-wrapper {
  width: 100%;
}

.upload-elegant :deep(.el-upload) {
  width: 100%;
}

.upload-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px dashed #e2e8f0;
  color: #64748b;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
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
  .file-management-container {
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
  .file-management-container {
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
  
  .input-elegant,
  .select-elegant {
    margin-left: 0;
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