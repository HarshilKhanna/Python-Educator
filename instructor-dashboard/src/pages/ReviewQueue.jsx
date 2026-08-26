import { useState, useEffect, useCallback } from 'react'
import { getPending, approveAdaptation, rejectAdaptation } from '../api'

export default function ReviewQueue() {
  const [items, setItems]         = useState([])
  const [loading, setLoading]     = useState(true)
  const [error, setError]         = useState(null)
  const [busy, setBusy]           = useState({})         // id → 'approving'|'rejecting'
  const [rejectText, setRejectText] = useState({})       // id → string
  const [showReject, setShowReject] = useState({})       // id → bool
  const [toast, setToast]         = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getPending()
      setItems(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3500)
  }

  const handleApprove = async (id) => {
    setBusy(b => ({ ...b, [id]: 'approving' }))
    try {
      await approveAdaptation(id)
      showToast('Adaptation approved and applied via LearnerModelService.')
      load()
    } catch (e) {
      showToast(e.message, 'error')
    } finally {
      setBusy(b => ({ ...b, [id]: null }))
    }
  }

  const handleReject = async (id) => {
    setBusy(b => ({ ...b, [id]: 'rejecting' }))
    try {
      const reason = rejectText[id] || ''
      await rejectAdaptation(id, reason)
      showToast('Recommendation rejected. No mastery change applied.')
      load()
    } catch (e) {
      showToast(e.message, 'error')
    } finally {
      setBusy(b => ({ ...b, [id]: null }))
      setShowReject(s => ({ ...s, [id]: false }))
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>📋 Review Queue</h1>
        <p>Adaptation recommendations from the Pedagogical Agent awaiting instructor approval.</p>
      </div>

      {toast && (
        <div className={`alert alert-${toast.type === 'error' ? 'error' : 'success'}`}>
          {toast.msg}
        </div>
      )}

      {loading && (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <div className="spinner" style={{ width: 28, height: 28, borderWidth: 3 }} />
        </div>
      )}

      {error && <div className="alert alert-error">Failed to load queue: {error}</div>}

      {!loading && !error && items.length === 0 && (
        <div className="card">
          <div className="empty-state">
            <div className="empty-icon">✅</div>
            <p>No pending recommendations. All caught up!</p>
          </div>
        </div>
      )}

      {!loading && items.length > 0 && (
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table>
            <thead>
              <tr>
                <th>Student</th>
                <th>Recommended Topic</th>
                <th>Activity Type</th>
                <th>Reason</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map(item => (
                <tr key={item.id}>
                  <td>
                    <code style={{ color: 'var(--accent)', fontSize: 12 }}>{item.student_id}</code>
                  </td>
                  <td>
                    <span className="badge badge-pending">{item.next_topic_id}</span>
                  </td>
                  <td>
                    <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                      {item.next_activity_type}
                    </span>
                  </td>
                  <td>
                    <span className="reason-text">{item.reason}</span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                      <div style={{ display: 'flex', gap: 6 }}>
                        <button
                          id={`approve-${item.id}`}
                          className="btn btn-success btn-sm"
                          disabled={!!busy[item.id]}
                          onClick={() => handleApprove(item.id)}
                        >
                          {busy[item.id] === 'approving'
                            ? <><span className="spinner" /> Approving…</>
                            : '✓ Approve'}
                        </button>
                        <button
                          id={`reject-toggle-${item.id}`}
                          className="btn btn-ghost btn-sm"
                          disabled={!!busy[item.id]}
                          onClick={() => setShowReject(s => ({ ...s, [item.id]: !s[item.id] }))}
                        >
                          ✗ Reject
                        </button>
                      </div>
                      {showReject[item.id] && (
                        <div className="reject-inline">
                          <input
                            id={`reject-reason-${item.id}`}
                            type="text"
                            placeholder="Reason (optional)"
                            value={rejectText[item.id] || ''}
                            onChange={e => setRejectText(t => ({ ...t, [item.id]: e.target.value }))}
                            onKeyDown={e => e.key === 'Enter' && handleReject(item.id)}
                            style={{ flex: 1, padding: '6px 10px', fontSize: 12 }}
                          />
                          <button
                            id={`reject-confirm-${item.id}`}
                            className="btn btn-danger btn-sm"
                            disabled={!!busy[item.id]}
                            onClick={() => handleReject(item.id)}
                          >
                            {busy[item.id] === 'rejecting' ? <span className="spinner" /> : 'Confirm'}
                          </button>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <button
        id="refresh-queue"
        className="btn btn-ghost btn-sm"
        onClick={load}
        disabled={loading}
        style={{ marginTop: 8 }}
      >
        ↻ Refresh
      </button>
    </div>
  )
}
