import { useState, useEffect, useCallback } from 'react'
import {
  getMonitoringStats,
  getAlerts,
  resolveAlert,
  getKillSwitch,
  setKillSwitch,
} from '../api'

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StatCard({ label, value, sub, accent }) {
  return (
    <div className="stat-card" style={{ borderTop: `3px solid ${accent}` }}>
      <div className="stat-value" style={{ color: accent }}>{value}</div>
      <div className="stat-label">{label}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  )
}

function TierBar({ label, count, total, color }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0
  return (
    <div className="tier-bar-row">
      <span className="tier-label">{label}</span>
      <div className="tier-bar-track">
        <div
          className="tier-bar-fill"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>
      <span className="tier-count">{count} ({pct}%)</span>
    </div>
  )
}

function KillSwitchPanel({ active, source, onToggle, loading }) {
  return (
    <div className={`kill-switch-panel ${active ? 'ks-active' : ''}`}>
      <div className="ks-header">
        <span className="ks-icon">{active ? '!' : '✓'}</span>
        <div>
          <div className="ks-title">Auto-Apply Kill-Switch</div>
          <div className="ks-desc">
            {active
              ? 'ACTIVE — all recommendations routed to manual review regardless of risk tier'
              : 'Inactive — risk-tiered auto-approval is running normally'}
          </div>
          <div className="ks-source">Setting source: <code>{source}</code></div>
        </div>
      </div>
      <button
        id="kill-switch-toggle"
        className={`btn ${active ? 'btn-danger' : 'btn-warning'}`}
        onClick={onToggle}
        disabled={loading}
      >
        {loading ? 'Updating…' : active ? 'Disable Kill-Switch' : 'Enable Kill-Switch'}
      </button>
    </div>
  )
}

