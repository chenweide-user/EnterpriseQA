/**
 * Axios 请求封装
 *
 * - 统一 baseURL（走 Vite 代理，避免跨域）；
 * - 请求拦截器自动携带 JWT；
 * - 响应拦截器统一解包和错误提示，401 时自动跳转登录页。
 */

import axios from 'axios'
import { ElMessage } from 'element-plus'

import { getToken, removeToken } from '../utils/auth'

// 创建 axios 实例
const service = axios.create({
  baseURL: '/api', // 由 vite.config.js 中的 proxy 转发到后端
  timeout: 120000, // 文档上传与向量化耗时较长，超时设为 2 分钟
})

// 请求拦截器：自动在请求头中挂载令牌
service.interceptors.request.use(
  (config) => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：成功直接返回响应体数据，失败统一弹提示
service.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    // 后端 401：令牌失效，清除本地登录态并跳转登录页
    if (status === 401) {
      removeToken()
      ElMessage.error('登录状态已失效，请重新登录')
      window.location.href = '/login'
    } else {
      // 优先展示后端返回的 detail / message
      const data = error.response?.data
      const message =
        typeof data?.detail === 'string'
          ? data.detail
          : data?.message || error.message || '请求失败'
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export default service
