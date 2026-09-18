<template>
  <div class="help-documentation">
    <!-- ================= 左侧导航栏 ================= -->
    <aside class="sidebar">
      <div class="header">
        <h1>
          <el-icon class="header-icon"><QuestionFilled /></el-icon>
          <span>帮助文档</span>
        </h1>
        <p>了解平台功能，快速上手使用</p>
      </div>

      <div class="search-box">
        <el-icon class="search-icon"><Search /></el-icon>
        <input
          type="text"
          v-model="searchTerm"
          placeholder="搜索功能、模块或问题…"
          @input="filterNavigation"
        >
        <button v-if="searchTerm" class="search-clear" title="清空搜索" @click="clearSearch">
          <el-icon><Close /></el-icon>
        </button>
      </div>

      <div class="nav-container" ref="navContainer">
        <!-- 快速开始 -->
        <div class="nav-item nav-item-plain" :class="{ 'is-active': activeSection === 'quick-start' }">
          <div
            class="nav-item-header"
            :class="{ active: activeSection === 'quick-start' }"
            @click="switchSection('quick-start')"
          >
            <div class="nav-item-label">
              <el-icon><Promotion /></el-icon>
              <span>快速开始</span>
            </div>
          </div>
        </div>

        <!-- 平台模块导航 -->
        <div
          v-for="menuItem in filteredMenu"
          :key="menuItem.path"
          class="nav-item"
          :class="{
            expanded: expandedItems.includes(menuItem.path),
            'active-parent': isParentActive(menuItem)
          }"
        >
          <div
            class="nav-item-header"
            :class="{ active: activeSection === menuItem.path }"
            @click="onParentClick(menuItem)"
          >
            <div class="nav-item-label">
              <el-icon><component :is="menuItem.icon" /></el-icon>
              <span>{{ menuItem.name }}</span>
            </div>
            <el-icon class="chevron" :class="{ rotated: expandedItems.includes(menuItem.path) }">
              <ArrowRight />
            </el-icon>
          </div>

          <div
            class="nav-subitems"
            :style="{ maxHeight: expandedItems.includes(menuItem.path) ? '1400px' : '0' }"
          >
            <div
              v-for="child in menuItem.children"
              :key="child.id"
              class="nav-subitem"
              :class="{ active: activeSection === sectionKey(menuItem, child) }"
              @click.stop="switchSection(sectionKey(menuItem, child))"
            >
              <el-icon><component :is="child.icon" /></el-icon>
              <span>{{ child.name }}</span>
            </div>
          </div>
        </div>

        <!-- 搜索无结果 -->
        <div v-if="searchTerm && !filteredMenu.length" class="nav-empty">
          <el-icon class="nav-empty-icon"><Search /></el-icon>
          <p class="nav-empty-title">没有匹配的功能</p>
          <p class="nav-empty-tip">试试「环境」「用例」「压测」「变量」「权限」等关键词</p>
        </div>
      </div>

      <div class="sidebar-footer">
        <span>共 {{ totalSections }} 个帮助页 · 持续更新</span>
      </div>
    </aside>

    <!-- ================= 右侧内容区域 ================= -->
    <main class="content" ref="contentContainer" @scroll="handleScroll">
      <div class="content-body">
        <div class="content-main">
          <!-- 快速开始 -->
          <section
            class="content-section"
            :class="{ active: activeSection === 'quick-start' }"
          >
            <div class="section-header">
              <h2 id="quick-start-top">
                <el-icon><Promotion /></el-icon>
                <span>{{ quickStartContent.title }}</span>
              </h2>
              <p>{{ quickStartContent.description }}</p>
            </div>
            <div class="section-content" v-html="quickStartContent.content"></div>
          </section>

          <!-- 平台各模块 -->
          <template v-for="menuItem in platformMenu" :key="`${menuItem.path}-main`">
            <!-- 一级模块总览 -->
            <section
              class="content-section"
              :class="{ active: activeSection === menuItem.path }"
            >
              <div class="section-header">
                <h2 :id="`${menuItem.path}-top`">
                  <el-icon><component :is="menuItem.icon" /></el-icon>
                  <span>{{ menuItem.name }}</span>
                </h2>
                <p>{{ getMenuContent(menuItem.name).description }}</p>
              </div>
              <div class="section-content" v-html="getMenuContent(menuItem.name).content"></div>
            </section>

            <!-- 二级页面详情 -->
            <section
              v-for="child in menuItem.children"
              :key="sectionKey(menuItem, child)"
              class="content-section"
              :class="{ active: activeSection === sectionKey(menuItem, child) }"
            >
              <div class="section-header">
                <h2 :id="`${sectionKey(menuItem, child)}-top`">
                  <el-icon><component :is="child.icon" /></el-icon>
                  <span>{{ child.name }}</span>
                </h2>
                <p>{{ getSubMenuContent(menuItem, child).description }}</p>
                <div class="section-breadcrumb">
                  <el-icon><Location /></el-icon>
                  <span>{{ menuItem.name }} / {{ child.name }}</span>
                </div>
              </div>
              <div class="section-content" v-html="getSubMenuContent(menuItem, child).content"></div>
            </section>
          </template>
        </div>

        <!-- 页面内锚点导航 -->
        <aside class="anchor-nav" :class="{ collapsed: !showAnchorNav }">
          <div class="anchor-header">
            <h3 v-if="showAnchorNav">
              <el-icon><Location /></el-icon>
              <span>页面导航</span>
            </h3>
            <button class="anchor-toggle" :title="showAnchorNav ? '收起导航' : '展开导航'" @click="toggleAnchorNav">
              <el-icon><component :is="showAnchorNav ? 'Close' : 'Operation'" /></el-icon>
            </button>
          </div>
          <div class="anchor-links" v-if="showAnchorNav">
            <a
              v-for="anchor in currentAnchors"
              :key="anchor.id"
              :href="'#' + anchor.id"
              class="anchor-link"
              :class="{ active: activeAnchor === anchor.id }"
              @click.prevent="scrollToAnchor(anchor.id)"
            >
              <el-icon><CaretRight /></el-icon>
              <span>{{ anchor.title }}</span>
            </a>
          </div>
        </aside>
      </div>

      <!-- 回到顶部 -->
      <button class="back-to-top" :class="{ visible: showBackToTop }" @click="scrollToTop">
        <el-icon><ArrowUp /></el-icon>
        <span>顶部</span>
      </button>
    </main>
  </div>
