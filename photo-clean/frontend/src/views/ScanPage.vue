<template>
  <div class="scan-page">
    <el-container>
      <el-header height="60px">
        <div class="header-content">
          <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
          <h2>扫描图片</h2>
          <div></div>
        </div>
      </el-header>

      <el-main>
        <div class="scan-content">
          <el-card v-if="!scanning && !taskId">
            <template #header>
              <div class="card-header">
                <span>配置扫描任务</span>
              </div>
            </template>

            <el-form :model="scanForm" label-width="120px">
              <el-form-item label="扫描模式">
                <el-radio-group v-model="scanForm.scan_mode">
                  <el-radio value="default">扫描全部照片目录</el-radio>
                  <el-radio value="custom">扫描指定子目录</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="扫描目录" v-if="scanForm.scan_mode === 'custom'">
                <el-input
                  v-model="scanForm.scan_dir"
                  placeholder="留空将扫描整个照片目录"
                />
                <span class="form-tip">相对于照片根目录的子目录路径</span>
              </el-form-item>

              <el-form-item label="递归扫描">
                <el-switch v-model="scanForm.recursive" />
                <span class="form-tip">是否扫描子目录</span>
              </el-form-item>

              <el-form-item label="相似度阈值">
                <div class="threshold-control">
                  <el-slider
                    v-model="scanForm.threshold"
                    :min="0"
                    :max="20"
                    :marks="{ 0: '最严格', 10: '推荐', 20: '最宽松' }"
                    show-input
                    :show-input-controls="false"
                  />
                  <div class="form-tip">阈值越小，匹配越严格（推荐值：10）</div>
                </div>
              </el-form-item>

              <el-form-item label="每页显示">
                <el-input-number
                  v-model="scanForm.pageSize"
                  :min="10"
                  :max="500"
                  :step="10"
                  controls-position="right"
                />
                <span class="form-tip">结果分页显示的数量（默认100）</span>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="startScan" :loading="starting">
                  开始扫描
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <el-card v-else>
            <template #header>
              <div class="card-header">
                <span>扫描进度</span>
              </div>
            </template>

            <ProgressBar
              :status="progress.status"
              :total-files="progress.total_files"
              :processed-files="progress.processed_files"
              :similar-groups="progress.similar_groups"
              :progress-percent="progress.progress_percent"
            />

            <div class="scan-actions" v-if="progress.status === 'completed'">
              <el-button type="primary" size="large" @click="viewResults">
                查看结果
              </el-button>
            </div>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { scanAPI } from '@/api'
import { useScanStore } from '@/store'
import ProgressBar from '@/components/ProgressBar.vue'

const router = useRouter()
const scanStore = useScanStore()

const scanForm = ref({
  scan_mode: 'default',  // 'default' 或 'custom'
  scan_dir: '',  // 留空表示使用配置的默认目录
  recursive: true,
  threshold: 10,
  pageSize: 100  // 分页大小
})

const scanning = ref(false)
const starting = ref(false)
const taskId = ref(null)
const progress = ref({
  status: 'pending',
  total_files: 0,
  processed_files: 0,
  similar_groups: 0,
  progress_percent: 0
})

let progressTimer = null

const goBack = () => {
  router.push('/')
}

const startScan = async () => {
  starting.value = true

  try {
    // 准备扫描参数
    const params = {
      recursive: scanForm.value.recursive,
      threshold: scanForm.value.threshold
    }

    // 只在自定义模式且指定了目录时才发送 scan_dir
    if (scanForm.value.scan_mode === 'custom' && scanForm.value.scan_dir) {
      params.scan_dir = scanForm.value.scan_dir
    }

    const result = await scanAPI.startScan(params)
    taskId.value = result.task_id
    scanning.value = true

    scanStore.setTaskId(result.task_id)

    ElMessage.success('扫描任务已启动')

    // 开始轮询进度
    startProgressPolling()
  } catch (error) {
    ElMessage.error('启动扫描失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    starting.value = false
  }
}

const startProgressPolling = () => {
  progressTimer = setInterval(async () => {
    try {
      const data = await scanAPI.getProgress(taskId.value)
      progress.value = data
      scanStore.updateProgress(data)

      // 如果扫描完成或失败，停止轮询
      if (data.status === 'completed' || data.status === 'failed') {
        stopProgressPolling()

        if (data.status === 'completed') {
          ElMessage.success('扫描完成！')
        } else {
          ElMessage.error('扫描失败')
        }
      }
    } catch (error) {
      console.error('获取进度失败:', error)
    }
  }, 2000) // 每2秒轮询一次
}

const stopProgressPolling = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

const viewResults = () => {
  // 将分页大小传递到结果页面
  router.push({
    path: `/result/${taskId.value}`,
    query: { pageSize: scanForm.value.pageSize }
  })
}

onMounted(() => {
  // 如果有正在进行的任务，恢复状态
  if (scanStore.currentTaskId) {
    taskId.value = scanStore.currentTaskId
    progress.value = scanStore.scanProgress
    scanning.value = true

    if (progress.value.status === 'running') {
      startProgressPolling()
    }
  }
})

onUnmounted(() => {
  stopProgressPolling()
})
</script>

<style scoped>
.scan-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.el-header {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-content h2 {
  margin: 0;
  flex: 1;
  text-align: center;
}

.el-main {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
}

.scan-content {
  width: 100%;
  max-width: 800px;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}

.scan-actions {
  margin-top: 30px;
  text-align: center;
}

.threshold-control {
  width: 100%;
}

.threshold-control :deep(.el-slider) {
  padding: 0 12px;
  margin-bottom: 30px;
}

.threshold-control :deep(.el-input-number) {
  width: 100px;
}

.threshold-control .form-tip {
  display: block;
  margin-left: 0;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .el-form {
    padding: 0 10px;
  }

  .threshold-control :deep(.el-slider) {
    margin-bottom: 35px;
  }

  .threshold-control :deep(.el-slider__marks-text) {
    font-size: 10px;
  }

  .threshold-control :deep(.el-input-number) {
    width: 80px;
  }

  .form-tip {
    display: block;
    margin-left: 0 !important;
    margin-top: 8px;
  }
}
</style>
