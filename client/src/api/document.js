/**
 * 文档管理相关接口
 */

import request from './request'

/**
 * 查询文档列表
 * @param {number | undefined} kbId 知识库ID（可选过滤条件）
 */
export function listDocuments(kbId) {
  return request.get('/documents', { params: { kb_id: kbId } })
}

/**
 * 上传文档（multipart/form-data）
 * @param {FormData} formData 包含 kb_id 和 file 的表单数据
 */
export function uploadDocument(formData) {
  return request.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    // 上传 + 解析 + 向量化可能耗时较久，关闭前端超时限制
    timeout: 600000,
  })
}

/**
 * 删除文档
 * @param {number} id 文档ID
 */
export function deleteDocument(id) {
  return request.delete(`/documents/${id}`)
}