</template>

<script>
/**
 * 帮助文档页（路由 /user/help）
 *
 * 本次重构要点（对应「帮助文档不够细致」的反馈）：
 *
 * 1. 内容与展示分离
 *    全部帮助内容抽到 ./helpContent/ 目录下按模块拆分维护（menu / intro / overview / sub-* / guide），
 *    本文件只负责渲染。原来的实现把约 1500 行 HTML 字符串堆在 data 里，无法维护。
 *    注意目录名用 helpContent 而非 help：本文件叫 Help.vue，若目录叫 help，在大小写不敏感
 *    的文件系统（Windows / macOS）上 webpack 会把 `./help` 解析成 `help.vue`（即本文件自身），
 *    触发 CaseSensitivePathsPlugin 报错并导致构建失败。
 *
 * 2. 二级菜单不再是套话模板
 *    原实现对每个二级菜单渲染固定模板：「XX是XX模块的一部分，主要用于管理XX相关的功能」，
 *    且 `child.name.toLowerCase()` 对中文无效。现改为按 `模块path-菜单id` 读取真实内容，
 *    并由 validateHelpContent() 在启动时校验是否漏写。
 *
 * 3. 修复样式不生效
 *    原实现把内容样式写在 <style scoped> 里，而内容经 v-html 注入不会带 scoped 属性，
 *    导致 .info-box / .step-list / .doc-table 等全部失效。现拆成两个 style 块：
 *    scoped 管页面骨架，全局块（.help-documentation 命名空间内）管 v-html 内容。
 *
 * 4. 修复图标全部空白
 *    原实现用 Font Awesome 的 `fas fa-*`，但整个前端工程并未安装 FA（全仓仅本文件用到 63 处），
 *    图标实际全部渲染为空白。现统一改用已全局注册的 element-plus 图标组件，
 *    并与平台主菜单的图标保持一致（图标名取自后端权限表的 icon 字段）。
 *
 * 5. 父菜单可点击查看总览
 *    原来点击一级菜单只展开 / 收起子项，其对应的总览内容永远显示不出来（死代码）。
 *    现在点击一级菜单会同时展开子项并切换到该模块总览。
 *
 * 6. 锚点导航数据驱动
 *    原来的 currentAnchors 是一大段 if-else 硬编码；现由内容数据自带的 anchors 提供，
 *    锚点 id 与正文标题 id 由同一份 sectionKey 生成，不会再对不上。
 */
