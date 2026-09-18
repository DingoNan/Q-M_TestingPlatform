import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createStore } from 'vuex'

/**
 * Menu.vue 主题切换按钮 · 组件级单元测试
 * 覆盖：按钮渲染、图标随主题切换（Sunny/Moon）、点击触发 toggleTheme
 *
 * 策略：Menu.vue 依赖重（api/router/element-plus/EnvManagement），
 * 用「最小复刻 + 真实模板片段」方式提取主题按钮的模板与逻辑做组件测试，
 * 并用 stub 验证真实 Menu.vue 的模板源码包含关键绑定（防模板回退）。
 */
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const menuSource = readFileSync(join(__dirname, '../../src/components/Menu.vue'), 'utf-8')

// 与 Menu.vue 一致的最小主题按钮组件（提取自其 toolbar 区块）
const ThemeButton = {
  template: `
    <div class="toolbar" data-test="toolbar">
      <div class="toolbar-item" data-test="theme-btn" @click="toggleTheme">
        <el-tooltip :content="theme === 'dark' ? '切换浅色' : '切换深色'" placement="bottom">
          <el-icon class="toolbar-icon">
            <Sunny v-if="theme === 'dark'" />
            <Moon v-else />
          </el-icon>
        </el-tooltip>
      </div>
    </div>
  `,
  computed: {
    theme() { return this.$store.state.theme },
  },
  methods: {
    toggleTheme() { this.$store.commit('toggleTheme') },
  },
}

const globalCfg = (store) => ({
  global: {
    plugins: [store],
    stubs: {
      'el-tooltip': { template: '<span><slot /></span>' },
      'el-icon': { template: '<i><slot /></i>' },
    },
    components: { Sunny: { template: '<svg data-icon="sunny" />' }, Moon: { template: '<svg data-icon="moon" />' } },
  },
})

function makeStore(initialTheme) {
  return createStore({
    state: { theme: initialTheme },
    mutations: {
      setTheme(s, t) { s.theme = t },
      toggleTheme(s) { s.theme = s.theme === 'dark' ? 'light' : 'dark' },
    },
  })
}

describe('Menu 组件 · 主题切换按钮', () => {
  beforeEach(() => {
    document.documentElement.className = ''
  })

  it('深色主题下应渲染 Sunny 图标（提示切换浅色）', () => {
    const wrapper = mount(ThemeButton, globalCfg(makeStore('dark')))
    expect(wrapper.find('[data-icon="sunny"]').exists()).toBe(true)
    expect(wrapper.find('[data-icon="moon"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('浅色主题下应渲染 Moon 图标', () => {
    const wrapper = mount(ThemeButton, globalCfg(makeStore('light')))
    expect(wrapper.find('[data-icon="moon"]').exists()).toBe(true)
    expect(wrapper.find('[data-icon="sunny"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('点击按钮应触发 toggleTheme（dark→light）', async () => {
    const store = makeStore('dark')
    const spy = vi.spyOn(store, 'commit')
    const wrapper = mount(ThemeButton, globalCfg(store))
    await wrapper.find('[data-test="theme-btn"]').trigger('click')
    expect(spy).toHaveBeenCalledWith('toggleTheme')
    expect(store.state.theme).toBe('light')
    wrapper.unmount()
  })

  it('连续点击两次应回到原主题', async () => {
    const store = makeStore('dark')
    const wrapper = mount(ThemeButton, globalCfg(store))
    const btn = wrapper.find('[data-test="theme-btn"]')
    await btn.trigger('click')
    await btn.trigger('click')
    expect(store.state.theme).toBe('dark')
    wrapper.unmount()
  })

  // ---- 真实源码契约测试：防止后续重构破坏主题按钮 ----
  it('真实 Menu.vue 源码应包含 toggleTheme 绑定', () => {
    expect(menuSource).toContain('@click="toggleTheme"')
  })

  it('真实 Menu.vue 源码应包含 Sunny/Moon 双图标与主题提示', () => {
    expect(menuSource).toContain('Sunny v-if="theme === \'dark\'"')
    expect(menuSource).toContain('<Moon v-else />')
    expect(menuSource).toContain("'切换浅色' : '切换深色'")
  })

  it('真实 Menu.vue 应通过 mapMutations 引入 toggleTheme', () => {
    expect(menuSource).toContain("mapMutations(['setPathPermission', 'toggleTheme'])")
  })
})
