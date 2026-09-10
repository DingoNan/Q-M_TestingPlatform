<template>
  <div class="tag-management-container">
    <!-- 搜索筛选区域 -->
    <el-card class="filter-card elegant-shadow">
      <div class="filter-header">
        <div class="header-title-section">
          <i class="icon-search"></i>
          <h3 class="filter-title">知识库筛选</h3>
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
        <el-form :model="searchForm" class="filter-form inline-form">
          <el-row :gutter="24">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-database"></i>
                  <span class="label-text">数据源</span>
                </div>
                <el-select 
                  v-model="searchForm.source_type" 
                  placeholder="全部" 
                  clearable
                  size='large'
                  class="select"
                  popper-class='select-dropdown-rounded'
                >
                  <el-option 
                    v-for="t in sourceTypeOptions" 
                    :key="t.value"
                    :label="t.label" 
                    :value="t.value" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-chunk"></i>
                  <span class="label-text">分块类型</span>
                </div>
                <el-select 
                  v-model="searchForm.chunk_type" 
                  :placeholder="searchForm.source_type ? '全部（已过滤）' : '全部'" 
                  clearable
                  size='large'
                  class="select"
                  popper-class='select-dropdown-rounded'
                >
                  <el-option 
                    v-for="t in filteredChunkTypeOptions" 
                    :key="t.value"
                    :label="t.label" 
                    :value="t.value" 
                  />
                </el-select>
              </el-form-item>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item class="form-item-inline">
                <div class="label-with-icon">
                  <i class="icon-keyword"></i>
                  <span class="label-text">关键词</span>
                </div>
                <el-input 
                  v-model="searchForm.keyword" 
                  placeholder="搜索文档内容" 
                  clearable
                  size='large'
                  class="input"
                  @keyup.enter="search"
                />
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
            <h3 class="content-title">知识库列表</h3>
            <div class="stats-info">
              <div class="stat-item">
                <span class="stat-label">总分块</span>
                <span class="stat-value">{{ stats.total_chunks || 0 }}</span>
              </div>
              <div class="stat-item stat-func">
                <span class="stat-label">功能用例</span>
                <span class="stat-value">{{ stats.sources?.func_case?.items || 0 }}</span>
              </div>
              <div class="stat-item stat-api">
                <span class="stat-label">接口文档</span>
                <span class="stat-value">{{ stats.sources?.api?.items || 0 }}</span>
              </div>
              <div class="stat-item stat-defect">
                <span class="stat-label">已解决缺陷</span>
                <span class="stat-value">{{ stats.sources?.defect?.items || 0 }}</span>
              </div>
              <div class="stat-item stat-element">
                <span class="stat-label">元素库</span>
                <span class="stat-value">{{ stats.sources?.element?.items || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">当前页</span>
                <span class="stat-value">{{ page_size_params.page }}</span>
              </div>
            </div>
          </div>
          <div class="header-action-btns">
            <div class="selected-count-badge" v-if="selectedIds.length > 0">
              <el-icon><Check /></el-icon>已选 {{ selectedIds.length }}
            </div>
            <el-button 
              class="batch-delete-btn"
              :disabled="selectedIds.length === 0"
              @click="handleBatchDelete"
            >
              <el-icon><Delete /></el-icon>批量删除
            </el-button>
            <el-dropdown 
              @command="handleRebuild" 
              trigger="click"
              class="batch-dropdown"
              popper-class="batch-dropdown-popper"
            >
              <el-button class="toolbar-btn">
                <el-icon><Refresh /></el-icon>按类型重建
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="func_case" class="batch-dropdown-item">
                    <span class="item-text">重建功能用例</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="api" class="batch-dropdown-item">
                    <span class="item-text">重建接口文档</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="defect" class="batch-dropdown-item">
                    <span class="item-text">重建缺陷</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="element" class="batch-dropdown-item">
                    <span class="item-text">重建元素库</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="all" class="batch-dropdown-item">
                    <span class="item-text">全量重建</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
            <el-button 
              v-if="permission.has_add_permission" 
              @click="addItem" 
              type="primary" 
              class="add-btn"
            >
              <el-icon><Plus /></el-icon>新增分块
            </el-button>
          </div>
        </div>
      </div>

      <!-- 数据表格 -->
      <div class="table-wrapper">
        <el-table 
          :data="tableData" 
          :max-height="'calc(100vh - 480px)'" 
          class="elegant-table"
          :header-row-style="headerRowStyle"
          v-loading="loading"
          row-key="id"
          ref="dataTable"
          @selection-change="handleSelectionChange"
          @select-all="handleSelectAll"
        >
          <el-table-column
            type="selection"
            width="45"
            align="center"
            :reserve-selection="true"
          />
          
          <el-table-column 
            label="名称" 
            min-width="200" 
            align="center"
            class-name="name-column"
          >
            <template #default="{ row }">
              <div class="name-cell">
                <el-link type="primary" class="name-link" @click="viewItem(row)">
                  {{ row.source_name }}
                </el-link>
                <el-tag 
                  v-if="row.is_chunked" 
                  size="small" 
                  type="info" 
                  effect="plain"
                  class="chunk-badge"
                >
                  {{ row.chunk_index }}/{{ row.chunk_total }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="数据源" 
            width="120" 
            align="center"
            class-name="source-column"
          >
            <template #default="{ row }">
              <el-tag 
                :type="getSourceTagType(row.source_type)" 
                effect="light"
                class="source-tag"
              >
                {{ row.source_type_label }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="分块类型" 
            width="140" 
            align="center"
            class-name="chunk-column"
          >
            <template #default="{ row }">
              <el-tag 
                :type="getChunkTagType(row.chunk_type, row.source_type)" 
                effect="light"
                class="chunk-tag"
              >
                {{ getChunkTagLabel(row.chunk_type, row.source_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="内容摘要" 
            prop="document" 
            min-width="300" 
            align="left"
            class-name="content-column"
          >
            <template #default="{ row }">
              <el-tooltip 
                placement="top" 
                effect="dark"
                :show-after="300"
                popper-class="content-tooltip"
              >
                <template #content>
                  <div style="max-width:600px;white-space:pre-wrap;word-break:break-word;line-height:1.6;font-size:13px;">{{ row.document }}</div>
                </template>
                <span class="doc-preview">{{ truncateText(row.document, 150) }}</span>
              </el-tooltip>
            </template>
          </el-table-column>
          
          <!-- 创建信息 -->
          <el-table-column 
            label="创建信息" 
            width="200" 
            align="center"
            class-name="creator-column"
          >
            <template #default="{ row }">
              <div class="user-time-cell">
                <div class="user-info">
                  <i class="icon-user"></i>
                  <span class="user-name">{{ row.create_by_name || '-' }}</span>
                </div>
                <div class="time-info">
                  <i class="icon-time-small"></i>
                  <span class="time-text">{{ row.create_time ? row.create_time.replace('T', ' ').substring(0, 19) : '-' }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <!-- 更新信息 -->
          <el-table-column 
            label="更新信息" 
            width="200" 
            align="center"
            class-name="updater-column"
          >
            <template #default="{ row }">
              <div class="user-time-cell">
                <div class="user-info">
                  <i class="icon-user"></i>
                  <span class="user-name">{{ row.update_by_name || '-' }}</span>
                </div>
                <div class="time-info">
                  <i class="icon-time-small"></i>
                  <span class="time-text">{{ row.update_time ? row.update_time.replace('T', ' ').substring(0, 19) : '-' }}</span>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            align="center" 
            width="120" 
            label="操作"
            class-name="action-column"
            fixed="right"
          >
            <template #default="scope">
              <div class="action-buttons">
                <el-tooltip 
                  content="查看详情" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="success" 
                    v-if="permission.has_read_permission" 
                    class="action-btn view-btn"
                    @click.stop="viewItem(scope.row)"
                    circle
                  >
                    <el-icon><View /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip 
                  v-if="scope.row.source_type === 'custom'"
                  content="删除（仅自定义知识）" 
                  placement="top" 
                  effect="dark"
                >
                  <el-button 
                    type="danger" 
                    v-if="permission.has_delete_permission" 
                    class="action-btn delete-btn"
                    @click.stop="handleDelete(scope.row)"
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
          :page-sizes="[10, 20, 30, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalCount"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          class="select input"
          :background="true"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog 
      v-model="detailDialogVisible" 
      :title="detailDialogTitle"
      fullscreen
      class="detail-dialog"
      :close-on-click-modal="false"
      destroy-on-close
      append-to-body
    >
      <div class="detail-dialog-body" v-if="currentItem">
        <!-- 第一行：基础信息(1/3) + Metadata(2/3) -->
        <div class="detail-top-row">
          <!-- 基础信息卡片 (1/3, 左) -->
          <div class="info-section">
            <div class="section-header">
              <el-icon class="section-icon"><Collection /></el-icon>
              <span class="section-title">基础信息</span>
            </div>
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">数据源</span>
                <el-tag :type="getSourceTagType(currentItem.source_type)" effect="light" size="default">
                  {{ currentItem.source_type_label }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="info-label">分块类型</span>
                <el-tag type="warning" effect="light" size="default">
                  {{ currentItem.chunk_type_label }}
                </el-tag>
              </div>
              <div class="info-item" v-if="currentItem.section">
                <span class="info-label">所属章节</span>
                <el-tag type="success" effect="plain" size="default">
                  <el-icon style="margin-right:4px;"><Folder /></el-icon>
                  {{ currentItem.section }}
                </el-tag>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间</span>
                <span class="info-value">{{ formatTime(currentItem.create_time) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建人</span>
                <span class="info-value">{{ currentItem.create_by_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">更新时间</span>
                <span class="info-value">{{ formatTime(currentItem.update_time) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">更新人</span>
                <span class="info-value">{{ currentItem.update_by_name || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- Metadata 区域 (2/3, 右) -->
          <div class="metadata-section">
            <div class="section-header">
              <el-icon class="section-icon"><EditPen /></el-icon>
              <span class="section-title">Metadata</span>
            </div>
            <div class="metadata-box">
              <pre class="metadata-content">{{ JSON.stringify(currentItem.metadata, null, 2) }}</pre>
            </div>
          </div>
        </div>

        <!-- 第二行：文档内容 (全宽) -->
        <div class="content-section">
          <div class="section-header">
            <el-icon class="section-icon"><Document /></el-icon>
            <span class="section-title">文档内容</span>
            <el-tag size="small" type="info" effect="plain" class="char-count">
              {{ currentItem.document?.length || 0 }} 字
            </el-tag>
          </div>
          <div class="doc-content-box">
            <pre class="doc-content">{{ currentItem.document }}</pre>
          </div>
        </div>
      </div>
    </el-dialog>

    <!-- 新增分块对话框 -->
    <el-dialog 
      v-model="createDialogVisible" 
      title="新增自定义知识" 
      width="700"
      class="elegant-dialog add-knowledge-dialog"
      :close-on-click-modal="false"
      destroy-on-close
      append-to-body
    >
      <div class="add-knowledge-container">
        <!-- 知识标题 -->
        <div class="knowledge-section">
          <div class="section-label">
            <el-icon><Collection /></el-icon>
            <span>知识标题</span>
            <span class="required-mark">*</span>
          </div>
          <el-input 
            v-model="createForm.source_name" 
            class="input"
            placeholder="请输入知识标题（如：项目规范、接口约定等）" 
            maxlength="100" 
            show-word-limit 
            size="large"
            clearable
          />
        </div>

        <!-- 分类标签 -->
        <div class="knowledge-section">
          <div class="section-label">
            <el-icon><ArrowDown /></el-icon>
            <span>分类标签</span>
          </div>
          <div class="chunk-type-group">
            <div 
              v-for="t in customChunkTypeOptions" 
              :key="t.value"
              class="chunk-type-card"
              :class="{ active: createForm.chunk_type === t.value }"
              @click="createForm.chunk_type = t.value"
            >
              <el-icon class="chunk-icon">
                <Document v-if="t.value === 'requirement'" />
                <Folder v-else />
              </el-icon>
              <span class="chunk-label">{{ t.label }}</span>
            </div>
          </div>
        </div>

        <!-- 知识内容输入区 -->
        <div class="knowledge-section content-section">
          <div class="section-label">
            <el-icon><EditPen /></el-icon>
            <span>知识内容</span>
            <span class="required-mark">*</span>
            <span class="section-hint">支持直接粘贴、拖拽上传文档/图片</span>
          </div>

          <!-- 附件预览区 -->
          <div v-if="pastedDocs.length || pastedImages.length" class="attachment-list">
            <template v-for="(doc, idx) in pastedDocs" :key="'doc-' + idx">
              <div class="attachment-item doc-item">
                <el-icon class="doc-icon"><Document /></el-icon>
                <div class="attachment-info">
                  <span class="attachment-name" :title="doc.name">{{ doc.name }}</span>
                  <span class="attachment-size">{{ doc.sizeText }}</span>
                </div>
                <el-icon class="attachment-remove" @click="removeDoc(idx)"><Close /></el-icon>
              </div>
            </template>
            <template v-for="(img, idx) in pastedImages" :key="'img-' + idx">
              <div class="attachment-item image-item">
                <img :src="img.url" class="attachment-thumb" />
                <div class="attachment-info">
                  <span class="attachment-name" :title="img.name">{{ img.name }}</span>
                </div>
                <el-icon class="attachment-remove" @click="removeImage(idx)"><Close /></el-icon>
              </div>
            </template>
          </div>

          <!-- 输入框 -->
          <div 
            class="content-input-wrapper" 
            :class="{ 'is-dragging': isDraggingFile }"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
          >
            <textarea
              v-model="createForm.document"
              class="content-textarea"
              placeholder="在此输入或粘贴文本内容，也可以拖拽文件到此处"
              @paste.native="onPaste"
              rows="8"
            ></textarea>
            
            <!-- 拖拽提示 -->
            <div v-if="isDraggingFile" class="drag-overlay">
              <el-icon :size="48" color="#8b5cf6"><UploadFilled /></el-icon>
              <span>松开上传文件</span>
            </div>

            <!-- 工具栏 -->
            <div class="input-toolbar">
              <div class="toolbar-left">
                <el-tooltip content="上传文档 (PDF/Word/Excel/Markdown/TXT)" placement="top" effect="dark">
                  <el-button circle size="small" class="tool-btn" @click="triggerFileInput">
                    <el-icon><Paperclip /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="上传图片" placement="top" effect="dark">
                  <el-button circle size="small" class="tool-btn" @click="triggerImageInput">
                    <el-icon><Picture /></el-icon>
                  </el-button>
                </el-tooltip>
                <input
                  type="file"
                  ref="fileInputRef"
                  class="hidden-input"
                  multiple
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.md,.txt,.csv"
                  @change="onFileSelect"
                />
                <input
                  type="file"
                  ref="imageInputRef"
                  class="hidden-input"
                  multiple
                  accept="image/*"
                  @change="onImageSelect"
                />
              </div>
              <div class="toolbar-right">
                <span class="char-count">{{ createForm.document.length }} 字</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div slot="footer" class="dialog-footer">
        <el-button @click="createDialogVisible = false" class="dialog-cancel-btn">
          取消
        </el-button>
        <el-button 
          type="primary" 
          @click="handleCreate" 
          :loading="saving"
          class="dialog-confirm-btn"
        >
          添加到知识库
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Search,
  Plus,
  ArrowDown,
  View,
  Delete,
  Check,
  Collection,
  Document,
  Folder,
  EditPen,
  Paperclip,
  Picture,
  Close,
  UploadFilled,
} from '@element-plus/icons-vue'

export default {
  name: 'VectorStoreManagement',
  computed: {
    ...mapState(['pathPermission', 'projectInfo', 'userInfo']),
    // 自定义知识的分块类型（仅需求文档和其它）
    customChunkTypeOptions() {
      return this.chunkTypeOptions.filter(t => ['requirement', 'other'].includes(t.value))
    },
    // 根据数据源类型过滤分块类型选项
    filteredChunkTypeOptions() {
      // 数据源类型 -> 允许的分块类型映射
      const sourceChunkMap = {
        'func_case': ['meta', 'text_step', 'step'],
        'api': ['core', 'request', 'response'],
        'defect': ['defect_core', 'detail'],
        'element': ['element_meta'],
        'custom': ['requirement', 'other'],
      }
      const sourceType = this.searchForm.source_type
      if (!sourceType || !sourceChunkMap[sourceType]) {
        // 未选择数据源或未知类型，返回全部
        return this.chunkTypeOptions
      }
      const allowedTypes = sourceChunkMap[sourceType]
      let filtered = this.chunkTypeOptions.filter(t => allowedTypes.includes(t.value))
      
      // 动态调整标签以适应上下文
      if (sourceType === 'defect') {
        filtered = filtered.map(t => {
          if (t.value === 'defect_core') return { ...t, label: '缺陷-基础信息' }
          return t
        })
      }
      return filtered
    },
    // 详情弹窗标题
    detailDialogTitle() {
      if (!this.currentItem) return '分块详情'
      const name = this.currentItem.source_name || '分块详情'
      if (this.currentItem.is_chunked) {
        return `${name} (${this.currentItem.chunk_index}/${this.currentItem.chunk_total})`
      }
      return name
    }
  },
  watch: {
    // 切换数据源时重置分块类型
    'searchForm.source_type'(newVal) {
      if (newVal) {
        // 检查当前选中的分块类型是否仍然有效
        const sourceChunkMap = {
          'func_case': ['meta', 'text_step', 'step'],
          'api': ['core', 'request', 'response'],
          'defect': ['core', 'detail'],
          'element': ['element_meta'],
          'custom': ['custom', 'meta', 'text_step', 'step', 'core', 'request', 'response', 'detail'],
        }
        const allowedTypes = sourceChunkMap[newVal] || []
        if (this.searchForm.chunk_type && !allowedTypes.includes(this.searchForm.chunk_type)) {
          this.searchForm.chunk_type = ''
        }
      } else {
        // 清除数据源时同时清除分块类型
        this.searchForm.chunk_type = ''
      }
    }
  },
  data() {
    return {
      permission: {},
      loading: false,
      rebuilding: false,
      saving: false,
      tableData: [],
      totalCount: 0,
      stats: {},
      selectedIds: [],
      selectedItems: [],

      sourceTypeOptions: [],
      chunkTypeOptions: [],

      searchForm: {
        source_type: '',
        keyword: '',
        chunk_type: '',
      },
      page_size_params: {
        page: 1,
        size: 10,
      },

      detailDialogVisible: false,
      currentItem: null,
      leftActiveNames: ['content'],

      createDialogVisible: false,
      createForm: {
        source_type: 'custom',
        source_name: '',
        chunk_type: 'requirement',
        document: '',
      },
      createRules: {
        source_name: [{ required: true, message: '请输入知识标题', trigger: 'blur' }],
        document: [{ required: true, message: '知识内容不能为空', trigger: 'blur' }],
      },
      // 文件处理相关
      pastedImages: [], // [{ url: 'data:image/...', base64: '...', name: 'image.png', type }]
      pastedDocs: [], // [{ name, ext, size, sizeText, base64, type }]
      isDraggingFile: false,
      maxFileSize: 20 * 1024 * 1024, // 20MB
      docAllowedExts: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'md', 'txt', 'csv'],
    }
  },
  components: {
    Refresh,
    Search,
    Plus,
    ArrowDown,
    View,
    Delete,
    Check,
    Collection,
    Document,
    Folder,
    EditPen,
    Paperclip,
    Picture,
    Close,
    UploadFilled,
  },
  methods: {
    formatTime(time) {
      if (!time) return '-'
      // 处理 Django 返回的带时区时间格式
      return time.replace('T', ' ').replace(/\.\d+\+.*$/, '').replace(/\.\d+Z$/, '')
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

    async check_permission() {
      const params = { user_id: this.userInfo.user_id, project_id: this.projectInfo.id, permission_id: this.pathPermission[this.$route.path] }
      try {
        const response = await this.$api.check_permission(params)
        if (response.status === 200) {
          this.permission = { ...response.data.result }
        }
      } catch (e) {
        this.permission = {
          has_permission: true,
          has_read_permission: true,
          has_edit_permission: true,
          has_add_permission: true,
          has_delete_permission: true,
        }
      }
    },

    async loadSourceTypes() {
      // 默认选项（前端兜底，防止API调用失败时下拉为空）
      const defaultSourceTypes = [
        { value: 'func_case', label: '功能用例' },
        { value: 'api', label: '接口文档' },
        { value: 'defect', label: '已解决缺陷' },
        { value: 'element', label: '元素库' },
        { value: 'custom', label: '自定义知识' },
      ]
      const defaultChunkTypes = [
        { value: 'meta', label: '用例-基础信息' },
        { value: 'text_step', label: '用例-文本步骤' },
        { value: 'step', label: '用例-表格步骤' },
        { value: 'core', label: '接口-基础信息' },
        { value: 'request', label: '接口-请求参数' },
        { value: 'response', label: '接口-响应结构' },
        { value: 'defect_core', label: '缺陷-基础信息' },
        { value: 'detail', label: '缺陷-详细描述' },
        { value: 'element_meta', label: '元素-定位信息' },
        { value: 'requirement', label: '需求文档' },
        { value: 'other', label: '其它' },
      ]
      
      try {
        const res = await this.$api.vectorstoreSourceTypes({ project: this.projectInfo.id })
        if (res.status === 200 && res.data) {
          this.sourceTypeOptions = res.data.source_types || defaultSourceTypes
          this.chunkTypeOptions = res.data.chunk_types || defaultChunkTypes
        } else {
          // API返回非200或data为空，使用默认选项
          this.sourceTypeOptions = defaultSourceTypes
          this.chunkTypeOptions = defaultChunkTypes
        }
      } catch (e) {
        // API调用失败，使用默认选项
        console.warn('加载数据源/分块类型选项失败，使用默认值:', e)
        this.sourceTypeOptions = defaultSourceTypes
        this.chunkTypeOptions = defaultChunkTypes
      }
    },

    async fetchData() {
      if (!this.projectInfo.id) return
      this.loading = true
      try {
        const params = {
          project: this.projectInfo.id,
          page: this.page_size_params.page,
          page_size: this.page_size_params.size,
        }
        if (this.searchForm.source_type) params.source_type = this.searchForm.source_type
        if (this.searchForm.keyword) params.keyword = this.searchForm.keyword
        if (this.searchForm.chunk_type) params.chunk_type = this.searchForm.chunk_type

        const res = await this.$api.vectorstoreList(params)
        if (res.status === 200) {
          this.tableData = res.data.results || []
          this.totalCount = res.data.count || 0
        }
      } catch (e) {
        ElMessage.error('加载知识库列表失败')
      } finally {
        this.loading = false
      }
    },

    async fetchStats() {
      if (!this.projectInfo.id) return
      try {
        const res = await this.$api.vectorstoreStats({ project: this.projectInfo.id })
        if (res.status === 200 && res.data) {
          // CustomRender 包装器将非列表接口数据放在 result 字段中
          this.stats = res.data.result || res.data
        } else {
          console.warn('获取向量库统计失败:', res.status, res.data)
        }
      } catch (e) {
        console.error('获取向量库统计异常:', e)
      }
    },

    search() {
      this.page_size_params.page = 1
      this.fetchData()
    },

    reset() {
      this.searchForm.source_type = ''
      this.searchForm.keyword = ''
      this.searchForm.chunk_type = ''
      this.page_size_params.page = 1
      this.fetchData()
    },

    handleCurrentChange(page) {
      this.page_size_params.page = page
      this.fetchData()
    },

    handleSizeChange(size) {
      this.page_size_params.size = size
      this.page_size_params.page = 1
      this.fetchData()
    },

    getSourceTagType(sourceType) {
      const map = { func_case: '', api: 'success', defect: 'danger', element: 'primary', custom: 'warning' }
      return map[sourceType] || ''
    },

    getChunkTagType(chunkType, sourceType) {
      const map = {
        'meta': 'info',
        'text_step': '',
        'step': 'success',
        'core': 'warning',
        'request': 'danger',
        'response': 'success',
        'defect_core': 'danger',
        'detail': 'info',
        'element_meta': 'primary',
        'requirement': 'warning',
        'other': 'info',
      }
      // 兼容旧数据：缺陷的核心信息旧值为'core'
      if (sourceType === 'defect' && chunkType === 'core') {
        return 'danger'
      }
      // 兼容旧数据：元素库分块旧值为'meta'
      if (sourceType === 'element' && chunkType === 'meta') {
        return 'primary'
      }
      return map[chunkType] || 'info'
    },

    getChunkTagLabel(chunkType, sourceType) {
      // 兼容旧数据：缺陷的核心信息旧值为'core'，新值为'defect_core'
      if (sourceType === 'defect' && chunkType === 'core') {
        return '缺陷-基础信息'
      }
      // 兼容旧数据：元素库分块旧值为'meta'，新值为'element_meta'
      if (sourceType === 'element' && chunkType === 'meta') {
        return '元素-定位信息'
      }
      const map = {
        'meta': '用例-基础信息',
        'text_step': '用例-文本步骤',
        'step': '用例-表格步骤',
        'core': '接口-基础信息',
        'request': '接口-请求参数',
        'response': '接口-响应结构',
        'defect_core': '缺陷-基础信息',
        'detail': '缺陷-详细描述',
        'element_meta': '元素-定位信息',
        'requirement': '需求文档',
        'other': '其它',
      }
      return map[chunkType] || chunkType
    },

    truncateText(text, maxLen) {
      if (!text) return ''
      return text.length > maxLen ? text.substring(0, maxLen) + '...' : text
    },

    viewItem(row) {
      this.currentItem = row
      this.detailDialogVisible = true
    },

    addItem() {
      this.createForm.source_type = 'custom'
      this.createForm.source_name = ''
      this.createForm.chunk_type = 'requirement'
      this.createForm.document = ''
      this.pastedImages = []
      this.pastedDocs = []
      this.isDraggingFile = false
      this.createDialogVisible = true
    },

    // ===== 文件上传处理 =====
    triggerFileInput() {
      this.$refs.fileInputRef?.click()
    },
    triggerImageInput() {
      this.$refs.imageInputRef?.click()
    },
    onFileSelect(e) {
      const files = e.target.files
      if (!files || files.length === 0) return
      this._handleFiles(files)
      e.target.value = ''
    },
    onImageSelect(e) {
      const files = e.target.files
      if (!files || files.length === 0) return
      Array.from(files).forEach(file => {
        this._compressImage(file).then(({ dataUrl, base64, name, type }) => {
          this.pastedImages.push({ url: dataUrl, base64, name, type })
        })
      })
      e.target.value = ''
    },

    // ===== 拖拽处理 =====
    onDragOver(e) {
      const files = e.dataTransfer?.files
      if (files && files.length > 0) {
        this.isDraggingFile = true
      }
    },
    onDragLeave() {
      this.isDraggingFile = false
    },
    onDrop(e) {
      this.isDraggingFile = false
      const files = e.dataTransfer?.files
      if (!files || files.length === 0) return
      this._handleFiles(files)
    },

    // ===== 粘贴处理 =====
    onPaste(e) {
      const items = e.clipboardData?.items
      if (!items || items.length === 0) return
      const imageItems = []
      const docItems = []
      for (let i = 0; i < items.length; i++) {
        const item = items[i]
        if (item.kind === 'file') {
          const ftype = item.type || ''
          if (ftype.startsWith('image/')) {
            imageItems.push(item)
          } else {
            docItems.push(item)
          }
        }
      }
      if (imageItems.length === 0 && docItems.length === 0) return
      e.preventDefault()
      imageItems.forEach((item) => {
        const file = item.getAsFile()
        if (!file) return
        this._compressImage(file).then(({ dataUrl, base64, name, type }) => {
          this.pastedImages.push({ url: dataUrl, base64, name, type })
        })
      })
      docItems.forEach((item) => {
        const file = item.getAsFile()
        if (!file) return
        this._processDocFile(file)
      })
    },

    // 处理文件列表
    _handleFiles(files) {
      Array.from(files).forEach(file => {
        if (file.type.startsWith('image/')) {
          this._compressImage(file).then(({ dataUrl, base64, name, type }) => {
            this.pastedImages.push({ url: dataUrl, base64, name, type })
          })
        } else {
          this._processDocFile(file)
        }
      })
    },

    // 处理文档文件
    _processDocFile(file) {
      const ext = (file.name?.split('.').pop() || '').toLowerCase()
      if (!this.docAllowedExts.includes(ext)) {
        ElMessage({ message: `不支持的文件类型: .${ext}`, type: 'warning' })
        return
      }
      if (file.size > this.maxFileSize) {
        ElMessage({ message: `文件 ${file.name} 超过20MB限制`, type: 'warning' })
        return
      }
      const reader = new FileReader()
      reader.onload = (ev) => {
        const base64 = ev.target.result.split(',')[1] || ''
        this.pastedDocs.push({
          name: file.name,
          ext,
          size: file.size,
          sizeText: this._formatFileSize(file.size),
          base64,
          type: file.type || `application/${ext}`,
        })
      }
      reader.readAsDataURL(file)
    },

    // 格式化文件大小
    _formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      return (bytes / 1024 / 1024).toFixed(1) + ' MB'
    },

    // 压缩图片
    _compressImage(file) {
      return new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = (ev) => {
          const img = new Image()
          img.onload = () => {
            const MAX_DIM = 1920
            let { width, height } = img
            if (width > MAX_DIM || height > MAX_DIM) {
              const ratio = Math.min(MAX_DIM / width, MAX_DIM / height)
              width = Math.round(width * ratio)
              height = Math.round(height * ratio)
            }
            const canvas = document.createElement('canvas')
            canvas.width = width
            canvas.height = height
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, width, height)
            const dataUrl = canvas.toDataURL('image/jpeg', 0.85)
            const base64 = dataUrl.split(',')[1] || ''
            const ext = file.name?.split('.').pop() || 'png'
            resolve({
              dataUrl,
              base64,
              name: file.name || `image_${Date.now()}.${ext}`,
              type: 'image/jpeg',
            })
          }
          img.onerror = () => {
            const dataUrl = ev.target.result
            resolve({
              dataUrl,
              base64: dataUrl.split(',')[1] || '',
              name: file.name || `image_${Date.now()}.png`,
              type: file.type || 'image/png',
            })
          }
          img.src = ev.target.result
        }
        reader.readAsDataURL(file)
      })
    },

    // 删除附件
    removeDoc(idx) {
      this.pastedDocs.splice(idx, 1)
    },
    removeImage(idx) {
      this.pastedImages.splice(idx, 1)
    },

    // 解析所有文件并追加到文本
    async handleCreate() {
      if (!this.createForm.source_name.trim()) {
        ElMessage.warning('请输入知识标题')
        return
      }
      if (!this.createForm.document.trim() && !this.pastedImages.length && !this.pastedDocs.length) {
        ElMessage.warning('请输入知识内容或上传文件')
        return
      }
      this.saving = true
      try {
        // 构建文件列表
        const allFiles = [
          ...this.pastedImages.map(img => ({
            base64: img.base64,
            name: img.name,
            ext: 'jpg',
            type: img.type,
            size: 0,
          })),
          ...this.pastedDocs.map(doc => ({
            base64: doc.base64,
            name: doc.name,
            ext: doc.ext,
            type: doc.type,
            size: doc.size,
          })),
        ]
        
        const res = await this.$api.vectorstoreCreate({
          project_id: this.projectInfo.id,
          source_type: this.createForm.source_type,
          source_id: 0,
          source_name: this.createForm.source_name,
          document: this.createForm.document,
          module_id: null,
          chunk_type: this.createForm.chunk_type,
          files: allFiles,
        })
        if (res.status === 201 || (res.status >= 200 && res.status < 300)) {
          const data = res.data?.result || res.data
          if (data?.chunked) {
            ElMessage.success(`添加成功，已自动拆分为 ${data.chunk_count} 个分块`)
          } else {
            ElMessage.success('添加成功')
          }
          this.createDialogVisible = false
          this.fetchData()
          this.fetchStats()
        } else {
          ElMessage.error(res.data?.error || '添加失败')
        }
      } catch (e) {
        ElMessage.error('添加失败')
      } finally {
        this.saving = false
      }
    },

    async rebuildVectorstore(params) {
      // 构建确认文案
      const typeMap = { func_case: '功能用例', api: '接口文档', defect: '缺陷', element: '元素库' }
      const typeLabel = params.source_type ? typeMap[params.source_type] : '全部数据'
      
      try {
        await ElMessageBox.confirm(
          `确定要重建${typeLabel}的向量库吗？此操作将清空原有数据并重新同步，可能需要较长时间。`,
          '确认重建',
          {
            confirmButtonText: '确定重建',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger',
            closeOnClickModal: false,
          }
        )
      } catch {
        return // 用户取消
      }

      this.rebuilding = true
      try {
        const res = await this.$api.aiRebuildVectorstore(params)
        // CustomRender 包装器会将数据放在 result 字段中
        const data = res.data?.result || res.data
        if (res.status === 200 && data?.success) {
          // 异步任务模式：任务已提交，通知去消息中心查看进度
          ElMessage.success({
            message: data.message || `${typeLabel}重建任务已提交`,
            duration: 5000,
            showClose: true,
          })
          this.fetchData()
          this.fetchStats()
        } else {
          ElMessage.error(data?.error || res.data?.detail || '重建失败')
        }
      } catch (e) {
        ElMessage.error('重建失败')
      } finally {
        this.rebuilding = false
      }
    },

    rebuildAll() {
      this.rebuildVectorstore({ project_id: this.projectInfo.id })
    },

    handleRebuild(command) {
      const params = { project_id: this.projectInfo.id }
      if (command !== 'all') {
        params.source_type = command
      }
      this.rebuildVectorstore(params)
    },

    // 全选/取消全选
    handleSelectAll(selection) {
      // 不做特殊处理，让 selection-change 统一管理
    },

    // 选中变化
    handleSelectionChange(selection) {
      // 收集所有选中行的ID
      this.selectedIds = selection.map(item => item.id)
      // 存储选中行的source_type映射，用于删除时过滤
      this.selectedItems = selection
    },

    // 批量删除（仅删除自定义知识）
    handleBatchDelete() {
      if (this.selectedIds.length === 0) return
      
      // 过滤出自定义知识的ID
      const customItems = this.selectedItems.filter(item => item.source_type === 'custom')
      const customIds = customItems.map(item => item.id)
      const nonCustomCount = this.selectedItems.length - customItems.length
      
      if (customIds.length === 0) {
        if (nonCustomCount === this.selectedItems.length) {
          // 选中的全部是业务数据
          ElMessageBox.alert(
            '当前选中的全部是业务数据（功能用例/接口文档/缺陷/元素库），这些数据由系统自动同步管理，无需手动删除。\n\n如需删除自定义知识，请点击"新增分块"添加后再操作。',
            '无法删除',
            { confirmButtonText: '知道了', type: 'info' }
          )
        } else {
          ElMessage.warning('选中项中没有可删除的自定义知识')
        }
        return
      }
      
      let msg = `确定要删除选中的 ${customIds.length} 条自定义知识吗？`
      if (nonCustomCount > 0) {
        msg += `\n（已忽略 ${nonCustomCount} 条业务数据，这些数据由系统自动同步管理）`
      }
      
      ElMessageBox.confirm(
        msg,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(async () => {
        try {
          const res = await this.$api.vectorstoreBatchDelete({ 
            project_id: this.projectInfo.id, 
            ids: customIds 
          })
          const data = res.data?.result || res.data
          const deletedCount = data?.deleted_count || customIds.length
          if (deletedCount > customIds.length) {
            ElMessage.success(`成功删除 ${customIds.length} 条知识，共 ${deletedCount} 个分块`)
          } else {
            ElMessage.success(`成功删除 ${customIds.length} 条知识`)
          }
          this.selectedIds = []
          this.selectedItems = []
          this.fetchData()
          this.fetchStats()
        } catch (e) {
          ElMessage.error('删除失败')
        }
      }).catch(() => {})
    },

    // 单个删除（仅自定义知识）
    handleDelete(row) {
      let msg = `确定要删除"${row.source_name}"吗？`
      if (row.is_chunked) {
        msg += `\n（该文档已拆分为 ${row.chunk_total} 个分块，将全部删除）`
      }
      ElMessageBox.confirm(
        msg,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(async () => {
        try {
          const res = await this.$api.vectorstoreDelete(row.id, { project: this.projectInfo.id })
          const data = res.data?.result || res.data
          const deletedCount = data?.deleted_count || 1
          if (row.is_chunked && deletedCount > 1) {
            ElMessage.success(`删除成功，共删除 ${deletedCount} 个分块`)
          } else {
            ElMessage.success('删除成功')
          }
          this.selectedIds = []
          this.fetchData()
          this.fetchStats()
        } catch (e) {
          ElMessage.error('删除失败')
        }
      }).catch(() => {})
    },
  },
  created() {
    this.check_permission()
    this.loadSourceTypes()
    this.fetchData()
    this.fetchStats()
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

.icon-database,
.icon-keyword,
.icon-chunk {
  width: 16px;
  height: 16px;
  display: inline-block;
  flex-shrink: 0;
  border-radius: 4px;
}

.icon-database {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
}

.icon-keyword {
  background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
}

.icon-chunk {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
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
  flex-wrap: wrap;
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
  gap: 10px;
  flex-wrap: wrap;
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

.stat-item.stat-func {
  background: #eff6ff;
  border-color: #bfdbfe;
}
.stat-item.stat-func .stat-value {
  color: #2563eb;
}

.stat-item.stat-api {
  background: #ecfdf5;
  border-color: #a7f3d0;
}
.stat-item.stat-api .stat-value {
  color: #059669;
}

.stat-item.stat-defect {
  background: #fefce8;
  border-color: #fde68a;
}
.stat-item.stat-defect .stat-value {
  color: #d97706;
}

.stat-item.stat-element {
  background: #faf5ff;
  border-color: #e9d5ff;
}
.stat-item.stat-element .stat-value {
  color: #7c3aed;
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

.header-action-btns {
  display: flex;
  gap: 12px;
}

.header-action-btns .batch-delete-btn {
  padding: 10px 16px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
  border: none !important;
  color: white !important;
  transition: all 0.3s ease !important;
}

.header-action-btns .batch-delete-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.header-action-btns .batch-delete-btn .el-icon {
  font-size: 16px;
}

.header-action-btns .batch-delete-btn:disabled {
  background: #f1f5f9 !important;
  color: #94a3b8 !important;
  cursor: not-allowed;
}

.action-btn.delete-btn {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
  border: none !important;
  transition: all 0.3s ease !important;
}

.action-btn.delete-btn:hover {
  transform: scale(1.1) !important;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4) !important;
}

/* ===== 已选中徽章 ===== */
.selected-count-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1d4ed8;
  font-size: 13px;
  font-weight: 600;
}

.selected-count-badge .el-icon {
  font-size: 14px;
}

/* ===== 批量操作下拉样式（参考 CaseList） ===== */
.batch-dropdown .toolbar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border-radius: 10px !important;
  font-weight: 500 !important;
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
  border: none !important;
  color: white !important;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
  transition: all 0.3s ease !important;
}

.batch-dropdown .toolbar-btn:hover:not(:disabled) {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4) !important;
}

.batch-dropdown .toolbar-btn .el-icon {
  transition: transform 0.3s ease;
}

.batch-dropdown .toolbar-btn:hover:not(:disabled) .el-icon {
  transform: rotate(15deg);
}

/* 下拉菜单 popper 样式 */
.batch-dropdown-popper.el-popper {
  padding: 12px !important;
  border-radius: 12px !important;
  border: none !important;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
  background: white !important;
  width: auto !important;
  min-width: 120px !important;
}

.batch-dropdown-popper .el-dropdown-menu {
  border: none !important;
  box-shadow: none !important;
  padding: 0 !important;
  background: transparent !important;
  width: 100% !important;
}

.batch-dropdown-popper .el-dropdown-menu__item {
  padding: 0 !important;
  margin: 0 !important;
  border-radius: 8px !important;
  overflow: hidden;
  padding-bottom: 12px !important;
  margin-bottom: 12px !important;
  border-bottom: 1px solid #f1f5f9 !important;
}

.batch-dropdown-popper .el-dropdown-menu__item:hover {
  background: transparent !important;
}

.batch-dropdown-popper .el-dropdown-menu__item:last-child {
  padding-bottom: 0 !important;
  margin-bottom: 0 !important;
  border-bottom: none !important;
}

.batch-dropdown-item {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  padding: 14px 20px !important;
  transition: all 0.2s ease !important;
  border-radius: 8px !important;
  white-space: nowrap;
  line-height: 1.5;
}

.batch-dropdown-item:hover {
  background: #eff6ff !important;
}

.item-text {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
  transition: all 0.2s ease;
}

.batch-dropdown-item:hover .item-text {
  color: #3b82f6;
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
}

.elegant-table >>> .el-table__body-wrapper td {
  border-bottom: 1px solid #f1f5f9;
  padding: 16px 0;
  transition: all 0.3s ease;
}

.elegant-table >>> .el-table__body-wrapper .cell {
  padding: 0 16px;
}

.name-link {
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.2s ease;
}

.name-link:hover {
  text-decoration: underline;
  color: #1d4ed8 !important;
}

.name-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
}

.chunk-badge {
  font-size: 11px;
  padding: 0 4px;
  height: 18px;
  line-height: 18px;
  flex-shrink: 0;
}

.source-tag {
  font-weight: 500;
  border-width: 2px;
  border-radius: 12px;
  padding: 4px 10px;
}

.chunk-tag {
  font-weight: 500;
  border-width: 2px;
  border-radius: 12px;
  padding: 4px 10px;
}

.doc-preview {
  color: #475569;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
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

/* 对话框样式 */
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
  padding: 24px 24px 0px 24px !important;
  background: rgba(255, 255, 255, 0.7) !important;
}

.dialog-content {
  padding: 0;
}

.dialog-form {
  margin: 0;
}

.form-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 500;
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

.doc-content {
  margin: 0;
  padding: 20px;
  background: #fafbfc;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
  color: #334155;
  border: none;
}

.metadata-content {
  margin: 0;
  background: #f8fafc;
  color: #334155;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
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

.elegant-dialog >>> .el-dialog__footer {
  padding: 0px 24px 24px;
  border-top: 1px solid #f1f5f9;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 12px;
}

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

.button-text {
  position: relative;
  display: inline-block;
  padding-bottom: 3px;
}

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

.dialog-cancel-btn .button-text::after {
  background: #3b82f6;
}

.dialog-confirm-btn .button-text::after {
  background: white;
}

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
  
  .elegant-dialog >>> .el-dialog {
    width: 90% !important;
    max-width: 700px;
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

/* 创建/更新信息列样式（参考 FunCaseList） */
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

/* 内容摘要悬浮提示样式 */
:deep(.content-tooltip.el-tooltip__popper) {
  max-width: 400px !important;
  white-space: pre-wrap !important;
  word-break: break-word !important;
  line-height: 1.6 !important;
  font-size: 13px !important;
}

/* ===== 新增知识库对话框样式 ===== */
.add-knowledge-container {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.knowledge-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}

.section-label .el-icon {
  color: #8b5cf6;
  font-size: 16px;
}

.required-mark {
  color: #ef4444;
  margin-left: 2px;
}

.section-hint {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 400;
  margin-left: auto;
}

/* 分类标签卡片组 */
.chunk-type-group {
  display: flex;
  gap: 12px;
}

.chunk-type-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fff;
}

.chunk-type-card:hover {
  border-color: #c4b5fd;
  background: #f5f3ff;
}

.chunk-type-card.active {
  border-color: #8b5cf6;
  background: #f5f3ff;
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.15);
}

.chunk-icon {
  font-size: 20px;
  color: #8b5cf6;
}

.chunk-label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.chunk-type-card.active .chunk-label {
  color: #6d28d9;
  font-weight: 600;
}

/* 内容输入区 */
.content-section {
  flex: 1;
}

/* 附件预览列表 */
.attachment-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  position: relative;
}

.attachment-item.doc-item .doc-icon {
  color: #3b82f6;
  font-size: 20px;
}

.attachment-item.image-item {
  padding: 6px;
}

.attachment-thumb {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border-radius: 4px;
}

.attachment-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 120px;
}

.attachment-name {
  font-size: 13px;
  color: #334155;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 180px;
}

.attachment-size {
  font-size: 11px;
  color: #94a3b8;
}

.attachment-remove {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 18px;
  height: 18px;
  background: #ef4444;
  color: #fff;
  border-radius: 50%;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.attachment-item:hover .attachment-remove {
  opacity: 1;
}

/* 输入框容器 */
.content-input-wrapper {
  position: relative;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  transition: border-color 0.2s;
  background: #fff;
}

.content-input-wrapper:focus-within {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.content-input-wrapper.is-dragging {
  border-color: #8b5cf6;
  border-style: dashed;
  background: #f5f3ff;
}

.content-textarea {
  width: 100%;
  min-height: 200px;
  padding: 14px 16px 44px;
  border: none;
  border-radius: 10px;
  resize: vertical;
  font-size: 14px;
  line-height: 1.6;
  color: #334155;
  background: transparent;
  outline: none;
  font-family: inherit;
}

.content-textarea::placeholder {
  color: #94a3b8;
}

.content-textarea:focus {
  outline: none;
}

/* 拖拽覆盖层 */
.drag-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(245, 243, 255, 0.95);
  border-radius: 10px;
  z-index: 10;
  font-size: 14px;
  color: #6d28d9;
  font-weight: 500;
}

/* 工具栏 */
.input-toolbar {
  position: absolute;
  bottom: 8px;
  left: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toolbar-left {
  display: flex;
  gap: 6px;
}

.tool-btn {
  background: transparent;
  border: 1px solid transparent;
  color: #64748b;
  transition: all 0.2s;
}

.tool-btn:hover {
  background: #f5f3ff;
  border-color: #c4b5fd;
  color: #8b5cf6;
}

.toolbar-right {
  font-size: 12px;
  color: #94a3b8;
}

.hidden-input {
  display: none;
}

/* 对话框底部按钮 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 0px 0px 24px;
  border-top: 1px solid #e2e8f0;
}

.dialog-cancel-btn {
  padding: 8px 20px;
  border-radius: 8px;
}

.dialog-confirm-btn {
  padding: 8px 24px;
  border-radius: 8px;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  border: none;
}

.dialog-confirm-btn:hover {
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
}

/* 全局样式 */
:deep(.el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* 详情弹窗 - 布局样式（已移到全局，因为 Teleport） */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */

.char-count {
  margin-left: auto;
  font-weight: 400;
}

/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
/* (moved to global style block due to Teleport) */
</style>

<!-- 全局样式：用于详情全屏弹窗（dialog被移到body上，需要非scoped样式） -->
<style>
/* 去除全屏弹窗所有层级的边距 - 用 body > .el-overlay 前缀提高优先级覆盖 global-form.css */
body > .el-overlay:has(.detail-dialog) {
  padding: 0 !important;
  margin: 0 !important;
}

body > .el-overlay:has(.detail-dialog) .el-overlay-dialog {
  padding: 0 !important;
  margin: 0 !important;
}

body > .el-overlay:has(.detail-dialog) .el-dialog__wrapper {
  padding: 0 !important;
  margin: 0 !important;
}

/* 弹窗整体 - 覆盖 global-form.css 的 .el-dialog 样式 */
body > .el-overlay:has(.detail-dialog) .el-dialog.detail-dialog {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  border-radius: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  transform: none !important;
  overflow: hidden !important;
  animation: none !important;
  box-shadow: none !important;
  border: none !important;
}

/* 头部 */
body > .el-overlay:has(.detail-dialog) .el-dialog.detail-dialog .el-dialog__header {
  flex-shrink: 0;
  padding: 16px 20px !important;
  margin: 0 !important;
  background: linear-gradient(to right, #f8fafc, #ffffff) !important;
  border-bottom: 1px solid #e2e8f0 !important;
  border-radius: 0 !important;
  position: relative !important;
  display: flex !important;
  align-items: center !important;
  min-height: 0 !important;
}

/* 关闭按钮位置修正 */
body > .el-overlay:has(.detail-dialog) .el-dialog.detail-dialog .el-dialog__headerbtn {
  top: 50% !important;
  transform: translateY(-50%) !important;
}

/* 主体 - 覆盖 global-form.css 的 max-height: 80vh 和 overflow-y: auto */
body > .el-overlay:has(.detail-dialog) .el-dialog.detail-dialog .el-dialog__body {
  flex: 1 !important;
  padding: 24px 24px 0 24px !important;
  overflow: hidden !important;
  min-height: 0 !important;
  max-height: none !important;
}

/* 去除 footer */
body > .el-overlay:has(.detail-dialog) .el-dialog.detail-dialog .el-dialog__footer {
  display: none !important;
}

/* ========== 详情弹窗内部内容样式（从 scoped 移到全局，因为 Teleport） ========== */

/* 基础信息卡片 - 占 1/3 */
body > .el-overlay:has(.detail-dialog) .info-section {
  flex: 1;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
}

/* Metadata 区域 - 占 2/3 */
body > .el-overlay:has(.detail-dialog) .metadata-section {
  flex: 2;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
}

/* 文档内容区域 - 全宽 */
body > .el-overlay:has(.detail-dialog) .content-section {
  flex: 1;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Metadata 内容框 */
body > .el-overlay:has(.detail-dialog) .metadata-box {
  flex: 1;
  overflow-y: auto;
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px 12px;
  min-height: 0;
  max-height: 400px;
  border: 1px solid #e2e8f0;
}

/* 基础信息内容框 - 与 metadata 高度一致 */
body > .el-overlay:has(.detail-dialog) .info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
  flex: 1;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 12px;
}

/* 文档内容框 */
body > .el-overlay:has(.detail-dialog) .doc-content-box {
  flex: 1;
  overflow-y: auto;
  background: #f8fafc;
  border-radius: 8px;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  min-height: 0;
}

/* Metadata 和文档内容 统一细滚动条 */
/* Metadata 的 scrollbar 实际在 <pre> 标签上，需要同时设置 */
.metadata-box::-webkit-scrollbar,
.metadata-content::-webkit-scrollbar,
.doc-content-box::-webkit-scrollbar {
  width: 4px !important;
}

.metadata-box::-webkit-scrollbar-track,
.metadata-content::-webkit-scrollbar-track,
.doc-content-box::-webkit-scrollbar-track {
  background: transparent !important;
}

.metadata-box::-webkit-scrollbar-thumb,
.metadata-content::-webkit-scrollbar-thumb,
.doc-content-box::-webkit-scrollbar-thumb {
  background-color: rgba(148, 163, 184, 0.5) !important;
  border-radius: 2px !important;
}

.metadata-box::-webkit-scrollbar-thumb:hover,
.metadata-content::-webkit-scrollbar-thumb:hover,
.doc-content-box::-webkit-scrollbar-thumb:hover {
  background-color: rgba(100, 116, 139, 0.7) !important;
}

/* 让 metadata-box 内的 <pre> 不自己产生滚动条，由父容器滚动 */
body > .el-overlay:has(.detail-dialog) .metadata-box .metadata-content {
  overflow: visible !important;
  height: auto !important;
  max-height: none !important;
}

/* 布局容器 */
body > .el-overlay:has(.detail-dialog) .detail-dialog-body {
  display: flex !important;
  flex-direction: column !important;
  gap: 16px !important;
  height: 100% !important;
  overflow-y: auto !important;
}

body > .el-overlay:has(.detail-dialog) .detail-top-row {
  display: flex !important;
  gap: 16px !important;
  flex-shrink: 0 !important;
}

/* 详情弹窗内容样式 - 基础文本元素 */
body > .el-overlay:has(.detail-dialog) .section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

body > .el-overlay:has(.detail-dialog) .section-icon {
  color: #3b82f6;
  font-size: 16px;
}

body > .el-overlay:has(.detail-dialog) .section-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

body > .el-overlay:has(.detail-dialog) .char-count {
  margin-left: auto;
  font-weight: 400;
}

body > .el-overlay:has(.detail-dialog) .info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

body > .el-overlay:has(.detail-dialog) .info-label {
  font-size: 12px;
  color: #64748b;
  min-width: 64px;
}

body > .el-overlay:has(.detail-dialog) .info-value {
  font-size: 13px;
  color: #334155;
  font-weight: 500;
}

body > .el-overlay:has(.detail-dialog) .doc-content {
  margin: 0;
  font-size: 13px;
  line-height: 1.8;
  color: #334155;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'Menlo', 'Monaco', 'Consolas', 'Courier New', monospace;
}

body > .el-overlay:has(.detail-dialog) .metadata-content {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: #334155;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Menlo', 'Monaco', 'Consolas', 'Courier New', monospace;
}

/* 去除 header 的默认关闭按钮区域的右边距（因为没有 footer 关闭按钮了） */
body > .el-overlay:has(.detail-dialog) .el-dialog.detail-dialog .el-dialog__headerbtn {
  display: flex !important;
}

/* 新增知识弹窗 body - 仅底部为0，覆盖全局 el-dialog__body 的 24px */
body > .el-overlay:has(.add-knowledge-dialog) .el-dialog.add-knowledge-dialog .el-dialog__body {
  padding: 24px 24px 0 24px !important;
}

/* 全局样式：用于悬浮提示（Tooltip 弹出层在 body 上，需要非 scoped 样式） */
.content-tooltip.el-tooltip__popper {
  max-width: 400px !important;
  white-space: pre-wrap !important;
  word-break: break-word !important;
  line-height: 1.6 !important;
  font-size: 13px !important;
}
</style>
