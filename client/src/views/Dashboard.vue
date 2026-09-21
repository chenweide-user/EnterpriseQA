<template>
  <!-- 数据概览页 -->
  <div v-loading="loading">
    <!-- 第一行：4 个指标卡片 -->
    <el-row :gutter="18">
      <el-col v-for="card in statCards" :key="card.label" :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-inner">
            <!-- 左侧图标，不同指标不同底色 -->
            <div class="stat-icon" :style="{ backgroundColor: card.color }">
              <el-icon :size="26" color="#fff">
                <component :is="card.icon" />
              </el-icon>
            </div>
            <!-- 右侧数值与名称 -->
            <div class="stat-content">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-label">{{ card.label }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：两个统计图表 -->
    <el-row :gutter="18" class="chart-row">
      <!-- 近7天提问趋势：曲线图 -->
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>
            <span class="chart-title">近 7 天提问趋势</span>
          </template>
          <v-chart class="chart" :option="lineOption" autoresize />
        </el-card>
      </el-col>

      <!-- 知识库文档占比：饼图 -->
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>
            <span class="chart-title">知识库文档占比</span>
          </template>
          <v-chart class="chart" :option="pieOption" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * 数据概览页面组件
 *
 * 页面加载时请求统计接口，展示 4 个核心指标，
 * 并用 ECharts 渲染提问趋势折线图和文档占比饼图。
 */

import 'echarts' // 全量引入 echarts，vue-echarts 自动使用
import { computed, onMounted, reactive, ref } from 'vue'
import VChart from 'vue-echarts'

import { getOverview } from '../api/stats'

// 页面加载状态
const loading = ref(false)

// 接口返回的原始统计数据
const stats = reactive({
  user_count: 0,
  kb_count: 0,
  doc_count: 0,
  today_question_count: 0,
  week_trend: [],
  kb_doc_ratio: [],
})

/**
 * 指标卡片配置（数值随接口数据动态计算）
 */
const statCards = computed(() => [
  { label: '用户总数', value: stats.user_count, icon: 'User', color: '#409eff' },
  { label: '知识库数量', value: stats.kb_count, icon: 'Collection', color: '#67c23a' },
  { label: '文档总数', value: stats.doc_count, icon: 'Document', color: '#e6a23c' },
  { label: '今日提问数', value: stats.today_question_count, icon: 'ChatDotRound', color: '#f56c6c' },
])

/**
 * 折线图配置：X 轴为日期，Y 轴为提问数
 */
const lineOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 30, bottom: 30 },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: stats.week_trend.map((item) => item.date.slice(5)), // 只显示 月-日
  },
  yAxis: {
    type: 'value',
    minInterval: 1, // 只允许整数刻度
  },
  series: [
    {
      name: '提问数',
      type: 'line',
      smooth: true, // 平滑曲线
      data: stats.week_trend.map((item) => item.count),
      itemStyle: { color: '#409eff' },
      areaStyle: { color: 'rgba(64,158,255,0.15)' }, // 面积填充
    },
  ],
}))

/**
 * 饼图配置：展示各知识库文档数量占比
 */
const pieOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 个 ({d}%)' },
  legend: { bottom: 0 },
  series: [
    {
      name: '文档数量',
      type: 'pie',
      radius: ['40%', '65%'], // 环形饼图
      center: ['50%', '45%'],
      data: stats.kb_doc_ratio,
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { formatter: '{b}\n{c} 个' },
    },
  ],
}))

/**
 * 页面挂载后拉取统计数据
 */
onMounted(async () => {
  loading.value = true
  try {
    const data = await getOverview()
    // 逐个字段赋值到响应式对象
    Object.assign(stats, data)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* 指标卡片 */
.stat-card {
  border-radius: 8px;
}

.stat-inner {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 图标方块 */
.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 数值与名称 */
.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  margin-top: 4px;
  font-size: 13px;
  color: #909399;
}

/* 图表区域间距 */
.chart-row {
  margin-top: 18px;
}

.chart-title {
  font-weight: 600;
}

.chart {
  height: 340px;
}
</style>
