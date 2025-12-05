import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import ScanPage from '../views/ScanPage.vue'
import ResultPage from '../views/ResultPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/scan',
    name: 'Scan',
    component: ScanPage
  },
  {
    path: '/result/:taskId',
    name: 'Result',
    component: ResultPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