import {
  platformMenu,
  quickStartContent,
  menuContentMap,
  subMenuContentMap,
  validateHelpContent
} from './helpContent'

export default {
  name: 'HelpDocumentation',
  data() {
    return {
      activeSection: 'quick-start',
      expandedItems: [],
      searchTerm: '',
      filteredMenu: [],
      showAnchorNav: true,
      activeAnchor: '',
      showBackToTop: false,
      scrollThrottle: null,
      contentContainer: null,
      // 内容数据（引用外部模块，保持响应式只读）
      platformMenu,
      quickStartContent,
      menuContentMap,
      subMenuContentMap
    }
  },
  computed: {
    /** 帮助页总数（快速开始 + 各模块总览 + 各二级页面） */
    totalSections() {
      const children = this.platformMenu.reduce((n, m) => n + (m.children ? m.children.length : 0), 0)
      return 1 + this.platformMenu.length + children
    },
    /**
     * 当前激活章节的元信息：顶部锚点 id / 标题 + 正文锚点列表。
     * 顶部锚点由这里按统一规则生成，与模板中 h2 的 id 一致，避免手工维护两处。
     */
    activeContent() {
      if (this.activeSection === 'quick-start') {
        return {
          topId: 'quick-start-top',
          topTitle: '快速开始',
          anchors: this.quickStartContent.anchors || []
        }
      }
      const top = this.platformMenu.find(m => m.path === this.activeSection)
      if (top) {
        return {
          topId: `${top.path}-top`,
          topTitle: top.name,
          anchors: this.getMenuContent(top.name).anchors || []
        }
      }
      for (const menuItem of this.platformMenu) {
        for (const child of menuItem.children || []) {
          if (this.activeSection === this.sectionKey(menuItem, child)) {
            return {
              topId: `${this.sectionKey(menuItem, child)}-top`,
              topTitle: child.name,
              anchors: this.getSubMenuContent(menuItem, child).anchors || []
            }
          }
        }
      }
      return { topId: '', topTitle: '', anchors: [] }
    },
    currentAnchors() {
      const c = this.activeContent
      const list = []
      if (c.topId) list.push({ id: c.topId, title: c.topTitle })
      return list.concat(c.anchors || [])
    }
  },
  mounted() {
    this.filteredMenu = [...this.platformMenu]

    // 默认展开第一个模块
    if (this.platformMenu.length > 0) {
      this.expandedItems.push(this.platformMenu[0].path)
    }

    this.contentContainer = this.$refs.contentContainer

    // 内容完整性自检：漏写某个二级页面详情时会回落到套话模板，这里提前暴露
    const check = validateHelpContent()
    this.$_helpContentCheck = check
    // 供自动化复核使用（UI 巡检会读取该字段断言帮助内容完整）
    if (typeof window !== 'undefined') {
      window.__helpContentCheck = check
    }
    if (!check.ok) {
      /* eslint-disable no-console */
      console.warn('[help] 帮助内容不完整', check)
      /* eslint-enable no-console */
    }

    this.$nextTick(() => {
      this.handleScroll()
    })
  },
  beforeUnmount() {
    if (this.scrollThrottle) {
      clearTimeout(this.scrollThrottle)
    }
  },
  watch: {
    activeSection() {
      this.activeAnchor = ''
      this.$nextTick(() => {
        this.handleScroll()
        if (this.contentContainer) {
          this.contentContainer.scrollTop = 0
        }
      })
    }
  },
  methods: {
    /**
     * 章节 key：`模块path-二级菜单id`
     * 使用显式 id 而非从 path 末段推导——审计日志的真实路径是 /user/auditLog，
     * 若按路径推导会与「用户管理」模块的 path 前缀冲突，导致父菜单高亮判断出错。
     */
    sectionKey(menuItem, child) {
      return `${menuItem.path}-${child.id}`
    },
    /** 当前激活的是该模块下的二级页面（用于父菜单高亮） */
    isParentActive(menuItem) {
      return this.activeSection.startsWith(`${menuItem.path}-`)
    },
    /** 点击一级菜单：既展开/收起子项，也切换到该模块总览 */
    onParentClick(menuItem) {
      const idx = this.expandedItems.indexOf(menuItem.path)
      if (idx > -1) {
        // 收起时若当前正停在本模块下的页面，保留展开以免内容区与导航脱节
        if (this.isParentActive(menuItem)) {
          this.switchSection(menuItem.path)
          return
        }
        this.expandedItems.splice(idx, 1)
      } else {
        this.expandedItems.push(menuItem.path)
      }
      this.switchSection(menuItem.path)
    },
    switchSection(sectionId) {
      this.activeSection = sectionId

      // 切到二级页面时确保父模块已展开
      if (sectionId.includes('-')) {
        const parentPath = sectionId.split('-')[0]
        if (!this.expandedItems.includes(parentPath)) {
          this.expandedItems.push(parentPath)
        }
      }

      this.$nextTick(() => {
        if (this.contentContainer) {
          this.contentContainer.scrollTop = 0
        }
      })
    },
    clearSearch() {
      this.searchTerm = ''
      this.filterNavigation()
    },
    /** 搜索：命中模块名 / 模块描述 / 二级页面名 / 二级页面描述 */
    filterNavigation() {
      const term = (this.searchTerm || '').trim().toLowerCase()
      if (!term) {
        this.filteredMenu = [...this.platformMenu]
        return
      }

      const matched = []
      this.platformMenu.forEach(menuItem => {
        const hitModule =
          menuItem.name.toLowerCase().indexOf(term) > -1 ||
          (menuItem.desc || '').toLowerCase().indexOf(term) > -1

        const hitChildren = (menuItem.children || []).filter(child => {
          const detail = this.getSubMenuContent(menuItem, child)
          return (
            child.name.toLowerCase().indexOf(term) > -1 ||
            (detail.description || '').toLowerCase().indexOf(term) > -1
          )
        })

        if (hitModule || hitChildren.length) {
          matched.push(menuItem)
          if (!this.expandedItems.includes(menuItem.path)) {
            this.expandedItems.push(menuItem.path)
          }
        }
      })
      this.filteredMenu = matched
    },
    getMenuContent(menuName) {
      return (
        this.menuContentMap[menuName] || {
          description: `${menuName}模块的帮助文档`,
          anchors: [],
          content: `<p>该模块的帮助内容正在补充中。</p>`
        }
      )
    },
    getSubMenuContent(menuItem, child) {
      const key = this.sectionKey(menuItem, child)
      return (
        this.subMenuContentMap[key] || {
          description: `${menuItem.name} > ${child.name}`,
          anchors: [],
          content: `<p>该页面的帮助内容正在补充中。</p>`
        }
      )
    },
    toggleAnchorNav() {
      this.showAnchorNav = !this.showAnchorNav
    },
    scrollToAnchor(anchorId) {
      this.$nextTick(() => {
        const element = document.getElementById(anchorId)
        if (!element || !this.contentContainer) {
          return
        }
        const containerRect = this.contentContainer.getBoundingClientRect()
        const elementRect = element.getBoundingClientRect()
        const offsetTop = elementRect.top - containerRect.top + this.contentContainer.scrollTop - 24

        this.contentContainer.scrollTo({
          top: Math.max(offsetTop, 0),
          behavior: 'smooth'
        })
        this.activeAnchor = anchorId

        if (this.scrollThrottle) {
          clearTimeout(this.scrollThrottle)
        }
        this.scrollThrottle = setTimeout(() => {
          this.handleScroll()
        }, 500)
      })
    },
    handleScroll() {
      if (!this.contentContainer) return

      const scrollTop = this.contentContainer.scrollTop
      this.showBackToTop = scrollTop > 300

      if (!this.currentAnchors.length) return

      const scrollPosition = scrollTop + 150
      let closestAnchor = null
      let closestDistance = Infinity

      for (const anchor of this.currentAnchors) {
        const element = document.getElementById(anchor.id)
        if (!element) continue
        const containerRect = this.contentContainer.getBoundingClientRect()
        const elementRect = element.getBoundingClientRect()
        const elementTop = elementRect.top - containerRect.top + scrollTop
        const distance = Math.abs(scrollPosition - elementTop)

        if (scrollPosition >= elementTop - 50 && distance < closestDistance) {
          closestDistance = distance
          closestAnchor = anchor.id
        }
      }

      if (closestAnchor) {
        this.activeAnchor = closestAnchor
      } else if (scrollTop < 100) {
        this.activeAnchor = this.currentAnchors[0] ? this.currentAnchors[0].id : ''
      }
    },
    scrollToTop() {
      if (this.contentContainer) {
        this.contentContainer.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
  }
}
</script>

<style scoped>
/* ================= 页面骨架 ================= */
.help-documentation {
  display: flex;
  height: 100vh;
  background-color: var(--qm-bg-1);
  color: var(--qm-text-1);
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

/* ---------- 左侧导航 ---------- */
.sidebar {
  flex: 0 0 262px;
  width: 262px;
  background: linear-gradient(180deg, #2c3e50 0%, #1a2530 100%);
  color: #ecf0f1;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 0 15px rgba(0, 0, 0, 0.12);
  z-index: 10;
}

.header {
  padding: 22px 20px 18px;
  border-bottom: 1px solid #34495e;
}

.header h1 {
  display: flex;
  align-items: center;
  gap: 9px;
  margin: 0 0 6px;
  font-size: 1.45rem;
  font-weight: 600;
  color: #fff;
}

.header-icon {
  color: #f59e0b;
  font-size: 22px;
}

.header p {
  margin: 0;
  font-size: 0.82rem;
  color: #bdc3c7;
  opacity: 0.85;
}

.search-box {
  position: relative;
  padding: 14px 18px;
  border-bottom: 1px solid #34495e;
}

.search-icon {
  position: absolute;
  left: 29px;
  top: 50%;
  transform: translateY(-50%);
  color: #8fa3b5;
  font-size: 14px;
  pointer-events: none;
}

.search-box input {
  width: 100%;
  box-sizing: border-box;
  padding: 9px 30px 9px 32px;
  border-radius: 6px;
  border: 1px solid transparent;
  background-color: #34495e;
  color: #ecf0f1;
  font-size: 0.86rem;
  outline: none;
}

.search-box input::placeholder {
  color: #8fa3b5;
}

.search-box input:focus {
  border-color: #f59e0b;
  background-color: #2c3e50;
}

.search-clear {
  position: absolute;
  right: 26px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  padding: 2px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: #8fa3b5;
  cursor: pointer;
}

.search-clear:hover {
  color: #f59e0b;
}

.nav-container {
  flex: 1;
  overflow-y: auto;
  padding: 14px 0 20px;
}

.nav-container::-webkit-scrollbar {
  width: 6px;
}

.nav-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.18);
  border-radius: 3px;
}

.nav-item {
  cursor: pointer;
}

.nav-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 18px;
  border-left: 4px solid transparent;
  font-size: 0.94rem;
  font-weight: 500;
  transition: background-color 0.25s ease, border-color 0.25s ease;
}

.nav-item-label {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.nav-item-label .el-icon {
  font-size: 16px;
  flex: 0 0 auto;
}

.nav-item-header:hover {
  background-color: rgba(255, 255, 255, 0.06);
}

.nav-item.expanded > .nav-item-header {
  background-color: rgba(52, 152, 219, 0.06);
}

.nav-item-header.active,
.nav-item.active-parent > .nav-item-header {
  background-color: rgba(52, 152, 219, 0.12);
  border-left-color: #f59e0b;
  color: #f59e0b;
}

.chevron {
  font-size: 13px;
  color: #8fa3b5;
  transition: transform 0.25s ease;
}

.chevron.rotated {
  transform: rotate(90deg);
}

.nav-subitems {
  overflow: hidden;
  background-color: rgba(0, 0, 0, 0.22);
  transition: max-height 0.32s ease;
}

.nav-subitem {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 10px 18px 10px 40px;
  border-left: 4px solid transparent;
  font-size: 0.87rem;
  color: #c8d3dd;
  transition: background-color 0.25s ease, color 0.25s ease;
}

.nav-subitem .el-icon {
  font-size: 14px;
  flex: 0 0 auto;
}

.nav-subitem:hover {
  background-color: rgba(255, 255, 255, 0.06);
  color: #ecf0f1;
}

.nav-subitem.active {
  background-color: rgba(52, 152, 219, 0.16);
  border-left-color: #f59e0b;
  color: #f59e0b;
  font-weight: 500;
}

.nav-empty {
  padding: 34px 20px;
  text-align: center;
  color: #8fa3b5;
}

.nav-empty-icon {
  font-size: 26px;
  margin-bottom: 10px;
  opacity: 0.6;
}

.nav-empty-title {
  margin: 0 0 6px;
  font-size: 0.88rem;
}

.nav-empty-tip {
  margin: 0;
  font-size: 0.78rem;
  line-height: 1.7;
  opacity: 0.75;
}

.sidebar-footer {
  padding: 12px 18px;
  border-top: 1px solid #34495e;
  font-size: 0.75rem;
  color: #8fa3b5;
}

/* ---------- 右侧内容 ---------- */
.content {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  background-color: var(--qm-bg-1);
  position: relative;
  padding: 30px 26px 90px;
}

.content-body {
  display: flex;
  align-items: flex-start;
  gap: 26px;
  max-width: 1360px;
  margin: 0 auto;
}

.content-main {
  flex: 1 1 auto;
  min-width: 0;
}

.content-section {
  display: none;
}

.content-section.active {
  display: block;
  animation: help-fade-in 0.24s ease;
}

@keyframes help-fade-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-header {
  padding-bottom: 16px;
  margin-bottom: 8px;
  border-bottom: 1px solid var(--qm-line);
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 8px;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--qm-text-1);
}

.section-header h2 .el-icon {
  color: var(--qm-accent);
  font-size: 24px;
}

.section-header p {
  margin: 0;
  font-size: 0.92rem;
  color: var(--qm-text-2);
  line-height: 1.7;
}

.section-breadcrumb {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  font-size: 0.78rem;
  color: var(--qm-text-3);
}

/* ---------- 锚点导航 ---------- */
.anchor-nav {
  flex: 0 0 226px;
  width: 226px;
  position: sticky;
  top: 0;
  align-self: flex-start;
  background-color: var(--qm-bg-2);
  border: 1px solid var(--qm-line);
  border-radius: 10px;
  box-shadow: var(--qm-shadow);
  overflow: hidden;
  transition: flex-basis 0.25s ease, width 0.25s ease;
}

.anchor-nav.collapsed {
  flex-basis: 46px;
  width: 46px;
}

.anchor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
  padding: 11px 14px;
  background-color: var(--qm-bg-3);
  border-bottom: 1px solid var(--qm-line);
}

