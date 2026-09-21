<template>
  <!-- 用户主页：个人信息维护 + 修改密码 -->
  <el-row :gutter="18">
    <!-- 左侧：个人信息卡片 -->
    <el-col :span="14">
      <el-card shadow="never">
        <template #header>
          <span class="card-title">个人信息</span>
        </template>

        <el-form
          ref="infoFormRef"
          :model="infoForm"
          :rules="infoRules"
          label-width="90px"
        >
          <!-- 头像与角色展示 -->
          <el-form-item label="用户头像">
            <el-avatar :size="56" class="profile-avatar">
              {{ avatarText }}
            </el-avatar>
            <el-tag
              :type="userStore.isAdmin ? 'danger' : 'success'"
              style="margin-left: 14px"
            >
              {{ userStore.isAdmin ? '管理员' : '普通用户' }}
            </el-tag>
          </el-form-item>

          <!-- 用户名不可修改 -->
          <el-form-item label="用户名">
            <el-input v-model="infoForm.username" disabled />
          </el-form-item>

          <el-form-item label="真实姓名" prop="real_name">
            <el-input v-model="infoForm.real_name" placeholder="请输入真实姓名" />
          </el-form-item>

          <el-form-item label="邮箱" prop="email">
            <el-input v-model="infoForm.email" placeholder="请输入邮箱" />
          </el-form-item>

          <el-form-item label="手机号" prop="phone">
            <el-input v-model="infoForm.phone" placeholder="请输入手机号" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="savingInfo" @click="handleSaveInfo">
              保存修改
            </el-button>
            <el-button @click="resetInfo">重 置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>

    <!-- 右侧：修改密码卡片 -->
    <el-col :span="10">
      <el-card shadow="never">
        <template #header>
          <span class="card-title">修改密码</span>
        </template>

        <el-form
          ref="pwdFormRef"
          :model="pwdForm"
          :rules="pwdRules"
          label-width="90px"
        >
          <el-form-item label="原密码" prop="old_password">
            <el-input
              v-model="pwdForm.old_password"
              type="password"
              show-password
              placeholder="请输入原密码"
            />
          </el-form-item>

          <el-form-item label="新密码" prop="new_password">
            <el-input
              v-model="pwdForm.new_password"
              type="password"
              show-password
              placeholder="至少6位"
            />
          </el-form-item>

          <el-form-item label="确认密码" prop="confirm_password">
            <el-input
              v-model="pwdForm.confirm_password"
              type="password"
              show-password
              placeholder="请再次输入新密码"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" :loading="savingPwd" @click="handleSavePwd">
              修改密码
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
/**
 * 用户主页页面组件
 *
 * 普通用户和管理员均可在此维护本人基础信息、修改登录密码。
 */

import { ElMessage } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import { updatePassword, updateProfile } from '../api/user'
import { useUserStore } from '../stores/user'

const userStore = useUserStore()

// 个人信息表单引用与状态
const infoFormRef = ref()
const savingInfo = ref(false)

// 个人信息表单数据
const infoForm = reactive({
  username: '',
  real_name: '',
  email: '',
  phone: '',
})

// 邮箱与手机号的简单校验规则
const infoRules = {
  email: [{ type: 'email', message: '邮箱格式不正确', trigger: 'blur' }],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
}

// 修改密码表单
const pwdFormRef = ref()
const savingPwd = ref(false)
const pwdForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// 密码校验：必填 + 长度 + 两次输入一致
const pwdRules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '新密码至少6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      // 自定义校验：两次密码必须一致
      validator: (_rule, value, callback) => {
        if (value !== pwdForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 头像文字：姓名或用户名首字符
const avatarText = computed(() => {
  const name = infoForm.real_name || infoForm.username
  return name.charAt(0).toUpperCase()
})

/**
 * 用当前用户信息回填表单
 */
function fillForm() {
  const user = userStore.userInfo
  if (!user) return
  infoForm.username = user.username
  infoForm.real_name = user.real_name || ''
  infoForm.email = user.email || ''
  infoForm.phone = user.phone || ''
}

/** 保存个人信息 */
async function handleSaveInfo() {
  await infoFormRef.value.validate()
  savingInfo.value = true
  try {
    await updateProfile({
      real_name: infoForm.real_name,
      email: infoForm.email,
      phone: infoForm.phone,
    })
    ElMessage.success('个人信息保存成功')
    // 同步刷新全局用户信息（顶部栏可能展示姓名）
    await userStore.fetchUserInfo()
  } finally {
    savingInfo.value = false
  }
}

/** 重置表单为最新的用户信息 */
function resetInfo() {
  fillForm()
  infoFormRef.value.clearValidate()
}

/** 提交修改密码 */
async function handleSavePwd() {
  await pwdFormRef.value.validate()
  savingPwd.value = true
  try {
    await updatePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    })
    ElMessage.success('密码修改成功，下次登录请使用新密码')
    // 清空密码表单
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm_password = ''
    pwdFormRef.value.clearValidate()
  } finally {
    savingPwd.value = false
  }
}

// 页面挂载：确保用户信息已加载并回填
onMounted(async () => {
  if (!userStore.userInfo) {
    await userStore.fetchUserInfo()
  }
  fillForm()
})
</script>

<style scoped>
.card-title {
  font-weight: 600;
}

.profile-avatar {
  background-color: #409eff;
  font-size: 22px;
}
</style>
