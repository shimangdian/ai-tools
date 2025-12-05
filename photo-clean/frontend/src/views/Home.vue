<template>
  <div class="home-container">
    <el-container>
      <el-header height="80px">
        <div class="header-content">
          <h1>Photo Clean</h1>
          <p>相似图片清理工具</p>
        </div>
      </el-header>

      <el-main>
        <div class="main-content">
          <el-card class="welcome-card">
            <template #header>
              <div class="card-header">
                <span>欢迎使用</span>
              </div>
            </template>

            <div class="welcome-content">
              <p class="intro">
                这是一款运行在群晖 NAS 上的相似图片清理工具，帮助您快速找到并清理相似的图片，节省存储空间。
              </p>

              <div class="features">
                <h3>主要功能</h3>
                <ul>
                  <li>快速扫描指定目录下的所有图片</li>
                  <li>使用感知哈希算法识别相似图片</li>
                  <li>智能推荐保留哪张图片</li>
                  <li>安全的回收站机制，支持恢复</li>
                  <li>批量删除操作</li>
                </ul>
              </div>

              <div class="actions">
                <el-button type="primary" size="large" @click="startScan">
                  开始扫描
                </el-button>
              </div>
            </div>
          </el-card>

          <el-card class="stats-card">
            <template #header>
              <div class="card-header">
                <span>系统信息</span>
              </div>
            </template>

            <div class="stats-content">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="stat-item">
                    <div class="stat-label">回收站文件数</div>
                    <div class="stat-value">{{ trashInfo.file_count }}</div>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="stat-item">
                    <div class="stat-label">回收站大小</div>
                    <div class="stat-value">{{ trashInfo.total_size_mb }} MB</div>
                  </div>
                </el-col>
              </el-row>

              <div class="trash-actions">
                <el-button type="danger" plain size="small" @click="cleanTrash">
                  清空回收站
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { imageAPI } from '@/api'

const router = useRouter()

const trashInfo = ref({
  file_count: 0,
  total_size_mb: 0,
  retention_days: 30
})

const startScan = () => {
  router.push('/scan')
}

const loadTrashInfo = async () => {
  try {
    const data = await imageAPI.getTrashInfo()
    trashInfo.value = data
  } catch (error) {
    console.error('获取回收站信息失败:', error)
  }
}

const cleanTrash = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空回收站吗？此操作不可恢复！',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const result = await imageAPI.cleanTrash()
    ElMessage.success(result.message)
    loadTrashInfo()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空回收站失败')
    }
  }
}

onMounted(() => {
  loadTrashInfo()
})
</script>

<style scoped>
.home-container {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.el-header {
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.header-content {
  text-align: center;
  color: white;
}

.header-content h1 {
  margin: 0;
  font-size: 36px;
  font-weight: 600;
}

.header-content p {
  margin: 5px 0 0 0;
  font-size: 16px;
  opacity: 0.9;
}

.el-main {
  display: flex;
  align-items: center;
  justify-content: center;
}

.main-content {
  width: 100%;
  max-width: 800px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-content {
  padding: 20px 0;
}

.intro {
  font-size: 16px;
  line-height: 1.8;
  color: #606266;
  margin-bottom: 30px;
}

.features {
  margin-bottom: 30px;
}

.features h3 {
  margin-bottom: 15px;
  color: #303133;
}

.features ul {
  list-style: none;
  padding: 0;
}

.features li {
  padding: 8px 0;
  color: #606266;
  position: relative;
  padding-left: 20px;
}

.features li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #67c23a;
  font-weight: bold;
}

.actions {
  text-align: center;
  margin-top: 30px;
}

.stats-content {
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.trash-actions {
  margin-top: 20px;
  text-align: center;
}
</style>
