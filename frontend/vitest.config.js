import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// Q·M 测试平台 · 前端单元测试配置（vitest + jsdom + @vue/test-utils）
// 独立配置，不侵入 vue-cli/webpack 构建链路
export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['tests/unit/**/*.spec.js'],
    coverage: {
      provider: 'v8',
      reportsDirectory: './tests/coverage',
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
