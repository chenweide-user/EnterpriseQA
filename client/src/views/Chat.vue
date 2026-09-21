<template>
  <!-- 智能问答页：顶部知识库选择 + 中间对话区 + 底部输入区 -->
  <el-card shadow="never" class="chat-card">
    <!-- 顶部工具栏 -->
    <div class="chat-toolbar">
      <div class="toolbar-left">
        <el-icon :size="18" color="#409eff"><ChatDotRound /></el-icon>
        <span class="toolbar-title">智能问答</span>
        <!-- 选择知识库 -->
        <el-select
          v-model="kbId"
          placeholder="请选择知识库"
          style="width: 220px"
          @change="handleKbChange"
        >
          <el-option
            v-for="kb in kbList"
            :key="kb.id"
            :label="kb.name"
            :value="kb.id"
          />
        </el-select>
      </div>

      <!-- 新建对话 -->
      <el-button :icon="Plus" @click="startNewConversation">
        新建对话
      </el-button>
    </div>

    <!-- 对话消息区 -->
    <div ref="messageArea" class="message-area">
      <!-- 空状态提示 -->
      <el-empty
        v-if="messages.length === 0"
        description="请选择知识库后开始提问"
      />

      <!-- 逐条渲染消息气泡 -->
      <div
        v-for="(msg, index) in messages"
        :key="index"
        class="message-row"
        :class="msg.role === 'user' ? 'is-user' : 'is-assistant'"
      >
        <!-- 头像 -->
        <el-avatar
          :size="36"
          :class="msg.role === 'user' ? 'avatar-user' : 'avatar-ai'"
        >
          <el-icon>
            <User v-if="msg.role === 'user'" />
            <Cpu v-else />
          </el-icon>
        </el-avatar>

        <!-- 消息内容：AI 消息支持换行展示 -->
        <div class="message-bubble" :class="`bubble-${msg.role}`">
          <span style="white-space: pre-wrap">{{ msg.content }}</span>
        </div>
      </div>

      <!-- 等待回答时的加载气泡 -->
      <div v-if="sending" class="message-row is-assistant">
        <el-avatar :size="36" class="avatar-ai">
          <el-icon><Cpu /></el-icon>
        </el-avatar>
        <div class="message-bubble bubble-assistant">
          <el-icon class="is-loading"><Loading /></el-icon>
          正在检索知识库并生成回答...
        </div>
      </div>
    </div>

    <!-- 底部输入区 -->
    <div class="input-area">
      <el-input
        v-model="inputQuestion"
        type="textarea"
        :rows="2"
        resize="none"
        placeholder="请输入你的问题，按 Enter 发送，Shift + Enter 换行"
        @keydown.enter.exact.prevent="handleSend"
      />
      <el-button type="primary" :icon="Promotion" @click="handleSend">
        发 送
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
/**
 * 智能问答页面组件
 *
 * 选择知识库后即可提问，前端维护对话气泡展示，
 * 后端基于 RAG 返回答案；未命中知识库时返回固定提示语。
 */

import { ChatDotRound, Cpu, Plus, Promotion, User } from '@element-plus/icons-vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { nextTick, onMounted, ref } from 'vue'

import { sendQuestion } from '../api/chat'
import { listKnowledge } from '../api/knowledge'

// 知识库列表与当前选中
const kbList = ref([])
const kbId = ref()

// 对话消息列表：[{ role: 'user'|'assistant', content: string }]
const messages = ref([])
// 当前会话ID（后端首次回答后返回）
const sessionId = ref(null)

// 输入内容与发送状态
const inputQuestion = ref('')
const sending = ref(false)

// 消息区域引用，用于自动滚动到底部
const messageArea = ref()

/**
 * 页面挂载时加载知识库列表
 */
onMounted(async () => {
  kbList.value = await listKnowledge()
  // 默认选中第一个知识库
  if (kbList.value.length > 0) {
    kbId.value = kbList.value[0].id
  }
})

/**
 * 切换知识库时清空当前对话
 */
function handleKbChange() {
  startNewConversation()
}

/** 开始一段全新对话 */
function startNewConversation() {
  messages.value = []
  sessionId.value = null
  inputQuestion.value = ''
}

/**
 * 滚动消息区到底部（新消息后调用）
 */
async function scrollToBottom() {
  await nextTick()
  const area = messageArea.value
  if (area) area.scrollTop = area.scrollHeight
}

/** 发送问题 */
async function handleSend() {
  // 正在等待回答时忽略重复点击（代替按钮 loading 动画）
  if (sending.value) return

  const question = inputQuestion.value.trim()

  // 基础校验
  if (!question) {
    ElMessage.warning('请输入问题')
    return
  }
  if (!kbId.value) {
    ElMessage.warning('请先选择知识库')
    return
  }

  // 用户消息先上屏
  messages.value.push({ role: 'user', content: question })
  inputQuestion.value = ''
  scrollToBottom()

  // 请求后端问答
  sending.value = true
  try {
    const data = await sendQuestion({
      kb_id: kbId.value,
      question,
      session_id: sessionId.value,
    })
    // 记录会话ID，后续提问在同一会话内进行（支持多轮追问）
    sessionId.value = data.session_id
    // AI 回答上屏
    messages.value.push({ role: 'assistant', content: data.answer })
    scrollToBottom()
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
/* 卡片采用纵向弹性布局，撑满可用空间 */
.chat-card {
  height: calc(100vh - 96px);
}

/* 让 el-card 的 body 成为弹性容器 */
.chat-card :deep(.el-card__body) {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
}

/* 顶部工具栏 */
.chat-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toolbar-title {
  font-size: 16px;
  font-weight: 600;
  margin-right: 8px;
}

/* 消息区域：占据剩余空间并可滚动 */
.message-area {
  flex: 1;
  overflow-y: auto;
  padding: 18px 10px;
}

/* 单条消息行 */
.message-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 18px;
}

/* 用户消息整体靠右 */
.message-row.is-user {
  flex-direction: row-reverse;
}

/* 头像底色 */
.avatar-user {
  background-color: #409eff;
}

.avatar-ai {
  background-color: #67c23a;
}

/* 气泡基础样式 */
.message-bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 8px;
  line-height: 1.6;
  font-size: 14px;
}

/* AI 气泡：浅灰底左对齐 */
.bubble-assistant {
  background-color: #f4f4f5;
  color: #303133;
}

/* 用户气泡：主题蓝底右对齐 */
.bubble-user {
  background-color: #409eff;
  color: #fff;
}

/* 加载图标旋转 */
.is-loading {
  animation: rotating 1.5s linear infinite;
  margin-right: 4px;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 底部输入区 */
.input-area {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.input-area .el-button {
  height: 48px;
}
</style>