function AlertRow({ alert, onResolve }) {
  const isNew = (Date.now() - new Date(alert.created_at).getTime()) < 5 * 60 * 1000
  return (
    <div className={`alert-row ${alert.alert_type === 'thrashing' ? 'alert-thrash' : 'alert-spike'}`}>
      <div className="alert-header">
        <span className="alert-type-badge">
          {alert.alert_type === 'thrashing' ? 'Thrashing' : 'Rate Spike'}
        </span>
        {isNew && <span className="alert-new-badge">NEW</span>}
        <span className="alert-time">{new Date(alert.created_at).toLocaleString()}</span>
      </div>
      <div className="alert-body">
        {alert.student_id && (
          <div className="alert-student">Student: <code>{alert.student_id.slice(0, 8)}…</code></div>
        )}
        {alert.alert_type === 'thrashing' ? (
          <div className="alert-detail">
            <strong>{alert.detail.count}</strong> auto-applied advancements in{' '}
            <strong>{alert.detail.window_minutes} min</strong> (threshold: {alert.detail.threshold})
          </div>
        ) : (
          <div className="alert-detail">
            Signal <code>{alert.detail.signal_type}</code>: <strong>{alert.detail.recent_count}</strong> events
            in last {alert.detail.recent_window_hours}h vs baseline{' '}
            <strong>{alert.detail.hourly_baseline}/hr</strong> ({alert.detail.spike_multiplier}× threshold)
          </div>
        )}
      </div>
      <button
        className="btn btn-sm btn-secondary"
        id={`resolve-alert-${alert.id}`}
        onClick={() => onResolve(alert.id)}
      >
        Resolve
      </button>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function Monitoring() {
  const [stats, setStats] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [ksActive, setKsActive] = useState(false)
  const [ksSource, setKsSource] = useState('env')
  const [windowHours, setWindowHours] = useState(24)
  const [loading, setLoading] = useState(true)
  const [ksLoading, setKsLoading] = useState(false)
  const [error, setError] = useState(null)

  const refresh = useCallback(async () => {
    try {
      setError(null)
      const [statsData, alertsData, ksData] = await Promise.all([
        getMonitoringStats(windowHours),
        getAlerts(),
        getKillSwitch(),
      ])
      setStats(statsData)
      setAlerts(alertsData)
      setKsActive(ksData.active)
      setKsSource(ksData.source)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [windowHours])

  useEffect(() => {
    setLoading(true)
    refresh()
    const interval = setInterval(refresh, 30_000)  // auto-refresh every 30s
    return () => clearInterval(interval)
  }, [refresh])

  const handleKsToggle = async () => {
    setKsLoading(true)
    try {
      await setKillSwitch(!ksActive)
      setKsActive(!ksActive)
      setKsSource('db')
    } catch (err) {
      setError(`Kill-switch error: ${err.message}`)
    } finally {
      setKsLoading(false)
    }
  }

  const handleResolve = async (alertId) => {
    try {
      await resolveAlert(alertId)
      setAlerts(prev => prev.filter(a => a.id !== alertId))
    } catch (err) {
      setError(`Resolve error: ${err.message}`)
    }
  }

  if (loading) {
    return (
      <div className="page-content">
        <div className="loading-spinner">
          <div className="spinner" />
          <span>LoadingMonitoring data…</span>
        </div>
      </div>
    )
  }

  const totalActivity = stats
    ? stats.total_auto_applied + stats.total_reviewed
    : 0

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">📊Monitoring</h1>
        <div className="page-actions">
          <select
            id="window-hours-select"
            className="select-input"
            value={windowHours}
            onChange={e => setWindowHours(Number(e.target.value))}
          >
            <option value={1}>Last 1 hour</option>
            <option value={6}>Last 6 hours</option>
            <option value={24}>Last 24 hours</option>
            <option value={168}>Last 7 days</option>
          </select>
          <button id="refresh-btn" className="btn btn-secondary" onClick={refresh}>
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">Error: {error}</div>
      )}

      {/* Kill-switch */}
      <section className="monitoring-section">
        <KillSwitchPanel
          active={ksActive}
          source={ksSource}
          onToggle={handleKsToggle}
          loading={ksLoading}
        />
      </section>

      {/* Stats overview */}
      {stats && (
        <section className="monitoring-section">
          <h2 className="section-title">Adaptation Volume</h2>
          <p className="section-sub">
            Last {stats.window_hours}h (since {new Date(stats.since).toLocaleString()})
          </p>
          <div className="stat-grid">
            <StatCard
              label="Auto-Applied"
              value={stats.total_auto_applied}
              sub="source=pedagogical_agent_auto"
              accent="var(--color-success)"
            />
            <StatCard
              label="Human Reviewed"
              value={stats.total_reviewed}
              sub="source=instructor_review_approval"
              accent="var(--color-primary)"
            />
            <StatCard
              label="Total Activity"
              value={totalActivity}
              accent="var(--color-text-secondary)"
            />
            <StatCard
              label="Open Alerts"
              value={alerts.length}
              accent={alerts.length > 0 ? 'var(--color-danger)' : 'var(--color-success)'}
            />
          </div>

          <h3 className="section-subtitle">Auto-Applied by Risk Tier</h3>
          <div className="tier-bars">
            <TierBar
              label="Low"
              count={stats.by_tier.low}
              total={stats.total_auto_applied}
              color="var(--color-success)"
            />
            <TierBar
              label="Medium"
              count={stats.by_tier.medium}
              total={stats.total_auto_applied}
              color="var(--color-warning)"
            />
            <TierBar
              label="High"
              count={stats.by_tier.high || 0}
              total={stats.total_auto_applied}
              color="var(--color-danger)"
            />
          </div>
        </section>
      )}

      {/* Anomaly alerts */}
      <section className="monitoring-section">
        <h2 className="section-title">
          Anomaly Alerts
          {alerts.length > 0 && (
            <span className="alert-badge-count">{alerts.length}</span>
          )}
        </h2>
        {alerts.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">✓</span>
            <p>No open anomaly alerts. System looks healthy.</p>
          </div>
        ) : (
          <div className="alerts-list">
            {alerts.map(alert => (
              <AlertRow key={alert.id} alert={alert} onResolve={handleResolve} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