.anchor-header h3 {
  display: flex;
  align-items: center;
  gap: 7px;
  margin: 0;
  font-size: 0.86rem;
  font-weight: 600;
  color: var(--qm-text-1);
  white-space: nowrap;
}

.anchor-header h3 .el-icon {
  color: var(--qm-accent);
}

.anchor-toggle {
  display: flex;
  align-items: center;
  padding: 4px;
  border: none;
  border-radius: 5px;
  background: transparent;
  color: var(--qm-text-3);
  cursor: pointer;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.anchor-toggle:hover {
  color: var(--qm-accent);
  background-color: var(--qm-accent-soft);
}

.anchor-links {
  max-height: min(62vh, 520px);
  overflow-y: auto;
  padding: 8px 0;
}

.anchor-links::-webkit-scrollbar {
  width: 6px;
}

.anchor-links::-webkit-scrollbar-thumb {
  background: var(--qm-line-strong);
  border-radius: 3px;
}

.anchor-link {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 14px;
  border-left: 3px solid transparent;
  color: var(--qm-text-2);
  text-decoration: none;
  font-size: 0.82rem;
  line-height: 1.5;
  transition: all 0.2s ease;
}

.anchor-link .el-icon {
  font-size: 11px;
  flex: 0 0 auto;
  opacity: 0.7;
}

.anchor-link:hover {
  background-color: var(--qm-bg-3);
  color: var(--qm-accent-strong);
  border-left-color: var(--qm-accent);
}

.anchor-link.active {
  background-color: var(--qm-accent-soft);
  color: var(--qm-accent-strong);
  font-weight: 600;
  border-left-color: var(--qm-accent);
}

/* ---------- 回到顶部 ---------- */
.back-to-top {
  position: fixed;
  right: 26px;
  bottom: 26px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 46px;
  height: 46px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--qm-accent) 0%, var(--qm-accent-2) 100%);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.34);
  transition: all 0.25s ease;
  opacity: 0;
  visibility: hidden;
  transform: translateY(16px);
  z-index: 90;
}

