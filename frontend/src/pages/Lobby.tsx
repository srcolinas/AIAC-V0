import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useGameStore, GameSummary } from '../store/gameStore'
import { useAuthStore } from '../store/authStore'
import './Lobby.css'

export default function Lobby() {
  const [joinToken, setJoinToken] = useState('')
  const [maxPlayers, setMaxPlayers] = useState(4)
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  const { myGames, isLoading, error, createGame, joinGame, fetchMyGames, clearError } = useGameStore()
  const { user } = useAuthStore()
  const navigate = useNavigate()
  
  useEffect(() => {
    fetchMyGames()
  }, [fetchMyGames])
  
  const handleCreateGame = async () => {
    clearError()
    const token = await createGame(maxPlayers)
    if (token) {
      navigate(`/game/${token}`)
    }
  }
  
  const handleJoinGame = async () => {
    if (!joinToken.trim()) return
    
    clearError()
    const success = await joinGame(joinToken.trim())
    if (success) {
      navigate(`/game/${joinToken.trim()}`)
    }
  }
  
  const handleRejoinGame = (token: string) => {
    navigate(`/game/${token}`)
  }
  
  const getStatusBadge = (status: string) => {
    const badges: Record<string, { class: string; text: string }> = {
      waiting: { class: 'badge-waiting', text: 'Waiting' },
      active: { class: 'badge-active', text: 'In Progress' },
      finished: { class: 'badge-finished', text: 'Finished' }
    }
    return badges[status] || { class: '', text: status }
  }
  
  return (
    <div className="lobby-page">
      <div className="lobby-header animate-slide-up">
        <h1>Welcome, {user?.username}</h1>
        <p>Choose your path to Teyuna</p>
      </div>
      
      <div className="lobby-content">
        {/* Actions */}
        <div className="lobby-actions animate-fade-in">
          <div className="action-card">
            <div className="action-icon">
              <svg viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2" />
                <path d="M24 14v20M14 24h20" stroke="currentColor" strokeWidth="2" />
              </svg>
            </div>
            <h3>Create New Game</h3>
            <p>Start a new game and invite others to join your settlement.</p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateModal(true)}
            >
              Create Game
            </button>
          </div>
          
          <div className="action-card">
            <div className="action-icon">
              <svg viewBox="0 0 48 48" fill="none">
                <path d="M12 24h24M36 24l-8 8M36 24l-8-8" stroke="currentColor" strokeWidth="2" />
                <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2" />
              </svg>
            </div>
            <h3>Join Existing Game</h3>
            <p>Enter a game token to join friends in their settlement.</p>
            <div className="join-form">
              <input
                type="text"
                className="input"
                value={joinToken}
                onChange={(e) => setJoinToken(e.target.value)}
                placeholder="Enter game token"
                maxLength={32}
              />
              <button 
                className="btn btn-primary"
                onClick={handleJoinGame}
                disabled={!joinToken.trim() || isLoading}
              >
                Join
              </button>
            </div>
          </div>
        </div>
        
        {error && (
          <div className="lobby-error">
            {error}
            <button onClick={clearError} className="error-close">×</button>
          </div>
        )}
        
        {/* My Games */}
        <div className="my-games animate-fade-in" style={{ animationDelay: '0.2s' }}>
          <h2>Your Games</h2>
          
          {myGames.length === 0 ? (
            <div className="no-games">
              <p>You haven't joined any games yet.</p>
              <p>Create a new game or join one using a token.</p>
            </div>
          ) : (
            <div className="games-list">
              {myGames.map((game: GameSummary) => {
                const badge = getStatusBadge(game.status)
                return (
                  <div key={game.id} className="game-card">
                    <div className="game-info">
                      <div className="game-token">
                        <span className="token-label">Token:</span>
                        <code>{game.token}</code>
                      </div>
                      <div className="game-meta">
                        <span className={`badge ${badge.class}`}>{badge.text}</span>
                        <span className="player-count">
                          {game.current_players}/{game.max_players} players
                        </span>
                      </div>
                    </div>
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleRejoinGame(game.token)}
                    >
                      {game.status === 'finished' ? 'View' : 'Enter'}
                    </button>
                  </div>
                )
              })}
            </div>
          )}
        </div>
        
        {/* Stats */}
        {user && (
          <div className="player-stats animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <h2>Your Legacy</h2>
            <div className="stats-grid">
              <div className="stat-item">
                <span className="stat-value">{user.games_played}</span>
                <span className="stat-label">Games Played</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{user.games_won}</span>
                <span className="stat-label">Victories</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{user.total_points}</span>
                <span className="stat-label">Total Points</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">
                  {user.games_played > 0 
                    ? Math.round((user.games_won / user.games_played) * 100) 
                    : 0}%
                </span>
                <span className="stat-label">Win Rate</span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Create Game Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Game</h2>
            <p>Choose how many players can join your settlement.</p>
            
            <div className="player-select">
              <button
                className={`player-option ${maxPlayers === 3 ? 'active' : ''}`}
                onClick={() => setMaxPlayers(3)}
              >
                <span className="player-count-big">3</span>
                <span>Players</span>
              </button>
              <button
                className={`player-option ${maxPlayers === 4 ? 'active' : ''}`}
                onClick={() => setMaxPlayers(4)}
              >
                <span className="player-count-big">4</span>
                <span>Players</span>
              </button>
            </div>
            
            <div className="modal-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCreateModal(false)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary"
                onClick={handleCreateGame}
                disabled={isLoading}
              >
                {isLoading ? 'Creating...' : 'Create Game'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

