/**
 * 路由配置
 *
 * 定义登录页和主框架下的全部业务路由，
 * 并通过全局前置守卫实现：未登录拦截、用户信息加载、角色权限控制。
 */

import { createRouter, createWebHistory } from 'vue-router'

import { useUserStore } from '../stores/user'
import { getToken } from '../utils/auth'

// 路由表
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '数据概览', icon: 'Odometer', roles: ['admin'] },
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import('../views/Knowledge.vue'),
        meta: { title: '知识库管理', icon: 'Collection', roles: ['admin'] },
      },
      {
        path: 'document',
        name: 'Document',
        component: () => import('../views/Document.vue'),
        meta: { title: '文档管理', icon: 'Document', roles: ['admin'] },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('../views/UserManage.vue'),
        meta: { title: '用户管理', icon: 'User', roles: ['admin'] },
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('../views/Chat.vue'),
        meta: { title: '智能问答', icon: 'ChatDotRound', roles: ['admin', 'user'] },
      },
      {
        path: 'history',
        name: 'History',
        component: () => import('../views/History.vue'),
        meta: { title: '对话历史', icon: 'Timer', roles: ['admin', 'user'] },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/Profile.vue'),
        meta: { title: '用户主页', icon: 'UserFilled', roles: ['admin', 'user'] },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局前置守卫
router.beforeEach(async (to) => {
  const token = getToken()

  // 登录页直接放行
  if (to.path === '/login') {
    return true
  }

  // 未登录一律跳转登录页
  if (!token) {
    return '/login'
  }

  const userStore = useUserStore()

  // 刷新页面后用户信息可能丢失，先拉取一次
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo()
  }

  // 角色不匹配：普通用户访问管理员页面时，重定向到智能问答
  const roles = to.meta.roles
  if (roles && !roles.includes(userStore.userInfo.role)) {
    return '/chat'
  }

  return true
})

export default router
