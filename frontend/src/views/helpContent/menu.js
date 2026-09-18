/**
 * 帮助文档 · 侧边栏菜单树
 *
 * 设计说明：
 * 1. 本菜单与后端 `backend/create_super_user.py::permissions`（权限表 tb_permission）
 *    及 `frontend/src/router/index.js` 的真实路由保持一一对应，避免帮助文档与平台实际
 *    功能脱节（旧版帮助文档写的是 /suite/list、/suite/task，而真实路由是 /exec/suite、
 *    /exec/task，数据库类型也写错了）。
 * 2. `icon` 统一使用 element-plus 图标组件名（如 Setting / Reading / TrendCharts）。
 *    平台主工程在 main.js 中已 `for (const [key, component] of Object.entries(ElementPlusIconsVue)) app.component(key, component)`
 *    全局注册，因此帮助页可直接用 <component :is="icon" /> 渲染。
 *    历史实现用的是 `fas fa-*`（Font Awesome），但整个工程并未安装 FA，63 个图标全部渲染为空，
 *    本次一并修正。
 * 3. 每个二级菜单都带显式 `id`，不再用 `path.split('/').pop()` 推导。
 *    原因：审计日志的真实路径是 /user/auditLog，若按路径末段推导会得到 'user-auditLog',
 *    与「用户管理」模块的路径前缀 'user' 冲突，导致父菜单高亮判断出错。
 *
 * 4. 「平台指南」是帮助文档自有的说明性章节（AI 助手 / 变量引用语法 / 常见问题），
 *    不对应平台里的真实菜单页面，其 `path` 仅用于生成章节 key（如 'guide-ai'）。
 *    帮助页的导航只切换内容、不跳转路由，因此不会产生无效链接。
 */