.back-to-top.visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.back-to-top:hover {
  transform: translateY(-3px);
  box-shadow: 0 7px 18px rgba(245, 158, 11, 0.45);
}

.back-to-top .el-icon {
  font-size: 16px;
}

.back-to-top span {
  font-size: 0.62rem;
  line-height: 1.2;
}

/* ---------- 响应式 ---------- */
@media (max-width: 1280px) {
  .anchor-nav {
    display: none;
  }
}

@media (max-width: 900px) {
  .sidebar {
    flex-basis: 214px;
    width: 214px;
  }
  .content {
    padding: 22px 16px 80px;
  }
}
</style>

<style>
/**
 * ============================================================================
 * 帮助文档 · 正文内容样式（非 scoped，必须）
 * ----------------------------------------------------------------------------
 * 正文由 v-html 注入，注入的 DOM 不会携带 scoped 的 data-v-xxx 属性，
 * 因此凡是给正文用的选择器都必须写在这个全局块里，并统一收在
 * `.help-documentation .section-content` 命名空间下，避免污染其它页面。
 * ============================================================================
 */

/* ---------- 标题与段落 ---------- */
.help-documentation .section-content {
  padding-top: 6px;
  font-size: 14.5px;
  line-height: 1.85;
  color: var(--qm-text-1);
  word-break: break-word;
}

