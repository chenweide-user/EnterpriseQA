<template>
  <!-- 知识库管理页 -->
  <el-card shadow="never">
    <!-- 顶部操作区 -->
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="输入名称搜索"
        clearable
        style="width: 240px"
        :prefix-icon="Search"
        @input="filterList"
      />
      <el-button type="primary" :icon="Plus" @click="openCreate">
        新建知识库
      </el-button>
    </div>

    <!-- 知识库表格 -->
    <el-table :data="filteredList" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="name" label="知识库名称" min-width="150" />
      <el-table-column
        prop="description"
        label="描述"
        min-width="220"
        show-overflow-tooltip
      />
      <el-table-column prop="doc_count" label="文档数" width="90" align="center" />
      <el-table-column prop="created_at" label="创建时间" width="180" align="center">
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

    <!-- 新建 / 编辑 弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="480px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="知识库描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入知识库描述（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确 定
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
/**
 * 知识库管理页面组件
 *
 * 支持知识库的列表展示、名称搜索、新建、编辑和删除。
 */

import {
  Delete,
  Edit,
  Plus,
  Search,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { computed, onMounted, reactive, ref } from 'vue'

import {
  createKnowledge,
  deleteKnowledge,
  listKnowledge,
  updateKnowledge,
} from '../api/knowledge'

// 表格数据与加载状态
const tableList = ref([])
const filteredList = ref([])
const loading = ref(false)
const keyword = ref('')

// 弹窗状态
const dialogVisible = ref(false)
const submitting = ref(false)
const formRef = ref()

// 表单数据（editingId 为 null 表示新建）
const editingId = ref(null)
const form = reactive({ name: '', description: '' })

// 表单校验规则
const rules = {
  name: [{ required: true, message: '请输入知识库名称', trigger: 'blur' }],
}

// 弹窗标题（随新建/编辑切换）
const dialogTitle = computed(() =>
  editingId.value === null ? '新建知识库' : '编辑知识库'
)

/**
 * 格式化时间，只保留到秒
 * @param {string} value ISO 时间字符串
 * @returns {string} 格式化后的时间
 */
function formatTime(value) {
  return value ? String(value).replace('T', ' ').slice(0, 19) : ''
}

/**
 * 加载知识库列表
 */
async function loadData() {
  loading.value = true
  try {
    tableList.value = await listKnowledge()
    filterList()
  } finally {
    loading.value = false
  }
}

/**
 * 根据关键词在前端过滤表格
 */
function filterList() {
  const key = keyword.value.trim()
  filteredList.value = key
    ? tableList.value.filter((item) => item.name.includes(key))
    : tableList.value
}

/** 打开新建弹窗 */
function openCreate() {
  editingId.value = null
  form.name = ''
  form.description = ''
  dialogVisible.value = true
}

/**
 * 打开编辑弹窗并回填数据
 * @param {object} row 当前行数据
 */
function openEdit(row) {
  editingId.value = row.id
  form.name = row.name
  form.description = row.description || ''
  dialogVisible.value = true
}

/** 提交新建 / 编辑表单 */
async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    if (editingId.value === null) {
      await createKnowledge({ ...form })
      ElMessage.success('知识库创建成功')
    } else {
      await updateKnowledge(editingId.value, { ...form })
      ElMessage.success('知识库修改成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitting.value = false
  }
}

/**
 * 删除知识库（二次确认）
 * @param {object} row 当前行
 */
function handleDelete(row) {
  ElMessageBox.confirm(
    `确定删除知识库「${row.name}」吗？其下文档和向量数据将一并删除！`,
    '删除确认',
    { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' }
  )
    .then(async () => {
      await deleteKnowledge(row.id)
      ElMessage.success('删除成功')
      loadData()
    })
    .catch(() => {})
}

/** 弹窗关闭后重置校验状态 */
function resetForm() {
  formRef.value?.clearValidate()
}

// 页面挂载时加载数据
onMounted(loadData)
</script>

<style scoped>
/* 顶部工具栏：两端对齐 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