export const platformMenu = [
  {
    name: '项目管理',
    level: 1,
    path: 'project',
    icon: 'FolderOpened',
    parent: 0,
    desc: '创建项目、维护项目成员、配置项目级 AI 与消息推送',
    children: [
      { name: '我的项目', level: 2, id: 'myProjects', path: '/myProjects', icon: 'HomeFilled', parent: 1 },
      { name: '项目列表', level: 2, id: 'projectList', path: '/project/list', icon: 'Files', parent: 1 },
      { name: '项目申请', level: 2, id: 'projectAppeal', path: '/project/appeal', icon: 'DocumentAdd', parent: 1 },
      { name: '项目设置', level: 2, id: 'systemSetting', path: '/project/systemSetting', icon: 'Setting', parent: 1 },
      { name: '测试工具箱', level: 2, id: 'tools', path: '/project/tools', icon: 'Suitcase', parent: 1 },
      { name: '审计日志', level: 2, id: 'auditLog', path: '/user/auditLog', icon: 'Document', parent: 1 }
    ]
  },
  {
    name: '用户管理',
    level: 1,
    path: 'user',
    icon: 'UserFilled',
    parent: 0,
    desc: '管理平台用户、角色与细粒度权限点',
    children: [
      { name: '用户列表', level: 2, id: 'userList', path: '/user/list', icon: 'User', parent: 1 },
      { name: '角色列表', level: 2, id: 'roleList', path: '/user/role', icon: 'Avatar', parent: 1 },
      { name: '权限列表', level: 2, id: 'permissionList', path: '/user/permission', icon: 'Key', parent: 1 }
    ]
  },
  {
    name: '环境管理',
    level: 1,
    path: 'env',
    icon: 'Monitor',
    parent: 0,
    desc: '配置测试环境、后端服务、前端平台与数据库连接',
    children: [
      { name: '环境配置', level: 2, id: 'envConfig', path: '/env/env', icon: 'Share', parent: 1 },
      { name: '服务配置', level: 2, id: 'serviceConfig', path: '/env/service', icon: 'SwitchFilled', parent: 1 },
      { name: '产品配置', level: 2, id: 'plantConfig', path: '/env/plant', icon: 'Box', parent: 1 },
      { name: '数据库配置', level: 2, id: 'dbConfig', path: '/env/db', icon: 'Coin', parent: 1 }
    ]
  },
  {
    name: '公共资源',
    level: 1,
    path: 'common',
    icon: 'Reading',
    parent: 0,
    desc: '文件、元素、常量、用户函数与可复用步骤',
    children: [
      { name: '文件管理', level: 2, id: 'file', path: '/common/file', icon: 'Files', parent: 1 },
      { name: '元素配置', level: 2, id: 'element', path: '/common/element', icon: 'Grape', parent: 1 },
      { name: '常量配置', level: 2, id: 'enumConfig', path: '/common/enum', icon: 'TakeawayBox', parent: 1 },
      { name: '用户函数', level: 2, id: 'python', path: '/common/python', icon: 'EditPen', parent: 1 },
      { name: '步骤管理', level: 2, id: 'step', path: '/common/step', icon: 'Connection', parent: 1 }
    ]
  },
  {
    name: '测试资产',
    level: 1,
    path: 'case',
    icon: 'SetUp',
    parent: 0,
    desc: '接口文档、功能用例、脚本用例、标签与向量智仓',
    children: [
      { name: '向量智仓', level: 2, id: 'knowledgeBase', path: '/resource/knowledgeBase', icon: 'Collection', parent: 1 },
      { name: '标签管理', level: 2, id: 'tag', path: '/resource/tag', icon: 'CollectionTag', parent: 1 },
      { name: '接口管理', level: 2, id: 'api', path: '/resource/api', icon: 'Link', parent: 1 },
      { name: '功能用例', level: 2, id: 'funcCase', path: '/resource/funcCase', icon: 'Briefcase', parent: 1 },
      { name: '脚本用例', level: 2, id: 'scriptCase', path: '/resource/scriptCase', icon: 'Coin', parent: 1 }
    ]
  },
  {
    name: '执行中心',
    level: 1,
    path: 'suite',
    icon: 'Film',
    parent: 0,
    desc: '测试计划、套件编排与定时任务',
    children: [
      { name: '测试计划', level: 2, id: 'plan', path: '/exec/plan', icon: 'Filter', parent: 1 },
      { name: '套件管理', level: 2, id: 'suite', path: '/exec/suite', icon: 'Orange', parent: 1 },
      { name: '定时任务', level: 2, id: 'task', path: '/exec/task', icon: 'AlarmClock', parent: 1 }
    ]
  },
  {
    name: '报告管理',
    level: 1,
    path: 'report',
    icon: 'Histogram',
    parent: 0,
    desc: '执行日志、功能报告与性能压测报告',
    children: [
      { name: '日志列表', level: 2, id: 'log', path: '/report/log', icon: 'VideoCameraFilled', parent: 1 },
      { name: '功能报告', level: 2, id: 'reportList', path: '/report/list', icon: 'PieChart', parent: 1 },
      { name: '性能报告', level: 2, id: 'locust', path: '/report/locust', icon: 'TrendCharts', parent: 1 }
    ]
  },
  {
    name: '缺陷管理',
    level: 1,
    path: 'defect',
    icon: 'DataLine',
    parent: 0,
    desc: '缺陷登记、流转与评论',
    children: [
      { name: '缺陷列表', level: 2, id: 'defectList', path: '/defect/list', icon: 'List', parent: 1 }
    ]
  },
  {
    name: '平台指南',
    level: 1,
    path: 'guide',
    icon: 'Guide',
    parent: 0,
    desc: 'AI 助手、变量引用语法与常见问题排查',
    children: [
      { name: 'AI 助手', level: 2, id: 'ai', path: '/guide/ai', icon: 'MagicStick', parent: 1 },
      { name: '变量引用语法', level: 2, id: 'vars', path: '/guide/vars', icon: 'PriceTag', parent: 1 },
      { name: '常见问题与避坑', level: 2, id: 'faq', path: '/guide/faq', icon: 'WarningFilled', parent: 1 }
    ]
  }
]

export default platformMenu
