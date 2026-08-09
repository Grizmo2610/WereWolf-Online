const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: options.method || 'GET',
    credentials: 'include',
    headers: options.body ? { 'Content-Type': 'application/json' } : undefined,
    body: options.body ? JSON.stringify(options.body) : undefined,
  })

  let data = null
  try {
    data = await res.json()
  } catch {
    // no body
  }

  if (!res.ok) {
    throw new ApiError(data?.detail || 'Có lỗi xảy ra', res.status)
  }
  return data
}

export const api = {
  register: (username, password, displayName) =>
    request('/auth/register', { method: 'POST', body: { username, password, display_name: displayName } }),
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: { username, password } }),
  logout: () => request('/auth/logout', { method: 'POST' }),
  me: () => request('/auth/me'),

  listScenarios: () => request('/rooms/scenarios'),
  createRoom: (scenarioId) => request('/rooms', { method: 'POST', body: { scenario_id: scenarioId } }),
  joinRoom: (roomCode) => request('/rooms/join', { method: 'POST', body: { room_code: roomCode } }),
  getRoom: (roomCode) => request(`/rooms/${roomCode}`),
}

export const WS_BASE = API_BASE.replace(/^http/, 'ws')

export { ApiError }
