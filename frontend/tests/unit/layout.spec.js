import { describe, it, expect } from 'vitest'
import { readFileSync, readdirSync, statSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

/**
 * 布局 / 导航结构 · 源码契约回归测试
 *
 * 三条历史缺陷的回归防护：
 *  1) 左侧树「展不开 / 被遮挡」—— 根因是 .sub-menu(即 el-sub-menu 的 li) 被设了
 *     display:flex，导致标题与子菜单 ul 排成一行、子菜单被挤出侧栏。
 *  2) 页面框架丢失 —— /project/systemSetting、/project/tools 曾被注册成顶层路由，
 *     脱离 /project 的 children，进入后 Menu 布局不渲染。
 *  3) 默认主题 —— 必须是浅色（深色对人类视觉不友好）。
 */
const __dirname = dirname(fileURLToPath(import.meta.url))
const SRC = join(__dirname, '../../src')
const menuSource = readFileSync(join(SRC, 'components/Menu.vue'), 'utf-8')
const routerSource = readFileSync(join(SRC, 'router/index.js'), 'utf-8')
const mainSource = readFileSync(join(SRC, 'main.js'), 'utf-8')

/** 取出某个 CSS 规则块的花括号内容 */
function cssBlock(source, selector) {
  const i = source.indexOf(selector)
  if (i < 0) return null
  const open = source.indexOf('{', i)
  const close = source.indexOf('}', open)
  if (open < 0 || close < 0) return null
  return source.slice(open + 1, close)
}

describe('左侧树 · 布局回归防护', () => {
  it('.sub-menu 规则块不得设置 display:flex（否则子菜单被挤出侧栏）', () => {
    const block = cssBlock(menuSource, '\n\t.sub-menu {')
      || cssBlock(menuSource, '.sub-menu {')
    expect(block).not.toBeNull()
    expect(block).not.toMatch(/display\s*:\s*flex/)
  })

  it('el-menu 不得使用 horizontal 模式（应为左侧垂直导航）', () => {
    expect(menuSource).not.toMatch(/mode\s*=\s*["']horizontal["']/)
  })

  it('el-menu 应绑定 collapse 以支持侧栏收起', () => {
    expect(menuSource).toMatch(/:collapse\s*=\s*["']?isCollapse/)
  })

  it('应存在垂直侧栏外壳 qm-sidebar / qm-topbar', () => {
    expect(menuSource).toContain('class="qm-sidebar"')
    expect(menuSource).toContain('qm-topbar')
  })

  it('收起状态应同步到 html[data-sidebar]，供内容区联动', () => {
    expect(menuSource).toContain("setAttribute('data-sidebar'")
  })
})

describe('路由结构 · 框架丢失回归防护', () => {
  function pathIndentMap() {
    const map = new Map()
    routerSource.split('\n').forEach((line) => {
      const m = line.match(/^(\s*)path:\s*'([^']+)'/)
      if (m) map.set(m[2], m[1].length)
    })
    return map
  }

  it('/project/systemSetting 必须挂在 /project 之下（缩进更深）', () => {
    const map = pathIndentMap()
    expect(map.has('/project')).toBe(true)
    expect(map.has('/project/systemSetting')).toBe(true)
    expect(map.get('/project/systemSetting')).toBeGreaterThan(map.get('/project'))
  })

  it('/project/tools 必须挂在 /project 之下（缩进更深）', () => {
    const map = pathIndentMap()
    expect(map.has('/project/tools')).toBe(true)
    expect(map.get('/project/tools')).toBeGreaterThan(map.get('/project'))
  })

  it('不得存在 index="0" 这类相对菜单索引（会跳转到 /project/0 空白页）', () => {
    expect(menuSource).not.toMatch(/index\s*=\s*"0"/)
  })

  it('品牌 Logo 应指向绝对路由 /myProjects', () => {
    expect(menuSource).toMatch(/index\s*=\s*"\/myProjects"/)
  })
})

describe('用户信息持久化 · 刷新后误判无权限回归防护', () => {
  const storeSource = readFileSync(join(SRC, 'store/index.js'), 'utf-8')

  it('store 初始 userInfo 应从 localStorage.qm-userInfo 恢复', () => {
    expect(storeSource).toMatch(/userInfo:\s*\(\(\)\s*=>\s*\{/)
    expect(storeSource).toContain("localStorage.getItem('qm-userInfo')")
  })

  it('saveUserInfo 应同时写入 localStorage', () => {
    const block = storeSource.slice(storeSource.indexOf('saveUserInfo(state'))
    expect(block.slice(0, 260)).toContain("localStorage.setItem('qm-userInfo'")
  })

  it('clearUserInfo 应清除 localStorage', () => {
    const block = storeSource.slice(storeSource.indexOf('clearUserInfo(state'))
    expect(block.slice(0, 220)).toContain("localStorage.removeItem('qm-userInfo')")
  })
})

describe('列表筛选 · module_list 空值崩溃回归防护', () => {
  it('所有 xxxSearch.module_list.join 必须带空值兜底', () => {
    const offenders = []
    for (const root of ['components', 'views']) {
      const dir = join(SRC, root)
      const walk = (d) => {
        for (const f of readdirSync(d)) {
          const p = join(d, f)
          if (statSync(p).isDirectory()) walk(p)
          else if (f.endsWith('.vue')) {
            const txt = readFileSync(p, 'utf-8')
            txt.split('\n').forEach((line, i) => {
              if (/\.module_list\.join\(/.test(line) && !/\|\|/.test(line)) {
                offenders.push(p + ':' + (i + 1))
              }
            })
          }
        }
      }
      walk(dir)
    }
    expect(offenders).toEqual([])
  })

  it('StepList 的 stepSearch 必须初始化 module_list', () => {
    const src = readFileSync(join(SRC, 'components/StepList.vue'), 'utf-8')
    const i = src.indexOf('stepSearch:{')
    expect(i).toBeGreaterThan(0)
    expect(src.slice(i, i + 300)).toContain('module_list: []')
  })
})

describe('默认主题 · 视觉友好回归防护', () => {
  it('main.js 未保存主题时应默认 light', () => {
    expect(mainSource).toMatch(/getItem\('qm-theme'\)\s*\|\|\s*'light'/)
  })

  it('store 中主题默认值应为 light', () => {
    const store = readFileSync(join(SRC, 'store/index.js'), 'utf-8')
    expect(store).toMatch(/theme:\s*localStorage\.getItem\('qm-theme'\)\s*\|\|\s*'light'/)
  })
})
