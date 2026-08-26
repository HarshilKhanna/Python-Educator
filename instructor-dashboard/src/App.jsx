import { useState } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import ReviewQueue from './pages/ReviewQueue'
import UploadMaterials from './pages/UploadMaterials'
import StudentMastery from './pages/StudentMastery'
import Login from './pages/Login'

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

  if (!isAuthenticated) {
    return <Login onLoginSuccess={() => setIsAuthenticated(true)} />
  }

  return (
    <div className="app">
      <nav className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-icon">🎓</span>
          <span className="logo-text">Python Educator</span>
          <span className="logo-badge">Instructor</span>
        </div>
        <ul className="nav-list">
          <li>
            <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <span className="nav-icon">📋</span>
              Review Queue
            </NavLink>
          </li>
          <li>
            <NavLink to="/upload" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <span className="nav-icon">📤</span>
              Upload Materials
            </NavLink>
          </li>
          <li>
            <NavLink to="/student" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
              <span className="nav-icon">👤</span>
              Student Mastery
            </NavLink>
          </li>
        </ul>
        {/* Logout button — replaces the dev-auth stub note */}
        <button
          id="logout-button"
          className="logout-button"
          onClick={() => handleLogout(setIsAuthenticated)}
        >
          Sign Out
        </button>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<ReviewQueue />} />
          <Route path="/upload" element={<UploadMaterials />} />
          <Route path="/student" element={<StudentMastery />} />
          <Route path="/student/:id" element={<StudentMastery />} />
        </Routes>
      </main>
    </div>
  )
}
