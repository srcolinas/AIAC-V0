import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './Layout.css'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const { isAuthenticated, user, logout } = useAuthStore()
  const navigate = useNavigate()
  
  const handleLogout = () => {
    logout()
    navigate('/')
  }
  
  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <Link to="/" className="logo">
            <svg className="logo-icon" viewBox="0 0 40 40" fill="none">
              <path 
                d="M20 2L38 12V28L20 38L2 28V12L20 2Z" 
                stroke="currentColor" 
                strokeWidth="2"
                fill="none"
              />
              <path 
                d="M20 8L32 15V25L20 32L8 25V15L20 8Z" 
                fill="currentColor" 
                opacity="0.3"
              />
              <circle cx="20" cy="20" r="5" fill="currentColor" />
            </svg>
            <span className="logo-text">Teyuna</span>
          </Link>
          
          <nav className="nav">
            <Link to="/rules" className="nav-link">Rules</Link>
            
            {isAuthenticated ? (
              <>
                <Link to="/lobby" className="nav-link">Play</Link>
                <div className="user-menu">
                  <span className="user-name">{user?.username}</span>
                  <button onClick={handleLogout} className="btn btn-secondary btn-sm">
                    Logout
                  </button>
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className="nav-link">Login</Link>
                <Link to="/register" className="btn btn-primary btn-sm">
                  Register
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>
      
      <main className="main">
        {children}
      </main>
      
      <footer className="footer">
        <div className="footer-content">
          <p className="footer-text">
            Teyuna — Honoring the legacy of the Tayrona people
          </p>
          <p className="footer-subtitle">
            Sierra Nevada de Santa Marta, Colombia
          </p>
        </div>
      </footer>
    </div>
  )
}

