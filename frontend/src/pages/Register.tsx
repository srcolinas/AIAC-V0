import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './Auth.css'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [localError, setLocalError] = useState('')
  
  const { register, isLoading, error, clearError } = useAuthStore()
  const navigate = useNavigate()
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    clearError()
    setLocalError('')
    
    if (password !== confirmPassword) {
      setLocalError('Passwords do not match')
      return
    }
    
    if (password.length < 6) {
      setLocalError('Password must be at least 6 characters')
      return
    }
    
    const success = await register(username, email, password)
    if (success) {
      navigate('/lobby')
    }
  }
  
  const displayError = localError || error
  
  return (
    <div className="auth-page">
      <div className="auth-container animate-slide-up">
        <div className="auth-header">
          <h1>Join Teyuna</h1>
          <p>Begin your journey to the Lost City</p>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form">
          {displayError && (
            <div className="auth-error">
              {displayError}
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
              placeholder="Choose a username"
              pattern="^[a-zA-Z0-9_]+$"
              minLength={3}
              maxLength={50}
              required
              autoFocus
            />
            <span className="input-hint">Letters, numbers, and underscores only</span>
          </div>
          
          <div className="form-group">
            <label className="label" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
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
              placeholder="Create a password"
              minLength={6}
              required
            />
            <span className="input-hint">At least 6 characters</span>
          </div>
          
          <div className="form-group">
            <label className="label" htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              className="input"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              required
            />
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Begin Journey'}
          </button>
        </form>
        
        <div className="auth-footer">
          <p>
            Already a citizen?{' '}
            <Link to="/login">Return to Teyuna</Link>
          </p>
        </div>
      </div>
      
      <div className="auth-decoration">
        <svg viewBox="0 0 200 200" className="auth-pattern">
          <defs>
            <pattern id="tayrona-pattern-2" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M20 0L40 20L20 40L0 20Z" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.3" />
              <circle cx="20" cy="20" r="3" fill="currentColor" opacity="0.2" />
            </pattern>
          </defs>
          <rect width="200" height="200" fill="url(#tayrona-pattern-2)" />
        </svg>
      </div>
    </div>
  )
}