.help-documentation .section-content h3 {
  position: relative;
  margin: 34px 0 14px;
  padding-left: 14px;
  font-size: 19px;
  font-weight: 600;
  line-height: 1.45;
  color: var(--qm-text-1);
  border-left: 4px solid var(--qm-accent);
}

.help-documentation .section-content h3:first-child {
  margin-top: 6px;
}

.help-documentation .section-content h4 {
  margin: 18px 0 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--qm-text-1);
}

.help-documentation .section-content p {
  margin: 9px 0;
  color: var(--qm-text-2);
}

.help-documentation .section-content strong,
.help-documentation .section-content b {
  font-weight: 600;
  color: var(--qm-text-1);
}

.help-documentation .section-content ul,
.help-documentation .section-content ol {
  margin: 10px 0;
  padding-left: 23px;
}

.help-documentation .section-content li {
  margin: 6px 0;
  color: var(--qm-text-2);
}

.help-documentation .section-content li::marker {
  color: var(--qm-accent);
}

.help-documentation .section-content a {
  color: var(--qm-accent-strong);
  text-decoration: none;
}

/* ---------- 行内代码 ---------- */
.help-documentation .section-content code {
  padding: 2px 6px;
  border-radius: 5px;
  background: var(--qm-accent-soft);
  color: var(--qm-accent-strong);
  font-family: 'JetBrains Mono', Consolas, Menlo, Monaco, monospace;
  font-size: 12.8px;
  word-break: break-all;
}

