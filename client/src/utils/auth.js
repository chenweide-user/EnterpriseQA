/**
 * 登录令牌本地存储工具
 *
 * 使用 localStorage 持久化保存后端下发的 JWT，
 * 刷新页面后登录状态不丢失。
 */

// 令牌在 localStorage 中的键名
const TOKEN_KEY = 'EnterpriseQA_Token'

/**
 * 获取令牌
 * @returns {string | null} 令牌字符串
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 保存令牌
 * @param {string} token JWT 令牌
 */
export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

/**
 * 移除令牌（退出登录时调用）
 */
export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}
