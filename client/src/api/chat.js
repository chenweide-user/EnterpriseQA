/**
 * 智能问答相关接口
 */

import request from './request'

/**
 * 发送一次问答请求
 * @param {{ kb_id: number, question: string, session_id?: number }} data 问答请求体
 * @returns {Promise<{ session_id: number, answer: string }>} 回答结果
 */
export function sendQuestion(data) {
  return request.post('/chat', data)
}