/* ---------- 表格 ---------- */
.help-documentation .section-content .doc-table {
  width: 100%;
  margin: 14px 0 20px;
  border-collapse: collapse;
  table-layout: fixed;
  font-size: 13.4px;
}

.help-documentation .section-content .doc-table th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  color: var(--qm-text-1);
  background: var(--qm-bg-3);
  border: 1px solid var(--qm-line);
  line-height: 1.6;
}

.help-documentation .section-content .doc-table td {
  padding: 10px 12px;
  color: var(--qm-text-2);
  border: 1px solid var(--qm-line);
  vertical-align: top;
  line-height: 1.75;
  word-break: break-word;
}

.help-documentation .section-content .doc-table tbody tr:nth-child(even) td {
  background: var(--qm-bg-2);
}

.help-documentation .section-content .doc-table tbody tr:hover td {
  background: var(--qm-accent-soft);
}

/* 表格内嵌代码块不要撑破单元格 */
.help-documentation .section-content .doc-table code {
  font-size: 12.4px;
}

/* ---------- 徽标（枚举值展示） ---------- */
.help-documentation .section-content .badge {
  display: inline-block;
  margin: 2px 6px 2px 0;
  padding: 2px 9px;
  border-radius: 999px;
  border: 1px solid var(--qm-accent-line);
  background: var(--qm-accent-soft);
  color: var(--qm-accent-strong);
  font-size: 12px;
  line-height: 1.65;
  white-space: nowrap;
}

/* ---------- 提示块 ---------- */
.help-documentation .section-content .callout {
  position: relative;
  margin: 16px 0;
  padding: 14px 18px 14px 48px;
  border: 1px solid var(--qm-line);
  border-radius: var(--qm-radius-sm);
  background: var(--qm-bg-2);
}

.help-documentation .section-content .callout::before {
  content: '';
  position: absolute;
  left: 16px;
  top: 15px;
  width: 18px;
  height: 18px;
  background-repeat: no-repeat;
  background-position: center;
  background-size: 18px 18px;
}

.help-documentation .section-content .callout h4 {
  margin: 0 0 6px;
  font-size: 14.5px;
}

