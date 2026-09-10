<template>
  <div class="help-documentation">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="header">
        <h1><i class="fas fa-question-circle"></i> 帮助文档</h1>
        <p>了解平台功能，快速上手使用</p>
      </div>
      
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchTerm" 
          placeholder="搜索帮助文档..."
          @input="filterNavigation"
        >
      </div>
      
      <div class="nav-container" ref="navContainer">
        <!-- 快速开始 -->
        <div 
          class="nav-item" 
          :class="{ active: activeSection === 'quick-start' }"
          @click="switchSection('quick-start')"
        >
          <div class="nav-item-header">
            <div>
              <i class="fas fa-rocket"></i> 快速开始
            </div>
          </div>
        </div>
        
        <!-- 平台菜单导航 -->
        <div 
          v-for="menuItem in filteredMenu" 
          :key="menuItem.path"
          class="nav-item"
          :class="{ 
            expanded: expandedItems.includes(menuItem.path),
            'active-parent': activeSection.startsWith(menuItem.path) && activeSection !== menuItem.path
          }"
        >
          <div 
            class="nav-item-header"
            :class="{ active: activeSection === menuItem.path }"
            @click="toggleMenuItem(menuItem)"
          >
            <div>
              <i :class="menuItem.icon"></i> {{ menuItem.name }}
            </div>
            <i 
              class="fas fa-chevron-right" 
              :class="{ rotated: expandedItems.includes(menuItem.path) }"
            ></i>
          </div>
          <div 
            class="nav-subitems" 
            :style="{ maxHeight: expandedItems.includes(menuItem.path) ? '1000px' : '0' }"
          >
            <div 
              v-for="child in menuItem.children" 
              :key="child.path"
              class="nav-subitem"
              :class="{ 
                active: activeSection === `${menuItem.path}-${getChildId(child)}` 
              }"
              @click.stop="switchSection(`${menuItem.path}-${getChildId(child)}`)"
            >
              <i :class="child.icon"></i> {{ child.name }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右侧内容区域 -->
    <div class="content" ref="contentContainer" @scroll="handleScroll">
      <!-- 右上角锚点导航 -->
      <div class="anchor-nav" :class="{ 'hidden': !showAnchorNav }">
        <div class="anchor-header">
          <h3><i class="fas fa-map-marker-alt"></i> 页面导航</h3>
          <button class="anchor-toggle" @click="toggleAnchorNav">
            <i class="fas" :class="showAnchorNav ? 'fa-times' : 'fa-bars'"></i>
          </button>
        </div>
        <div class="anchor-links" v-if="showAnchorNav">
          <a 
            v-for="anchor in currentAnchors" 
            :key="anchor.id"
            :href="'#' + anchor.id"
            class="anchor-link"
            :class="{ 'active': activeAnchor === anchor.id }"
            @click.prevent="scrollToAnchor(anchor.id)"
          >
            <i class="fas fa-caret-right"></i> {{ anchor.title }}
          </a>
        </div>
      </div>
      
      <!-- 回到顶部按钮 -->
      <button 
        class="back-to-top" 
        :class="{ 'visible': showBackToTop }"
        @click="scrollToTop"
      >
        <i class="fas fa-arrow-up"></i>
        <span>顶部</span>
      </button>
      
      <!-- 快速开始内容 -->
      <section 
        class="content-section" 
        :class="{ active: activeSection === 'quick-start' }"
        ref="quickStartSection"
      >
        <div class="section-header">
          <h2 id="quick-start-top"><i class="fas fa-rocket"></i> {{ quickStartContent.title }}</h2>
          <p>{{ quickStartContent.description }}</p>
        </div>
        <div class="section-content" v-html="quickStartContent.content" ref="quickStartContent"></div>
      </section>
      
      <!-- 平台菜单内容 -->
      <template v-for="menuItem in platformMenu"  :key="`${menuItem.path}-main`">
        <!-- 一级菜单内容 -->
        <section 
          class="content-section" 
          :class="{ active: activeSection === menuItem.path }"
          :ref="`section-${menuItem.path}`"
        >
          <div class="section-header">
            <h2 :id="`${menuItem.path}-top`"><i :class="menuItem.icon"></i> {{ menuItem.name }}</h2>
            <p>{{ getMenuContent(menuItem.name).description }}</p>
          </div>
          <div class="section-content" v-html="getMenuContent(menuItem.name).content" :ref="`content-${menuItem.path}`"></div>
        </section>
        
        <!-- 二级菜单内容 -->
        <section 
          v-for="child in menuItem.children" 
          :key="`${menuItem.path}-${getChildId(child)}`"
          class="content-section" 
          :class="{ 
            active: activeSection === `${menuItem.path}-${getChildId(child)}` 
          }"
          :ref="`section-${menuItem.path}-${getChildId(child)}`"
        >
          <div class="section-header">
            <h2 :id="`${menuItem.path}-${getChildId(child)}-top`"><i :class="child.icon"></i> {{ child.name }}</h2>
            <p>{{ menuItem.name }} > {{ child.name }} 功能说明</p>
          </div>
          <div class="section-content" :ref="`content-${menuItem.path}-${getChildId(child)}`">
            <h3 :id="`${menuItem.path}-${getChildId(child)}-function-intro`">功能介绍</h3>
            <p>{{ child.name }}是{{ menuItem.name }}模块的一部分，主要用于管理{{ child.name.toLowerCase() }}相关的功能。</p>
            
            <h3 :id="`${menuItem.path}-${getChildId(child)}-main-operations`">主要操作</h3>
            <ul>
              <li>查看{{ child.name.toLowerCase() }}</li>
              <li>添加新的{{ child.name.toLowerCase() }}</li>
              <li>编辑现有{{ child.name.toLowerCase() }}</li>
              <li>删除{{ child.name.toLowerCase() }}</li>
              <li>搜索和筛选{{ child.name.toLowerCase() }}</li>
            </ul>
            
            <h3 :id="`${menuItem.path}-${getChildId(child)}-usage-example`">使用示例</h3>
            <p>以下是如何使用{{ child.name }}功能的简单示例：</p>
            <ol>
              <li>进入{{ menuItem.name }}模块</li>
              <li>点击{{ child.name }}菜单</li>
              <li>查看{{ child.name.toLowerCase() }}列表</li>
              <li>点击"新增"按钮创建新的{{ child.name.toLowerCase() }}</li>
              <li>填写必要信息并保存</li>
            </ol>
            
            <div class="info-box">
              <h4><i class="fas fa-exclamation-circle"></i> 注意事项</h4>
              <p>1. 确保您有足够的权限访问{{ child.name }}功能</p>
              <p>2. 重要操作（如删除）可能需要管理员确认</p>
              <p>3. 定期备份重要数据，防止意外丢失</p>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script>
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
      platformMenu: [
        {
          'name': '用户管理',
          'level': 1,
          'path': 'user',
          'icon': 'fas fa-users',
          'parent': 0,
          'children': [
            {
              'name': '用户列表',
              'level': 2,
              'path': '/user/list',
              'icon': 'fas fa-user',
              'parent': 1,
            },
            {
              'name': '角色列表',
              'level': 2,
              'path': '/user/role',
              'icon': 'fas fa-user-tag',
              'parent': 1,
            },
            {
              'name': '权限列表',
              'level': 2,
              'path': '/user/permission',
              'icon': 'fas fa-key',
              'parent': 1,
            }
          ]
        },
        {
          'name': '环境管理',
          'level': 1,
          'path': 'env',
          'icon': 'fas fa-server',
          'parent': 0,
          'children': [
            {
              'name': '环境配置',
              'level': 2,
              'path': '/env/env',
              'icon': 'fas fa-cogs',
              'parent': 1,
            },
            {
              'name': '服务配置',
              'level': 2,
              'path': '/env/service',
              'icon': 'fas fa-network-wired',
              'parent': 1,
            },
            {
              'name': '产品配置',
              'level': 2,
              'path': '/env/plant',
              'icon': 'fas fa-box',
              'parent': 1,
            },
            {
              'name': '数据库配置',
              'level': 2,
              'path': '/env/db',
              'icon': 'fas fa-database',
              'parent': 1,
            },
          ]
        },
        {
          'name': '公共资源',
          'level': 1,
          'path': 'common',
          'icon': 'fas fa-folder-open',
          'parent': 0,
          'children': [
            {
              'name': '文件管理',
              'level': 2,
              'path': '/common/file',
              'icon': 'fas fa-file',
              'parent': 1,
            },
            {
              'name': '元素配置',
              'level': 2,
              'path': '/common/element',
              'icon': 'fas fa-code',
              'parent': 1,
            },
            {
              'name': '常量配置',
              'level': 2,
              'path': '/common/enum',
              'icon': 'fas fa-list',
              'parent': 1,
            },
            {
              'name': '用户函数',
              'level': 2,
              'path': '/common/python',
              'icon': 'fas fa-code',
              'parent': 1,
            },
            {
              'name': '步骤管理',
              'level': 2,
              'path': '/test/step',
              'icon': 'fas fa-step-forward',
              'parent': 1,
            },
            {
              'name': 'Selenium',
              'level': 2,
              'path': '/common/selenium',
              'icon': 'fas fa-window-maximize',
              'parent': 1,
            },
            {
              'name': 'Appium',
              'level': 2,
              'path': '/common/appium',
              'icon': 'fas fa-mobile-alt',
              'parent': 1,
            },
          ]
        },
        {
          'name': '接口管理',
          'level': 1,
          'path': 'interface',
          'icon': 'fas fa-plug',
          'parent': 0,
          'children': [
            {
              'name': '接口列表',
              'level': 2,
              'path': '/interface/api',
              'icon': 'fas fa-link',
              'parent': 1,
            },
          ]
        },
        {
          'name': '用例管理',
          'level': 1,
          'path': 'case',
          'icon': 'fas fa-tasks',
          'parent': 0,
          'children': [
            {
              'name': '用例标签',
              'level': 2,
              'path': '/test/tag',
              'icon': 'fas fa-tag',
              'parent': 1,
            },
            {
              'name': '功能用例',
              'level': 2,
              'path': '/test/func_case',
              'icon': 'fas fa-check-circle',
              'parent': 1,
            },
            {
              'name': '脚本用例',
              'level': 2,
              'path': '/test/case',
              'icon': 'fas fa-terminal',
              'parent': 1,
            },
          ]
        },
        {
          'name': '测试计划',
          'level': 1,
          'path': 'suite',
          'icon': 'fas fa-calendar-alt',
          'parent': 0,
          'children': [
            {
              'name': '功能套件',
              'level': 2,
              'path': '/suite/list',
              'icon': 'fas fa-layer-group',
              'parent': 1,
            },
            {
              'name': '定时任务',
              'level': 2,
              'path': '/suite/task',
              'icon': 'fas fa-clock',
              'parent': 1,
            },
          ]
        },
        {
          'name': '报告管理',
          'level': 1,
          'path': 'report',
          'icon': 'fas fa-chart-bar',
          'parent': 0,
          'children': [
            {
              'name': '日志列表',
              'level': 2,
              'path': '/report/log',
              'icon': 'fas fa-clipboard-list',
              'parent': 1
            },
            {
              'name': '功能报告',
              'level': 2,
              'path': '/report/list',
              'icon': 'fas fa-chart-pie',
              'parent': 1
             },
            {
              'name': '性能报告',
              'level': 2,
              'path': '/report/locust',
              'icon': 'fas fa-chart-line',
              'parent': 1
             },
          ]
        },
      ],
      quickStartContent: {
        id: 'quick-start',
        title: '快速开始',
        icon: 'fas fa-rocket',
        description: '欢迎使用 Q·M 测试平台！本指南将帮助您快速了解平台功能并开始使用。',
        content: `
          <h3 id="platform-overview">平台概述</h3>
          <p>Q·M 是一款现代化的 Web 应用测试平台，专为测试团队设计，自动化测试平台支持接口测试、Mock 服务、UI 自动化及性能测试，并提供可视化报告输出。平台集成多种主流测试框架，显著降低用例编写难度，助力团队高效开展自动化测试，提升整体测试效率与协作能力</p>
          
          <div class="info-box">
            <h3 id="create-interface"><i class="fas fa-lightbulb"></i> 创建我的第一个接口文档并调试</h3>
			<p>下面会以 Q·M 测试平台为测试对象，来介绍怎么去创建接口文档，创建API用例</p>
            <ul class="step-list">
              <li>
                <h4>1. 创建测试环境</h4>
                <p>首先进入<strong>用户管理</strong>模块，根据团队成员的角色分配相应的权限。您可以创建用户、定义角色和配置权限。</p>
              </li>
              <li>
                <h4>2. 创建测试产品</h4>
                <p>在<strong>环境管理</strong>中配置测试所需的环境信息，包括测试环境、预发布环境和生产环境等。</p>
              </li>
              <li>
                <h4>3. 创建测试微服务</h4>
                <p>在<strong>公共资源</strong>中配置测试过程中需要使用的共享资源，如文件、元素定位信息、常量等。</p>
              </li>
              <li>
                <h4>4. 创建接口文档</h4>
                <p>在<strong>接口管理</strong>和<strong>用例管理</strong>中创建和组织您的测试用例。</p>
              </li>
              <li>
                <h4>5. 执行测试</h4>
                <p>通过<strong>测试计划</strong>模块组织测试套件，安排定时任务并执行测试。</p>
              </li>
              <li>
                <h4>6. 查看结果</h4>
                <p>在<strong>报告管理</strong>中查看测试执行结果、日志和详细的测试报告。</p>
              </li>
            </ul>
          </div>
          
          <h3 id="first-api-case">创建我的第一个API自动化用例</h3>
          <ul class="step-list">
            <li>
              <h4>1. 用户配置</h4>
              <p>首先进入<strong>用户管理</strong>模块，根据团队成员的角色分配相应的权限。您可以创建用户、定义角色和配置权限。</p>
            </li>
            <li>
              <h4>2. 环境配置</h4>
              <p>在<strong>环境管理</strong>中配置测试所需的环境信息，包括测试环境、预发布环境和生产环境等。</p>
            </li>
            <li>
              <h4>3. 资源准备</h4>
              <p>在<strong>公共资源</strong>中配置测试过程中需要使用的共享资源，如文件、元素定位信息、常量等。</p>
            </li>
            <li>
              <h4>4. 创建测试内容</h4>
              <p>在<strong>接口管理</strong>和<strong>用例管理</strong>中创建和组织您的测试用例。</p>
            </li>
            <li>
              <h4>5. 执行测试</h4>
              <p>通过<strong>测试计划</strong>模块组织测试套件，安排定时任务并执行测试。</p>
            </li>
            <li>
              <h4>6. 查看结果</h4>
              <p>在<strong>报告管理</strong>中查看测试执行结果、日志和详细的测试报告。</p>
            </li>
          </ul>
          
          <h3 id="core-features">核心功能模块</h3>
          <div class="feature-grid">
            <div class="feature-card">
              <h4><i class="fas fa-users"></i> 用户管理</h4>
              <p>管理平台用户、角色和权限，确保团队成员拥有适当的访问权限。</p>
            </div>
            <div class="feature-card">
              <h4><i class="fas fa-server"></i> 环境管理</h4>
              <p>配置和管理不同测试环境，包括环境变量、微服务地址和数据库连接。</p>
            </div>
            <div class="feature-card">
              <h4><i class="fas fa-folder-open"></i> 公共资源</h4>
              <p>集中管理测试过程中使用的共享资源，提高资源复用率。</p>
            </div>
            <div class="feature-card">
              <h4><i class="fas fa-plug"></i> 接口管理</h4>
              <p>管理和测试API接口，支持接口调试和接口Mock功能。</p>
            </div>
            <div class="feature-card">
              <h4><i class="fas fa-tasks"></i> 用例管理</h4>
              <p>创建、组织和管理测试用例，支持功能测试用例编写和脚本测试用例编写。</p>
            </div>
            <div class="feature-card">
              <h4><i class="fas fa-chart-bar"></i> 报告管理</h4>
              <p>查看测试执行结果、日志和生成详细的测试报告。</p>
            </div>
          </div>
        `
      },
      menuContentMap: {
        '用户管理': {
          description: '管理平台用户、角色和权限配置',
          content: `
            <h3 id="user-user-list">用户列表</h3>
            <p>在用户列表页面，您可以查看、添加、编辑和删除平台用户。每个用户都可以分配一个或多个角色。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>查看所有用户信息</li>
              <li>添加新用户</li>
              <li>编辑用户信息和状态</li>
              <li>为用户分配角色</li>
              <li>重置用户密码</li>
            </ul>
            
            <h3 id="user-role-list">角色列表</h3>
            <p>角色列表用于管理用户角色，每个角色可以关联一组权限，用户通过角色获得相应的平台访问权限。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>创建和管理角色</li>
              <li>为角色分配权限</li>
              <li>查看角色下的用户</li>
              <li>设置角色优先级</li>
            </ul>
            
            <h3 id="user-permission-list">权限列表</h3>
            <p>权限列表展示了平台所有可配置的权限点，可以细粒度控制用户对平台功能的访问。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>查看所有权限点</li>
              <li>权限分类管理</li>
              <li>权限与菜单关联</li>
              <li>权限搜索和过滤</li>
            </ul>
            
            <div class="info-box">
              <h4 id="user-notice"><i class="fas fa-exclamation-triangle"></i> 注意事项</h4>
              <p>1. 超级管理员角色拥有所有权限，无法被修改或删除</p>
              <p>2. 权限分配遵循最小权限原则，只授予用户完成工作所必需的权限</p>
              <p>3. 角色变更后，已登录用户需要重新登录才能生效</p>
            </div>
          `
        },
        '环境管理': {
          description: '配置和管理测试环境、服务和数据库',
          content: `
            <h3 id="env-env-config">环境配置</h3>
            <p>环境配置用于管理不同测试环境（如开发环境、测试环境、预生产环境、生产环境）的基本信息。</p>
            <p><strong>主要配置项：</strong></p>
            <ul>
              <li>环境名称和标识</li>
              <li>环境访问地址</li>
              <li>环境变量配置</li>
              <li>环境状态管理</li>
            </ul>
            
            <h3 id="env-service-config">服务配置</h3>
            <p>服务配置用于管理环境中各个微服务的地址和配置信息，支持服务发现和负载均衡配置。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>服务注册和管理</li>
              <li>服务地址配置</li>
              <li>健康检查设置</li>
              <li>服务依赖关系</li>
            </ul>
            
            <h3 id="env-product-config">产品配置</h3>
            <p>产品配置用于管理不同产品的环境配置，支持多产品线并行测试。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>产品信息管理</li>
              <li>产品与环境关联</li>
              <li>产品版本管理</li>
            </ul>
            
            <h3 id="env-db-config">数据库配置</h3>
            <p>数据库配置用于管理不同环境下的数据库连接信息，支持多种数据库类型。</p>
            <p><strong>支持的数据类型：</strong></p>
            <ul>
              <li>MySQL</li>
              <li>PostgreSQL</li>
              <li>Oracle</li>
              <li>SQL Server</li>
              <li>Redis</li>
              <li>MongoDB</li>
            </ul>
            
            <div class="info-box">
              <h4 id="env-best-practice"><i class="fas fa-lightbulb"></i> 最佳实践</h4>
              <p>1. 为每个测试环境创建独立的配置，避免环境间相互影响</p>
              <p>2. 定期检查和更新环境配置，确保配置信息的准确性</p>
              <p>3. 使用环境变量存储敏感信息，如数据库密码</p>
            </div>
          `
        },
        '公共资源': {
          description: '管理测试过程中使用的公共资源和工具',
          content: `
            <h3 id="common-file-management">文件管理</h3>
            <p>文件管理用于存储和管理测试过程中使用的文件，如测试数据文件、脚本文件、配置文件等。</p>
            <p><strong>支持的文件类型：</strong></p>
            <ul>
              <li>文本文件（.txt, .csv, .json, .xml）</li>
              <li>脚本文件（.py, .js, .sh）</li>
              <li>文档文件（.doc, .pdf, .xlsx）</li>
              <li>图像文件（.png, .jpg, .gif）</li>
            </ul>
            
            <h3 id="common-element-config">元素配置</h3>
            <p>元素配置用于管理UI自动化测试中的页面元素定位信息，支持多种定位方式。</p>
            <p><strong>支持的定位方式：</strong></p>
            <ul>
              <li>ID定位</li>
              <li>CSS选择器</li>
              <li>XPath</li>
              <li>名称定位</li>
              <li>链接文本</li>
            </ul>
            
            <h3 id="common-constant-config">常量配置</h3>
            <p>常量配置用于管理测试过程中使用的常量值，如状态码、错误信息、固定参数等。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>常量分类管理</li>
              <li>常量值维护</li>
              <li>常量引用查看</li>
            </ul>
            
            <h3 id="common-user-functions">用户函数</h3>
            <p>用户函数用于创建和管理自定义函数，可以在测试用例中调用，提高测试脚本的复用性。</p>
            <p><strong>支持的语言：</strong></p>
            <ul>
              <li>Python</li>
              <li>JavaScript</li>
              <li>Shell脚本</li>
            </ul>
            
            <h3 id="common-step-management">步骤管理</h3>
            <p>步骤管理用于创建和管理可复用的测试步骤，支持步骤组合和参数化。</p>
            
            <h3 id="common-selenium-config">Selenium配置</h3>
            <p>Selenium配置用于管理Web自动化测试的浏览器驱动和配置信息。</p>
            
            <h3 id="common-appium-config">Appium配置</h3>
            <p>Appium配置用于管理移动端自动化测试的设备和应用配置。</p>
            
            <div class="info-box">
              <h4 id="common-tips"><i class="fas fa-lightbulb"></i> 使用技巧</h4>
              <p>1. 将常用的测试数据和配置放在公共资源中，便于多测试用例共享使用</p>
              <p>2. 使用用户函数封装复杂的测试逻辑，提高脚本的可维护性</p>
              <p>3. 定期清理不再使用的文件，保持资源库的整洁</p>
            </div>
          `
        },
        '接口管理': {
          description: '管理和测试API接口',
          content: `
            <h3 id="interface-interface-list">接口列表</h3>
            <p>接口列表用于管理所有API接口，支持接口的增删改查、调试和测试。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>接口信息管理（名称、路径、方法、描述）</li>
              <li>请求参数配置（Header、Query、Body）</li>
              <li>响应结果验证</li>
              <li>接口调试和测试</li>
              <li>接口文档生成</li>
            </ul>
            
            <h3 id="interface-interface-test-process">接口测试流程</h3>
            <ol class="step-list">
              <li>
                <h4>1. 创建接口</h4>
                <p>填写接口的基本信息，包括接口名称、请求方法、请求路径等。</p>
              </li>
              <li>
                <h4>2. 配置请求参数</h4>
                <p>配置请求头、查询参数、路径参数和请求体。</p>
              </li>
              <li>
                <h4>3. 配置断言规则</h4>
                <p>设置响应状态码、响应头和响应体的验证规则。</p>
              </li>
              <li>
                <h4>4. 调试接口</h4>
                <p>发送测试请求，验证接口返回结果是否符合预期。</p>
              </li>
              <li>
                <h4>5. 保存并关联用例</h4>
                <p>将配置好的接口保存，并可以关联到测试用例中。</p>
              </li>
            </ol>
            
            <div class="info-box">
              <h4 id="interface-notice"><i class="fas fa-exclamation-triangle"></i> 注意事项</h4>
              <p>1. 接口路径应使用相对路径，避免包含完整域名</p>
              <p>2. 敏感参数（如密码、token）应使用变量代替明文</p>
              <p>3. 定期检查接口的有效性，及时更新已变更的接口</p>
            </div>
          `
        },
        '用例管理': {
          description: '创建和管理测试用例',
          content: `
            <h3 id="case-case-tags">用例标签</h3>
            <p>用例标签用于对测试用例进行分类，便于用例的组织和筛选。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>创建和管理标签</li>
              <li>标签分类和层级</li>
              <li>为用例分配标签</li>
              <li>按标签筛选用例</li>
            </ul>
            
            <h3 id="case-functional-cases">功能用例</h3>
            <p>功能用例用于创建和管理功能测试用例，支持可视化用例编排。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>可视化用例设计</li>
              <li>步骤参数化配置</li>
              <li>数据驱动测试</li>
              <li>用例版本管理</li>
            </ul>
            
            <h3 id="case-script-cases">脚本用例</h3>
            <p>脚本用例用于创建和管理脚本测试用例，支持多种编程语言。</p>
            <p><strong>支持的语言：</strong></p>
            <ul>
              <li>Python</li>
              <li>JavaScript</li>
              <li>Java</li>
              <li>Shell</li>
            </ul>
            
            <h3 id="case-case-design-principles">用例设计原则</h3>
            <div class="feature-grid">
              <div class="feature-card">
                <h4><i class="fas fa-check-circle"></i> 独立性</h4>
                <p>每个测试用例应独立运行，不依赖其他用例的执行结果。</p>
              </div>
              <div class="feature-card">
                <h4><i class="fas fa-redo"></i> 可重复性</h4>
                <p>测试用例应能够在相同环境下重复执行，得到相同的结果。</p>
              </div>
              <div class="feature-card">
                <h4><i class="fas fa-bullseye"></i> 针对性</h4>
                <p>每个测试用例应针对特定的功能点或场景进行测试。</p>
              </div>
              <div class="feature-card">
                <h4><i class="fas fa-exchange-alt"></i> 可维护性</h4>
                <p>测试用例应易于维护和更新，适应系统变更。</p>
              </div>
            </div>
          `
        },
        '测试计划': {
          description: '组织和管理测试计划与任务',
          content: `
            <h3 id="suite-function-suites">功能套件</h3>
            <p>功能套件用于组织和管理一组相关的测试用例，支持套件的执行和调度。</p>
            <p><strong>主要功能：</strong></p>
            <ul>
              <li>创建和管理测试套件</li>
              <li>向套件中添加/移除用例</li>
              <li>套件执行顺序配置</li>
              <li>套件执行环境选择</li>
            </ul>
            
            <h3 id="suite-scheduled-tasks">定时任务</h3>
            <p>定时任务用于配置和管理定期执行的测试任务，支持多种触发方式。</p>
            <p><strong>触发方式：</strong></p>
            <ul>
              <li>定时执行（cron表达式）</li>
              <li>间隔执行</li>
              <li>手动触发</li>
              <li>事件触发</li>
            </ul>
            
            <h3 id="suite-test-plan-execution">测试计划执行流程</h3>
            <ol class="step-list">
              <li>
                <h4>1. 创建测试套件</h4>
                <p>选择要执行的测试用例，组成测试套件。</p>
              </li>
              <li>
                <h4>2. 配置执行环境</h4>
                <p>选择测试执行的环境，配置环境变量和参数。</p>
              </li>
              <li>
                <h4>3. 设置执行策略</h4>
                <p>配置用例执行顺序、失败重试机制等。</p>
              </li>
              <li>
                <h4>4. 执行测试</h4>
                <p>立即执行或配置定时任务执行测试。</p>
              </li>
              <li>
                <h4>5. 查看结果</h4>
                <p>在报告管理中查看测试执行结果。</p>
              </li>
            </ol>
            
            <div class="info-box">
              <h4 id="suite-best-practice"><i class="fas fa-lightbulb"></i> 最佳实践</h4>
              <p>1. 将核心功能用例组织到每日执行的回归测试套件中</p>
              <p>2. 为不同环境创建不同的测试套件，确保环境适配性</p>
              <p>3. 设置合理的失败重试机制，减少环境波动导致的误报</p>
            </div>
          `
        },
        '报告管理': {
          description: '查看测试执行结果和报告',
          content: `
            <h3 id="report-log-list">日志列表</h3>
            <p>日志列表展示了测试执行的详细日志，便于问题排查和调试。</p>
            <p><strong>日志类型：</strong></p>
            <ul>
              <li>执行日志</li>
              <li>错误日志</li>
              <li>调试日志</li>
              <li>系统日志</li>
            </ul>
            
            <h3 id="report-functional-reports">功能报告</h3>
            <p>功能报告展示了功能测试的执行结果，包括通过率、失败用例、执行时间等统计信息。</p>
            <p><strong>报告内容：</strong></p>
            <ul>
              <li>测试执行概览</li>
              <li>用例通过/失败统计</li>
              <li>失败用例详情</li>
              <li>执行趋势分析</li>
              <li>问题分布统计</li>
            </ul>
            
            <h3 id="report-performance-reports">性能报告</h3>
            <p>性能报告展示了性能测试的执行结果，包括响应时间、吞吐量、错误率等指标。</p>
            <p><strong>性能指标：</strong></p>
            <ul>
              <li>响应时间（平均、最小、最大、百分位）</li>
              <li>吞吐量（请求/秒）</li>
              <li>并发用户数</li>
              <li>错误率</li>
              <li>资源使用率（CPU、内存、网络）</li>
            </ul>
            
            <h3 id="report-report-analysis">报告分析技巧</h3>
            <div class="feature-grid">
              <div class="feature-card">
                <h4><i class="fas fa-chart-line"></i> 趋势分析</h4>
                <p>通过对比历史报告，识别测试质量的变化趋势。</p>
              </div>
              <div class="feature-card">
                <h4><i class="fas fa-bug"></i> 问题定位</h4>
                <p>利用日志和失败用例详情，快速定位问题根源。</p>
              </div>
              <div class="feature-card">
                <h4><i class="fas fa-tachometer-alt"></i> 性能评估</h4>
                <p>分析性能指标，评估系统性能是否满足要求。</p>
              </div>
              <div class="feature-card">
                <h4><i class="fas fa-clipboard-check"></i> 质量评估</h4>
                <p>基于测试通过率和问题分布，评估软件发布质量。</p>
              </div>
            </div>
          `
        }
      }
    }
  },
  computed: {
    currentAnchors() {
      // 根据当前激活的页面返回对应的锚点列表
      if (this.activeSection === 'quick-start') {
        return [
          { id: 'quick-start-top', title: '快速开始' },
          { id: 'platform-overview', title: '平台概述' },
          { id: 'create-interface', title: '创建接口并调试' },
          { id: 'first-api-case', title: '创建第一个API用例' },
          { id: 'core-features', title: '核心功能模块' }
        ]
      } else if (this.activeSection === 'user') {
        return [
          { id: 'user-top', title: '用户管理' },
          { id: 'user-user-list', title: '用户列表' },
          { id: 'user-role-list', title: '角色列表' },
          { id: 'user-permission-list', title: '权限列表' },
          { id: 'user-notice', title: '注意事项' }
        ]
      } else if (this.activeSection === 'env') {
        return [
          { id: 'env-top', title: '环境管理' },
          { id: 'env-env-config', title: '环境配置' },
          { id: 'env-service-config', title: '服务配置' },
          { id: 'env-product-config', title: '产品配置' },
          { id: 'env-db-config', title: '数据库配置' },
          { id: 'env-best-practice', title: '最佳实践' }
        ]
      } else if (this.activeSection === 'common') {
        return [
          { id: 'common-top', title: '公共资源' },
          { id: 'common-file-management', title: '文件管理' },
          { id: 'common-element-config', title: '元素配置' },
          { id: 'common-constant-config', title: '常量配置' },
          { id: 'common-user-functions', title: '用户函数' },
          { id: 'common-step-management', title: '步骤管理' },
          { id: 'common-selenium-config', title: 'Selenium配置' },
          { id: 'common-appium-config', title: 'Appium配置' },
          { id: 'common-tips', title: '使用技巧' }
        ]
      } else if (this.activeSection === 'interface') {
        return [
          { id: 'interface-top', title: '接口管理' },
          { id: 'interface-interface-list', title: '接口列表' },
          { id: 'interface-interface-test-process', title: '接口测试流程' },
          { id: 'interface-notice', title: '注意事项' }
        ]
      } else if (this.activeSection === 'case') {
        return [
          { id: 'case-top', title: '用例管理' },
          { id: 'case-case-tags', title: '用例标签' },
          { id: 'case-functional-cases', title: '功能用例' },
          { id: 'case-script-cases', title: '脚本用例' },
          { id: 'case-case-design-principles', title: '用例设计原则' }
        ]
      } else if (this.activeSection === 'suite') {
        return [
          { id: 'suite-top', title: '测试计划' },
          { id: 'suite-function-suites', title: '功能套件' },
          { id: 'suite-scheduled-tasks', title: '定时任务' },
          { id: 'suite-test-plan-execution', title: '测试计划执行流程' },
          { id: 'suite-best-practice', title: '最佳实践' }
        ]
      } else if (this.activeSection === 'report') {
        return [
          { id: 'report-top', title: '报告管理' },
          { id: 'report-log-list', title: '日志列表' },
          { id: 'report-functional-reports', title: '功能报告' },
          { id: 'report-performance-reports', title: '性能报告' },
          { id: 'report-report-analysis', title: '报告分析技巧' }
        ]
      } else {
        // 对于二级菜单页面
        for (const menuItem of this.platformMenu) {
          for (const child of menuItem.children) {
            const childId = this.getChildId(child)
            const sectionId = `${menuItem.path}-${childId}`
            if (this.activeSection === sectionId) {
              return [
                { id: `${menuItem.path}-${childId}-top`, title: child.name },
                { id: `${menuItem.path}-${childId}-function-intro`, title: '功能介绍' },
                { id: `${menuItem.path}-${childId}-main-operations`, title: '主要操作' },
                { id: `${menuItem.path}-${childId}-usage-example`, title: '使用示例' }
              ]
            }
          }
        }
        return []
      }
    }
  },
  mounted() {
    // 初始化过滤后的菜单
    this.filteredMenu = [...this.platformMenu]
    
    // 默认展开第一个菜单项
    if (this.platformMenu.length > 0) {
      this.expandedItems.push(this.platformMenu[0].path)
    }
    
    // 获取内容容器
    this.contentContainer = this.$refs.contentContainer
    
    // 初始滚动位置检查
    this.$nextTick(() => {
      this.handleScroll()
    })
  },
  beforeUnmount() {
    // 清理
    if (this.scrollThrottle) {
      clearTimeout(this.scrollThrottle)
    }
  },
  watch: {
    activeSection() {
      // 切换页面时重置激活的锚点
      this.activeAnchor = ''
      // 等待DOM更新后检查滚动位置
      this.$nextTick(() => {
        this.handleScroll()
        // 滚动到顶部
        if (this.contentContainer) {
          this.contentContainer.scrollTop = 0
        }
      })
    }
  },
  methods: {
    getChildId(child) {
      // 从路径中提取子菜单ID
      return child.path.split('/').pop()
    },
    switchSection(sectionId) {
      this.activeSection = sectionId
      
      // 如果是子菜单项，确保其父菜单是展开的
      if (sectionId.includes('-')) {
        const parentPath = sectionId.split('-')[0]
        if (!this.expandedItems.includes(parentPath)) {
          this.expandedItems.push(parentPath)
        }
      }
      
      // 滚动到顶部
      this.$nextTick(() => {
        if (this.contentContainer) {
          this.contentContainer.scrollTop = 0
        }
      })
    },
    toggleMenuItem(menuItem) {
      // 有子菜单的父菜单，点击后只展开/收起子菜单，不切换内容
      const index = this.expandedItems.indexOf(menuItem.path)
      if (index > -1) {
        this.expandedItems.splice(index, 1)
      } else {
        this.expandedItems.push(menuItem.path)
      }
    },
    filterNavigation() {
      if (!this.searchTerm.trim()) {
        this.filteredMenu = [...this.platformMenu]
        return
      }
      
      const searchTerm = this.searchTerm.toLowerCase()
      this.filteredMenu = this.platformMenu.filter(menuItem => {
        // 检查一级菜单是否匹配
        if (menuItem.name.toLowerCase().includes(searchTerm)) {
          return true
        }
        
        // 检查二级菜单是否匹配
        const matchingChildren = menuItem.children.filter(child => 
          child.name.toLowerCase().includes(searchTerm)
        )
        
        if (matchingChildren.length > 0) {
          // 如果有匹配的子项，展开该菜单
          if (!this.expandedItems.includes(menuItem.path)) {
            this.expandedItems.push(menuItem.path)
          }
          return true
        }
        
        return false
      })
    },
    getMenuContent(menuName) {
      return this.menuContentMap[menuName] || {
        description: `${menuName}模块的帮助文档`,
        content: `<p>这是${menuName}模块的帮助文档内容。您可以在这里找到关于该模块的详细使用说明。</p>`
      }
    },
    toggleAnchorNav() {
      this.showAnchorNav = !this.showAnchorNav
    },
    scrollToAnchor(anchorId) {
      // 等待DOM更新，确保元素存在
      this.$nextTick(() => {
        const element = document.getElementById(anchorId)
        if (element && this.contentContainer) {
          // 计算元素相对于内容容器的位置
          const containerRect = this.contentContainer.getBoundingClientRect()
          const elementRect = element.getBoundingClientRect()
          const offsetTop = elementRect.top - containerRect.top + this.contentContainer.scrollTop - 100
          
          // 滚动到指定位置
          this.contentContainer.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
          })
          
          // 更新激活的锚点
          this.activeAnchor = anchorId
          
          // 滚动结束后再更新一次
          if (this.scrollThrottle) {
            clearTimeout(this.scrollThrottle)
          }
          this.scrollThrottle = setTimeout(() => {
            this.handleScroll()
          }, 500)
        } else if (!element) {
          console.warn(`Anchor element #${anchorId} not found`)
        }
      })
    },
    handleScroll() {
      if (!this.contentContainer) return
      
      // 控制回到顶部按钮的显示
      const scrollTop = this.contentContainer.scrollTop
      this.showBackToTop = scrollTop > 300
      
      // 更新当前激活的锚点
      if (!this.currentAnchors.length) return
      
      // 获取当前滚动位置
      const scrollPosition = scrollTop + 150 // 增加偏移量，让高亮更准确
      
      // 找到当前滚动位置对应的锚点
      let closestAnchor = null
      let closestDistance = Infinity
      
      for (const anchor of this.currentAnchors) {
        const element = document.getElementById(anchor.id)
        if (element) {
          // 计算元素相对于内容容器的位置
          const containerRect = this.contentContainer.getBoundingClientRect()
          const elementRect = element.getBoundingClientRect()
          const elementTop = elementRect.top - containerRect.top + scrollTop
          
          const distance = Math.abs(scrollPosition - elementTop)
          
          // 如果元素在可视区域上方或接近可视区域顶部
          if (scrollPosition >= elementTop - 50 && distance < closestDistance) {
            closestDistance = distance
            closestAnchor = anchor.id
          }
        }
      }
      
      // 更新激活的锚点
      if (closestAnchor) {
        this.activeAnchor = closestAnchor
      } else if (scrollTop < 100) {
        // 如果在页面顶部，高亮第一个锚点
        this.activeAnchor = this.currentAnchors[0]?.id || ''
      }
    },
    scrollToTop() {
      if (this.contentContainer) {
        this.contentContainer.scrollTo({
          top: 0,
          behavior: 'smooth'
        })
      }
    }
  }
}
</script>

