import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import api from './api/index.js'
import VxeUI from 'vxe-pc-ui'
import 'vxe-pc-ui/lib/style.css'
import VxeUITable from 'vxe-table'
import 'vxe-table/lib/style.css'
import VxeUIPluginRenderElement from '@vxe-ui/plugin-render-element'
import '@vxe-ui/plugin-render-element/dist/style.css'
import '@/assets/css/theme.css'
import '@/assets/css/global-form.css'
import '@/assets/css/global-table.css'
// const debounce = (fn, delay) => {
//   let timer = null;
//   return function () {
//     let context = this;
//     let args = arguments;
//     clearTimeout(timer);
//     timer = setTimeout(function () {
//       fn.apply(context, args);
//     }, delay);
//   }
// }

// const _ResizeObserver = window.ResizeObserver;
// window.ResizeObserver = class ResizeObserver extends _ResizeObserver {
//   constructor(callback) {
//     callback = debounce(callback, 16);
//     super(callback);
//   }
// }

// 主题初始化：默认深色科技风，可从 localStorage 持久化切换
// 默认浅色主题（人类视觉更友好，长时间办公不易疲劳）
const savedTheme = localStorage.getItem('qm-theme') || 'light'
document.documentElement.classList.toggle('dark', savedTheme === 'dark')

var app = createApp(App)

app.config.globalProperties.$api = api

app.use(ElementPlus, {
  locale: zhCn,
})

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// VxeUI.use(VxeUIPluginRenderElement)
// VxeUI.setConfig({
//   table: {
//     scrollX: {
//       enabled: true,
//       gt: 60
//     },
//     scrollY: {
//       enabled: true,
//       gt: 100
//     }
//   }
// })
app.use(store).use(router).use(VxeUI).use(VxeUITable).mount('#app')
