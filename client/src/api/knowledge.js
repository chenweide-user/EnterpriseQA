/**
 * 知识库相关接口
 */

import request from './request'

/** 查询全部知识库 */
export function listKnowledge() {
  return request.get('/knowledge')
}

/**
 * 新建知识库（管理员）
 * @param {{ name: string, description?: string }} data 知识库信息
 */
export function createKnowledge(data) {
  return request.post('/knowledge', data)
}

/**
 * 编辑知识库（管理员）
 * @param {number} id 知识库ID
 * @param {object} data 名称 / 描述
 */
export function updateKnowledge(id, data) {
  return request.put(`/knowledge/${id}`, data)
}

/**
 * 删除知识库（管理员）
 * @param {number} id 知识库ID
 */
export function deleteKnowledge(id) {
  return request.delete(`/knowledge/${id}`)
}
