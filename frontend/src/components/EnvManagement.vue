<template>
  <el-dialog
    v-model="visible"
    title="环境管理"
    fullscreen
    append-to-body
    modal-class="env-mgmt-overlay"
    class="elegant-dialog env-mgmt-dialog env-mgmt-dialog--fullscreen"
    :close-on-click-modal="false"
    @open="handleOpen"
    @close="handleClose"
  >
    <div class="env-mgmt-wrapper env-mgmt-wrapper--fullscreen">
      <!-- 左侧菜单 -->
      <div class="env-mgmt-sider">
        <div
          v-for="group in filteredMenuGroups"
          :key="group.key"
          class="menu-group"
        >
          <div class="menu-group-title">
            <el-icon class="group-icon"><component :is="group.icon" /></el-icon>
            <span>{{ group.label }}</span>
          </div>
          <ul class="menu-item-list">
            <li
              v-for="item in group.children"
              :key="item.key"
              class="menu-item"
              :class="{ active: activeMenuItem === item.key }"
              @click="handleMenuClick(group, item)"
            >
              <span class="menu-item-text">{{ item.label }}</span>
              <el-icon v-if="activeMenuItem === item.key" class="menu-item-arrow"><Right /></el-icon>
            </li>
          </ul>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="env-mgmt-content">
        <div v-if="currentView === 'Env'" class="view-wrapper env-view-wrapper">
          <Env ref="envRef" />
        </div>
        <div v-if="currentView === 'Service'" class="view-wrapper service-view-wrapper">
          <Service ref="serviceRef" />
        </div>
        <div v-if="currentView === 'Plant'" class="view-wrapper plant-view-wrapper">
          <Plant ref="plantRef" />
        </div>
        <div v-if="currentView === 'Db'" class="view-wrapper db-view-wrapper">
          <Db ref="dbRef" />
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script>
import { Right, Setting, SwitchFilled, Box } from '@element-plus/icons-vue'
import Env from '../views/env/Env.vue'
import Service from '../views/env/Service.vue'
import Plant from '../views/env/Plant.vue'
import Db from '../views/env/Db.vue'

