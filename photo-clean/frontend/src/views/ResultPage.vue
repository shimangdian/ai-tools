<template>
  <div class="result-page">
    <el-container>
      <el-header height="60px">
        <div class="header-content">
          <el-button icon="ArrowLeft" @click="goBack">返回</el-button>
          <h2>扫描结果</h2>
          <el-button type="primary" @click="batchDelete" :disabled="selectedImages.length === 0">
            删除选中 ({{ selectedImages.length }})
          </el-button>
        </div>
      </el-header>

      <el-main>
        <div class="result-content">
          <div v-if="loading" class="loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>

          <div v-else-if="groups.length === 0" class="empty">
            <el-empty description="未找到相似图片" />
          </div>

          <div v-else class="groups-container">
            <div class="summary">
              <el-alert
                :title="`找到 ${totalGroups} 组相似图片，共 ${totalImages} 张图片`"
                type="success"
                :closable="false"
              />
            </div>

            <!-- 分页控件 - 顶部 -->
            <div class="pagination-top" v-if="totalPages > 1">
              <el-pagination
                :current-page="currentPage"
                :page-size="pageSize"
                :page-sizes="[50, 100, 200, 500]"
                :total="totalGroups"
                :background="true"
                layout="total, sizes, prev, pager, next, jumper"
                @current-change="handlePageChange"
                @size-change="handleSizeChange"
              />
            </div>

            <div v-for="(group, index) in groups" :key="group.group_id" class="group-card">
              <el-card>
                <template #header>
                  <div class="group-header">
                    <span>相似组 #{{ group.group_id }}</span>
                    <div class="group-actions">
                      <el-button size="small" @click="selectAllInGroup(group, true)">
                        全选
                      </el-button>
                      <el-button size="small" @click="selectAllInGroup(group, false)">
                        取消全选
                      </el-button>
                      <el-button size="small" type="primary" @click="keepBest(group)">
                        保留最佳
                      </el-button>
                    </div>
                  </div>
                </template>

                <el-row :gutter="20">
                  <el-col
                    v-for="image in group.images"
                    :key="image.id"
                    :xs="24"
                    :sm="12"
                    :md="8"
                    :lg="6"
                  >
                    <ImageCard
                      :image="image"
                      :is-selected="selectedImages.includes(image.file_path)"
                      @select="handleImageSelect"
                    />
                  </el-col>
                </el-row>
              </el-card>
            </div>

            <!-- 分页控件 - 底部 -->
            <div class="pagination-bottom" v-if="totalPages > 1">
              <el-pagination
                :current-page="currentPage"
                :page-size="pageSize"
                :page-sizes="[50, 100, 200, 500]"
                :total="totalGroups"
                :background="true"
                layout="total, sizes, prev, pager, next, jumper"
                @current-change="handlePageChange"
                @size-change="handleSizeChange"
              />
            </div>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import { scanAPI, imageAPI } from '@/api'
import ImageCard from '@/components/ImageCard.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const groups = ref([])
const selectedImages = ref([])

// 分页相关
const currentPage = ref(1)
const pageSize = ref(parseInt(route.query.pageSize) || 100)
const totalGroups = ref(0)
const totalPages = ref(0)

const taskId = computed(() => route.params.taskId)

const totalImages = computed(() => {
  return groups.value.reduce((sum, group) => sum + group.images.length, 0)
})

const goBack = () => {
  router.push('/scan')
}

const loadResults = async () => {
  loading.value = true

  try {
    const data = await scanAPI.getSimilarGroups(taskId.value, currentPage.value, pageSize.value)
    groups.value = data.groups
    totalGroups.value = data.total_groups
    totalPages.value = data.total_pages
  } catch (error) {
    ElMessage.error('加载结果失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadResults()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadResults()
}

const handleImageSelect = (filePath, selected) => {
  if (selected) {
    if (!selectedImages.value.includes(filePath)) {
      selectedImages.value.push(filePath)
    }
  } else {
    const index = selectedImages.value.indexOf(filePath)
    if (index > -1) {
      selectedImages.value.splice(index, 1)
    }
  }
}

const selectAllInGroup = (group, select) => {
  // 强制更新每个图片的选中状态
  const imagePaths = group.images.map(img => img.file_path)

  if (select) {
    // 全选：添加所有不在列表中的图片
    imagePaths.forEach(path => {
      if (!selectedImages.value.includes(path)) {
        selectedImages.value.push(path)
      }
    })
  } else {
    // 取消全选：移除所有在列表中的图片
    selectedImages.value = selectedImages.value.filter(
      path => !imagePaths.includes(path)
    )
  }

  // 触发界面更新
  selectedImages.value = [...selectedImages.value]
}

const keepBest = (group) => {
  // 找出最佳图片（分辨率最高、文件最大）
  let best = group.images[0]
  for (const image of group.images) {
    const currentScore = image.width * image.height + image.file_size / 1000
    const bestScore = best.width * best.height + best.file_size / 1000

    if (currentScore > bestScore) {
      best = image
    }
  }

  // 选中除最佳之外的所有图片
  group.images.forEach(image => {
    if (image.id !== best.id) {
      handleImageSelect(image.file_path, true)
    } else {
      handleImageSelect(image.file_path, false)
    }
  })

  ElMessage.success(`已选中 ${group.images.length - 1} 张图片，保留最佳图片`)
}

const batchDelete = async () => {
  if (selectedImages.value.length === 0) {
    ElMessage.warning('请先选择要删除的图片')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedImages.value.length} 张图片吗？图片将移动到回收站，可以恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const result = await imageAPI.deleteImages(selectedImages.value)

    if (result.success) {
      ElMessage.success(result.message)
      selectedImages.value = []
      // 重新加载结果
      loadResults()
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

onMounted(() => {
  loadResults()
})
</script>

<style scoped>
.result-page {
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
  padding: 20px;
}

.result-content {
  max-width: 1400px;
  margin: 0 auto;
}

.loading,
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #909399;
}

.loading .el-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.summary {
  margin-bottom: 20px;
}

.group-card {
  margin-bottom: 20px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-header span {
  font-size: 16px;
  font-weight: 600;
}

.group-actions {
  display: flex;
  gap: 10px;
}

.pagination-top,
.pagination-bottom {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.pagination-top {
  margin-bottom: 10px;
}

.pagination-bottom {
  margin-top: 10px;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .el-main {
    padding: 10px;
  }

  .header-content h2 {
    font-size: 18px;
  }

  .group-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .group-actions {
    width: 100%;
    justify-content: space-between;
  }

  .group-actions .el-button {
    flex: 1;
    padding: 8px 5px;
    font-size: 12px;
  }

  /* 分页控件移动端优化 */
  .pagination-top :deep(.el-pagination),
  .pagination-bottom :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }

  .pagination-top :deep(.el-pagination__sizes),
  .pagination-bottom :deep(.el-pagination__sizes) {
    margin: 5px 0;
  }

  .pagination-top :deep(.el-pagination__jump),
  .pagination-bottom :deep(.el-pagination__jump) {
    margin-left: 0;
    margin-top: 5px;
  }

  /* 简化移动端分页布局 */
  .pagination-top :deep(.el-pagination) {
    font-size: 13px;
  }

  .pagination-bottom :deep(.el-pagination) {
    font-size: 13px;
  }
}
</style>
