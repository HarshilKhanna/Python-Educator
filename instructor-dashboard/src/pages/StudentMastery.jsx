import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getStudentMastery, getStudents } from '../api'

export default function StudentMastery() {
  const { id: paramId } = useParams()
  const navigate = useNavigate()
  const [studentId, setStudentId] = useState(paramId || '')
  const [students, setStudents] = useState([])
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getStudents()
      .then(res => setStudents(res.students || []))
      .catch(console.error)
  }, [])

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!studentId.trim()) return
    setLoading(true)
    setError(null)
    setData(null)
    navigate(`/student/${studentId}`, { replace: true })
    try {
      const result = await getStudentMastery(studentId.trim())
      setData(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  // Auto-load if there's a param ID
  if (paramId && !data && !loading && !error) {
    handleSearch()
  }

  const masteryColor = (level) => {
    if (level >= 0.7) return 'var(--success)'
    if (level >= 0.4) return 'var(--warning)'
    return 'var(--danger)'
  }

  return (
    <div>
      <div className="page-header"><div className="page-header-left">
        <h1>Student Mastery View</h1>
        <p>Per-topic mastery state and recent adaptation reasons — the instructor's explainability view.</p></div>
      </div>

      <div className="card">
        <form id="student-search-form" onSubmit={handleSearch} style={{ display: 'flex', gap: 10 }}>
          <select
            id="student-id-input"
            value={studentId}
            onChange={e => setStudentId(e.target.value)}
            style={{ flex: 1 }}
            className="form-input"
          >
            <option value="" disabled>Select a student...</option>
            {students.map(s => (
              <option key={s.id} value={s.id}>
                {s.email} ({s.id.slice(0, 8)}...)
              </option>
            ))}
          </select>
          <button
            id="student-search-btn"
            type="submit"
            className="btn btn-primary"
            disabled={!studentId.trim() || loading}
          >
            {loading ? <><span className="spinner" /> Loading…</> : 'View Mastery'}
          </button>
        </form>
      </div>

      {error && <div className="alert alert-error">Failed to load: {error}</div>}

      {data && (
        <>
          <div className="card">
            <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: 'var(--text-muted)' }}>
              Per-topic mastery — <code style={{ color: 'var(--accent)' }}>{data.student_id}</code>
            </h2>
            {data.mastery.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">!</div>
                <p>No mastery data yet. Student hasn't completed any activities.</p>
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Topic</th>
                    <th>Mastery</th>
                    <th>Confidence</th>
                    <th>Last Updated</th>
                  </tr>
                </thead>
                <tbody>
                  {data.mastery.map(m => (
                    <tr key={m.topic_id}>
                      <td>
                        <span className="badge badge-pending">{m.topic_id}</span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div className="mastery-bar-wrap">
                            <div
                              className="mastery-bar"
                              style={{
                                width: `${Math.round(m.mastery_level * 100)}%`,
                                background: masteryColor(m.mastery_level),
                              }}
                            />
                          </div>
                          <span style={{ fontSize: 13, color: masteryColor(m.mastery_level), fontWeight: 600 }}>
                            {Math.round(m.mastery_level * 100)}%
                          </span>
                        </div>
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 13 }}>
                        {Math.round(m.confidence * 100)}%
                      </td>
                      <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                        {m.last_updated ? new Date(m.last_updated).toLocaleString() : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="card">
            <h2 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16, color: 'var(--text-muted)' }}>
              Recent adaptation events
            </h2>
            {data.recent_events.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">-</div>
                <p>No adaptation events recorded yet.</p>
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Topic</th>
                    <th>Signal</th>
                    <th>Δ Mastery</th>
                    <th>Why (Pedagogical Agent reason)</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent_events.map((ev, i) => (
                    <tr key={i}>
                      <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        {ev.timestamp ? new Date(ev.timestamp).toLocaleString() : '—'}
                      </td>
                      <td>
                        <span className="badge badge-pending">{ev.topic_id}</span>
                      </td>
                      <td>
                        <span className={`badge ${ev.signal === 'correct' ? 'badge-approved' : ev.signal === 'incorrect' ? 'badge-rejected' : 'badge-pending'}`}>
                          {ev.signal}
                        </span>
                      </td>
                      <td style={{ fontSize: 13, color: ev.delta >= 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 600 }}>
                        {ev.delta >= 0 ? '+' : ''}{ev.delta.toFixed(3)}
                      </td>
                      <td>
                        {ev.reason
                          ? <span className="reason-text">{ev.reason}</span>
                          : <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>—</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  )
}
