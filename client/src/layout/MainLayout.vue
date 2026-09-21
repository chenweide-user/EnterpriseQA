<template>
  <!-- 主布局：左侧菜单 + 顶部栏 + 右侧内容区 -->
  <el-container class="layout-container">
    <!-- 左侧侧边栏 -->
    <el-aside width="220px" class="layout-aside">
      <!-- 系统标题 -->
      <div class="logo-area">
        <el-icon :size="22"><Cpu /></el-icon>
        <span class="logo-text">企业知识库问答</span>
      </div>

      <!-- 导航菜单：根据路由表和用户角色动态渲染 -->
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#1d2b3a"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item
          v-for="item in menuList"
          :key="item.path"
          :index="item.path"
        >
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧主体 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="layout-header">
        <!-- 当前模块名称 -->
        <div class="header-title">{{ currentTitle }}</div>

        <!-- 右上角用户信息下拉（点击触发，兼顾触屏设备） -->
        <el-dropdown trigger="click" @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="30" class="user-avatar">
              {{ avatarText }}
            </el-avatar>
            <span class="user-name">
              {{ userStore.userInfo?.real_name || userStore.userInfo?.username }}
            </span>
            <el-tag
              :type="userStore.isAdmin ? 'danger' : 'success'"
              size="small"
              effect="plain"
            >
              {{ userStore.isAdmin ? '管理员' : '普通用户' }}
            </el-tag>
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">用户主页</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <!-- 内容区：子路由渲染位置 -->
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
/**
 * 主布局组件
 *
 * 负责整体框架的渲染：侧边菜单按角色过滤，
 * 顶部下拉支持进入用户主页和退出登录。
 */

import { ElMessageBox } from 'element-plus'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 当前激活的菜单（高亮用）
const activeMenu = computed(() => route.path)

// 当前页面标题
const currentTitle = computed(() => route.meta.title || '')

// 头像文字：取真实姓名/用户名的第一个字符
const avatarText = computed(() => {
  const name = userStore.userInfo?.real_name || userStore.userInfo?.username || ''
  return name.charAt(0).toUpperCase()
})

/**
 * 根据路由表生成当前角色可见的菜单列表
 * 路由结构：根路由 / 的 children 即菜单项
 */
const menuList = computed(() => {
  // 找到 path 为 '/' 的主框架路由
  const rootRoute = router.options.routes.find((r) => r.path === '/')
  if (!rootRoute?.children) return []

  const role = userStore.userInfo?.role
  return rootRoute.children
    .filter((child) => {
      // meta.roles 中包含当前角色才显示
      return child.meta?.roles?.includes(role)
    })
    .map((child) => ({
      path: `/${child.path}`,
      title: child.meta.title,
      icon: child.meta.icon,
    }))
})

/**
 * 处理顶部下拉菜单点击
 * @param {string} command 下拉项命令标识
 */
function handleCommand(command) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'logout') {
    // 二次确认后退出
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
      .then(() => {
        userStore.logout()
        router.push('/login')
      })
      .catch(() => {})
  }
}
</script>

<style scoped>
/* 整体撑满高度 */
.layout-container {
  height: 100%;
}

/* 侧边栏样式 */
.layout-aside {
  background-color: #1d2b3a;
  overflow-x: hidden;
}

/* Logo 区域 */
.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #fff;
  background-color: #15212e;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

/* 去掉菜单右侧边框 */
.el-menu {
  border-right: none;
}

/* 顶部栏样式 */
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  border-bottom: 1px solid #ebeef5;
}

.header-title {
  font-size: 17px;
  font-weight: 600;
}

/* 用户信息区域 */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  outline: none;
}

.user-avatar {
  background-color: #409eff;
}

.user-name {
  font-size: 14px;
}

/* 内容区 */
.layout-main {
  background-color: #f5f7fa;
  padding: 18px;
}
</style>
