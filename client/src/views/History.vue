<template>
  <!-- 对话历史页 -->
  <el-card shadow="never">
    <!-- 顶部筛选 -->
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
    </div>

    <!-- 会话表格 -->
    <el-table :data="tableList" v-loading="loading" border stripe>
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="title" label="会话标题" min-width="260" show-overflow-tooltip />
      <el-table-column label="所属知识库" width="160">
        <template #default="{ row }">
          {{ getKbName(row.kb_id) }}
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" align="center">
        <template #default="{ row }">
          <el-button link type="primary" :icon="View" @click="openDetail(row)">
            查看详情
          </el-button>
          <el-button link type="danger" :icon="Delete" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 会话详情抽屉 -->
    <el-drawer v-model="detailVisible" title="对话详情" size="55%">
      <div class="detail-area">
        <!-- 逐消息展示 -->
        <div
          v-for="msg in detailMessages"
          :key="msg.id"
          class="detail-row"
          :class="msg.role === 'user' ? 'is-user' : 'is-assistant'"
        >
          <el-tag :type="msg.role === 'user' ? 'primary' : 'success'" size="small">
            {{ msg.role === 'user' ? '我' : 'AI' }}
          </el-tag>
          <div class="detail-content">{{ msg.content }}</div>
          <div class="detail-time">{{ formatTime(msg.created_at) }}</div>
        </div>
      </div>
    </el-drawer>
  </el-card>
</template>

<script setup>
/**
 * 对话历史页面组件
 *
 * 按知识库筛选本人历史会话，支持查看完整对话内容和删除会话。
 */

import { Delete, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, ref } from 'vue'

import { deleteSession, getSession, listSessions } from '../api/history'
import { listKnowledge } from '../api/knowledge'

// 知识库与过滤条件
const kbList = ref([])
const filterKbId = ref()

// 表格数据
const tableList = ref([])
const loading = ref(false)

// 详情抽屉
const detailVisible = ref(false)
const detailMessages = ref([])

/**
 * 获取知识库名称
 * @param {number} kbId 知识库ID
 * @returns {string} 名称
 */
function getKbName(kbId) {
  return kbList.value.find((kb) => kb.id === kbId)?.name || '-'
}

/**
 * 时间格式化
 * @param {string} value ISO 时间
 * @returns {string} 标准时间
 */
function formatTime(value) {
  return value ? String(value).replace('T', ' ').slice(0, 19) : ''
}

/** 加载知识库列表 */
async function loadKbList() {
  kbList.value = await listKnowledge()
}

/** 加载会话列表 */
async function loadData() {
  loading.value = true
  try {
    tableList.value = await listSessions(filterKbId.value)
  } finally {
    loading.value = false
  }
}

/**
 * 打开详情抽屉：拉取会话的全部消息
 * @param {object} row 当前行
 */
async function openDetail(row) {
  const detail = await getSession(row.id)
  detailMessages.value = detail.messages
  detailVisible.value = true
}

/**
 * 删除会话
 * @param {object} row 当前行
 */
function handleDelete(row) {
  ElMessageBox.confirm(`确定删除会话「${row.title}」吗？`, '删除确认', {
    type: 'warning',
  })
    .then(async () => {
      await deleteSession(row.id)
      ElMessage.success('删除成功')
      loadData()
    })
    .catch(() => {})
}

onMounted(() => {
  loadKbList()
  loadData()
})
</script>

<style scoped>
.toolbar {
  margin-bottom: 16px;
}

/* 详情区域 */
.detail-area {
  padding: 0 4px;
}

.detail-row {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* 用户提问右对齐，AI回答左对齐 */
.detail-row.is-user {
  align-items: flex-end;
}

.detail-row.is-assistant {
  align-items: flex-start;
}

.detail-content {
  max-width: 90%;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.6;
  background-color: #f4f4f5;
}

.detail-row.is-user .detail-content {
  background-color: #ecf5ff;
  color: #409eff;
}

.detail-time {
  font-size: 12px;
  color: #c0c4cc;
}
</style>