export default {
  name: 'EnvManagement',
  components: { Env, Service, Plant, Db },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    menus: {
      type: [Array, String],
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      visible: false,
      currentView: 'Env',
      activeMenuItem: 'env',
      savedOverflowStyles: [], // 保存被修改的祖先元素 overflow 原始状态
      menuGroups: [
        {
          key: 'env_group',
          label: '环境配置',
          icon: Setting,
          view: 'Env',
          permissionPath: '/env/env',
          children: [
            { key: 'env', label: '环境列表', tabName: 'env' },
            { key: 'global_params', label: '全局变量配置', tabName: 'global_params' },
            { key: 'params', label: '环境变量配置', tabName: 'params' },
            { key: 'web', label: '浏览器集群配置', tabName: 'web' },
            { key: 'app', label: '手机设备配置', tabName: 'app' },
            { key: 'header', label: '全局请求头配置', tabName: 'header' },
            { key: 'cookie', label: '全局会话配置', tabName: 'cookie' }
          ]
        },
        {
          key: 'service_group',
          label: '服务配置',
          icon: SwitchFilled,
          view: 'Service',
          permissionPath: '/env/service',
          children: [
            { key: 'service', label: '服务列表', tabName: 'service' },
            { key: 'service_config', label: '服务域名配置', tabName: 'service_config' }
          ]
        },
        {
          key: 'plant_group',
          label: '产品配置',
          icon: Box,
          view: 'Plant',
          permissionPath: '/env/plant',
          children: [
            { key: 'plant', label: '产品列表', tabName: 'plant' },
            { key: 'plant_env', label: '产品域名配置', tabName: 'plant_env' }
          ]
        },
        {
          key: 'db_group',
          label: '数据库配置',
          icon: Setting,
          view: 'Db',
          permissionPath: '/env/db',
          children: [
            { key: 'db', label: '数据库列表', tabName: 'db' },
            { key: 'env_db', label: '数据库环境配置', tabName: 'env_db' }
          ]
        }
      ]
    }
  },
  computed: {
    // 从 menus 中提取"环境管理"各子项的 has_permission，按 path 映射
    permissionMap() {
      const map = {}
      if (!this.menus || !Array.isArray(this.menus)) return map
      const envMenu = this.menus.find(m => m.name === '环境管理')
      if (!envMenu || !envMenu.children) return map
      envMenu.children.forEach(child => {
        if (child.path) {
          map[child.path] = !!child.has_permission
        }
      })
      return map
    },
    // 按权限过滤后的菜单组
    filteredMenuGroups() {
      return this.menuGroups.filter(group => {
        return this.permissionMap[group.permissionPath]
      })
    }
  },
  watch: {
    modelValue: {
      handler(val) {
        this.visible = val
        if (val) {
          this.$nextTick(() => {
            // 打开弹窗时，默认选中第一个有权限的菜单项
            this.selectFirstAvailable()
          })
        }
      },
      immediate: true
    },
    visible(val) {
      this.$emit('update:modelValue', val)
    }
  },
  methods: {
    // 选中第一个有权限的菜单项
    selectFirstAvailable() {
      const groups = this.filteredMenuGroups
      if (groups.length === 0) return
      const firstGroup = groups[0]
      const firstItem = firstGroup.children[0]
      if (firstItem) {
        this.activeMenuItem = firstItem.key
        this.currentView = firstGroup.view
        this.$nextTick(() => {
          this.syncTab(firstGroup.view, firstItem.tabName)
        })
      }
    },
    handleMenuClick(group, item) {
      const prevView = this.currentView
      this.activeMenuItem = item.key
      this.currentView = group.view
      if (prevView !== group.view) {
        // 跨组件视图切换（v-if 重新挂载）：需要更多帧让组件挂载完成
        // $refs 不是响应式的，不能用 computed 缓存，必须等挂载后直接读取
        this.$nextTick(() => {
          this.$nextTick(() => {
            this.$nextTick(() => {
              this.syncTab(group.view, item.tabName)
            })
          })
        })
      } else {
        this.$nextTick(() => {
          this.syncTab(group.view, item.tabName)
        })
      }
    },
    syncTab(view, tabName) {
      const refMap = {
        Env: 'envRef',
        Service: 'serviceRef',
        Plant: 'plantRef',
        Db: 'dbRef'
      }
      // 直接读取 $refs，不用 computed（$refs 非响应式，computed 不会更新）
      const ref = this.$refs[refMap[view]]
      if (!ref) return
      ref.activeName = tabName
      this.$nextTick(() => {
        // 查找内部 el-tabs 实例，调用 setCurrentName 确保 tab 真正切换
        let tabsInstance = null
        const refs = ref.$refs || {}
        for (const k in refs) {
          const r = refs[k]
          if (r && typeof r.setCurrentName === 'function') {
            tabsInstance = r
            break
          }
        }
        if (!tabsInstance && ref.$children && ref.$children.length) {
          const find = (arr) => {
            for (let i = 0; i < arr.length; i++) {
              const c = arr[i]
              if (c && typeof c.setCurrentName === 'function') return c
              if (c.$children && c.$children.length) {
                const r = find(c.$children)
                if (r) return r
              }
            }
            return null
          }
          tabsInstance = find(ref.$children)
        }
        if (tabsInstance) {
          tabsInstance.setCurrentName(tabName)
        }
        if (ref.$forceUpdate) ref.$forceUpdate()
      })
    },
    handleOpen() {
      // dialog 打开后，从 dialog 自身开始向上遍历所有祖先元素（含自身），
      // 凡是 overflow 是 auto/scroll 的，强制设为 hidden
      // 解决 Element Plus 全屏 dialog 最外层垂直滚动条
      this.$nextTick(() => {
        // 先清空上次保存的记录
        this.savedOverflowStyles = []
        const dialog = document.querySelector('.env-mgmt-dialog--fullscreen')
        if (!dialog) return
        let el = dialog
        while (el && el !== document.documentElement) {
          const cs = window.getComputedStyle(el)
          if (cs.overflowY === 'auto' || cs.overflowY === 'scroll' ||
              cs.overflow === 'auto' || cs.overflow === 'scroll') {
            // 保存原始 inline style 中的 overflow 和 overflowY 值
            this.savedOverflowStyles.push({
              element: el,
              overflow: el.style.overflow,
              overflowY: el.style.overflowY,
              overflowPriority: el.style.getPropertyPriority('overflow'),
              overflowYPriority: el.style.getPropertyPriority('overflow-y')
            })
            el.style.setProperty('overflow', 'hidden', 'important')
          }
          el = el.parentElement
        }
      })
    },
    handleClose() {
      // 恢复所有被修改的祖先元素的原始 overflow 值，防止关闭后页面无法滚动
      this.savedOverflowStyles.forEach(item => {
        const { element, overflow, overflowY, overflowPriority, overflowYPriority } = item
        if (!element) return
        if (overflow) {
          element.style.setProperty('overflow', overflow, overflowPriority || '')
        } else {
          element.style.removeProperty('overflow')
        }
        if (overflowY) {
          element.style.setProperty('overflow-y', overflowY, overflowYPriority || '')
        } else {
          element.style.removeProperty('overflow-y')
        }
      })
      this.savedOverflowStyles = []
      this.visible = false
    }
  }
}
</script>

