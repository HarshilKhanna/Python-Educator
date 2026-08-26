/**
 * API client for the FastAPI backend.
 *
 * All requests include a dev-only auth stub header.
 * NOTE: This is NOT production authentication — hardcoded token for the
 * Research Prototype phase only. Replace with real JWT/RBAC before any pilot.
 */

const BASE_URL = '/api'

// DEV-ONLY: hardcoded instructor token. NOT production-ready.
const AUTH_HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer dev-token-instructor',
}

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { ...AUTH_HEADERS, ...(options.headers || {}) },
  })
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

export const uploadMaterial = (formData) =>
  fetch(`${BASE_URL}/materials/upload`, {
    method: 'POST',
    headers: { Authorization: AUTH_HEADERS.Authorization },
    body: formData,
  }).then(async (res) => {
    if (!res.ok) {
      const text = await res.text()
      throw new Error(`Upload error ${res.status}: ${text}`)
    }
    return res.json()
  })

// Students
export const getStudentMastery = (studentId) =>
  request(`/students/${studentId}/mastery`)
