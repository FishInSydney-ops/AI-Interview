export interface ApiResponse<T> {
  code: string
  message: string
  data: T
  request_id: string
  details?: { field: string; reason: string }[]
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code: string,
    public requestId: string,
  ) {
    super(message)
  }
}

export interface Readiness {
  status: 'ready' | 'degraded'
  services: Record<'mysql' | 'redis' | 'minio', 'ok' | 'unavailable'>
}

// 相对 URL 由当前前端的 Vite 代理转发；从不把密码或令牌写入 localStorage。
export async function getReadiness(signal?: AbortSignal): Promise<ApiResponse<Readiness>> {
  const response = await fetch('/api/v1/ready', { credentials: 'same-origin', signal })
  const body: ApiResponse<Readiness> = await response.json()
  // 503 的 data 包含真实依赖状态，交给状态组件展示；其他错误统一抛出。
  if ((!response.ok && response.status !== 503) || !['OK', 'SERVICE_UNAVAILABLE'].includes(body.code)) {
    throw new ApiError(body.message, response.status, body.code, body.request_id)
  }
  return body
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body) headers.set('Content-Type', 'application/json')
  if (init.method && !['GET', 'HEAD'].includes(init.method.toUpperCase())) {
    headers.set('X-Requested-With', 'XMLHttpRequest')
  }
  const response = await fetch(path, {
    ...init, headers, credentials: 'same-origin',
    signal: init.signal ?? AbortSignal.timeout(15000),
  })
  let body: ApiResponse<T>
  try {
    body = await response.json()
  } catch {
    throw new ApiError('服务响应异常，请稍后重试', response.status, 'INVALID_RESPONSE', '')
  }
  if (!response.ok || body.code !== 'OK') {
    throw new ApiError(body.message, response.status, body.code, body.request_id)
  }
  return body.data
}
