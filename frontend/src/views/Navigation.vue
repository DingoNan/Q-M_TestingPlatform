<template>
  <div class="navigation-management-container">
    <!-- 顶部固定导航栏 -->
    <div class="fixed-header elegant-shadow">
      <div class="header-content">
        <!-- Logo区域 -->
        <div class="logo-section">
          <div class="logo-wrapper">
            <!-- 平台Logo -->
            <div class="logo-circle">
              <svg class="logo-icon" viewBox="0 0 100 100">
                <path d="M50,10 L90,30 L90,70 L50,90 L10,70 L10,30 Z" class="logo-hexagon"></path>
                <circle cx="50" cy="50" r="20" class="logo-center"></circle>
                <path d="M35,35 L65,35 L65,65 L35,65 Z" class="logo-square"></path>
              </svg>
              <div class="logo-glow"></div>
            </div>
            <div class="platform-info">
              <h1 class="platform-name">Q·M 测试平台</h1>
              <p class="platform-slogan">智能测试解决方案</p>
            </div>
          </div>
        </div>

        <!-- 搜索区域 -->
        <div class="search-section">
          <div class="search-wrapper">
            <div class="search-container">
              <!-- 分组选择 -->
              <el-select
                v-model="search.id"
                class="group-selector"
                multiple
                collapse-tags
                collapse-tags-tooltip
                placeholder="请选择分组"
                size='large'
                popper-class='select-dropdown-rounded'
                clearable
              >
                <el-option
                  v-for="group_obj in all_groups"
                  :key="group_obj.id"
                  :label="group_obj.name"
                  :value="group_obj.id"
                />
              </el-select>
              
              <!-- 搜索输入框 -->
              <el-input
                v-model="search.key"
                placeholder="请输入导航名称"
                class="search-input"
                clearable
                size='large'
              >
                <template #prefix>
                  <el-icon class="search-icon"><search /></el-icon>
                </template>
              </el-input>
              
              <!-- 搜索按钮 -->
              <el-button
                type="primary"
                @click="handleSearch"
                size='large'
                class="search-action-btn"
              >
                <el-icon><Search /></el-icon>
                搜索
              </el-button>
            </div>
          </div>
        </div>

        <!-- 操作按钮区域 -->
        <div class="action-section">
          <el-button
            type="primary"
            @click="addGroup"
			size='large'
            class="add-group-btn elegant-shadow"
          >
            <el-icon><Plus /></el-icon>
            添加分组
          </el-button>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-wrapper">
        <!-- 分组卡片区域 -->
        <div v-for="group_obj in group_list" :key="group_obj.id" class="group-container">
          <el-card
            v-if="!hasSearched || group_obj.navigation_set.length !== 0"
            class="group-card elegant-shadow"
            :class="{ 'empty-group': group_obj.navigation_set.length === 0 }"
          >
            <!-- 分组标题栏 -->
            <template #header>
              <div class="card-header">
                <div class="group-title-section">
                  <div class="group-title-wrapper">
                    <div class="group-indicator"></div>
                    <h3 class="group-title">{{ group_obj.name }}</h3>
                    <el-tag size="small" type="info" effect="plain">
                      {{ group_obj.navigation_set.length }} 个导航
                    </el-tag>
                  </div>
                  <div class="group-actions">
                    <el-button
                      type="primary"
					  size='large'
                      @click="handleAddNavigation(group_obj)"
                      class="add-navigation-btn"
                    >
                      <el-icon><Plus /></el-icon>
                      添加导航
                    </el-button>
                    <el-dropdown @command="(command) => handleGroupCommand(command, group_obj)">
                      <el-button class="group-dropdown-btn" size='large'>
                        操作
                        <el-icon><ArrowDown /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item :command="{ type: 'edit', group_obj: group_obj }">
                            <el-icon><EditPen /></el-icon>
                            编辑分组
                          </el-dropdown-item>
                          <el-dropdown-item
                            :command="{ type: 'delete', group_obj: group_obj }"
                            divided
                            class="delete-item"
                          >
                            <el-icon><Delete /></el-icon>
                            删除分组
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </div>
              </div>
            </template>

            <!-- 导航项目 -->
            <div class="navigation-grid">
              <div
                v-for="navigation_obj in group_obj.navigation_set"
                :key="navigation_obj.id"
                class="navigation-item"
                @click="jumpLink(navigation_obj.url)"
              >
                <el-card
                  class="navigation-card elegant-shadow"
                  :style="{
                    '--card-bg-color': navigation_obj.color || '#f59e0b',
                    '--card-hover-bg-color': getHoverColor(navigation_obj.color || '#f59e0b')
                  }"
                  @click="jumpLink(navigation_obj.url)"
                >
                  <div class="navigation-content">
                    <!-- 导航图标 -->
                    <div class="navigation-icon-wrapper">
                      <el-avatar
                        :src="navigation_obj.icon_url"
                        :size="48"
                        class="navigation-icon"
                        :style="{ backgroundColor: navigation_obj.color || '#f59e0b' }"
                      >
                        <span v-if="!navigation_obj.icon_url" class="icon-placeholder">
                          {{ getFirstChar(navigation_obj.name) }}
                        </span>
                      </el-avatar>
                    </div>

                    <!-- 导航名称 -->
                    <div class="navigation-info">
                      <el-tooltip
                        :content="navigation_obj.name"
                        placement="top"
                        effect="light"
                      >
                        <span class="navigation-name">{{ navigation_obj.name }}</span>
                      </el-tooltip>
                      <span class="navigation-url">{{ getDomain(navigation_obj.url) }}</span>
                    </div>

                    <!-- 操作菜单 -->
                    <div class="navigation-actions" @click.stop>
                      <el-dropdown @command="(command) => handleNavigationCommand(command, navigation_obj)">
                        <el-button
                          size="small"
                          text
                          circle
                          class="navigation-action-btn"
                        >
                          <el-icon><More /></el-icon>
                        </el-button>
                        <template #dropdown>
                          <el-dropdown-menu>
                            <el-dropdown-item :command="{ type: 'edit', navigation_obj: navigation_obj }">
                              <el-icon><EditPen /></el-icon>
                              编辑
                            </el-dropdown-item>
                            <el-dropdown-item
                              :command="{ type: 'delete', navigation_obj: navigation_obj }"
                              divided
                              class="delete-item"
                            >
                              <el-icon><Delete /></el-icon>
                              删除
                            </el-dropdown-item>
                          </el-dropdown-menu>
                        </template>
                      </el-dropdown>
                    </div>
                  </div>
                </el-card>
              </div>

              <!-- 空状态 -->
              <div v-if="group_obj.navigation_set.length === 0" class="empty-navigation">
                <div class="empty-content">
                  <el-icon class="empty-icon"><Grid /></el-icon>
                  <p class="empty-text">暂无导航项目</p>
                  <el-button
                    type="primary"
                    link
                    @click="handleAddNavigation(group_obj)"
                  >
                    点击添加第一个导航
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>

        <!-- 空状态 - 根据搜索条件显示不同内容 -->
        <div v-if="group_list.length === 0 || isSearchResultEmpty" class="empty-state">
          <div class="empty-state-content">
            <el-icon class="empty-state-icon" :class="{ 'search-empty': search.key || search.id.length > 0 }">
              <component :is="search.key || search.id.length > 0 ? 'Search' : 'FolderOpened'" />
            </el-icon>
            <h3 class="empty-state-title">
              {{ search.key || search.id.length > 0 ? '暂无数据' : '暂无分组' }}
            </h3>
            <p class="empty-state-description">
              {{ search.key || search.id.length > 0 ? '没有找到匹配的导航项目，请尝试其他搜索条件' : '创建分组来组织您的导航项目' }}
            </p>
            <el-button
              v-if="!search.key && search.id.length === 0"
              type="primary"
              @click="addGroup"
              class="empty-state-btn"
            >
              <el-icon><Plus /></el-icon>
              创建第一个分组
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分组表单对话框 -->
    <el-dialog
      v-model="addGroupDialogVisible"
      :title="group_title"
      width="500"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <el-form
        :model="addGroupForm"
        :rules="groupRules"
        ref="groupFormRef"
        label-position="left"
        class="dialog-form"
      >
        <el-form-item label="分组名称" prop="name" class="dialog-form-item">
          <el-input
            v-model="addGroupForm.name"
            placeholder="请输入分组名称"
            class="input"
			size='large'
            :maxlength="20"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="排序数值" prop="sort" class="dialog-form-item">
          <el-input-number
            v-model="addGroupForm.sort"
            :min="0"
            :max="999"
            :step="1"
            controls-position="right"
            class="input"
            size='large'
          />
          <div class="sort-tip">数值越小，排序越靠前</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addGroupDialogVisible = false" class="dialog-cancel-btn">
            取消
          </el-button>
          <el-button
            v-if="is_add_group"
            type="primary"
            @click="createGroup"
            class="dialog-confirm-btn"
          >
            确认添加
          </el-button>
          <el-button
            v-if="!is_add_group"
            type="primary"
            @click="updateGroup"
            class="dialog-confirm-btn"
          >
            确认修改
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 导航表单对话框 -->
    <el-dialog
      v-model="addNavigationDialogVisible"
      :title="is_add_group ? '添加导航' : '编辑导航'"
      width="600"
      class="elegant-dialog"
      :close-on-click-modal="false"
    >
      <el-form
        :model="saveNavigation"
        :rules="navigationRules"
        ref="navigationFormRef"
        label-position="right"
        class="dialog-form"
      >
        <el-form-item label="所属分组" prop="group" class="dialog-form-item">
          <el-select
            v-model="saveNavigation.group"
            placeholder="请选择分组"
            class="select"
            size='large'
            popper-class='select-dropdown-rounded'
            :disabled="!is_add_group"
          >
            <el-option
              v-for="group in group_list"
              :key="group.id"
              :label="group.name"
              :value="group.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="导航名称" prop="name" class="dialog-form-item">
          <el-input
            v-model="saveNavigation.name"
            placeholder="请输入导航名称"
            class="input"
            size='large'
            :maxlength="20"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="背景颜色" prop="color" class="dialog-form-item">
          <div class="color-picker-wrapper">
            <el-color-picker
              v-model="saveNavigation.color"
              show-alpha
              :predefine="predefineColors"
            />
            <span class="color-value">{{ saveNavigation.color }}</span>
          </div>
        </el-form-item>
        <el-form-item label="图标地址" prop="icon_url" class="dialog-form-item">
          <el-input
            v-model="saveNavigation.icon_url"
            placeholder="请输入图标URL地址"
           class="input"
           size='large'
          />
          <div class="icon-preview" v-if="saveNavigation.icon_url">
            <span class="preview-label">预览：</span>
            <el-avatar
              :src="saveNavigation.icon_url"
              :size="32"
              class="preview-icon"
            />
          </div>
        </el-form-item>
        <el-form-item label="导航地址" prop="url" class="dialog-form-item">
          <el-input
            v-model="saveNavigation.url"
            placeholder="请输入完整的URL地址（以 http:// 或 https:// 开头）"
            class="input"
            size='large'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addNavigationDialogVisible = false" class="dialog-cancel-btn">
            取消
          </el-button>
          <el-button
            v-if="is_add_group"
            type="primary"
            @click="createNavigation"
            class="dialog-confirm-btn"
          >
            确认添加
          </el-button>
          <el-button
            v-if="!is_add_group"
            type="primary"
            @click="updateNavigation"
            class="dialog-confirm-btn"
          >
            确认修改
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage, ElMessageBox } from 'element-plus'
import { mapState } from 'vuex'
import {
  Search,
  Plus,
  EditPen,
  Delete,
  ArrowDown,
  More,
  Grid,
  FolderOpened
} from '@element-plus/icons-vue'

