import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ApiError } from '@yunshu/shared/api'
import { authApi, type AdminSession } from '../api/auth'

export const useAdminAuth = defineStore('admin-auth', () => {
  const session = ref<AdminSession | null>(null)

  async function refreshSession() {
    try {
      session.value = await authApi.session()
      return session.value
    } catch (error) {
      session.value = null
      if (error instanceof ApiError && error.status === 401) return null
      throw error
    }
  }

  async function login(username: string, password: string) {
    await authApi.login(username, password)
    await refreshSession()
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (error) {
      // 会话已经失效时同样返回登录页；网络失败时保留当前状态并反馈。
      if (!(error instanceof ApiError && error.status === 401)) throw error
    }
    session.value = null
  }

  return { session, refreshSession, login, logout }
})
