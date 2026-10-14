import { describe, it, expect } from 'vitest'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import {
  platformMenu,
  quickStartContent,
  menuContentMap,
  subMenuContentMap,
  validateHelpContent
} from '@/views/helpContent'

const __dirname = dirname(fileURLToPath(import.meta.url))

/**
 * 帮助文档内容装配自检
 *
 * 为什么值得单测：
 * 1. 二级页面漏写内容时页面会回落到模板化套话，用户看到的是没有信息量的占位文本；
 *    validateHelpContent() 已内建该检查，这里把它固化成断言，防止回归。
 * 2. 内容是模板字符串，正文里出现未转义的 `${...}` 会被 JS 当插值解析，
 *    历史版本正因此丢过整段变量语法示例（intro.js 头部有警示注释）。
 * 3. 2026-10-14 新增「Web 自动化录制」章节与录制插件下载入口，这里锁定关键锚点存在，
 *    防止后续改动把章节误删后没人发现。
 */
describe('帮助文档内容装配', () => {
  it('所有一级/二级页面都有详情内容，且没有孤儿 key', () => {
    const r = validateHelpContent()
    expect(r.missing, `缺失内容: ${r.missing.join(', ')}`).toEqual([])
    expect(r.orphan, `孤儿 key: ${r.orphan.join(', ')}`).toEqual([])
    expect(r.ok).toBe(true)
    expect(r.total).toBeGreaterThan(30)
  })

  it('「Web 自动化录制」章节已挂到平台指南下', () => {
    const guide = platformMenu.find(m => m.path === 'guide')
    expect(guide).toBeTruthy()
    const rec = (guide.children || []).find(c => c.id === 'recording')
    expect(rec, '菜单树缺少 Web 自动化录制').toBeTruthy()
    expect(rec.name).toBe('Web 自动化录制')

    const content = subMenuContentMap['guide-recording']
    expect(content, '缺少 guide-recording 内容').toBeTruthy()
    const anchorIds = (content.anchors || []).map(a => a.id)
    expect(anchorIds).toContain('sub-rec-entry')   // 三个入口分清
    expect(anchorIds).toContain('sub-rec-install') // 插件安装（含下载位置）
    expect(anchorIds).toContain('sub-rec-review')  // 审阅与落库
  })

  it('录制章节讲清了三个入口与插件下载位置', () => {
    const html = subMenuContentMap['guide-recording'].content
    expect(html).toContain('录制履历')
    expect(html).toContain('导入录制')
    expect(html).toContain('Q·M 录制器')
    // 下载位置必须写清楚，否则用户仍然找不到插件
    expect(html).toContain('qm-recorder-extension-v0.1.0.zip')
    expect(html).toContain('chrome://extensions')
  })

  it('脚本用例章节包含录制与标签就地新增说明', () => {
    const html = subMenuContentMap['case-scriptCase'].content
    const anchorIds = (subMenuContentMap['case-scriptCase'].anchors || []).map(a => a.id)
    expect(anchorIds).toContain('sub-script-rec')
    expect(anchorIds).toContain('sub-script-tag')
    expect(html).toContain('Q·M 录制器')
    expect(html).toContain('就地新建')
  })

  it('元素配置章节说明了 AI 生成的登录态两种配法', () => {
    const html = subMenuContentMap['common-element'].content
    expect(html).toContain('本次登录态')
    expect(html).toContain('全局会话配置')
  })

  it('常见问题不少于 21 条，且覆盖本轮新问题', () => {
    const html = subMenuContentMap['guide-faq'].content
    const rows = html.match(/<tr><td>\d+<\/td>/g) || []
    expect(rows.length).toBeGreaterThanOrEqual(21)
    expect(html).toContain('提示条里直接下载') // FAQ 21：插件在哪下载
  })

  it('快速开始提到录制插件入口', () => {
    expect(quickStartContent.content).toContain('Q·M 录制器')
  })

  it('内容模板字符串中不存在 ${...} 表达式（历史踩坑：整段示例被 JS 吃掉）', () => {
    // 精确做法：解析 AST，检查每个模板字符串是否带表达式。
    // 不能改成「检查渲染后的文本里有没有 ${」——文档本来就要展示变量语法，
    // 合法写法 `\${变量名}` 渲染后正是 `${变量名}`，那样会永远报错。
    const { parse } = require('@babel/parser')
    const { readFileSync } = require('node:fs')
    const files = [
      'intro.js', 'overview.js', 'sub-basics.js',
      'sub-assets.js', 'sub-exec.js', 'guide.js', 'menu.js'
    ]
    const base = join(__dirname, '../../src/views/helpContent')
    for (const f of files) {
      const ast = parse(readFileSync(join(base, f), 'utf8'), {
        sourceType: 'module', plugins: []
      })
      const bad = []
      // 浅遍历即可：本目录全是字面量导出，没有动态拼接场景
      JSON.stringify(ast, (k, v) => {
        if (v && v.type === 'TemplateLiteral' && v.expressions && v.expressions.length) {
          bad.push(`第 ${v.loc && v.loc.start.line} 行模板字符串含 ${v.expressions.length} 个表达式`)
        }
        return v
      })
      expect(bad, `${f}: ${bad.join('; ')}`).toEqual([])
    }
  })
})