<style scoped>
/* 左侧菜单样式（这些元素在组件内部，scoped 正常生效） */
.menu-group + .menu-group {
  margin-top: 8px;
}

.menu-group-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px 10px 16px;
  font-size: 15px;
  font-weight: 700;
  color: #1a1a1a;
  position: relative;
}

.menu-group-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 18px;
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 2px;
}

.group-icon {
  color: #6366f1;
  font-size: 18px;
}

.menu-item-list {
  list-style: none;
  margin: 4px 0 0;
  padding: 0 0 0 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px 10px 24px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #475569;
  transition: all 0.25s ease;
  margin-bottom: 2px;
}

.menu-item:hover {
  background: rgba(99, 102, 241, 0.08);
  color: #6366f1;
}

.menu-item.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.12) 100%);
  color: #6366f1;
  font-weight: 600;
  box-shadow: inset 3px 0 0 #6366f1;
}

.menu-item-text {
  flex: 1;
}

.menu-item-arrow {
  font-size: 14px;
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.25s ease;
}

.menu-item.active .menu-item-arrow {
  opacity: 1;
  transform: translateX(0);
}
</style>

<style>
/* ===== 以下样式必须放在非 scoped 块中 =====
   原因：el-dialog 使用 append-to-body，dialog DOM 被 teleport 到 <body> 下，
   scoped 的 :deep() 和 data-v-xxx 属性选择器无法匹配到 dialog 内部元素。
   用 .env-mgmt-dialog 前缀限定作用域，避免污染全局。 */

/* 弹窗外观 */
.env-mgmt-dialog.el-dialog {
  border-radius: 24px;
  overflow: hidden;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.env-mgmt-dialog .el-dialog__header {
  padding: 24px 24px 0;
  margin: 0;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e2e8f0;
  flex-shrink: 0;
}

.env-mgmt-dialog .el-dialog__title {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 12px;
  padding-left: 12px;
  position: relative;
}

.env-mgmt-dialog .el-dialog__title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 2px;
}

/* 关键：dialog body 必须是 flex 列布局 + overflow hidden，否则内容溢出会产生滚动条 */
.env-mgmt-dialog .el-dialog__body {
  padding: 0 !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  min-height: 0 !important;
  flex: 1 !important;
}

/* 全屏模式覆盖 */
.env-mgmt-dialog--fullscreen.el-dialog {
  border-radius: 0 !important;
  box-shadow: none !important;
  display: flex !important;
  flex-direction: column !important;
  margin: 0 !important;
  height: 100vh !important;
  max-height: 100vh !important;
  overflow: hidden !important;
}

.env-mgmt-dialog--fullscreen .el-dialog__body {
  max-height: none !important;
  height: auto !important;
  flex: 1 !important;
  min-height: 0 !important;
  overflow: hidden !important;
}

/* 防止 Element Plus 全屏 dialog 的外层 overlay 出现垂直滚动条
   modal-class="env-mgmt-overlay" 会把 class 加到 .el-overlay 上 */
.env-mgmt-overlay {
  overflow: hidden !important;
}

/* 兜底：overlay 内部的 .el-overlay-dialog 也可能产生滚动条 */
.el-overlay-dialog:has(.env-mgmt-dialog--fullscreen) {
  overflow: hidden !important;
}

/* 主容器 wrapper：flex 行布局，占满 body 剩余高度 */
.env-mgmt-dialog .env-mgmt-wrapper {
  display: flex !important;
  flex: 1 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  padding: 16px 16px 16px 6px;
  gap: 13px;
  box-sizing: border-box;
}

/* 左侧菜单 */
.env-mgmt-dialog .env-mgmt-sider {
  width: 300px;
  flex-shrink: 0;
  align-self: flex-start;
  max-height: 100%;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.08);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px 12px;
  box-sizing: border-box;
  position: relative;
}

/* 左侧区域自定义滚动条样式 —— 轨道视觉缩短一半（其它不动）*/
.env-mgmt-dialog .env-mgmt-sider::-webkit-scrollbar {
  width: 6px;
}
.env-mgmt-dialog .env-mgmt-sider::-webkit-scrollbar-track {
  background: transparent;
}
.env-mgmt-dialog .env-mgmt-sider::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 4px;
  background-clip: padding-box;
  border: 8px solid transparent;
  min-height: 40px;
}
.env-mgmt-dialog .env-mgmt-sider::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
  background-clip: padding-box;
  border: 8px solid transparent;
}

