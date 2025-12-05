import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useScanStore = defineStore('scan', () => {
  const currentTaskId = ref(null)
  const scanProgress = ref({
    status: 'idle',
    total_files: 0,
    processed_files: 0,
    similar_groups: 0,
    progress_percent: 0
  })

  function setTaskId(taskId) {
    currentTaskId.value = taskId
  }

  function updateProgress(progress) {
    scanProgress.value = progress
  }

  function reset() {
    currentTaskId.value = null
    scanProgress.value = {
      status: 'idle',
      total_files: 0,
      processed_files: 0,
      similar_groups: 0,
      progress_percent: 0
    }
  }

  return {
    currentTaskId,
    scanProgress,
    setTaskId,
    updateProgress,
    reset
  }
})
