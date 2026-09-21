/**
 * 对话历史相关接口
 */

import request from './request'

/**
 * 查询我的会话列表
 * @param {number | undefined} kbId 知识库ID（可选）
 */
export function listSessions(kbId) {
  return request.get('/history/sessions', { params: { kb_id: kbId } })
}

/**
 * 查询会话详情（含全部消息）
 * @param {number} id 会话ID
 */
export function getSession(id) {
  return request.get(`/history/sessions/${id}`)
}

/**
 * 删除会话
 * @param {number} id 会话ID
 */
export function deleteSession(id) {
  return request.delete(`/history/sessions/${id}`)
}
