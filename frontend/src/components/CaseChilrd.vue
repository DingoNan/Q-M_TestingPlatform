<template>
  <!-- 模块编辑对话框 -->
  <el-dialog v-model="editModuleVisible" :title="moduleTitle" width='450' class="elegant-dialog">
    <div class="dialog-content">
      <el-form :model="moduleSave" label-position='top' :rules="moduleRules" ref='moduleRef' class="dialog-form" :disabled="moduleView">
        <el-form-item label="模块名称" prop='name' class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-module"></i>
            模块名称
          </label>
          <el-input v-model="moduleSave.name" autocomplete="off" placeholder="请输入模块名称" class="dialog-input"/>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <span class="dialog-footer" v-if='!moduleView'>
        <el-button @click="editModuleVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" @click="save" class="dialog-confirm-btn">保存</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 用例编辑对话框 -->
  <el-dialog v-model="editCaseVisible" :title="title" width="450" :close-on-click-modal='false' class="elegant-dialog">
    <div class="dialog-content">
      <el-form :model="caseForm" label-position='top' :disabled='caseView' :rules="caseRules" ref='caseRef' class="dialog-form">
        <el-form-item label="用例名称" prop="name" class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-case"></i>
            用例名称
          </label>
          <el-input v-model="caseForm.name" autocomplete="off" placeholder="请输入用例名称" class="dialog-input"/>
        </el-form-item>
        
        <el-form-item label="所属模块" prop='module' class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-folder"></i>
            所属模块
          </label>
          <el-cascader 
            placeholder='请选择或输入模块名称' 
            collapse-tags 
            v-model="caseForm.module" 
            :options="plant_module_list" 
            :props="moduleEditProps" 
            clearable
            filterable
            class="dialog-cascader"
          />
        </el-form-item>
        
        <el-form-item label="用例标签" prop="tag" class="dialog-form-item">
          <label class="dialog-label">
            <i class="icon-tag-dialog"></i>
            用例标签
          </label>
          <el-select v-model="caseForm.tag" placeholder="请选择用例标签" clearable multiple class="dialog-select">
            <el-option v-for="tag in tag_list" :label='tag.name' :value="tag.id" />
          </el-select>
        </el-form-item>
      </el-form>
    </div>
    
    <template #footer>
      <span class="dialog-footer" v-if='!caseView'>
        <el-button @click="editCaseVisible = false" class="dialog-cancel-btn">取消</el-button>
        <el-button type="primary" v-if='title === "新增用例"' @click="createCase" class="dialog-confirm-btn">确认</el-button>
        <el-button type="primary" v-if='title === "编辑用例"' @click="updateCase" class="dialog-confirm-btn">确认</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- 主容器 -->
  <div class="case-management-container">
    <!-- 左侧模块树 -->
    <div class="sidebar-card elegant-shadow">
      <div class="sidebar-header">
        <i class="icon-tree"></i>
        <h3 class="sidebar-title">模块管理</h3>
        <el-tag size="small" type="info" effect="plain" class="sidebar-tag">树状视图</el-tag>
      </div>
      
      <div class="sidebar-content">
        <div class="search-wrapper">
          <el-input 
            v-model="filterText" 
            placeholder="请输入模块名称" 
            clearable
            class="tree-search-input"
            :prefix-icon="Search"
          />
          <el-divider class="tree-divider" />
        </div>
        
        <div class="tree-wrapper">
          <el-tree 
            ref="treeRef"
            highlight-current
            node-key='id'
            :expand-on-click-node='false'
            @current-change='moduleSelect'
            :current-node-key='selectNode'
            :filter-node-method="filterNode"
            :data='plant_module_list' 
            :props="{label: 'name'}" 
            class="elegant-tree"
          >
            <template #default="{ node, data }">
              <div class="custom-tree-node">
                <div class="node-content">
                  <i class="icon-folder-tree" :class="{ 'icon-folder-tree-root': data.id < 0 }"></i>
                  <el-tooltip :content="node.label" v-if='node.label.length > 14'>
                    <span class="node-label">{{ node.label.slice(0, 14) }}...</span>
                  </el-tooltip>
                  <span v-else class="node-label">{{ node.label }}</span>
                </div>
                <div class="node-actions">
                  <el-dropdown @command="controlCommand" trigger="click">
                    <el-button class="node-dropdown-btn" circle size="small">
                      <el-icon><Setting /></el-icon>
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item v-if='permission.has_add_permission' :command="{ action: 'add', node: node }">
                          <el-icon><Plus /></el-icon>新增模块
                        </el-dropdown-item>
                        <el-dropdown-item v-if='permission.has_edit_permission && node.data.id > 0' divided :command="{ action: 'edit', node: node }">
                          <el-icon><EditPen /></el-icon>编辑模块
                        </el-dropdown-item>
                        <el-dropdown-item v-if='permission.has_delete_permission && node.data.id > 0' divided :command="{ action: 'delete', node: node }" class="danger-item">
                          <el-icon><Delete /></el-icon>删除模块
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
            <el-button @click="expandAllNodes" class="tree-btn" size="small">
              <el-icon><Expand /></el-icon>全部展开
            </el-button>
            <el-button @click="collapseAllNodes" class="tree-btn" size="small">
              <el-icon><Fold /></el-icon>全部折叠
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧主要内容区域 -->
    <div class="main-content">
      <!-- 自动化类型快速筛选 -->
      <el-card class="type-filter-card elegant-shadow">
        <div class="type-filter-header">
          <i class="icon-automation"></i>
          <h3 class="type-filter-title">自动化类型</h3>
        </div>
        <div class="type-filter-content">
          <el-radio-group v-model="caseSearch.type" @change="handleTypeChange" class="type-radio-group">
            <el-radio-button label="">全部类型</el-radio-button>
            <el-radio-button 
              v-for="type in automationTypes" 
              :key="type.value" 
              :label="type.value"
              :class="`type-${type.value.toLowerCase()}`"
            >
              <div class="type-item-content">
                <i :class="`type-icon type-icon-${type.value.toLowerCase()}`"></i>
                <span class="type-text">{{ type.label }}</span>
              </div>
            </el-radio-button>
          </el-radio-group>
        </div>
      </el-card>

      <!-- 筛选区域 -->
      <el-card class="filter-card elegant-shadow">
        <div class="filter-header">
          <div class="header-title-section">
            <i class="icon-search"></i>
            <h3 class="filter-title">用例筛选</h3>
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
          <el-form :model="caseSearch" class="filter-form inline-form">
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="inline-form-item">
                  <div class="inline-label-wrapper">
                    <i class="icon-case"></i>
                    <span class="inline-label-text">用例名称</span>
                  </div>
                  <el-input 
                    v-model="caseSearch.name" 
                    placeholder="请输入用例名称" 
                    clearable
                    class="input-inline"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="inline-form-item">
                  <div class="inline-label-wrapper">
                    <i class="icon-tag"></i>
                    <span class="inline-label-text">用例标签</span>
                  </div>
                  <el-select 
                    v-model="caseSearch.tag" 
                    placeholder="请选择用例标签" 
                    clearable
                    class="select-inline"
                  >
                    <el-option v-for="tag in tag_list" :label='tag.name' :value="tag.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item class="inline-form-item">
                  <div class="inline-label-wrapper">
                    <i class="icon-result"></i>
                    <span class="inline-label-text">测试结果</span>
                  </div>
                  <el-select 
                    v-model="caseSearch.recent_test_result" 
                    placeholder="请选择最近测试结果" 
                    clearable
                    class="select-inline"
                  >
                    <el-option v-for="result in result_list" :label='result.label' :value="result.value" />
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
                    v-model="caseSearch.create_by" 
                    placeholder="请选择创建人" 
                    clearable
                    filterable
                    class="select-inline"
                  >
                    <el-option v-for="user_obj in user_list" :label='user_obj.username' :value="user_obj.id" />
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
                    v-model="caseSearch.update_by" 
                    placeholder="请选择更新人" 
                    clearable
                    filterable
                    class="select-inline"
                  >
                    <el-option v-for="user_obj in user_list" :label='user_obj.username' :value="user_obj.id" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
      </el-card>

      <!-- 用例列表区域 -->
      <el-card class="content-card elegant-shadow">
        <div class="content-header">
          <div class="content-title-section">
            <div class="title-with-stats">
              <h3 class="content-title">用例列表</h3>
              <div class="stats-info">
                <div class="stat-item">
                  <span class="stat-label">总计</span>
                  <span class="stat-value">{{ case_list.count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">当前页</span>
                  <span class="stat-value">{{ case_list.results ? case_list.results.length : 0 }}</span>
                </div>
                <div class="stat-item type-badge" v-if="caseSearch.type">
                  <i :class="`type-icon-small type-icon-${caseSearch.type.toLowerCase()}`"></i>
                  <span class="stat-value">{{ getTypeLabel(caseSearch.type) }}</span>
                </div>
              </div>
            </div>
            <el-button 
              v-if="permission.has_add_permission" 
              @click="addCase" 
              type="primary" 
              class="add-btn"
            >
              <el-icon><Plus /></el-icon>新增用例
            </el-button>
          </div>
        </div>

        <!-- 数据表格 -->
        <div class="table-wrapper">
          <el-table 
            :data="case_list.results" 
            :max-height="550"
            class="elegant-table"
            :header-row-style="headerRowStyle"
            @row-dblclick="editStep"
            @row-click="handleRowClick"
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
              label="用例信息" 
              min-width="250" 
              align="center"
              class-name="case-info-column"
            >
              <template #default='scope'>
                <div class="case-info-cell">
                  <div class="case-type-badge">
                    <el-tag 
                      size="small" 
                      :type="getTypeTagType(scope.row.type_name)"
                      effect="light"
                      class="type-tag"
                    >
                      <i :class="`type-icon-cell type-icon-${scope.row.type.toLowerCase()}`"></i>
                      {{ scope.row.type_name }}
                    </el-tag>
                  </div>
                  <el-link type="primary" @click='editStepTwo(scope.row)' class="case-link">
                    {{ scope.row.name }}
                  </el-link>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column 
              label="测试结果" 
              prop="recent_test_result_name" 
              width="120" 
              align="center"
              class-name="result-column"
            >
              <template #default="scope">
                <el-tag 
                  v-if='scope.row.recent_test_result_name ==="成功"' 
                  effect="dark" 
                  type="success"
                  class="result-tag"
                >{{ scope.row.recent_test_result_name }}</el-tag>
                <el-tag 
                  v-if='scope.row.recent_test_result_name ==="失败"' 
                  effect="dark" 
                  type="danger"
                  class="result-tag"
                >{{ scope.row.recent_test_result_name }}</el-tag>
                <el-tag 
                  v-if='scope.row.recent_test_result_name ==="错误"' 
                  effect="dark" 
                  type="danger"
                  class="result-tag"
                >{{ scope.row.recent_test_result_name }}</el-tag>
                <el-tag 
                  v-if='scope.row.recent_test_result_name ==="未执行"' 
                  effect="dark" 
                  type="info"
                  class="result-tag"
                >{{ scope.row.recent_test_result_name }}</el-tag>
              </template>
            </el-table-column>
            
            <el-table-column 
              label="用例标签" 
              prop="tag_name" 
              min-width="160" 
              align="center"
              class-name="tag-column"
            >
              <template #default="scope">
                <div class="tags-container">
                  <el-tag 
                    v-for='obj in scope.row.tag_name' 
                    :key="obj.id"
                    size="small"
                    :type="getTagType(obj.name)"
                    effect="light"
                    class="case-tag"
                  >
                    {{ obj.name }}
                  </el-tag>
                  <span v-if="!scope.row.tag_name || scope.row.tag_name.length === 0" class="no-tag">-</span>
                </div>
              </template>
            </el-table-column>
            
            <!-- 合并列：创建信息 -->
            <el-table-column 
              label="创建信息" 
              width="200" 
              align="center"
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
                    content="查看用例" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="success" 
                      v-if="permission.has_read_permission" 
                      class="action-btn view-btn"
                      @click.stop="viewCase(scope.row)"
                      circle
                    >
                      <el-icon><View /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="编辑用例" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="warning" 
                      v-if="permission.has_edit_permission" 
                      class="action-btn edit-btn"
                      @click.stop="editCase(scope.row)"
                      circle
                    >
                      <el-icon><EditPen /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="复制用例" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="primary" 
                      v-if="permission.has_add_permission" 
                      class="action-btn copy-btn"
                      @click.stop="copy(scope.row)"
                      circle
                    >
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </el-tooltip>
                  
                  <el-tooltip 
                    content="删除用例" 
                    placement="top" 
                    effect="dark"
                  >
                    <el-button 
                      type="danger" 
                      v-if="permission.has_delete_permission" 
                      @click.stop="deleteCase(scope.row.id)" 
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
            :total="case_list.count"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            class="elegant-pagination"
            :background="true"
          />
        </div>
      </el-card>
    </div>
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
  CopyDocument,
  Setting,
  Expand,
  Fold
} from '@element-plus/icons-vue'

export default{
  watch: {
    filterText(val) {
      if (this.$refs.treeRef) {
        this.$refs.treeRef.filter(val)
      }
    }
  },
  computed:{
    ...mapState(['pathPermission', 'projectInfo']),
    calcMinWidth() {
      let visibleButtons = 0
      if (this.permission.has_read_permission) visibleButtons += 1
      if (this.permission.has_edit_permission) visibleButtons += 1
      if (this.permission.has_add_permission) visibleButtons += 1
      if (this.permission.has_delete_permission) visibleButtons += 1
      return Math.max(10, visibleButtons * 48)
    }
  },
  data() {
    return {
      module_node: {},
      moduleRules: {
        name: [{
          required: true,
          message: '模块名称不能为空',
          trigger: 'blur',
        }],
      },
      moduleSave:{
        project: '',
        name: '',
        plant: '',
        parent: 0,
      },
      editModuleVisible: false,
      selectNode: 0,
      filterText: '',
      caseView: false,
      automationTypes: [
        { label: '接口自动化', value: 'API' },
        { label: 'Web自动化', value: 'WEB_UI' },
        { label: 'App自动化', value: 'APP_UI' },
        { label: '造数脚本', value: 'CreateData' },
        { label: '性能测试', value: 'Performace' },
      ],
      result_list: [
        {label: '成功', value: 1},
        {label: '失败', value: 2},
        {label: '错误', value: 3},
        {label: '未执行', value: 4},
      ],
      tag_list: '',
      caseForm:{
        project: '',
        id: '',
        module: '',
        name: '',
        type: 'API',
        tag: '',
        params: [],
      },
      caseRules: {
        name: [{
          required: true,
          message: '用例名称不能为空',
          trigger: 'blur',
        }],
        module: [{
          required: true,
          message: '请选择所属模块',
          trigger: 'change',
        }],
        tag: [{
          required: true,
          message: '请选择用例标签',
          trigger: 'change',
        }],
      },
      caseFormTmp:{
        project: '',
        id: '',
        module: '',
        name: '',
        type: 'API',
        tag: '',
        params: [],
      },
      editCaseVisible: false,
      moduleEditProps:{
        emitPath: false,
        value: 'id',
        label: 'name',
        checkStrictly: true,
      },
      permission: {},
      caseSearch:{
        name: '',
        service: '',
        method: '',
        url: '',
        project: '',
        type: '',
        tag: '',
        module_list: [],
        recent_test_result: '',
        create_by: '',
        update_by: '',
      },
      page_size_params: {
        page: 1,
        size: 10,
      },
      count: 1,
      title: '新增用例',
      moduleTitle: '',
      case_list: [],
      user_list: [],
      service_list: [],
      plant_module_list: [],
      role_names: [],
    }
  },
  components: {
    Refresh,
    Search,
    Plus,
    View,
    Delete,
    EditPen,
    CopyDocument,
    Setting,
    Expand,
    Fold
  },
  methods:{
    ...mapActions(['getRolePermission']),
    
    handleTypeChange() {
      this.page_size_params.page = 1
      this.getCases()
    },
    
    getTypeLabel(type) {
      const typeObj = this.automationTypes.find(t => t.value === type)
      return typeObj ? typeObj.label : ''
    },
    
    getTypeTagType(typeName) {
      const typeMap = {
        'API': '',
        'WEB_UI': 'success',
        'APP_UI': 'warning',
        'CreateData': 'info',
        'Performace': 'danger'
      }
      const typeKey = this.automationTypes.find(t => t.label === typeName)?.value || 'API'
      return typeMap[typeKey] || ''
    },
    
    handleCurrentChange(page) {
      this.page_size_params.page = page
      this.getCases()
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
    
    handleSizeChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.getCases()
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
    
    controlCommand(command){
      this.module_node = command
      if(command.action === 'add'){
        this.editModuleVisible = true
        this.moduleTitle = '新增模块'
      }else if(command.action === 'edit'){
        this.moduleSave = {...this.module_node.node.data}
        this.editModuleVisible = true
        this.moduleTitle = '编辑模块'
      }else if(command.action === 'delete'){
        this.deleteModule(this.module_node.node.data.id)
      }
    },
    
    save(){
      if (this.module_node.action === 'add'){
        this.createModule()
      }else if(this.module_node.action === 'edit'){
        this.updateModule()
      }
    },
    
    async createModule(){
      this.$refs['moduleRef'].validate(async (valid, fields)=>{
        if (valid){
          if (this.module_node.node.data.id < 0){
            this.moduleSave.plant = -this.module_node.node.data.id
            this.moduleSave.parent = null
          }else{
            this.moduleSave.plant = this.module_node.node.data.plant_id
            this.moduleSave.parent = this.module_node.node.data.id
          }
          this.moduleSave.project = this.projectInfo.id
          const response = await this.$api.createModule(this.moduleSave)
          if(response.status === 201){
            this.editModuleVisible = false
            this.getPlantModule()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async updateModule(){
      this.$refs['moduleRef'].validate(async (valid, fields)=>{
        if (valid){
          this.moduleSave.project = this.module_node.node.data.project_id
          this.moduleSave.plant = this.module_node.node.data.plant_id
          const response = await this.$api.updateModule(this.moduleSave.id, this.moduleSave)
          if(response.status === 200){
            this.editModuleVisible = false
            this.getPlantModule()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
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
    
    filterNode(value, data) {
      if (!value) return true
      return data?.name?.includes(value) || false
    },
    
    moduleSelect(node, data, $event){
      localStorage.setItem('case_node', JSON.stringify(node))
      this.caseSearch.module_list = this.getAllIds(node)
      this.getCases(false)
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
    
    search(){
      this.getCases()
    },
    
    copy(row_data){
      this.caseForm = {...row_data}
      this.caseForm.name = this.caseForm.name + '副本'
      this.createCase()
    },
    
    reset(){
      for(let key in this.caseSearch){
        if(key === 'module_list'){
          this.caseSearch[key] = []
        }else if(key === 'type'){
          this.caseSearch.type = ''
        }else{
          this.caseSearch[key] = ''
        }
      }
    },
    
    editCase(row_data){
      this.editCaseVisible = true
      this.caseView = false
      this.title = '编辑用例'
      this.caseForm = {...row_data}
      this.$nextTick(() => {
        if (this.$refs.caseRef) {
          this.$refs.caseRef.clearValidate()
        }
      })
    },
    
    viewCase(row_data){
      this.editCaseVisible = true
      this.title = '查看用例'
      this.caseView = true
      this.caseForm = {...row_data}
    },
    
    addCase(){
      this.title = '新增用例'
      this.caseView = false
      this.caseForm = {...this.caseFormTmp}
      // 默认选择当前筛选的用例类型
      if (this.caseSearch.type) {
        this.caseForm.type = this.caseSearch.type
      }
      this.editCaseVisible = true
      const node = this.$refs.treeRef.getCurrentNode()
      if ( node && node.id > 0){
        this.caseForm.module = node.id
      }
      this.$nextTick(() => {
        if (this.$refs.caseRef) {
          this.$refs.caseRef.resetFields()
        }
      })
    },
    
    async createCase(){
      if(this.caseForm.module < 0){
        ElMessage({message: "所属模块不能选择根节点", type: 'error'})
        return 
      }
      this.$refs['caseRef'].validate(async (valid, fields)=>{
        if(valid){
          this.caseForm.project = this.projectInfo.id
          const response = await this.$api.createCase(this.caseForm)
          if (response.status === 201){
            this.editCaseVisible = false
            this.getCases()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async updateCase(){
      if(this.caseForm.module < 0){
        ElMessage({message: "所属模块不能选择根节点", type: 'error'})
        return 
      }
      this.$refs['caseRef'].validate(async (valid, fields)=>{
        if(valid){
          const response = await this.$api.updateCase(this.caseForm.id, this.caseForm)
          if (response.status === 200){
            this.editCaseVisible = false
            this.getCases()
            ElMessage({message: "保存成功", type: 'success'})
          }
        }
      })
    },
    
    async deleteCase(id){
      ElMessageBox.confirm(
        '确定删除此用例？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async() => {
        const response = await this.$api.deleteCase(id)
        if (response.status === 204){
          this.getCases()
          ElMessage({
            type: 'success',
            message: '删除成功',
          })
        }
      }).catch(() => {})
    },
    
    async getPlantModule(){
      const response = await this.$api.getAllPlantModule({project: this.projectInfo.id})
      if (response.status === 200){
        this.plant_module_list = response.data.results
      }
    },
    
    async getCases(){
      this.caseSearch.project = this.projectInfo.id
      const data = Object.assign(this.caseSearch, this.page_size_params)
      this.caseSearch.module = this.caseSearch.module_list.join(',')
      const response = await this.$api.getCases(data)
      if (response.status === 200){
        this.case_list = {...response.data}
      }
    },
    
    async getTags(){
      const response = await this.$api.getTags({project: this.projectInfo.id})
      if (response.status === 200){
        this.tag_list = response.data.results
      }
    },
    
    editStep(row, column, event){
      localStorage.setItem('case_model', 'tree')
      this.$router.push({name: 'caseStepEdit', query: {id: row.id}})
    },
    
    editStepTwo(row){
      localStorage.setItem('case_model', 'tree')
      this.$router.push({name: 'caseStepEdit', query: {id: row.id}})
    },
  },
  created() {
    this.user_list = JSON.parse(localStorage.getItem('user_list')) || []
    const node = JSON.parse(localStorage.getItem('case_node'))
    if (node) {
      this.$nextTick(() => {
        if (this.$refs.treeRef) {
          this.$refs.treeRef.setCurrentKey(node.id)
        }
      })
      this.caseSearch.module_list = this.getAllIds(node)
    }
    this.getCases()
    this.getRolePermission(this.pathPermission[this.$route.path]).then(res =>{
      this.permission = {...res.result}
      localStorage.setItem('caseListPermission', JSON.stringify(this.permission))
    })
    this.getPlantModule()
    this.getTags()
  }
}
</script>

<style scoped>
.case-management-container {
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 15px;
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
  gap: 12px;
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

.tree-search-input >>> .el-input__inner {
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
}

.tree-search-input >>> .el-input__inner:hover {
  border-color: #cbd5e1;
  background: white;
}

.tree-search-input >>> .el-input__inner:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
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

.custom-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  overflow: hidden;
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

.node-label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  color: #334155;
}

.node-actions {
  opacity: 0;
  transition: opacity 0.3s ease;
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

/* 自动化类型筛选卡片 */
.type-filter-card {
  background: white;
  border: none;
  border-radius: 16px;
  overflow: hidden;
}

.type-filter-header {
  padding: 15px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-automation {
  display: inline-block;
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  border-radius: 8px;
  position: relative;
}

.icon-automation::before {
  content: '';
  position: absolute;
  top: 6px;
  left: 6px;
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 1px;
}

.icon-automation::after {
  content: '';
  position: absolute;
  top: 14px;
  left: 6px;
  width: 12px;
  height: 2px;
  background: white;
  border-radius: 1px;
}

.type-filter-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  flex: 1;
}

.type-filter-content {
  padding: 16px 24px;
}

.type-radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  width: 100%;
}

.type-radio-group >>> .el-radio-button {
  flex: 1;
  min-width: 140px;
}

.type-radio-group >>> .el-radio-button__inner {
  width: 100%;
  padding: 16px 12px;
  border-radius: 12px !important;
  border: 2px solid #e2e8f0;
  background: white;
  color: #64748b;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
}

.type-radio-group >>> .el-radio-button__original-radio:checked + .el-radio-button__inner {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  color: #1e40af;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
}

.type-item-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-icon {
  width: 24px;
  height: 24px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.type-icon-api {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%233b82f6' d='M21 10c-1.1 0-2 .9-2 2v3H5v-3c0-1.1-.9-2-2-2s-2 .9-2 2v5c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2v-5c0-1.1-.9-2-2-2zm-3-5H6c-1.1 0-2 .9-2 2v2.15c1.16.41 2 1.51 2 2.82V14h12v-2.03c0-1.3.84-2.4 2-2.82V7c0-1.1-.9-2-2-2z'/%3E%3C/svg%3E");
}

.type-icon-web_ui {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%2310b981' d='M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm-5 14H4v-4h11v4zm0-5H4V9h11v4zm5 5h-4V9h4v9z'/%3E%3C/svg%3E");
}

.type-icon-app_ui {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23f59e0b' d='M17 1.01L7 1c-1.1 0-2 .9-2 2v18c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2V3c0-1.1-.9-1.99-2-1.99zM17 19H7V5h10v14z'/%3E%3C/svg%3E");
}

.type-icon-createdata {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%236b7280' d='M19 3h-4.18C14.4 1.84 13.3 1 12 1c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm2 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z'/%3E%3C/svg%3E");
}

.type-icon-performace {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23ef4444' d='M16 6l2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6z'/%3E%3C/svg%3E");
}

.type-text {
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

/* 不同类型按钮的样式 */
.type-radio-group >>> .type-api .el-radio-button__inner {
  border-color: #dbeafe;
  background: #eff6ff;
  color: #1e40af;
}

.type-radio-group >>> .type-web_ui .el-radio-button__inner {
  border-color: #d1fae5;
  background: #ecfdf5;
  color: #065f46;
}

.type-radio-group >>> .type-app_ui .el-radio-button__inner {
  border-color: #fef3c7;
  background: #fffbeb;
  color: #92400e;
}

.type-radio-group >>> .type-createdata .el-radio-button__inner {
  border-color: #f3f4f6;
  background: #f9fafb;
  color: #374151;
}

.type-radio-group >>> .type-performace .el-radio-button__inner {
  border-color: #fee2e2;
  background: #fef2f2;
  color: #991b1b;
}

.type-radio-group >>> .type-api .el-radio-button__original-radio:checked + .el-radio-button__inner {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  color: #1e40af;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
}

.type-radio-group >>> .type-web_ui .el-radio-button__original-radio:checked + .el-radio-button__inner {
  border-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  color: #065f46;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
}

.type-radio-group >>> .type-app_ui .el-radio-button__original-radio:checked + .el-radio-button__inner {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  color: #92400e;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
}

.type-radio-group >>> .type-createdata .el-radio-button__original-radio:checked + .el-radio-button__inner {
  border-color: #6b7280;
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  color: #374151;
  box-shadow: 0 4px 12px rgba(107, 114, 128, 0.2);
}

.type-radio-group >>> .type-performace .el-radio-button__original-radio:checked + .el-radio-button__inner {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #991b1b;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

/* 筛选卡片 */
.filter-card {
  background: white;
  border: none;
  border-radius: 16px;
  overflow: hidden;
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

.icon-case,
.icon-result,
.icon-folder {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-case {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z'/%3E%3C/svg%3E");
}

.icon-result {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z'/%3E%3C/svg%3E");
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
  padding: 15px 24px 0px 24px;
}

.inline-form {
  margin-bottom: 0;
}

.inline-form-item {
  margin-bottom: 0;
  display: flex;
  align-items: center;
  height: 56px;
}

.inline-label-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 100px;
  flex-shrink: 0;
}

.inline-label-text {
  font-size: 14px;
  font-weight: 500;
  color: #475569;
  white-space: nowrap;
}

.icon-tag,
.icon-creator,
.icon-updater {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-tag {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z'/%3E%3C/svg%3E");
}

.icon-creator {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
}

.icon-updater {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23475569' d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E");
}

.input-inline >>> .el-input__inner,
.select-inline >>> .el-input__inner {
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  padding: 0 15px;
  box-shadow: none;
  transition: all 0.3s ease;
  flex: 1;
  margin-left: 12px;
}

.input-inline >>> .el-input__inner:hover,
.select-inline >>> .el-input__inner:hover {
  border-color: #cbd5e1;
  background: white;
}

.input-inline >>> .el-input__inner:focus,
.select-inline >>> .el-input__inner:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select-inline {
  flex: 1;
  margin-left: 12px;
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

.type-badge {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
  border: 1px solid #bfdbfe;
}

.type-badge .stat-value {
  color: #1e40af;
  font-weight: 600;
}

.type-icon-small {
  width: 16px;
  height: 16px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
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
  padding: 0 24px;
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

.case-info-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.case-type-badge {
  width: 100%;
  display: flex;
  justify-content: center;
}

.type-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  border-width: 1px;
}

.type-icon-cell {
  width: 14px;
  height: 14px;
  display: inline-block;
  background-size: contain;
  background-repeat: no-repeat;
  margin-right: 4px;
  vertical-align: -2px;
}

.case-link {
  font-weight: 500;
  font-size: 14px;
  transition: all 0.3s ease;
}

.case-link:hover {
  color: #3b82f6;
  text-decoration: underline;
}

.result-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 12px;
  border: none;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
  align-items: center;
  min-height: 32px;
}

.case-tag {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 500;
  border-width: 1px;
}

.no-tag {
  color: #94a3b8;
  font-size: 13px;
}

/* 合并列样式 */
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
  color: #334155;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.time-text {
  font-size: 12px;
  color: #64748b;
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

.action-btn.copy-btn:hover {
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
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

.action-btn.copy-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
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

.icon-module,
.icon-tag-dialog {
  width: 16px;
  height: 16px;
  background-size: contain;
  background-repeat: no-repeat;
  flex-shrink: 0;
}

.icon-module {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z'/%3E%3C/svg%3E");
}

.icon-tag-dialog {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23334155' d='M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z'/%3E%3C/svg%3E");
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
  .case-management-container {
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
  
  .type-radio-group >>> .el-radio-button {
    min-width: 120px;
  }
}

@media screen and (max-width: 768px) {
  .case-management-container {
    padding: 12px;
  }
  
  .type-radio-group {
    flex-direction: column;
  }
  
  .type-radio-group >>> .el-radio-button {
    width: 100%;
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
    flex-wrap: wrap;
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

.sidebar-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.type-filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
}

.filter-card {
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.2s both;
}

.content-card {
  animation: slideInRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) 0.3s both;
}
</style>