<style scoped>
.help-documentation {
  display: flex;
  height: 100vh;
  background-color: var(--qm-text-1);
  color: var(--qm-text-1);
  font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

/* 左侧导航栏样式 */
.sidebar {
  width: 250px;
  background: linear-gradient(180deg, #2c3e50 0%, #1a2530 100%);
  color: #ecf0f1;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 0 15px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.header {
  padding: 25px 20px;
  border-bottom: 1px solid #34495e;
}

.header h1 {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 5px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header h1 i {
  color: #f59e0b;
}

.header p {
  font-size: 0.9rem;
  color: #bdc3c7;
  opacity: 0.8;
}

.search-box {
  padding: 15px 20px;
  border-bottom: 1px solid #34495e;
}

.search-box input {
  width: 90%;
  padding: 10px 15px;
  border-radius: 6px;
  border: none;
  background-color: #34495e;
  color: #ecf0f1;
  font-size: 0.9rem;
}

.search-box input:focus {
  outline: 2px solid #f59e0b;
  background-color: #2c3e50;
}

.nav-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
}

.nav-item {
  padding: 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

/* 快速开始菜单项激活状态 */
.nav-item:first-child.active {
  background-color: rgba(52, 152, 219, 0.1);
}

.nav-item:first-child.active .nav-item-header {
  border-left: 4px solid #f59e0b;
}

/* 父菜单展开状态 */
.nav-item.expanded {
  background-color: rgba(52, 152, 219, 0.05);
}

/* 父菜单激活状态（自身被激活） */
.nav-item .nav-item-header.active {
  background-color: rgba(52, 152, 219, 0.1);
  border-left: 4px solid #f59e0b;
}

.nav-item-header {
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  border-left: 4px solid transparent;
  transition: background-color 0.3s ease;
}

.nav-item-header:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-item-header i.fa-chevron-right {
  font-size: 0.9rem;
  transition: transform 0.3s ease;
}

.nav-item-header i.fa-chevron-right.rotated {
  transform: rotate(90deg);
}

.nav-subitems {
  overflow: hidden;
  background-color: rgba(0, 0, 0, 0.2);
  transition: max-height 0.5s ease;
}

.nav-subitem {
  padding: 12px 20px 12px 40px;
  border-left: 4px solid transparent;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

.nav-subitem:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-subitem.active {
  background-color: rgba(52, 152, 219, 0.15);
  border-left-color: #f59e0b;
  color: #f59e0b;
  font-weight: 500;
}

.nav-subitem i {
  width: 18px;
  text-align: center;
  font-size: 0.9rem;
}

/* 右侧内容区域样式 */
.content {
  flex: 1;
  overflow-y: auto;
  padding: 40px;
  background-color: var(--qm-bg-2);
  position: relative;
}

/* 锚点导航样式 */
.anchor-nav {
  position: fixed;
  top: 40px;
  right: 40px;
  width: 220px;
  background-color: var(--qm-bg-2);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  transition: all 0.3s ease;
  border: 1px solid #eaeaea;
  overflow: hidden;
}

.anchor-nav.hidden {
  width: 50px;
  height: 50px;
}

.anchor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: var(--qm-bg-1);
  border-bottom: 1px solid #eaeaea;
}

.anchor-header h3 {
  font-size: 1rem;
  color: #2c3e50;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.anchor-header h3 i {
  color: #f59e0b;
}

.anchor-toggle {
  background: none;
  border: none;
  color: #7f8c8d;
  cursor: pointer;
  font-size: 1.1rem;
  padding: 5px;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.anchor-toggle:hover {
  color: #f59e0b;
  background-color: rgba(52, 152, 219, 0.1);
}

.anchor-links {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px 0;
}

.anchor-link {
  display: block;
  padding: 10px 20px;
  color: #555;
  text-decoration: none;
  font-size: 0.9rem;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.anchor-link:hover {
  background-color: var(--qm-bg-1);
  color: #f59e0b;
  border-left-color: #f59e0b;
}

.anchor-link.active {
  background-color: rgba(52, 152, 219, 0.1);
  color: #f59e0b;
  font-weight: 500;
  border-left-color: #f59e0b;
}

.anchor-link i {
  margin-right: 8px;
  font-size: 0.8rem;
}

/* 回到顶部按钮样式 */
.back-to-top {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 50px;
  height: 50px;
  background-color: #f59e0b;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
  transition: all 0.3s ease;
  opacity: 0;
  visibility: hidden;
  transform: translateY(20px);
  z-index: 99;
}

.back-to-top.visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.back-to-top:hover {
  background-color: #2980b9;
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(52, 152, 219, 0.4);
}

.back-to-top i {
  font-size: 1.2rem;
  margin-bottom: 2px;
}

.back-to-top span {
  font-size: 0.7rem;
}

.content-section {
  display: none;
  min-width: 700px;
  margin: 0 300px 0px 0px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.content-section.active {
  display: block;
}

.section-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eaeaea;
}

.section-header h2 {
  font-size: 2.2rem;
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 15px;
  scroll-margin-top: 100px; /* 为锚点跳转提供偏移 */
}

.section-header h2 i {
  color: #f59e0b;
}

.section-header p {
  font-size: 1.1rem;
  color: #7f8c8d;
  line-height: 1.6;
}

.section-content {
  line-height: 1.7;
}

.section-content h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin: 25px 0 15px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #e0e0e0;
  padding-top: 20px; /* 为锚点跳转提供一些空间 */
  scroll-margin-top: 100px; /* 为锚点跳转提供偏移 */
}

.section-content p {
  margin-bottom: 15px;
  color: #555;
}

.section-content ul, .section-content ol {
  margin: 15px 0 20px 25px;
}

.section-content li {
  margin-bottom: 10px;
  color: #555;
}

.section-content code {
  background-color: var(--qm-bg-1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  color: #e74c3c;
}

.info-box {
  background-color: var(--qm-bg-1);
  border-left: 4px solid #f59e0b;
  padding: 20px;
  margin: 25px 0;
  border-radius: 0 6px 6px 0;
}

.info-box h4 {
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  scroll-margin-top: 100px; /* 为锚点跳转提供偏移 */
}

.step-list {
  counter-reset: step-counter;
  list-style-type: none;
  margin: 25px 0;
}

.step-list li {
  counter-increment: step-counter;
  margin-bottom: 25px;
  padding-left: 50px;
  position: relative;
}

.step-list li:before {
  content: counter(step-counter);
  background-color: #f59e0b;
  color: white;
  font-weight: bold;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  left: 0;
  top: 0;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin: 25px 0;
}

.feature-card {
  background-color: var(--qm-bg-1);
  border-radius: 8px;
  padding: 20px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.feature-card h4 {
  color: #2c3e50;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.feature-card i {
  color: #f59e0b;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .anchor-nav {
    right: 20px;
    width: 200px;
  }
  
  .anchor-nav.hidden {
    width: 50px;
    height: 50px;
  }
  
  .back-to-top {
    right: 20px;
    bottom: 20px;
  }
  
  .content-section {
    margin: 0 20px;
  }
}

@media (max-width: 992px) {
  .help-documentation {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    max-height: 60vh;
  }
  
  .nav-container {
    max-height: 40vh;
  }
  
  .anchor-nav {
    position: relative;
    top: 0;
    right: 0;
    width: 100%;
    margin-bottom: 20px;
  }
  
  .anchor-nav.hidden {
    width: 100%;
    height: auto;
  }
  
  .back-to-top {
    bottom: 20px;
    right: 20px;
  }
  
  .content {
    padding: 20px;
  }
  
  .content-section {
    min-width: auto;
    margin: 0;
  }
}

@media (max-width: 768px) {
  .content {
    padding: 20px;
  }
  
  .section-header h2 {
    font-size: 1.8rem;
  }
  
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .anchor-nav {
    position: relative;
    margin-bottom: 20px;
  }
  
  .back-to-top {
    width: 45px;
    height: 45px;
    bottom: 15px;
    right: 15px;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #bdc3c7;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #95a5a6;
}
</style>