/* 右侧内容 */
.env-mgmt-dialog .env-mgmt-content {
  flex: 1 !important;
  min-width: 0;
  min-height: 0 !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
}

.env-mgmt-dialog .view-wrapper {
  flex: 1 !important;
  min-height: 0 !important;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
}

/* === 覆盖四个 env 组件根容器 === */
.env-mgmt-dialog .environment-management-container,
.env-mgmt-dialog .service-management-container,
.env-mgmt-dialog .plant-management-container,
.env-mgmt-dialog .database-management-container {
  height: 100% !important;
  min-height: 0 !important;
  max-height: none !important;
  padding: 0px !important;
  gap: 16px !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 16px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.08) !important;
  box-sizing: border-box !important;
}

.env-mgmt-dialog .drawer-card {
  flex: 1 !important;
  min-height: 0 !important;
  height: auto !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}

.env-mgmt-dialog .drawer-card .el-card__body {
  flex: 1 !important;
  min-height: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}

/* 隐藏 tabs 内部 header 的方式：视觉隐藏但保留 DOM 结构，避免 el-tabs 切换时读取 header 内部元素失败。
   之前用 display:none 导致部分 tab 切换不响应（只有 env 默认值能切） */
.env-mgmt-dialog .drawer-tabs .el-tabs__header {
  visibility: hidden !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  pointer-events: none !important;
  border: none !important;
}

.env-mgmt-dialog .drawer-tabs {
  flex: 1 !important;
  min-height: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  overflow: hidden !important;
}

.env-mgmt-dialog .drawer-tabs .el-tabs__content {
  flex: 1 !important;
  min-height: 0 !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
}

/* tab-pane：display 完全交给 Element Plus（inline style block/none）控制。
   作为 el-tabs__content(flex column) 的子项，pane 是 flex item：
   flex:1 让激活的 pane(由 Element 设 display:block) 占满剩余高度；
   非激活 pane 被 Element 设 display:none，不参与排版。
   —— 不能写 display:flex !important，否则会覆盖 Element 的 display:none，
      导致所有tab同时显示（之前出现过的bug）。
   —— overflow-x:hidden 防止切换 tab 时表格列宽重算瞬间出现水平滚动条 */
.env-mgmt-dialog .drawer-tabs .el-tab-pane {
  flex: 1;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  width: 100%;
}

/* 筛选卡片 / 内容卡片在 pane 里正常流式布局，不再需要 flex-shrink
   pane 设为 overflow:auto，内容多时 pane 整体滚动，表格内部仍可独立滚动（el-table 自带 max-height 处理） */

/* 整条链路统一禁止水平滚动：切换 tab/菜单时 el-table 列宽重算会瞬间产生水平溢出，
   各层 overflow-x:hidden 把水平溢出在最早阶段截断，避免出现一闪而过的水平滚动条 */
.env-mgmt-dialog .env-mgmt-content,
.env-mgmt-dialog .view-wrapper,
.env-mgmt-dialog .environment-management-container,
.env-mgmt-dialog .service-management-container,
.env-mgmt-dialog .plant-management-container,
.env-mgmt-dialog .database-management-container,
.env-mgmt-dialog .drawer-card,
.env-mgmt-dialog .drawer-card .el-card__body,
.env-mgmt-dialog .drawer-tabs,
.env-mgmt-dialog .drawer-tabs .el-tabs__content {
  overflow-x: hidden !important;
}

/* 隐藏 tabs 内部 header 的方式改为：视觉隐藏但保留 DOM 结构，避免 el-tabs 切换时读取 header 内部元素失败。
   之前用 display:none 导致部分 tab 切换不响应（只有 env 默认值能切） */
.env-mgmt-dialog .drawer-tabs .el-tabs__header {
  visibility: hidden !important;
  height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
  pointer-events: none !important;
  border: none !important;
}

/* 去掉卡片外层多余边距 */
.env-mgmt-dialog .drawer-card.el-card,
.env-mgmt-dialog .el-card.drawer-card {
  border: none !important;
  margin: 0 !important;
}

/* 统一分页对齐方式：所有 pagination-wrapper 右对齐
   原文件中部分有 float:right（Env/Plant/Db），部分没有（Service），导致分页位置不一致 */
.env-mgmt-dialog .pagination-wrapper {
  float: right !important;
  display: flex !important;
  justify-content: flex-end !important;
  width: 100%;
  box-sizing: border-box;
  margin-bottom: 10px !important;
  padding-right: 10px !important;
}
</style>
