<template>
  <!-- 用户管理页（管理员） -->
  <el-card shadow="never">
    <!-- 顶部操作区 -->
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索用户名 / 姓名"
        clearable
        style="width: 240px"
        :prefix-icon="Search"
        @keyup.enter="loadData"
      />
      <div>
        <el-button :icon="Search" @click="loadData">搜 索</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">
          新增用户
        </el-button>
      </div>
    </div>

    <!-- 用户表格 -->
    <el-table :data="tableList" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="username" label="用户名" min-width="120" />
      <el-table-column prop="real_name" label="真实姓名" min-width="110" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column prop="phone" label="手机号" min-width="130" />
      <el-table-column label="角色" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'success'" size="small">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'primary' : 'info'" size="small">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="170" align="center">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" :icon="Edit" @click="openEdit(row)">
            编辑
          </el-button>
          <el-button link type="danger" :icon="Delete" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增用户弹窗 -->
    <el-dialog v-model="createVisible" title="新增用户" width="480px">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="createForm.username" placeholder="请输入登录用户名" />
        </el-form-item>
        <el-form-item label="初始密码" prop="password">
          <el-input v-model="createForm.password" placeholder="默认 123456" />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="createForm.real_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="createForm.email" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="createForm.phone" />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="createForm.role">
            <el-radio value="user">普通用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleCreate">确 定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑用户弹窗 -->
    <el-dialog v-model="editVisible" title="编辑用户" width="480px">
      <el-form label-position="top">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="editForm.real_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="editForm.role">
            <el-radio value="user">普通用户</el-radio>
            <el-radio value="admin">管理员</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="editForm.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取 消</el-button>
        <el-button type="primary" @click="handleEditSubmit">保 存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
/**
 * 用户管理页面组件（管理员）
 *
 * 提供用户搜索、新增、编辑（角色/状态/资料）和删除功能。
 */

import { Delete, Edit, Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, reactive, ref } from 'vue'

import {
  createUser,
  deleteUser,
  listUsers,
  updateUser,
} from '../api/user'

// 表格与搜索
const tableList = ref([])
const keyword = ref('')
const loading = ref(false)

// 新增弹窗
const createVisible = ref(false)
const createFormRef = ref()
const createForm = reactive({
  username: '',
  password: '123456',
  real_name: '',
  email: '',
  phone: '',
  role: 'user',
})
const createRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入初始密码', trigger: 'blur' }],
}

// 编辑弹窗
const editVisible = ref(false)
const editForm = reactive({
  id: null,
  username: '',
  real_name: '',
  email: '',
  phone: '',
  role: 'user',
  status: 1,
})

/**
 * 时间格式化
 * @param {string} value ISO 时间
 * @returns {string} 标准时间
 */
function formatTime(value) {
  return value ? String(value).replace('T', ' ').slice(0, 19) : ''
}

/** 加载用户列表 */
async function loadData() {
  loading.value = true
  try {
    tableList.value = await listUsers(keyword.value || undefined)
  } finally {
    loading.value = false
  }
}

/** 打开新增弹窗 */
function openCreate() {
  Object.assign(createForm, {
    username: '',
    password: '123456',
    real_name: '',
    email: '',
    phone: '',
    role: 'user',
  })
  createVisible.value = true
}

/** 提交新增用户 */
async function handleCreate() {
  await createFormRef.value.validate()
  await createUser({ ...createForm, status: 1 })
  ElMessage.success('用户创建成功')
  createVisible.value = false
  loadData()
}

/**
 * 打开编辑弹窗并回填
 * @param {object} row 当前行
 */
function openEdit(row) {
  Object.assign(editForm, {
    id: row.id,
    username: row.username,
    real_name: row.real_name || '',
    email: row.email || '',
    phone: row.phone || '',
    role: row.role,
    status: row.status,
  })
  editVisible.value = true
}

/** 提交编辑内容 */
async function handleEditSubmit() {
  await updateUser(editForm.id, { ...editForm })
  ElMessage.success('用户信息修改成功')
  editVisible.value = false
  loadData()
}

/**
 * 删除用户（二次确认）
 * @param {object} row 当前行
 */
function handleDelete(row) {
  ElMessageBox.confirm(`确定删除用户「${row.username}」吗？`, '删除确认', {
    type: 'warning',
  })
    .then(async () => {
      await deleteUser(row.id)
      ElMessage.success('删除成功')
      loadData()
    })
    .catch(() => {})
}

onMounted(loadData)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
