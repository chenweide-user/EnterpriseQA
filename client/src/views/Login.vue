<template>
  <!-- 登录页：全屏渐变背景 + 居中登录卡片 -->
  <div class="login-container">
    <el-card class="login-card" shadow="always">
      <!-- 标题区 -->
      <div class="login-header">
        <el-icon :size="34" color="#409eff"><Cpu /></el-icon>
        <h2 class="login-title">企业知识库问答系统</h2>
        <p class="login-subtitle">RAG 智能问答平台</p>
      </div>

      <!-- 登录表单：回车即提交 -->
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @keyup.enter="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <!-- 登录按钮：请求中显示加载状态 -->
        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 测试账号提示 -->
      <div class="login-tip">
        管理员：admin / 123456<br />
        普通用户：zhangsan / 123456
      </div>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 登录页面组件
 *
 * 校验表单后调用 Pinia 中的登录动作，
 * 成功后跳转到系统首页（路由守卫会按角色二次定向）。
 */

import { Lock, User } from '@element-plus/icons-vue'
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()

// 表单引用，用于调用校验方法
const formRef = ref()
// 登录请求加载状态
const loading = ref(false)

// 登录表单数据
const form = reactive({
  username: '',
  password: '',
})

// 表单校验规则
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

/**
 * 处理登录：先校验表单，再请求后端获取令牌
 */
async function handleLogin() {
  // 表单校验不通过则中断
  await formRef.value.validate()

  loading.value = true
  try {
    await userStore.login({ ...form })
    // 拉取用户信息后再跳转，守卫中即可识别角色
    await userStore.fetchUserInfo()
    // 管理员进入数据概览，普通用户进入智能问答
    router.push(userStore.isAdmin ? '/dashboard' : '/chat')
  } finally {
    // 无论成功失败都关闭加载状态
    loading.value = false
  }
}
</script>

<style scoped>
/* 全屏渐变背景，居中显示卡片 */
.login-container {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f2d3d 0%, #409eff 100%);
}

.login-card {
  width: 400px;
  border-radius: 10px;
}

/* 标题区域 */
.login-header {
  text-align: center;
  margin-bottom: 20px;
}

.login-title {
  margin-top: 10px;
  font-size: 22px;
  color: #303133;
}

.login-subtitle {
  margin-top: 6px;
  font-size: 13px;
  color: #909399;
}

/* 登录按钮撑满整行 */
.login-button {
  width: 100%;
}

/* 测试账号提示 */
.login-tip {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px dashed #ebeef5;
  font-size: 12px;
  color: #909399;
  line-height: 1.8;
  text-align: center;
}
</style>