export default {
  name: 'NavigationManagement',
  computed: {
    ...mapState(['projectInfo']),
    // 判断搜索结果是否为空（有搜索条件但没有匹配的导航）
    isSearchResultEmpty() {
      // 如果有搜索条件，但所有分组都没有导航项目，则显示暂无数据
      if (this.search.key || this.search.id.length > 0) {
        return this.group_list.every(group => group.navigation_set.length === 0)
      }
      return false
    }
  },
  data() {
    return {
      addGroupDialogVisible: false,
      addNavigationDialogVisible: false,
      group_title: '添加分组',
      is_add_group: true,
      search: {
        key: '',
        id: [],
        ids: ''
      },
      hasSearched: false, // 是否已执行搜索
      group_list: [],
      all_groups: [], // 保存所有分组，用于下拉选择
      addGroupForm: {
        name: '',
        sort: 0
      },
      saveNavigation: {
        name: '',
        url: '',
        color: '#f59e0b',
        icon_url: '',
        group: '',
        group_name: ''
      },
      groupRules: {
        name: [
          { required: true, message: '请输入分组名称', trigger: 'blur' },
          { min: 1, max: 20, message: '分组名称长度在1-20个字符之间', trigger: 'blur' }
        ],
        sort: [
		  { required: true, message: '请输入排序值', trigger: 'blur' },
          { type: 'number', message: '排序值必须为数字', trigger: 'blur' }
        ]
      },
      navigationRules: {
        name: [
          { required: true, message: '请输入导航名称', trigger: 'blur' },
          { min: 1, max: 20, message: '导航名称长度在1-20个字符之间', trigger: 'blur' }
        ],
		color: [
		  { required: true, message: '请选择背景颜色', trigger: 'blur' },
		],
		icon_url: [
		  { required: true, message: '请输入图标地址', trigger: 'blur' },
		  {
		    pattern: /^(https?:\/\/)/,
		    message: '请输入有效的URL地址（以 http:// 或 https:// 开头）',
		    trigger: 'blur'
		  }
		],
        url: [
          { required: true, message: '请输入导航地址', trigger: 'blur' },
          {
            pattern: /^(https?:\/\/)/,
            message: '请输入有效的URL地址（以 http:// 或 https:// 开头）',
            trigger: 'blur'
          }
        ],
        group: [
          { required: true, message: '请选择所属分组', trigger: 'change' }
        ]
      },
      predefineColors: [
        '#f59e0b',
        '#67C23A',
        '#E6A23C',
        '#F56C6C',
        '#909399',
        '#1E90FF',
        '#32CD32',
        '#FFD700',
        '#FF69B4',
        '#8A2BE2'
      ]
    }
  },
  components: {
    Search,
    Plus,
    EditPen,
    Delete,
    ArrowDown,
    More,
    Grid,
    FolderOpened
  },
  methods: {
    getFirstChar(name) {
      return name ? name.charAt(0).toUpperCase() : 'N'
    },

    getDomain(url) {
      if (!url) return ''
      try {
        const urlObj = new URL(url)
        return urlObj.hostname
      } catch {
        return url.length > 30 ? url.substring(0, 30) + '...' : url
      }
    },

    getHoverColor(baseColor) {
      // 生成稍微暗一点的颜色作为悬停色
      if (!baseColor) return '#357ae8'
      return baseColor.replace(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/, (match, r, g, b) => {
        return `rgb(${Math.max(0, r - 20)}, ${Math.max(0, g - 20)}, ${Math.max(0, b - 20)})`
      })
    },

    jumpLink(url) {
      if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
        window.open(url, '_blank')
      } else {
        ElMessage.warning('无效的链接地址')
      }
    },

    handleGroupCommand(command, group_obj) {
      if (command.type === 'edit') {
        this.group_title = '编辑分组'
        this.addGroupDialogVisible = true
        this.is_add_group = false
        this.addGroupForm = { ...group_obj }
      } else if (command.type === 'delete') {
        this.deleteGroup(group_obj)
      }
    },

    handleNavigationCommand(command, navigation_obj) {
      if (command.type === 'edit') {
        this.is_add_group = false
        this.addNavigationDialogVisible = true
        this.saveNavigation = { ...navigation_obj }
      } else if (command.type === 'delete') {
        this.deleteNavigation(navigation_obj.id)
      }
    },

    handleAddNavigation(group_obj) {
      this.is_add_group = true
      this.saveNavigation = {
        name: '',
        url: '',
        color: '#f59e0b',
        icon_url: '',
        group: group_obj.id,
        group_name: group_obj.name
      }
      this.addNavigationDialogVisible = true
    },

    handleSearch() {
      this.hasSearched = true
      // 检查是否有任何搜索条件
      const hasSearchCondition = this.search.key && this.search.key.trim() !== '' || 
                                 (this.search.id && this.search.id.length > 0)
      // 如果没有任何搜索条件，直接获取全部数据
      if (!hasSearchCondition) {
        this.getGroups(false)
      } else {
        this.getGroups(true)
      }
    },

    // 获取分组列表
    // isSearch: 是否是搜索操作（true: 带搜索条件，false: 获取全部分组）
    async getGroups(isSearch = false) {
      try {
        let searchParams = {}
        // 如果是搜索操作，只有当有搜索关键词或选中分组时才带上搜索条件
        if (isSearch) {
          searchParams = { ...this.search }
          // 只有当有选中分组时才添加ids参数
          if (this.search.id && this.search.id.length > 0) {
            searchParams.ids = this.search.id.join(',')
          } else {
            // 没有选中分组时，移除ids参数以获取全部数据
            delete searchParams.ids
            delete searchParams.id
          }
          // 如果没有任何搜索条件，直接获取全部数据
          if (!searchParams.key && (!searchParams.ids || searchParams.ids === '')) {
            searchParams = {}
          }
        }
        const response = await this.$api.getGroups(searchParams)
        if (response.status === 200) {
          const results = response.data.results || []
          if (isSearch) {
            // 搜索时，只更新显示的分组列表
            this.group_list = results
          } else {
            // 初始加载或刷新时，重置搜索状态并更新所有分组
            this.hasSearched = false
            this.all_groups = results
            this.group_list = results
          }
        }
      } catch (error) {
        console.error('获取分组列表失败:', error)
      }
    },

    addGroup() {
      this.group_title = '添加分组'
      this.is_add_group = true
      this.addGroupForm = {
        name: '',
        sort: 0
      }
      this.addGroupDialogVisible = true
      this.$nextTick(() => {
        if (this.$refs.groupFormRef) {
          this.$refs.groupFormRef.clearValidate()
        }
      })
    },

    async createGroup() {
      try {
        await this.$refs.groupFormRef.validate()
        const response = await this.$api.createGroup(this.addGroupForm)
        if (response.status === 201) {
          this.getGroups()
          ElMessage.success('分组创建成功')
          this.addGroupDialogVisible = false
        }
      } catch (error) {
        if (error.errors) return // 验证失败
        console.error('创建分组失败:', error)
        ElMessage.error('创建分组失败')
      }
    },

    async updateGroup() {
      try {
        await this.$refs.groupFormRef.validate()
        const response = await this.$api.updateGroup(this.addGroupForm.id, this.addGroupForm)
        if (response.status === 200) {
          this.getGroups()
          ElMessage.success('分组更新成功')
          this.addGroupDialogVisible = false
          this.is_add_group = true
        }
      } catch (error) {
        if (error.errors) return // 验证失败
        console.error('更新分组失败:', error)
        ElMessage.error('更新分组失败')
      }
    },

    async createNavigation() {
      try {
        await this.$refs.navigationFormRef.validate()
        const response = await this.$api.createNavigation(this.saveNavigation)
        if (response.status === 201) {
          this.getGroups()
          ElMessage.success('导航创建成功')
          this.addNavigationDialogVisible = false
        }
      } catch (error) {
        if (error.errors) return // 验证失败
        console.error('创建导航失败:', error)
        ElMessage.error('创建导航失败')
      }
    },

    async updateNavigation() {
      try {
        await this.$refs.navigationFormRef.validate()
        const response = await this.$api.updateNavigation(
          this.saveNavigation.id,
          this.saveNavigation
        )
        if (response.status === 200) {
          this.getGroups()
          ElMessage.success('导航更新成功')
          this.addNavigationDialogVisible = false
          this.is_add_group = true
        }
      } catch (error) {
        if (error.errors) return // 验证失败
        console.error('更新导航失败:', error)
        ElMessage.error('更新导航失败')
      }
    },

    deleteNavigation(id) {
      ElMessageBox.confirm(
        '确定删除此导航？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        try {
          const response = await this.$api.deleteNavigation(id)
          if (response.status === 204) {
            this.getGroups()
            ElMessage.success('删除成功')
          }
        } catch (error) {
          console.error('删除导航失败:', error)
          ElMessage.error('删除失败')
        }
      }).catch(() => {})
    },

    deleteGroup(group_obj) {
      if (group_obj.navigation_set.length > 0) {
        ElMessage.warning('该分组下存在导航项目，请先删除所有导航后再删除分组')
        return
      }

      ElMessageBox.confirm(
        '确定删除此分组？删除后数据将无法恢复。',
        '确认删除',
        {
          confirmButtonText: '确认删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'confirm-dialog'
        }
      ).then(async () => {
        try {
          const response = await this.$api.deleteGroup(group_obj.id)
          if (response.status === 204) {
            this.getGroups()
            ElMessage.success('删除成功')
          }
        } catch (error) {
          console.error('删除分组失败:', error)
          ElMessage.error('删除失败')
        }
      }).catch(() => {})
    }
  },
  created() {
    this.getGroups()
  }
}
</script>

