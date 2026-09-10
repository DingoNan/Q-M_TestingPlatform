<template>
  <div class="python-container">
    <!-- 左侧模块树 -->
    <div class="sidebar-card elegant-shadow">
      <div class="sidebar-header">
        <div class="sidebar-title-wrapper">
          <i class="icon-tree"></i>
          <h3 class="sidebar-title">模块树</h3>
        </div>
        <el-radio-group v-model="includeChildren" @change="onIncludeChildrenChange" size="small" class="include-children-radio">
          <el-radio-button :label="true">含子节点</el-radio-button>
          <el-radio-button :label="false">仅当前</el-radio-button>
        </el-radio-group>
      </div>
      
      <div class="sidebar-content">
        <div class="search-wrapper">
          <el-input 
            v-model="filterText" 
            placeholder="请输入模块名称" 
            clearable
            class="input"
            size='large'
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-divider class="tree-divider" />
        </div>
        
        <div class="tree-wrapper">
          <el-tree 
            ref="treeRef"
            highlight-current
            node-key='id'
            :expand-on-click-node='false'
            :indent='10'
            @node-click='moduleSelect'
            :current-node-key='selectNode'
            :filter-node-method="filterNode"
            :data='module_tree' 
            :props="{label: 'name', children: 'children'}" 
            class="elegant-tree"
          >
		    <template #empty>
			  <div class="empty-tree">
				<el-empty description="暂无产品数据" :image-size="100">
				  <template #description>
					<div style="margin-bottom: 10px;">暂无产品数据</div>
						<el-button
					  type="primary"
					  @click="goToCreatePlant"
					  class="add-btn"
					>
					  <el-icon><Plus /></el-icon>去新建产品
					</el-button>
				  </template>
				</el-empty>
			  </div>
		    </template>
            <template #default="{ node, data }">
              <div class="custom-tree-node">
                <div class="node-content">
                  <i class="icon-folder-tree" :class="{ 
                    'icon-folder-tree-root': data.id < 0,
                    'icon-page-node': data.node_type === 'page',
                    'icon-module-node': data.node_type === 'module'
                  }"></i>
                  <el-tooltip :content="node.label" :show-after="500">
                    <span class="node-label">{{ node.label }}</span>
                  </el-tooltip>
                </div>
                <div class="node-actions">
                  <el-dropdown @command="controlCommand" trigger="click">
                    <el-button class="node-dropdown-btn" circle size="small">
                      <el-icon><Setting /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item v-if='permission.has_add_permission' :command="{ action: 'add', node: node }">
                          <el-icon><Plus /></el-icon>新增
                        </el-dropdown-item>
                        <el-dropdown-item v-if='permission.has_edit_permission && node.data.id > 0' divided :command="{ action: 'edit', node: node }">
                          <el-icon><EditPen /></el-icon>编辑
                        </el-dropdown-item>
                        <el-dropdown-item v-if='permission.has_delete_permission && node.data.id > 0' divided :command="{ action: 'delete', node: node }" class="danger-item">
                          <el-icon><Delete /></el-icon>删除
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </div>
            </template>
          </el-tree>
        </div>
        
        <div class="tree-actions">
          <el-divider class="tree-divider" />
          <div class="tree-buttons">
            <el-button @click="expandAllNodes" class="tree-btn" type='success'>
              <el-icon><Expand /></el-icon>全部展开
            </el-button>
            <el-button @click="collapseAllNodes" class="tree-btn">
              <el-icon><Fold /></el-icon>全部折叠
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧主要内容区域 -->
    <div class="main-content">
      <!-- 搜索筛选区域 -->
      <el-card class="filter-card elegant-shadow">
        <div class="filter-header">
          <div class="header-title-section">
            <i class="icon-search"></i>
            <h3 class="filter-title">用户函数筛选</h3>
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
        
        <!-- 筛选表单 -->
        <div class="filter-form-wrapper">
          <el-form :model="pythonSearch" class="filter-form inline-form">
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-function"></i>
                    <span>函数名称</span>
                  </div>
                  <el-input 
                    v-model="pythonSearch.name" 
                    placeholder="请输入函数名称" 
                    clearable
                    class="input"
                    size='large'
                  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-creator"></i>
                    <span>创建人</span>
                  </div>
                  <el-select
                    v-model="pythonSearch.create_by" 
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
                <el-form-item class="form-item-enhanced">
                  <div class="label-with-icon">
                    <i class="icon-updater"></i>
                    <span>更新人</span>
                  </div>
                  <el-select
                    v-model="pythonSearch.update_by" 
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
              <h3 class="content-title">用户函数管理</h3>
              <div class="stats-info">
                <div class="stat-item">
                  <span class="stat-label">总计</span>
                  <span class="stat-value">{{ page_list.count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">当前页</span>
                  <span class="stat-value">{{ page_size_params.page }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="content-action-section">
            <el-button 
              v-if='permission.has_add_permission' 
              @click="addPython" 
              type="primary" 
              class="add-btn"
            >
              <el-icon><Plus /></el-icon>新增函数
            </el-button>
          </div>
        </div>

        <!-- 表格区域 -->
        <div class="table-section">
          <div class="table-wrapper">
            <el-table 
              :data="page_list.results" 
              class="elegant-table"
			  @sort-change='handleSortChange'
              :header-row-style="headerRowStyle"
              :show-overflow-tooltip='true'
              :max-height="'calc(100vh - 485px)'" 
            >
              <el-table-column label="序号" width="70" type="index" align="center" class-name="index-column">
                <template #default="scope">
                  <div class="index-cell">
                    {{ scope.$index + 1 + (page_size_params.page - 1) * page_size_params.size }}
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column label="函数名称" prop="name" width="150" align="center" class-name="function-column">
                <template #default="scope">
                  <div class="function-cell">
                    <div class="function-icon">
                      <el-icon>
                        <DataLine />
                      </el-icon>
                    </div>
                    <span class="function-name">{{ scope.row.name }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column label="函数描述" prop="desc" min-width="180" align="center" class-name="desc-column" />
              
              <el-table-column label="所属模块" prop="module_name" width="150" align="center" class-name="module-column" />
              
              <el-table-column label="创建人" prop="create_by_name" width="120" align="center" class-name="creator-column" />
              
              <el-table-column label="更新人" prop="update_by_name" width="120" align="center" class-name="updater-column" />
              
              <el-table-column label="创建时间" prop="create_time" sortable="custom"  width="180" align="center" class-name="time-column">
                <template #default="scope">
                  <div class="time-cell">
                    <i class="icon-time"></i>
                    <span>{{ formatTime(scope.row.create_time) }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column label="更新时间" prop="update_time" sortable="custom"  width="180" align="center" class-name="time-column">
                <template #default="scope">
                  <div class="time-cell">
                    <i class="icon-time"></i>
                    <span>{{ formatTime(scope.row.update_time) }}</span>
                  </div>
                </template>
              </el-table-column>
              
              <el-table-column align="center" :width='calcMinWidth' label="操作" class-name="action-column" fixed="right">
                <template #default="scope">
                  <div class="action-buttons">
                    <el-tooltip content="查看函数" placement="top" effect="dark">
                      <el-button 
                        type="success" 
                        v-if="permission.has_read_permission" 
                        class="action-btn view-btn"
                        @click.stop="viewPython(scope.row)"
                        circle
                      >
                        <el-icon><View /></el-icon>
                      </el-button>
                    </el-tooltip>
                    
                    <el-tooltip content="编辑函数" placement="top" effect="dark">
                      <el-button 
                        type="warning" 
                        v-if="permission.has_read_permission" 
                        class="action-btn edit-btn"
                        @click.stop="editPython(scope.row)"
                        circle
                      >
                        <el-icon><EditPen /></el-icon>
                      </el-button>
                    </el-tooltip>
                    
                    <el-tooltip content="删除函数" placement="top" effect="dark">
                      <el-button 
                        type="danger" 
                        v-if="permission.has_read_permission" 
                        class="action-btn delete-btn"
                        @click.stop="deletePython(scope.row.id)"
                        circle
                      >
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </el-tooltip>
                    
                    <el-tooltip content="选择函数" placement="top" effect="dark" v-if="isCanChoose === true">
                      <el-button 
                        type="primary" 
                        class="action-btn choose-btn"
                        @click.stop="choosePythonFunc(scope.row)"
                      >
                        <el-icon><Select /></el-icon>
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
              :total="page_list.count"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              class="select input"
			  style='float: right'
              :background="true"
            />
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 编辑抽屉 -->
    <el-dialog 
      v-model="editDrawerVisible" 
      direction="rtl" 
      :title="title" 
      fullscreen
      destroy-on-close
    >
      <div class="drawer-content">
        <el-form 
          :model="PythonSave" 
          label-position="top" 
          :disabled='funcView' 
          :rules="pythonRules" 
          ref='pythonRef'
          class="drawer-form"
        >
          <!-- 函数名称 -->
          <el-form-item  prop="name" class="drawer-form-item">
            <div class="drawer-label-container">
              <div class="drawer-label">
                <i class="icon-function-dialog"></i>
                函数名称
              </div>
              <div class="form-tips">函数名称请和函数体函数名保持一致</div>
            </div>
            <el-input 
              v-model="PythonSave.name" 
              autocomplete="off" 
              placeholder="请输入函数名称"
              class="input"
              size='large'
			  maxlength="20"
			  show-word-limit
            />
          </el-form-item>
          
          <!-- 函数说明 -->
          <el-form-item  prop='desc' class="drawer-form-item">
            <div class="drawer-label-container">
              <div class="drawer-label">
                <i class="icon-desc-dialog"></i>
                函数说明
              </div>
            </div>
            <el-input 
              v-model="PythonSave.desc" 
              autocomplete="off"  
              :autosize="{ minRows: 2, maxRows: 4 }" 
              type="textarea" 
              placeholder="请输入函数说明"
			  maxlength="200"
			  show-word-limit
              class="text"
            />
          </el-form-item>
          
          <!-- 所属模块 - 修改为两行布局 -->
          <el-form-item  prop='module' class="drawer-form-item drawer-form-item-two-rows">
            <div class="drawer-label-container" style='width: 100%'>
              <div class="drawer-label">
                <i class="icon-module-dialog"></i>
                所属模块
              </div>
              <div class="form-tips" v-if="!funcView">请选择函数所属的模块</div>
              <el-cascader
                collapse-tags 
                v-model='PythonSave.module' 
                :options="module_tree" 
                :props="editProps" 
                clearable
                class="cascader"
                size='large'
                placeholder="请选择所属模块"
                style='width: 100%'
                :disabled="funcView"
              />
            </div>
          </el-form-item>
          
          <!-- 折叠面板 -->
          <el-collapse v-model="activeNames" class="elegant-collapse">
            <el-collapse-item name="0">
              <template #title>
                <div class="collapse-title">
                  <i class="icon-import"></i>
                  <span>导入模块</span>
                </div>
              </template>
              <BodyEdit 
                :bind_case_data='bind_case_data' 
                v-model='PythonSave.package' 
                lang='python' 
                height="150px"
                class="body-editor"
              />
            </el-collapse-item>
            
            <el-collapse-item name="1">
              <template #title>
                <div class="collapse-title">
                  <i class="icon-script"></i>
                  <span>函数体</span>
                </div>
              </template>
              <BodyEdit 
                :bind_case_data='bind_case_data' 
                v-model='PythonSave.script' 
                lang='python' 
                height="400px"
                class="body-editor"
              />
            </el-collapse-item>
          </el-collapse>
        </el-form>
      </div>
      
      <template #footer>
        <span class="dialog-footer" v-if='!funcView'>
          <el-button @click="editDrawerVisible = false" class="drawer-cancel-btn">取消</el-button>
          <el-button 
            type="primary" 
            @click="save" 
            class="drawer-confirm-btn"
            v-if='permission.has_add_permission || permission.has_edit_permission'
          >
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 模块编辑对话框 -->
    <el-dialog v-model="editNodeVisible" :title="moduleTitle" width='450' class="elegant-dialog" style='border-radius: 12px !important;'>
      <div class="dialog-content">
        <el-form :model="nodeSave" label-position='top' :rules="nodeRules" ref='nodeRef' class="dialog-form" :disabled="nodeView">
          <el-form-item  prop='name' class="dialog-form-item">
            <label class="dialog-label">
              <i class="icon-module"></i>
              模块名称
            </label>
            <el-input v-model="nodeSave.name" size='large' autocomplete="off" placeholder="请输入模块名称" class="input"/>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer" v-if='!nodeView'>
          <el-button @click="editNodeVisible = false" class="dialog-cancel-btn">取消</el-button>
          <el-button type="primary" @click="saveModule" class="dialog-confirm-btn">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import {mapState, mapActions} from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  View, 
  Delete, 
  Plus, 
  EditPen, 
  Refresh, 
  Search, 
  DataLine, 
  Select,
  Setting,
  Expand,
  Fold
} from '@element-plus/icons-vue'
import BodyEdit from './BodyEdit.vue'

export default{
  components:{
    BodyEdit
  },
  props: {
    'isCanChoose': {
      type: Boolean,
      default: false,
    },
  },
  computed:{
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),
    choosePythonFuncVisible: {
      get(){
        return this.choosePythonFuncVisible
      },
      set(value){
        this.$emit('update:choosePythonFuncVisible', value)
      }
    },
    calcMinWidth() {
      let visibleButtons = 0;
      if (this.permission.has_read_permission) visibleButtons += 1;
      if (this.permission.has_edit_permission) visibleButtons += 1;
      if (this.permission.has_delete_permission) visibleButtons += 1;
      if (this.isCanChoose === true) visibleButtons += 1;
      return Math.max(10, visibleButtons * 60);
    }
  },
  emits: ['update:choosePythonFuncVisible', 'setPythonFuncData'],
  data() {
    return {
      bind_case_data: [],
      activeNames: ['1'],
      funcView: false,
      props: {
        multiple: true,
        emitPath: false,
        value: 'id',
        label: 'name',
      },
      editProps:{
        emitPath: false,
        value: 'id',
        label: 'name',
        checkStrictly: true,
      },
      permission: {},
      pythonSearch:{
        name: '',
        project: '',
        module: '',
        module_list: [],
        create_by: '',
        update_by: '',
      },
      pythonSearchTmp: {},
      page_size_params: {
        page: 1,
        size: 10,
      },
	  sort_params: {
	    ordering: '-update_time',  // 排序字段，例如 'create_time', '-create_time', 'update_time', '-update_time'
	  },
      title: 'Python函数',
      isAdd: true,
      editDrawerVisible: false,
      page_list: [],
      plant_module_list: [],
      PythonSaveTmp: {},
      PythonSave:{
        project: '',
        name: '',
        desc: '',
        package: 'import random',
        module: '',
        script: 'def functionName(max_value: int):\n    pass'
      },
      pythonRules: {
        name: [{
          required: true,
          message: '请输入函数名称',
          trigger: 'blur',
        }],
        desc: [{
          required: true,
          message: '请输入函数描述',
          trigger: 'blur',
        }],
        module: [{
          required: true,
          message: '请选择所属模块',
          trigger: 'change',
        }],
      },
      // 树结构相关数据
      filterText: '',
      selectNode: 0,
      includeChildren: true,
      module_tree: [],
      nodeRules: {
        name: [{
          required: true,
          message: '模块名称不能为空',
          trigger: 'blur',
        }],
      },
      nodeSave:{
        project: '',
        name: '',
        plant: '',
        parent: 0,
        node_type: 'module', // 'module' 或 'page'
      },
      editNodeVisible: false,
      moduleTitle: '',
      nodeView: false,
      currentNode: {},
      user_list: [],
    }
  },
  watch: {
    filterText(val) {
      if (this.$refs.treeRef) {
        this.$refs.treeRef.filter(val)
      }
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
     this.getPythons()
   },
   
    choosePythonFunc(data){
      this.$emit('update:choosePythonFuncVisible', false)
      this.$emit('setPythonFuncData', data)
    },
    
    handleCurrentChange(){
      this.getPythons()
    },
    
    handleSizeChange(){
      this.page_size_params.page = 1
      this.getPythons()
    },
    
    search(){
      this.page_size_params.page = 1
      this.getPythons()
    },
    
    reset(){
      for(let key in this.pythonSearch){
        if(key === 'module_list'){
          continue
        }else{
          this.pythonSearch[key] = ''
        }
      }
      this.getPythons()
    },
    
    editPython(row_data){
      this.isAdd = false
      this.title= '编辑用户函数'
      this.funcView = false
      this.getPython(row_data.id)
      this.editDrawerVisible = true
    },
    
    viewPython(row_data){
      this.isAdd = false
      this.title= '查看用户函数'
      this.funcView = true
      this.getPython(row_data.id)
      this.editDrawerVisible = true
    },
    
    addPython(){
      this.title= '新增用户函数' 
      this.funcView = false
      this.PythonSave = {...this.PythonSaveTmp}
      this.editDrawerVisible = true
      this.isAdd = true
	  const node = this.$refs.treeRef.getCurrentNode()
	  if ( node && node.id > 0){
	    this.PythonSave.module = node.id
	  }
      this.$nextTick(() => {
        if (this.$refs.pythonRef) {
          this.$refs.pythonRef.resetFields()
        }
      })
    },
    
    save(){
      if (this.isAdd){
        this.createPython()
      } else {
        this.updatePython()
      }
    },
	
    goToCreatePlant(){
    	this.$router.push({name: 'plant'})
    },
	
    async createPython(){
      if(this.PythonSave.module < 0){
        ElMessage({message: "所属模块不能选择根节点", type: 'error'})
        return 
      }
      this.$refs['pythonRef'].validate(async (valid, fields)=>{
        if(valid){
          this.PythonSave.project = this.projectInfo.id
          const response = await this.$api.createPython(this.PythonSave)
          if(response.status === 201){
            this.editDrawerVisible = false
            this.getPythons()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async updatePython(){
      if(this.PythonSave.module < 0){
        ElMessage({message: "所属模块不能选择根节点", type: 'error'})
        return 
      }
      this.$refs['pythonRef'].validate(async (valid, fields)=>{
        if(valid){
          this.PythonSave.project = this.projectInfo.id
          const response = await this.$api.updatePython(this.PythonSave.id, this.PythonSave)
          if(response.status === 200){
            this.editDrawerVisible = false
            this.getPythons()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async deletePython(id){
      ElMessageBox.confirm(
        '确定删除此用户函数？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async() => {
        const response = await this.$api.deletePython(id)
        if (response.status === 204){
          this.getPythons()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
    async getPython(id){
      const response = await this.$api.getPython(id)
      if (response.status === 200){
        this.PythonSave = {...response.data.result}
      }
    },
    
    async getPythons(){
      this.pythonSearch.project = this.projectInfo.id
      this.PythonSave.project = this.projectInfo.id
      this.pythonSearch.module = this.pythonSearch.module_list.join(',')
      const response = await this.$api.getPythons(Object.assign(this.pythonSearch, this.page_size_params, this.sort_params))
      if (response.status === 200){
        this.page_list = {...response.data}
      }
    },
    
    // 树结构相关方法
    filterNode(value, data) {
      if (!value) return true
      return data?.name?.includes(value) || false
    },
    
    moduleSelect(node){
      if (!node) {
        this.selectNode = null
        this.pythonSearch.module_list = []
        this.getPythons()
        return
      }
      // 如果点击的是已选中的节点，取消选中
      if (this.selectNode === node.id) {
        this.$refs.treeRef?.setCurrentKey(null)
        this.selectNode = null
        this.pythonSearch.module_list = []
        localStorage.removeItem('python_node')
        this.getPythons()
        return
      }
      localStorage.setItem('python_node', JSON.stringify(node))
      this.selectNode = node.id
      if (this.includeChildren) {
        this.pythonSearch.module_list = this.getAllIds(node)
      } else {
        this.pythonSearch.module_list = [node.id]
      }
      this.getPythons()
    },
    
    onIncludeChildrenChange() {
      const node = this.$refs.treeRef?.getCurrentNode()
      if (node) {
        if (this.includeChildren) {
          this.pythonSearch.module_list = this.getAllIds(node)
        } else {
          this.pythonSearch.module_list = [node.id]
        }
        this.getPythons()
      }
    },
    
    getAllIds(node) {
      if (!node) return []
      const ids = [node.id]
      if (node.children && Array.isArray(node.children)) {
        node.children.forEach(child => {
          ids.push(...this.getAllIds(child))
        })
      }
      return ids
    },
    
    controlCommand(command){
      this.currentNode = command
      if(command.action === 'add'){
        this.editNodeVisible = true
        this.nodeView = false
        this.moduleTitle = '新增模块'
        this.nodeSave = {
          project: '',
          name: '',
          plant: '',
          parent: 0,
          node_type: 'module'
        }
      }else if(command.action === 'edit'){
        this.nodeSave = {...this.currentNode.node.data}
        this.editNodeVisible = true
        this.nodeView = false
        this.moduleTitle = '编辑模块'
      }else if(command.action === 'delete'){
        this.deleteModule(this.currentNode.node.data.id)
      }
    },
    
    async saveModule(){
      this.$refs['nodeRef'].validate(async (valid, fields)=>{
        if (valid){
          if (this.currentNode.action === 'add'){
            await this.createModule()
          }else if(this.currentNode.action === 'edit'){
            await this.updateModule()
          }
        }
      })
    },
    
    async createModule(){
      const saveData = {...this.nodeSave}
      saveData.project = this.projectInfo.id
      
      if (this.currentNode.node.data.id < 0){
        saveData.plant = -this.currentNode.node.data.id
        saveData.parent = null
      }else{
        saveData.plant = this.currentNode.node.data.plant_id || this.projectInfo.id
        saveData.parent = this.currentNode.node.data.id
      }
      
      const response = await this.$api.createModule(saveData)
      if(response.status === 201){
        this.editNodeVisible = false
        this.getPlantModule()
        ElMessage({message: "保存成功", type: 'success'})
      }
    },
    
    async updateModule(){
      const saveData = {...this.nodeSave}
      saveData.project = this.currentNode.node.data.project_id || this.projectInfo.id
      saveData.plant = this.currentNode.node.data.plant_id || this.projectInfo.id
      
      const response = await this.$api.updateModule(saveData.id, saveData)
      if(response.status === 200){
        this.editNodeVisible = false
        this.getPlantModule()
        ElMessage({message: "保存成功", type: 'success'})
      }
    },
    
    async deleteModule(id){
      ElMessageBox.confirm(
        '确定删除此模块？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async() => {
        const response = await this.$api.deleteModule(id)
        if (response.status === 204){
          this.getPlantModule()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
    expandAllNodes() {
      const allNodes = this.$refs.treeRef.store._getAllNodes()
      allNodes.forEach(node => {
        node.expanded = true
      })
    },
    
    collapseAllNodes() {
      const allNodes = this.$refs.treeRef.store._getAllNodes()
      allNodes.forEach(node => {
        node.expanded = false
      })
    },

     async  check_permission(){
			const params = {user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path]}
			const response = await this.$api.check_permission(params)
			if (response.status === 200){
				this.permission = { ...response.data.result }
			}
 	 	},
    
    async getPlantModule(){
      const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
      if (response.status === 200){
        this.module_tree = response.data.results
      }
    },
    
  },
  created() {
    this.check_permission()
    this.PythonSaveTmp = JSON.parse(JSON.stringify(this.PythonSave))
    this.pythonSearchTmp = {...this.pythonSearch}
    this.user_list = JSON.parse(localStorage.getItem('user_list'))
    
    const node = JSON.parse(localStorage.getItem('python_node'))
    if (node) {
      this.$nextTick(() => {
        if (this.$refs.treeRef) {
          this.$refs.treeRef.setCurrentKey(node.id)
        }
      })
      this.pythonSearch.module_list = this.getAllIds(node)
    }
    
    this.getPlantModule()
    this.getPythons()
  }
}
</script>

<style scoped>
.python-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 20px 15px 15px 15px;
  box-sizing: border-box;
  display: flex;
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

/* 侧边栏样式 */
.sidebar-card {
  width: 320px;
  flex-shrink: 0;
  background: white;
  border: none;
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.sidebar-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.include-children-radio {
  flex-shrink: 0;
}

.icon-tree {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border-radius: 8px;
  position: relative;
}

.icon-tree::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 8px;
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
}

.icon-tree::after {
  content: '';
  position: absolute;
  top: 15px;
  left: 7px;
  width: 10px;
  height: 6px;
  background: white;
  clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
}

.sidebar-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  flex: 1;
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.search-wrapper {
  padding: 16px 24px 0;
}

.tree-divider {
  margin: 16px 0;
  border-color: #f1f5f9;
}

.tree-wrapper {
  flex: 1;
  padding: 0 24px;
  min-height: 0;
  overflow-y: auto;
}

.elegant-tree >>> .el-tree {
  background: transparent;
}

.elegant-tree >>> .el-tree-node__content {
  height: 40px;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: all 0.3s ease;
}

.elegant-tree >>> .el-tree-node__content:hover {
  background: #f1f8ff;
}

.elegant-tree >>> .el-tree-node.is-current > .el-tree-node__content {
  background: #ebf5ff;
  position: relative;
}

.elegant-tree >>> .el-tree-node.is-current > .el-tree-node__content::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #3b82f6 0%, #1d4ed8 100%);
  border-radius: 0 2px 2px 0;
}

/* 修复：节点名称过长时设置按钮被隐藏的问题 */
.custom-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
  min-width: 0;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  overflow: hidden;
  min-width: 0;
  max-width: calc(100% - 32px);
}

.icon-folder-tree {
  width: 16px;
  height: 16px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2364748b' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-folder-tree-root {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z'/%3E%3C/svg%3E");
}

.icon-page-node {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-module-node {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
}

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  color: #334155;
  min-width: 0;
}

.node-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
  margin-left: 8px;
}

.elegant-tree >>> .el-tree-node__content:hover .node-actions {
  opacity: 1;
}

.node-dropdown-btn {
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  color: #94a3b8;
  transition: all 0.3s ease;
}

.node-dropdown-btn:hover {
  background: #f1f5f9;
  color: #64748b;
}

.danger-item {
  color: #ef4444;
}

.tree-actions {
  padding: 0 24px 20px;
}

.tree-buttons {
  display: flex;
  gap: 12px;
}

.tree-btn {
  flex: 1;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
}

.tree-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.tree-btn .el-icon {
  margin-right: 6px;
  font-size: 14px;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-width: 0;
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

/* 筛选表单 */
.filter-form-wrapper {
  padding: 25px 24px 0px 24px;
}

.inline-form {
  margin-bottom: 0;
}

.form-item-enhanced {
  margin-bottom: 25px;
  display: flex;
  flex-direction: row;
  align-items: center;
  height: 40px;
}

.form-item-enhanced :deep(.el-form-item__content) {
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

.icon-function,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-function {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-5 3c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm4 8h-8v-1c0-1.33 2.67-2 4-2s4 .67 4 2v1z'/%3E%3C/svg%3E");
}

.icon-creator {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-updater {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
}

/* 查询区渐变图标 */
.label-with-icon .icon-function,
.label-with-icon .icon-creator,
.label-with-icon .icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.label-with-icon .icon-function { background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); }
.label-with-icon .icon-creator { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.label-with-icon .icon-updater { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }


/* 内容卡片 */
.content-card {
  flex: 1;
  background: white;
  border: none;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.content-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.content-title-section {
  display: flex;
  align-items: center;
  gap: 20px;
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

.content-action-section {
  display: flex;
  align-items: center;
  gap: 12px;
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
.table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
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

/* 序号单元格 */
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

/* 函数单元格 */
.function-cell {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
}

.function-icon {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.function-icon .el-icon {
  font-size: 20px;
}

.function-name {
  font-weight: 500;
  color: #1a1a1a;
}

/* 时间单元格 */
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

.action-btn.view-btn:hover {
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
}

.action-btn.edit-btn:hover {
  box-shadow: 0 6px 20px rgba(245, 158, 11, 0.4);
}

.action-btn.delete-btn:hover {
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.action-btn.choose-btn:hover {
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
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

.action-btn.choose-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
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

/* 分页组件 */
.pagination-wrapper {
  padding: 20px 24px 0px 24px;
  border-top: 1px solid #f1f5f9;
  flex-shrink: 0;
  
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

/* =============== 抽屉样式 - 优化部分 =============== */
.drawer-content {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.drawer-form {
  margin: 0;
}

/* 抽屉表单项样式优化 */
.drawer-form-item {
  margin-bottom: 28px;
}

.drawer-form-item-two-rows {
  display: flex;
  flex-direction: column;
}

.drawer-label-container {
  margin-bottom: 12px;
}

.drawer-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.form-tips {
  font-size: 12px;
  color: #64748b;
  font-style: italic;
  line-height: 1.4;
}

/* 抽屉图标 */
.icon-function-dialog,
.icon-desc-dialog,
.icon-module-dialog,
.icon-import,
.icon-script {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
}

.icon-function-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-5 3c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm4 8h-8v-1c0-1.33 2.67-2 4-2s4 .67 4 2v1z'/%3E%3C/svg%3E");
}

.icon-desc-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-module-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
}

.icon-import {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z'/%3E%3C/svg%3E");
}

.icon-script {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.drawer-input >>> .el-input__inner,
.drawer-textarea >>> .el-textarea__inner,
.drawer-cascader >>> .el-input__inner {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.drawer-input >>> .el-input__inner,
.drawer-cascader >>> .el-input__inner {
  height: 44px;
  line-height: 44px;
}

.drawer-input >>> .el-input__inner:hover,
.drawer-textarea >>> .el-textarea__inner:hover,
.drawer-cascader >>> .el-input__inner:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.drawer-input >>> .el-input__inner:focus,
.drawer-textarea >>> .el-textarea__inner:focus,
.drawer-cascader >>> .el-input__inner:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.drawer-cascader {
  width: 100%;
}

.drawer-textarea >>> .el-textarea__inner {
  padding: 12px 16px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

/* 折叠面板 */
.elegant-collapse {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  margin-top: 10px;
}

.elegant-collapse >>> .el-collapse-item__header {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
  padding: 0 20px;
  height: 56px;
  line-height: 56px;
  font-weight: 600;
  color: #334155;
}

.elegant-collapse >>> .el-collapse-item__wrap {
  border-bottom: none;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.body-editor {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  margin: 16px;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.drawer-cancel-btn {
  padding: 10px 24px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s ease;
}

.drawer-cancel-btn:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.drawer-confirm-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.drawer-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

/* 对话框样式 */
.elegant-dialog >>> .el-dialog {
  border-radius: 20px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.elegant-dialog >>> .el-dialog__header {
  padding: 24px 24px 0;
  margin: 0;
}

.elegant-dialog >>> .el-dialog__title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 12px;
}

.elegant-dialog >>> .el-dialog__title::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
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
  margin-bottom: 24px;
}

.dialog-form-item:last-child {
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

.dialog-input >>> .el-input__inner,
.dialog-cascader >>> .el-input__inner,
.dialog-select >>> .el-input__inner {
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: white;
  padding: 0 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.dialog-input >>> .el-input__inner:hover,
.dialog-cascader >>> .el-input__inner:hover,
.dialog-select >>> .el-input__inner:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input >>> .el-input__inner:focus,
.dialog-cascader >>> .el-input__inner:focus,
.dialog-select >>> .el-input__inner:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.elegant-dialog >>> .el-dialog__footer {
  padding: 16px 24px 24px;
  border-top: 1px solid #f1f5f9;
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
  .python-container {
    padding: 16px;
    flex-direction: column;
  }
  
  .sidebar-card {
    width: 100%;
    margin-bottom: 20px;
  }
  
  .sidebar-content {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .search-wrapper {
    width: 100%;
  }
  
  .tree-wrapper {
    flex: 1;
    min-height: 300px;
  }
  
  .tree-actions {
    width: 100%;
    margin-top: 20px;
  }
  
  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .content-action-section {
    width: 100%;
    justify-content: flex-end;
  }
}

@media screen and (max-width: 768px) {
  .python-container {
    padding: 12px;
  }
  
  .filter-header {
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
  
  .form-item-enhanced {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 16px;
    min-height: auto;
  }
  
  .label-with-icon {
    margin-right: 0;
    margin-bottom: 8px;
    min-width: auto;
    width: 100%;
  }
  
  .input,
  .select {
    width: 100%;
  }
  
  .filter-form >>> .el-form-item__content {
    width: 100%;
  }
  
  .table-wrapper {
    overflow-x: auto;
  }
  
  .elegant-table {
    min-width: 1000px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .drawer-form-item {
    margin-bottom: 20px;
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

.sidebar-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.content-card {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

/* 抽屉动画 */
@keyframes slideInFromRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 滚动条美化 */
.table-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

.drawer-content::-webkit-scrollbar {
  width: 8px;
}

.drawer-content::-webkit-scrollbar-track {
  background: #f8fafc;
  border-radius: 4px;
}

.drawer-content::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 4px;
}

.drawer-content::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>

<style>
html body .el-radio-group.include-children-radio .el-radio-button.is-active .el-radio-button__inner {
  background: #10b981 !important;
  color: #ffffff !important;
  border-color: #10b981 !important;
  box-shadow: -1px 0 0 0 #10b981 !important;
}

html body .el-radio-group.include-children-radio .el-radio-button:first-child .el-radio-button__inner {
  border-radius: 6px 0 0 6px !important;
}

html body .el-radio-group.include-children-radio .el-radio-button:last-child .el-radio-button__inner {
  border-radius: 0 6px 6px 0 !important;
}

html body .el-radio-group.include-children-radio .el-radio-button__inner {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 0 !important;
  border: 1px solid #e2e8f0 !important;
  background: #ffffff;
  color: #64748b;
  transition: all 0.3s ease;
}

.tree-wrapper::-webkit-scrollbar {
  width: 6px;
}

.tree-wrapper::-webkit-scrollbar-track {
  background: #f8fafc;
  border-radius: 4px;
}

.tree-wrapper::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 4px;
}

.tree-wrapper::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>