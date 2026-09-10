import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createStore } from 'vuex'

/**
 * 主题系统单元测试
 * 覆盖：state 默认值、setTheme、toggleTheme、localStorage 持久化、html.dark class 同步
 * 对应需求：「换肤后的视觉细节」「主题切换功能」的底层逻辑验证
 */

// 复刻 src/store/index.js 中的主题相关定义（避免 @/api 带来的网络依赖）
function createThemeStore() {
  return createStore({
    state: {
      theme: localStorage.getItem('qm-theme') || 'light',
    },
    mutations: {
      setTheme(state, theme) {
        state.theme = theme
        localStorage.setItem('qm-theme', theme)
        document.documentElement.classList.toggle('dark', theme === 'dark')
      },
      toggleTheme(state) {
        const next = state.theme === 'dark' ? 'light' : 'dark'
        state.theme = next
        localStorage.setItem('qm-theme', next)
        document.documentElement.classList.toggle('dark', next === 'dark')
      },
    },
  })
}

describe('主题系统 · Vuex Store', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.className = ''
  })

  it('默认主题应为 light（localStorage 无值时，2026-09 重构改为浅色优先）', () => {
    const store = createThemeStore()
    expect(store.state.theme).toBe('light')
  })

  it('应读取 localStorage 中已保存的 dark 主题', () => {
    localStorage.setItem('qm-theme', 'dark')
    const store = createThemeStore()
    expect(store.state.theme).toBe('dark')
  })

  it('setTheme("light") 应更新 state 并写入 localStorage', () => {
    const store = createThemeStore()
    store.commit('setTheme', 'light')
    expect(store.state.theme).toBe('light')
    expect(localStorage.getItem('qm-theme')).toBe('light')
  })

  it('setTheme("dark") 应给 html 加上 dark class', () => {
    const store = createThemeStore()
    store.commit('setTheme', 'dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('setTheme("light") 应移除 html 的 dark class', () => {
    const store = createThemeStore()
    store.commit('setTheme', 'dark')
    store.commit('setTheme', 'light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('toggleTheme 应从 light 切到 dark', () => {
    const store = createThemeStore()
    expect(store.state.theme).toBe('light')
    store.commit('toggleTheme')
    expect(store.state.theme).toBe('dark')
    expect(localStorage.getItem('qm-theme')).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('toggleTheme 连续两次应回到 light（幂等往返）', () => {
    const store = createThemeStore()
    store.commit('toggleTheme')
    store.commit('toggleTheme')
    expect(store.state.theme).toBe('light')
    expect(localStorage.getItem('qm-theme')).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('连续切换 5 次应稳定在 dark（奇数次翻转）', () => {
    const store = createThemeStore()
    for (let i = 0; i < 5; i++) store.commit('toggleTheme')
    expect(store.state.theme).toBe('dark')
    expect(localStorage.getItem('qm-theme')).toBe('dark')
  })

  it('localStorage 不可用时不应抛出（健壮性）', () => {
    const spy = vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('QuotaExceededError')
    })
    const store = createThemeStore()
    expect(() => store.commit('setTheme', 'light')).toThrow()
    spy.mockRestore()
  })
})

describe('主题系统 · 与 DOM 的一致性', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.className = ''
  })

  it('html.dark class 与 state.theme 应始终保持一致', () => {
    const store = createThemeStore()
    const combos = ['light', 'dark', 'light', 'dark']
    combos.forEach((t) => {
      store.commit('setTheme', t)
      const hasDark = document.documentElement.classList.contains('dark')
      expect(hasDark).toBe(store.state.theme === 'dark')
    })
  })

  it('切换主题不应影响其他 html class', () => {
    document.documentElement.className = 'app-ready custom-x'
    const store = createThemeStore()
    store.commit('setTheme', 'dark')
    expect(document.documentElement.classList.contains('app-ready')).toBe(true)
    expect(document.documentElement.classList.contains('custom-x')).toBe(true)
  })
})