<style scoped>
.navigation-management-container {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  display: flex;
  flex-direction: column;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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

/* 固定顶部栏 - 高度调整为74px */
.fixed-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  padding: 0 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  height: 74px;
  display: flex;
  align-items: center;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 24px;
}

/* Logo区域 - 重新设计 */
.logo-section {
  flex-shrink: 0;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.logo-wrapper:hover {
  transform: translateX(-2px);
}

/* Logo样式 - 与登录页保持一致 */
.logo-circle {
  position: relative;
  width: 50px;
  height: 50px;
  flex-shrink: 0;
}

.logo-icon {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 0 15px rgba(245, 158, 11, 0.5));
  animation: logoFloat 6s ease-in-out infinite;
}

.logo-hexagon {
  fill: none;
  stroke: #f59e0b;
  stroke-width: 4;
  stroke-linecap: round;
  stroke-linejoin: round;
  animation: hexagonPulse 3s ease-in-out infinite;
}

.logo-center {
  fill: #f59e0b;
  opacity: 0.8;
  animation: centerPulse 2s ease-in-out infinite;
}

.logo-square {
  fill: rgba(255, 255, 255, 0.9);
}

.logo-glow {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.3) 0%, transparent 70%);
  animation: glowPulse 4s ease-in-out infinite;
}

