/**
 * 用户状态管理（Pinia）
 *
 * 集中管理登录令牌和当前用户信息，
 * 供路由守卫、布局菜单等模块共享使用。
 */

import { defineStore } from 'pinia'

import { getMyInfo, login as loginApi } from '../api/auth'
import { getToken, removeToken, setToken } from '../utils/auth'

export const useUserStore = defineStore('user', {
  // 状态：token 初始值取自 localStorage，用户信息初始为空
  state: () => ({
    token: getToken() || '',
    userInfo: null,
  }),

  getters: {
    /**
     * 当前用户是否为管理员
     * @param {object} state 状态对象
     * @returns {boolean}
     */
    isAdmin: (state) => state.userInfo?.role === 'admin',
  },

  actions: {
    /**
     * 登录：调用接口获取令牌并持久化
     * @param {{ username: string, password: string }} form 登录表单
     */
    async login(form) {
      const data = await loginApi(form)
      this.token = data.access_token
      setToken(data.access_token)
    },

    /**
     * 拉取并缓存当前登录用户信息
     * @returns {Promise<object>} 用户信息
     */
    async fetchUserInfo() {
      this.userInfo = await getMyInfo()
      return this.userInfo
    },

    /**
     * 退出登录：清空内存状态和本地令牌
     */
    logout() {
      this.token = ''
      this.userInfo = null
      removeToken()
    },
  },
})
