<template>
  <div class="image-card">
    <el-card :body-style="{ padding: '10px' }">
      <img :src="imageUrl" :alt="image.file_name" class="image" />
      <div class="info">
        <div class="filename" :title="image.file_name">{{ image.file_name }}</div>
        <div class="details">
          <span>{{ formatSize(image.file_size) }}</span>
          <span>{{ image.width }} x {{ image.height }}</span>
        </div>
      </div>
      <div class="actions">
        <el-checkbox
          v-model="selected"
          @change="$emit('select', image.file_path, selected)"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  image: {
    type: Object,
    required: true
  },
  modelValue: {
    type: Boolean,
    default: false
  },
  isSelected: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select', 'update:modelValue'])

const selected = ref(props.isSelected || props.modelValue)

// 监听外部选中状态变化
watch(() => props.isSelected, (newVal) => {
  selected.value = newVal
})

const imageUrl = computed(() => {
  // 使用后端预览接口
  // 开发环境使用完整 URL，生产环境使用相对路径（通过 Nginx 代理）
  const apiUrl = import.meta.env.VITE_API_URL || ''
  return `${apiUrl}/api/images/preview?file_path=${encodeURIComponent(props.image.file_path)}`
})

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return (bytes / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i]
}
</script>

<style scoped>
.image-card {
  width: 100%;
  margin-bottom: 20px;
}

.image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
  border-radius: 4px;
}

.info {
  padding: 10px 0;
}

.filename {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.details {
  font-size: 12px;
  color: #909399;
  display: flex;
  justify-content: space-between;
}

.actions {
  display: flex;
  justify-content: center;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
}
</style>
