import { useState, useEffect } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import ReviewQueue from './pages/ReviewQueue'
import UploadMaterials from './pages/UploadMaterials'
import StudentMastery from './pages/StudentMastery'
import Monitoring from './pages/Monitoring'
import Login from './pages/Login'
import { getKillSwitch, setKillSwitch } from './api'

function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    () => !!localStorage.getItem('auth_token')
  )
  return { isAuthenticated, setIsAuthenticated }
}

function handleLogout(setIsAuthenticated) {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user_role')
  localStorage.removeItem('user_id')
  setIsAuthenticated(false)
}

export default function App() {
  const { isAuthenticated, setIsAuthenticated } = useAuth()
  const [killSwitchActive, setKillSwitchActive] = useState(false)

  useEffect(() => {
    if (isAuthenticated) {
      getKillSwitch().then(res => setKillSwitchActive(res.active)).catch(console.error)
    }
  }, [isAuthenticated])

  const toggleKillSwitch = async () => {
    const newState = !killSwitchActive
    setKillSwitchActive(newState)
    try {
      await setKillSwitch(newState)
    } catch (e) {
      console.error(e)
      setKillSwitchActive(!newState) // Revert on failure
    }
  }

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />
  }

  return (
    <div className="app">
      <header className="navbar">
        <div className="nav-brand">
          <span className="logo-text">Python Educator</span>
        </div>
        <nav className="nav-links">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
            Review Queue
          </NavLink>
          <NavLink to="/upload" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
            Materials
          </NavLink>
          <NavLink to="/student" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
            Mastery
          </NavLink>
          <NavLink to="/monitoring" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
            Monitoring
          </NavLink>
        </nav>
        <div className="nav-actions">
          <button
            onClick={toggleKillSwitch}
            className={`btn ${killSwitchActive ? 'btn-danger' : 'btn-ghost'} btn-sm`}
          >
            {killSwitchActive ? 'AI MANUAL' : 'AI AUTO'}
          </button>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => handleLogout(setIsAuthenticated)}
          >
            Sign Out
          </button>
        </div>
      </header>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<ReviewQueue />} />
          <Route path="/upload" element={<UploadMaterials />} />
          <Route path="/student" element={<StudentMastery />} />
          <Route path="/student/:id" element={<StudentMastery />} />
          <Route path="/monitoring" element={<Monitoring />} />
        </Routes>
      </main>
    </div>
  )
}
