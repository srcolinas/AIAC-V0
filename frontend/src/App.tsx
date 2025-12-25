import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Lobby from './pages/Lobby'
import Game from './pages/Game'
import Rules from './pages/Rules'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/rules" element={<Rules />} />
        <Route 
          path="/lobby" 
          element={
            <ProtectedRoute>
              <Lobby />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/game/:token" 
          element={
            <ProtectedRoute>
              <Game />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </Layout>
  )
}

export default App