.platform-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.platform-name {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: -0.5px;
  line-height: 1;
}

.platform-slogan {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  margin: 0;
  font-weight: 400;
  letter-spacing: 0.5px;
}

/* Logo动画 */
@keyframes logoFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-5px) rotate(3deg); }
  75% { transform: translateY(3px) rotate(-3deg); }
}

@keyframes hexagonPulse {
  0%, 100% { stroke-width: 4; }
  50% { stroke-width: 5; }
}

@keyframes centerPulse {
  0%, 100% { opacity: 0.8; r: 20; }
  50% { opacity: 1; r: 21; }
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.4; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.05); }
}

/* 搜索区域 - 优化样式 */
.search-section {
  flex: 1;
  max-width: 700px;
}

.search-wrapper {
  width: 100%;
}

/* 新的搜索容器样式 */
.search-container {
  display: flex;
  align-items: stretch;
  background: var(--qm-bg-2);
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  height: 48px;
}

/* 确保所有子元素都填充高度 */
.search-container > * {
  height: 100%;
}

.search-container:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.search-container:focus-within {
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2), 0 6px 20px rgba(0, 0, 0, 0.15);
}

/* 分组选择器 - 调整垂直对齐 */
.group-selector {
  width: 180px;
  flex-shrink: 0;
  /* 用 margin 向下调整位置 */
  margin-top: 4px;
  /* 覆盖所有边框变量 */
  --el-select-border-color-hover: transparent !important;
  --el-select-border-color-focus: transparent !important;
  --el-input-border-color: transparent !important;
  --el-input-border-color-hover: transparent !important;
  --el-input-border-color-focus: transparent !important;
  --el-border-color: transparent !important;
  --el-border-color-light: transparent !important;
  --el-border-color-lighter: transparent !important;
  --el-fill-color-blank: transparent !important;
}