.help-documentation .section-content .callout > *:last-child {
  margin-bottom: 0;
}

.help-documentation .section-content .callout-info {
  background: var(--qm-info-soft);
  border-color: rgba(59, 130, 246, 0.3);
}

.help-documentation .section-content .callout-info::before {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233b82f6' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M12 16v-5'/%3E%3Cpath d='M12 8h.01'/%3E%3C/svg%3E");
}

.help-documentation .section-content .callout-tip {
  background: rgba(16, 185, 129, 0.08);
  border-color: rgba(16, 185, 129, 0.3);
}

.help-documentation .section-content .callout-tip::before {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2310b981' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 18h6'/%3E%3Cpath d='M10 22h4'/%3E%3Cpath d='M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z'/%3E%3C/svg%3E");
}

.help-documentation .section-content .callout-warn {
  background: var(--qm-warning-soft);
  border-color: var(--qm-warning-line);
}

.help-documentation .section-content .callout-warn::before {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f59e0b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M10.3 3.6 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0z'/%3E%3Cpath d='M12 9v4'/%3E%3Cpath d='M12 17h.01'/%3E%3C/svg%3E");
}

.help-documentation .section-content .callout-danger {
  background: var(--qm-red-soft);
  border-color: rgba(239, 68, 68, 0.3);
}

.help-documentation .section-content .callout-danger::before {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ef4444' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='12' cy='12' r='9'/%3E%3Cpath d='M15 9l-6 6'/%3E%3Cpath d='M9 9l6 6'/%3E%3C/svg%3E");
}

/* ---------- 流程条 ---------- */
.help-documentation .section-content .flow {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(178px, 1fr));
  gap: 12px;
  margin: 16px 0;
}

.help-documentation .section-content .flow-step {
  padding: 13px 15px;
  border: 1px solid var(--qm-line);
  border-radius: var(--qm-radius-sm);
  background: var(--qm-bg-2);
}

.help-documentation .section-content .flow-idx {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  margin-bottom: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--qm-accent) 0%, var(--qm-accent-2) 100%);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.help-documentation .section-content .flow-step b {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
  color: var(--qm-text-1);
}

.help-documentation .section-content .flow-step p {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
}

/* ---------- 步骤列表 ---------- */
.help-documentation .section-content .step-list {
  list-style: none;
  margin: 14px 0;
  padding-left: 0;
}

.help-documentation .section-content .step-list > li {
  margin: 0 0 10px;
  padding: 12px 16px;
  border: 1px solid var(--qm-line);
  border-left: 3px solid var(--qm-accent);
  border-radius: var(--qm-radius-sm);
  background: var(--qm-bg-2);
}

.help-documentation .section-content .step-list > li h4 {
  margin: 0 0 5px;
  font-size: 14.5px;
  color: var(--qm-text-1);
}

.help-documentation .section-content .step-list > li p {
  margin: 0 0 4px;
  font-size: 13.5px;
}

.help-documentation .section-content .step-list > li p:last-child {
  margin-bottom: 0;
}

.help-documentation .section-content .step-list > li ul,
.help-documentation .section-content .step-list > li ol {
  margin: 6px 0 0;
}

/* ---------- 兼容：卡片网格 ---------- */
.help-documentation .section-content .feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(206px, 1fr));
  gap: 12px;
  margin: 16px 0;
}

.help-documentation .section-content .feature-card {
  padding: 14px 16px;
  border: 1px solid var(--qm-line);
  border-radius: var(--qm-radius-sm);
  background: var(--qm-bg-2);
}

.help-documentation .section-content .feature-card h4 {
  margin: 0 0 6px;
  font-size: 14.5px;
}

.help-documentation .section-content .feature-card p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
}

/* ---------- 兼容：旧样式类名 ---------- */
.help-documentation .section-content .info-box {
  margin: 16px 0;
  padding: 14px 18px;
  border: 1px solid var(--qm-line);
  border-left: 3px solid var(--qm-accent);
  border-radius: var(--qm-radius-sm);
  background: var(--qm-bg-2);
}

.help-documentation .section-content .info-box h4 {
  margin: 0 0 6px;
}

/* ---------- 深色主题下的个别微调 ---------- */
html.dark .help-documentation .section-content .doc-table tbody tr:nth-child(even) td {
  background: var(--qm-bg-1);
}

html.dark .help-documentation .section-content .doc-table tbody tr:hover td {
  background: var(--qm-accent-soft);
}
</style>
