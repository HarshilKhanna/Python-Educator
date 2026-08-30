/**
 * API client for the FastAPI backend.
 *
 * Phase 14 update: the hardcoded dev-token-instructor stub is removed.
 * Tokens are read dynamically from localStorage on every request.
 * A 401 response triggers logout and redirect to the login screen.
 */

const BASE_URL = '/api'

/**
 * Get the current auth token from localStorage.
 * Returns null if not logged in.
 */
function getToken() {
  return localStorage.getItem('auth_token')
}

/**
 * Handle a 401 response — clear stored credentials and redirect to login.
 * This covers both expired tokens and revoked tokens.
 */
function handleUnauthorized() {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_id')
  // Force a full page reload so App.jsx re-evaluates auth state
  window.location.reload()
}

async function request(path, options = {}) {
  const token = getToken()
  const authHeader = token ? { Authorization: `Bearer ${token}` } : {}

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader,
      ...(options.headers || {}),
    },
  })

  if (res.status === 401) {
    handleUnauthorized()
    throw new Error('Session expired. Please log in again.')
  }

  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json()
}

// Review queue
export const getPending = () => request('/review/pending')

export const approveAdaptation = (id) =>
  request(`/review/${id}/approve`, { method: 'POST' })

export const rejectAdaptation = (id, reason) =>
  request(`/review/${id}/reject`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  })

// Materials
export const getTopics = () => request('/curriculum/topics')

export const uploadMaterial = (formData) => {
  const token = getToken()
  return fetch(`${BASE_URL}/materials/upload`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  }).then(async (res) => {
    if (res.status === 401) {
      handleUnauthorized()
      throw new Error('Session expired. Please log in again.')
    }
    if (!res.ok) {
      const text = await res.text()
      throw new Error(`Upload error ${res.status}: ${text}`)
    }
    return res.json()
  })
}

// Students
export const getStudentMastery = (studentId) =>
  request(`/students/${studentId}/mastery`)

// Monitoring — Phase 21
export const getMonitoringStats = (windowHours = 24) =>
  request(`/monitoring/stats?window_hours=${windowHours}`)

export const getAlerts = () => request('/monitoring/alerts')

export const resolveAlert = (id) =>
  request(`/monitoring/alerts/${id}/resolve`, { method: 'POST' })

export const getKillSwitch = () => request('/monitoring/kill-switch')

export const setKillSwitch = (active) =>
  request('/monitoring/kill-switch', {
    method: 'POST',
    body: JSON.stringify({ active }),
  })

export async function getStudents() {
  return request('/students');
}

