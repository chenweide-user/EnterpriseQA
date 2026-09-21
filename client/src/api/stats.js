/**
 * 数据概览统计相关接口
 */

import request from './request'

/**
 * 获取首页数据概览（管理员）
 * @returns {Promise<object>} 指标与图表数据
 */
export function getOverview() {
  return request.get('/stats/overview')
}
