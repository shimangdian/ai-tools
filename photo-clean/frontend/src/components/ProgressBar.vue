<template>
  <div class="progress-bar">
    <el-progress
      :percentage="progressPercent"
      :status="progressStatus"
      :stroke-width="20"
    >
      <template #default="{ percentage }">
        <span class="percentage-label">{{ percentage }}%</span>
      </template>
    </el-progress>
    <div class="progress-info">
      <div class="info-item">
        <span class="label">状态:</span>
        <span class="value">{{ statusText }}</span>
      </div>
      <div class="info-item">
        <span class="label">已处理:</span>
        <span class="value">{{ processedFiles }} / {{ totalFiles }}</span>
      </div>
      <div class="info-item">
        <span class="label">相似组数:</span>
        <span class="value">{{ similarGroups }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    default: 'pending'
  },
  totalFiles: {
    type: Number,
    default: 0
  },
  processedFiles: {
    type: Number,
    default: 0
  },
  similarGroups: {
    type: Number,
    default: 0
  },
  progressPercent: {
    type: Number,
    default: 0
  }
})

const statusText = computed(() => {
  const statusMap = {
    pending: '等待中',
    running: '扫描中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[props.status] || '未知'
})

const progressStatus = computed(() => {
  if (props.status === 'completed') return 'success'
  if (props.status === 'failed') return 'exception'
  return ''
})
</script>

<style scoped>
.progress-bar {
  width: 100%;
}

.progress-info {
  margin-top: 20px;
  display: flex;
  justify-content: space-around;
}

.info-item {
  text-align: center;
}

.label {
  font-size: 14px;
  color: #909399;
  margin-right: 5px;
}

.value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.percentage-label {
  font-size: 14px;
  font-weight: 600;
}
</style>
