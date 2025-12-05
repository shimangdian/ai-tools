import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000 // 5分钟超时
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 扫描相关接口
export const scanAPI = {
  // 开始扫描
  startScan(data) {
    return api.post('/scan/start', data)
  },

  // 获取扫描进度
  getProgress(taskId) {
    return api.get(`/scan/progress/${taskId}`)
  },

  // 获取相似图片组（支持分页）
  getSimilarGroups(taskId, page = 1, pageSize = 100) {
    return api.get(`/scan/groups/${taskId}`, {
      params: { page, page_size: pageSize }
    })
  }
}

// 图片操作接口
export const imageAPI = {
  // 删除图片
  deleteImages(filePaths) {
    return api.post('/images/delete', { file_paths: filePaths })
  },

  // 恢复图片
  restoreImages(filePaths) {
    return api.post('/images/restore', { file_paths: filePaths })
  },

  // 清理回收站
  cleanTrash() {
    return api.post('/images/clean-trash')
  },

  // 获取回收站信息
  getTrashInfo() {
    return api.get('/images/trash-info')
  }
}

export default api
