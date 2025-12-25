import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './Auth.css'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { login, isLoading, error, clearError } = useAuthStore()
  const navigate = useNavigate()
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    clearError()
    
    const success = await login(username, password)
    if (success) {
      navigate('/lobby')
    }
  }
  
  return (
    <div className="auth-page">
      <div className="auth-container animate-slide-up">
        <div className="auth-header">
          <h1>Return to Teyuna</h1>
          <p>Welcome back, traveler</p>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="auth-error">
              {error}
            </div>
          )}
          
          <div className="form-group">
            <label className="label" htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              className="input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              autoFocus
            />
          </div>
          
          <div className="form-group">
            <label className="label" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Entering...' : 'Enter the City'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>
            New to Teyuna?{' '}
            <Link to="/register">Begin your journey</Link>
          </p>
        </div>
      </div>
      
      <div className="auth-decoration">
        <svg viewBox="0 0 200 200" className="auth-pattern">
          <defs>
            <pattern id="tayrona-pattern" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M20 0L40 20L20 40L0 20Z" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.3" />
              <circle cx="20" cy="20" r="3" fill="currentColor" opacity="0.2" />
            </pattern>
          </defs>
          <rect width="200" height="200" fill="url(#tayrona-pattern)" />
        </svg>
      </div>
    </div>
  )
}

