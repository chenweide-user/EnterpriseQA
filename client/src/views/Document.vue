<template>
  <!-- 文档管理页 -->
  <el-card shadow="never">
    <!-- 顶部操作区：知识库过滤 + 上传按钮 -->
    <div class="toolbar">
      <el-select
        v-model="filterKbId"
        placeholder="全部知识库"
        clearable
        style="width: 220px"
        @change="loadData"
      >
        <el-option
          v-for="kb in kbList"
          :key="kb.id"
          :label="kb.name"
          :value="kb.id"
        />
      </el-select>

      <el-button type="primary" :icon="Upload" @click="openUpload">
        上传文档
      </el-button>
    </div>

    <!-- 文档表格 -->
    <el-table :data="tableList" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="file_name" label="文件名" min-width="220" />
      <el-table-column label="所属知识库" width="150">
        <template #default="{ row }">
          {{ getKbName(row.kb_id) }}
        </template>
      </el-table-column>
      <el-table-column prop="file_type" label="类型" width="80" align="center">
        <template #default="{ row }">
          <el-tag size="small">{{ row.file_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="大小" width="100" align="center">
        <template #default="{ row }">
          {{ formatSize(row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column prop="chunk_count" label="切片数" width="90" align="center" />
      <el-table-column label="状态" width="110" align="center">
        <template #default="{ row }">
          <!-- 不同状态用不同标签颜色 -->
          <el-tag
            :type="statusType(row.status)"
            size="small"
          >
            {{ statusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="上传时间" width="170" align="center">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" :icon="Delete" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传文档" width="480px">
      <el-form label-position="top">
        <el-form-item label="选择知识库" required>
          <el-select v-model="uploadKbId" placeholder="请选择知识库" style="width: 100%">
            <el-option
              v-for="kb in kbList"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="文档文件（支持 pdf / docx / txt / md）" required>
          <!-- 关闭自动上传，点确定时手动提交；file-list 双向绑定便于读取已选文件 -->
          <el-upload
            ref="uploadRef"
            v-model:file-list="fileList"
            :auto-upload="false"
            :limit="1"
            accept=".pdf,.docx,.txt,.md"
            :on-exceed="handleExceed"
          >
            <el-button :icon="Document">选择文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadVisible = false">取 消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">
          开始上传
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
/**
 * 文档管理页面组件
 *
 * 管理员可按知识库筛选文档、上传新文档（上传时必须选择知识库），
 * 上传后后端自动完成解析、切片和向量化。
 */

import { Delete, Document, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox, genFileId } from 'element-plus'
import { onMounted, ref } from 'vue'

import { deleteDocument, listDocuments, uploadDocument } from '../api/document'
import { listKnowledge } from '../api/knowledge'

// 知识库列表与过滤条件
const kbList = ref([])
const filterKbId = ref()

// 表格数据与加载状态
const tableList = ref([])
const loading = ref(false)

// 上传弹窗状态
const uploadVisible = ref(false)
const uploadKbId = ref()
const uploadRef = ref()
const uploading = ref(false)
// 已选择的文件列表（与 el-upload 双向绑定）
const fileList = ref([])

/**
 * 根据知识库ID获取名称（表格展示用）
 * @param {number} kbId 知识库ID
 * @returns {string} 知识库名称
 */
function getKbName(kbId) {
  return kbList.value.find((kb) => kb.id === kbId)?.name || '-'
}

/**
 * 文件大小友好显示
 * @param {number} size 字节数
 * @returns {string} 带单位的大小
 */
function formatSize(size) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

/**
 * 时间格式化
 * @param {string} value ISO 时间
 * @returns {string} 标准时间
 */
function formatTime(value) {
  return value ? String(value).replace('T', ' ').slice(0, 19) : ''
}

/**
 * 文档状态对应的标签类型
 * @param {string} status 状态码
 * @returns {string} Element Plus 标签类型
 */
function statusType(status) {
  const map = { completed: 'success', processing: 'warning', failed: 'danger' }
  return map[status] || 'info'
}

/**
 * 文档状态中文文本
 * @param {string} status 状态码
 * @returns {string} 中文状态
 */
function statusText(status) {
  const map = { completed: '已完成', processing: '处理中', failed: '失败' }
  return map[status] || status
}

/** 加载知识库列表 */
async function loadKbList() {
  kbList.value = await listKnowledge()
}

/** 加载文档列表 */
async function loadData() {
  loading.value = true
  try {
    tableList.value = await listDocuments(filterKbId.value)
  } finally {
    loading.value = false
  }
}

/** 打开上传弹窗并重置选择 */
function openUpload() {
  uploadKbId.value = filterKbId.value
  fileList.value = []
  uploadRef.value?.clearFiles()
  uploadVisible.value = true
}

/**
 * 文件超出数量限制时的处理：移除旧文件后替换为新选择的文件
 * @param {File[]} files 新选择的文件数组
 */
function handleExceed(files) {
  uploadRef.value.clearFiles()
  // handleStart 要求文件对象带 uid 标识，需手动生成
  const file = files[0]
  file.uid = genFileId()
  uploadRef.value.handleStart(file)
}

/** 执行上传：校验后拼装 FormData 提交 */
async function handleUpload() {
  // 校验知识库
  if (!uploadKbId.value) {
    ElMessage.warning('请选择知识库')
    return
  }
  // 取出选中的文件（raw 为原始 File 对象）
  const file = fileList.value[0]?.raw
  if (!file) {
    ElMessage.warning('请选择要上传的文档')
    return
  }

  // multipart/form-data：字段名需与后端一致（kb_id、file）
  const formData = new FormData()
  formData.append('kb_id', uploadKbId.value)
  formData.append('file', file)

  uploading.value = true
  try {
    await uploadDocument(formData)
    ElMessage.success('文档上传并向量化成功')
    uploadVisible.value = false
    loadData()
    loadKbList() // 文档数量可能变化
  } finally {
    uploading.value = false
  }
}

/**
 * 删除文档（二次确认）
 * @param {object} row 当前行
 */
function handleDelete(row) {
  ElMessageBox.confirm(`确定删除文档「${row.file_name}」吗？`, '删除确认', {
    type: 'warning',
  })
    .then(async () => {
      await deleteDocument(row.id)
      ElMessage.success('删除成功')
      loadData()
      loadKbList()
    })
    .catch(() => {})
}

// 页面挂载时并行加载知识库和文档
onMounted(() => {
  loadKbList()
  loadData()
})
</script>

<style scoped>
/* 顶部工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
