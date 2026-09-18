/**
 * 帮助文档 · 内容汇总出口
 *
 * 目录名为 helpContent 而非 help：同目录下的 Help.vue 与之仅大小写不同，
 * 在大小写不敏感的文件系统上 `import ... from './help'` 会被解析成 Help.vue 自身，
 * 导致构建失败（CaseSensitivePathsPlugin）。
 *
 * 目录结构：
 *   menu.js          侧边栏菜单树（对齐后端权限表与前端真实路由 + element-plus 图标名）
 *   intro.js         快速开始
 *   overview.js      一级模块总览（menuContentMap）
 *   sub-basics.js    二级详情：项目管理 / 用户管理 / 环境管理
 *   sub-assets.js    二级详情：公共资源 / 测试资产
 *   sub-exec.js      二级详情：执行中心 / 报告管理 / 缺陷管理
 *   guide.js         平台指南：AI 助手 / 变量引用语法 / 常见问题
 */

import platformMenu from './menu'
import quickStartContent from './intro'
import menuContentMap from './overview'
import basicsChildren from './sub-basics'
import assetsChildren from './sub-assets'
import execChildren from './sub-exec'
import guideChildren from './guide'

/**
 * 二级菜单详情，key 规则为 `${一级模块 path}-${二级菜单 id}`
 */
export const subMenuContentMap = {
  ...basicsChildren,
  ...assetsChildren,
  ...execChildren,
  ...guideChildren
}

/**
 * 帮助内容完整性自检
 *
 * 旧版帮助文档对二级菜单渲染的是模板化套话（「XX是XX模块的一部分，主要用于管理XX相关的功能」），
 * 这类内容对使用者没有价值。改为数据驱动后，一旦漏写某个二级页面的详情，
 * 页面会回落到套话模板——这个自检就是为了让漏写能被立刻发现。
 *
 * @returns {{ok: boolean, missing: string[], orphan: string[], total: number}}
 */
export function validateHelpContent() {
  const missing = []
  const expectedKeys = []

  platformMenu.forEach(menuItem => {
    if (!menuContentMap[menuItem.name]) {
      missing.push(`[一级] ${menuItem.name}`)
    }
    ;(menuItem.children || []).forEach(child => {
      const key = `${menuItem.path}-${child.id}`
      expectedKeys.push(key)
      if (!subMenuContentMap[key]) {
        missing.push(`[二级] ${menuItem.name} > ${child.name} (${key})`)
      }
    })
  })

  const orphan = Object.keys(subMenuContentMap).filter(k => expectedKeys.indexOf(k) === -1)

  return {
    ok: missing.length === 0 && orphan.length === 0,
    missing,
    orphan,
    total: expectedKeys.length
  }
}

export { platformMenu, quickStartContent, menuContentMap }

export default {
  platformMenu,
  quickStartContent,
  menuContentMap,
  subMenuContentMap
}
