/**
 * 前端应用入口
 *
 * 依次挂载：Element Plus 组件库（含中文语言包和图标）、
 * Pinia 状态管理、Vue Router 路由。
 */

import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import './style.css'

// 创建 Vue 应用实例
const app = createApp(App)

// 注册 Pinia
app.use(createPinia())
// 注册路由
app.use(router)
// 注册 Element Plus，并指定简体中文语言包
app.use(ElementPlus, { locale: zhCn })

// 全量注册 Element Plus 图标为全局组件，菜单中可直接用名称引用
for (const [iconName, iconComponent] of Object.entries(ElementPlusIconsVue)) {
  app.component(iconName, iconComponent)
}

// 挂载到 index.html 中的 #app 节点
app.mount('#app')
