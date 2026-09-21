/**
 * 用户管理相关接口
 */

import request from './request'

/**
 * 查询用户列表（管理员）
 * @param {string | undefined} keyword 搜索关键词
 */
export function listUsers(keyword) {
  return request.get('/users', { params: { keyword } })
}

/**
 * 新建用户（管理员）
 * @param {object} data 用户信息
 */
export function createUser(data) {
  return request.post('/users', data)
}

/**
 * 编辑用户（管理员）
 * @param {number} id 用户ID
 * @param {object} data 待更新字段
 */
export function updateUser(id, data) {
  return request.put(`/users/${id}`, data)
}

/**
 * 删除用户（管理员）
 * @param {number} id 用户ID
 */
export function deleteUser(id) {
  return request.delete(`/users/${id}`)
}

/**
 * 编辑当前登录用户个人信息
 * @param {object} data 姓名 / 邮箱 / 手机号
 */
export function updateProfile(data) {
  return request.put('/users/profile', data)
}

/**
 * 修改当前登录用户密码
 * @param {{ old_password: string, new_password: string }} data 密码表单
 */
export function updatePassword(data) {
  return request.put('/users/password', data)
}
