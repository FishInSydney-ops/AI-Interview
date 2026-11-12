import { apiRequest } from '@yunshu/shared/api'

export interface AdminSession {
  id: number
  is_super: boolean
  must_change_password: boolean
  permissions: string[]
  username: string
  expires_at: string
}

export const authApi = {
  login: (username: string, password: string) => apiRequest<{ expires_at: string }>(
    '/api/v1/admin/auth/sessions', { method: 'POST', body: JSON.stringify({ username, password }) },
  ),
  session: () => apiRequest<AdminSession>('/api/v1/admin/auth/session'),
  logout: () => apiRequest<null>('/api/v1/admin/auth/session', { method: 'DELETE' }),
}
