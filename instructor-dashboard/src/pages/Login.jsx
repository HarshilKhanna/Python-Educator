import { useState } from 'react'

const BASE_URL = '/api'

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        if (res.status === 401) {
          throw new Error('Incorrect email or password.')
        }
        throw new Error(data.detail || `Login failed (${res.status})`)
      }

      const data = await res.json()

      // Require instructor role — students don't belong in this dashboard
      if (data.role !== 'instructor') {
        throw new Error(
          'This dashboard is for instructors only. ' +
          'Please log in with an instructor account.'
        )
      }

      // Store token in localStorage for this session
      localStorage.setItem('auth_token', data.access_token)
      localStorage.setItem('user_role', data.role)
      localStorage.setItem('user_id', data.user_id)

      onLoginSuccess()
    } catch (err) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <h1 style={{ fontSize: '28px', fontWeight: '900', color: 'var(--text)', marginBottom: '8px' }}>Python Educator</h1>
          <p className="login-subtitle" style={{ color: 'var(--text-muted)', fontWeight: '700', marginBottom: '24px' }}>Instructor Dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
              placeholder="instructor@school.edu"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="form-input"
            />
          </div>

          {error && (
            <div className="alert alert-error" role="alert" style={{ marginBottom: '16px', color: 'var(--danger)', fontWeight: '700' }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '16px', fontSize: '16px' }}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="spinner-small" />
            ) : (
              'Sign In'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