/* 直接调整选择器位置 */
.group-selector :deep(.el-input__wrapper) {
  border-radius: 12px 0 0 12px !important;
  background: var(--qm-bg-1) !important;
  border: none !important;
  box-shadow: none !important;
  position: relative;
  transform: translateY(30px);
}

/* 彻底移除所有状态下的边框 */
.group-selector :deep(.el-select__wrapper),
.group-selector :deep(.el-select__wrapper.is-focus),
.group-selector :deep(.el-select__wrapper:hover),
.group-selector :deep(.el-input__wrapper.is-focus),
.group-selector :deep(.el-input__wrapper:hover),
.group-selector :deep(.el-input__wrapper),
.group-selector :deep(.el-input),
.group-selector :deep(*) {
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
}

/* 覆盖所有状态 */
.group-selector :deep(.el-input__wrapper.is-focus),
.group-selector :deep(.el-input__wrapper:hover) {
  border: none !important;
  box-shadow: none !important;
}

/* 多选标签样式 - 折叠显示 */
.group-selector :deep(.el-select__tags) {
  flex-wrap: nowrap;
  max-width: 130px;
}

/* 确保 placeholder 和选中项正常显示 */
.group-selector :deep(.el-select__placeholder),
.group-selector :deep(.el-select__selected-item) {
  max-width: 130px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.group-selector :deep(.el-select__tag) {
  max-width: 90px;
  height: 22px;
  line-height: 20px;
  font-size: 11px;
  flex-shrink: 0;
}

.group-selector :deep(.el-select__tags-text) {
  max-width: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.group-selector :deep(.el-select__collapse-tag) {
  height: 22px;
  line-height: 20px;
  font-size: 11px;
  flex-shrink: 0;
  min-width: 28px;
  justify-content: center;
}

/* 搜索输入框 */
.search-input {
  flex: 1;
  min-width: 150px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 0;
  box-shadow: none !important;
  border: none !important;
  padding: 0 16px 0 8px;
  background: var(--qm-bg-1);
  min-height: 48px;
  height: 48px;
  display: flex;
  align-items: center;
}

.search-input :deep(.el-input__inner) {
  height: 48px;
  line-height: 48px;
}



/* 搜索图标 */
.search-icon {
  color: var(--qm-text-3);
  font-size: 18px;
}

.search-wrapper :deep(.el-input__prefix) {
  height: 48px;
  display: flex;
  align-items: center;
  left: 0;
}

/* 搜索按钮 */
.search-action-btn {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  border-radius: 0 12px 12px 0;
  padding: 0 20px;
  height: 48px;
  line-height: 48px;
  margin: 0;
}

.search-action-btn:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.4);
}

