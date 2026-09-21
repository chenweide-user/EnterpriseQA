/**
 * 认证相关接口
 */

import request from './request'

/**
 * 用户登录
 * @param {{ username: string, password: string }} data 登录表单
 * @returns {Promise<{ access_token: string, token_type: string }>} 令牌信息
 */
export function login(data) {
  return request.post('/auth/login', data)
}

/**
 * 获取当前登录用户信息
 * @returns {Promise<object>} 用户信息
 */
export function getMyInfo() {
  return request.get('/auth/me')
}