.search-action-btn:active {
  transform: scale(0.98);
}

/* 操作按钮区域 */
.action-section {
  flex-shrink: 0;
}

.add-group-btn {
  padding: 12px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-group-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
}

/* 主内容区域 */
.main-content {
  flex: 1;
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 分组卡片 */
.group-container {
  animation: slideInUp 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.group-card {
  border-radius: 20px;
  border: 1px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  overflow: hidden;
}

.group-card.empty-group {
  opacity: 0.8;
}

.group-card :deep(.el-card__header) {
  padding: 20px 24px;
  background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  border-bottom: none !important;
}

.card-header {
  padding: 0;
}

.group-title-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.group-title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.group-indicator {
  width: 4px;
  height: 24px;
  background: linear-gradient(180deg, #f59e0b 0%, #f97316 100%);
  border-radius: 2px;
}

.group-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: var(--qm-text-1);
}

.group-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.add-navigation-btn {
  padding: 8px 16px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.add-navigation-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.group-dropdown-btn {
  padding: 8px 16px;
  border-radius: 10px;
  background: var(--qm-bg-2);
  border: 1px solid var(--qm-line-strong);
  color: var(--qm-text-2);
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.group-dropdown-btn:hover {
  border-color: var(--qm-line-strong);
  background: var(--qm-bg-1);
  transform: translateY(-1px);
}

/* 导航网格 */
.navigation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 24px;
}

.navigation-item {
  cursor: pointer;
  transition: transform 0.3s ease;
}

.navigation-item:hover {
  transform: translateY(-4px);
}

.navigation-card {
  border-radius: 16px;
  border: none;
  background-color: var(--card-bg-color);
  height: 100%;
  min-height: 120px;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.navigation-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
}

.navigation-card:hover {
  background-color: var(--card-hover-bg-color);
  transform: translateY(-4px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
}

.navigation-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  height: 100%;
  color: white;
}

.navigation-icon-wrapper {
  flex-shrink: 0;
}

.navigation-icon {
  border: 3px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.navigation-card:hover .navigation-icon {
  transform: scale(1.1);
  border-color: rgba(255, 255, 255, 0.5);
}

.icon-placeholder {
  font-size: 20px;
  font-weight: bold;
  color: white;
}

.navigation-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.navigation-name {
  font-size: 16px;
  font-weight: 600;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.navigation-url {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.navigation-actions {
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.navigation-item:hover .navigation-actions {
  opacity: 1;
}

.navigation-action-btn {
  background: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
  border: none;
}

.navigation-action-btn:hover {
  background: rgba(255, 255, 255, 0.3) !important;
}

/* 空状态 */
.empty-navigation {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--qm-text-3);
}

.empty-icon {
  font-size: 48px;
  color: var(--qm-line-strong);
}

.empty-text {
  margin: 0;
  font-size: 16px;
  color: var(--qm-text-2);
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: var(--qm-bg-2);
  border-radius: 20px;
  border: 2px dashed var(--qm-line-strong);
  margin-top: 24px;
}

.empty-state-content {
  text-align: center;
  max-width: 400px;
  padding: 48px;
}

.empty-state-icon {
  font-size: 72px;
  color: var(--qm-line-strong);
  margin-bottom: 24px;
  display: inline-block;
}

.empty-state-icon.search-empty {
  color: var(--qm-text-3);
}

.empty-state-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--qm-text-1);
}

.empty-state-description {
  margin: 0 0 24px 0;
  color: var(--qm-text-2);
  font-size: 16px;
}

.empty-state-btn {
  padding: 12px 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border: none;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.empty-state-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.3);
}

/* 对话框样式 - 优化为与登录页一致的设计语言 */
.elegant-dialog >>> .el-dialog {
  border-radius: 24px;
  overflow: hidden;
  background: linear-gradient(135deg, var(--qm-bg-2) 0%, var(--qm-bg-1) 100%);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.elegant-dialog >>> .el-dialog__header {
  padding: 24px 24px 0;
  margin: 0;
  background: linear-gradient(180deg, var(--qm-bg-1) 0%, var(--qm-bg-3) 100%);
  border-bottom: 1px solid var(--qm-line-strong);
}

.elegant-dialog >>> .el-dialog__title {
  font-size: 20px;
  font-weight: 700;
  color: var(--qm-text-1);
  display: flex;
  align-items: center;
  gap: 12px;
  padding-left: 12px;
  position: relative;
}

.elegant-dialog >>> .el-dialog__title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #f59e0b 0%, #f97316 100%);
  border-radius: 2px;
}

.elegant-dialog >>> .el-dialog__body {
  padding: 24px;
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

.dialog-form-item >>> .el-form-item__label {
  font-size: 14px;
  font-weight: 600;
  color: var(--qm-text-2);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.dialog-form-item >>> .el-form-item__label::before {
  content: '•';
  color: #f59e0b;
  font-size: 18px;
}

.dialog-input >>> .el-input__inner {
  border-radius: 12px;
  border: 2px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  padding: 0 16px;
  height: 48px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
  font-size: 14px;
}

.dialog-input >>> .el-input__inner:hover {
  border-color: var(--qm-line-strong);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-input >>> .el-input__inner:focus {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
}

.dialog-select >>> .el-input__inner {
  border-radius: 12px;
  border: 2px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  padding: 0 16px;
  height: 48px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.sort-input {
  width: 100%;
}

.sort-input >>> .el-input-number__increase,
.sort-input >>> .el-input-number__decrease {
  background: var(--qm-bg-1);
  border-color: var(--qm-line-strong);
  color: var(--qm-text-2);
}

.sort-input >>> .el-input-number__increase:hover,
.sort-input >>> .el-input-number__decrease:hover {
  background: var(--qm-line-strong);
}

.sort-tip {
  font-size: 12px;
  color: var(--qm-text-3);
  margin-top: 8px;
  font-style: italic;
}

.color-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-picker-wrapper >>> .el-color-picker__trigger {
  border-radius: 10px;
  border: 2px solid var(--qm-line-strong);
  width: 40px;
  height: 40px;
}

.color-value {
  font-size: 14px;
  color: var(--qm-text-2);
  font-family: 'Consolas', monospace;
  background: var(--qm-bg-1);
  padding: 4px 8px;
  border-radius: 6px;
  border: 1px solid var(--qm-line-strong);
}

.icon-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.preview-label {
  font-size: 14px;
  color: var(--qm-text-2);
  font-weight: 500;
}

.preview-icon {
  border: 2px solid var(--qm-line-strong);
  background: var(--qm-bg-2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  /* border-top: 1px solid var(--qm-line-strong); */
  background: var(--qm-bg-1);
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.dialog-confirm-btn {
  padding: 10px 24px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-confirm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(245, 158, 11, 0.4);
}

/* 删除项样式 */
.delete-item >>> .el-dropdown-menu__item {
  color: #f56c6c;
  font-weight: 500;
}

.delete-item >>> .el-dropdown-menu__item:hover {
  background-color: rgba(245, 108, 108, 0.1);
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

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media screen and (max-width: 1200px) {
  .fixed-header {
    height: auto;
    min-height: 74px;
    padding: 12px 24px;
  }
  
  .header-content {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .search-section {
    order: 3;
    max-width: 100%;
  }
  
  .navigation-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
    padding: 20px;
  }
  
  .logo-circle {
    width: 50px;
    height: 50px;
  }
  
  .platform-name {
    font-size: 20px;
  }
  
  .platform-slogan {
    font-size: 11px;
  }
}

@media screen and (max-width: 768px) {
  .fixed-header {
    padding: 12px 16px;
    height: auto;
    min-height: 74px;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .logo-section {
    text-align: center;
  }
  
  .logo-wrapper {
    justify-content: center;
  }
  
  .action-section {
    text-align: center;
  }
  
  .group-title-section {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .group-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .navigation-grid {
    grid-template-columns: 1fr;
    gap: 12px;
    padding: 16px;
  }
  
  .navigation-content {
    padding: 16px;
  }
  
  .elegant-dialog >>> .el-dialog {
    width: 90% !important;
    max-width: 400px;
    margin-top: 5vh !important;
  }
  
  .logo-circle {
    width: 45px;
    height: 45px;
  }
  
  .platform-name {
    font-size: 18px;
  }
}

@media screen and (max-width: 480px) {
  .platform-name {
    font-size: 16px;
  }
  
  .platform-slogan {
    font-size: 10px;
  }
  
  .logo-circle {
    width: 40px;
    height: 40px;
  }
  
  .navigation-grid {
    padding: 12px;
  }
  
  .group-card >>> .el-card__header {
    padding: 16px;
  }
  
  .add-group-btn,
  .search-action-btn {
    width: 100%;
    justify-content: center;
  }
  
  .group-dropdown-btn,
  .add-navigation-btn {
    width: 100%;
    justify-content: center;
    margin-bottom: 8px;
  }
}

/* 自定义滚动条 - 与登录页保持一致 */
.navigation-management-container::-webkit-scrollbar {
  width: 8px;
}

.navigation-management-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.navigation-management-container::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.5);
  border-radius: 4px;
}

.navigation-management-container::-webkit-scrollbar-thumb:hover {
  background: rgba(245, 158, 11, 0.7);
}

/* 页面加载动画 */
@keyframes pageLoad {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.navigation-management-container {
  animation: pageLoad 0.5s ease-out;
}
</style>