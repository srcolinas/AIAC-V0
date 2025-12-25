import { useEffect, useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useGameStore, Player, HexTile } from '../store/gameStore'
import { useAuthStore } from '../store/authStore'
import { GameWebSocket } from '../services/api'
import HexBoard from '../components/game/HexBoard'
import PlayerPanel from '../components/game/PlayerPanel'
import ResourceBar from '../components/game/ResourceBar'
import GameActions from '../components/game/GameActions'
import './Game.css'

export default function Game() {
  const { token } = useParams<{ token: string }>()
  const navigate = useNavigate()
  
  const { currentGame, isLoading, error, fetchGame, startGame, rollDice, build, endTurn, clearError } = useGameStore()
  const { user, token: authToken } = useAuthStore()
  
  const [ws, setWs] = useState<GameWebSocket | null>(null)
  const [lastRoll, setLastRoll] = useState<{ dice1: number; dice2: number } | null>(null)
  const [selectedAction, setSelectedAction] = useState<string | null>(null)
  const [chatMessages, setChatMessages] = useState<Array<{ user_id: number; message: string }>>([])
  
  // Fetch game on mount
  useEffect(() => {
    if (token) {
      fetchGame(token)
    }
  }, [token, fetchGame])
  
  // Setup WebSocket
  useEffect(() => {
    if (token && authToken && currentGame) {
      const websocket = new GameWebSocket(token, authToken, (data) => {
        handleWsMessage(data)
      })
      websocket.connect()
      setWs(websocket)
      
      return () => {
        websocket.disconnect()
      }
    }
  }, [token, authToken, currentGame?.game_id])
  
  const handleWsMessage = useCallback((data: any) => {
    switch (data.type) {
      case 'player_connected':
      case 'player_disconnected':
      case 'game_started':
      case 'dice_rolled':
      case 'build':
      case 'turn_ended':
        // Refresh game state
        if (token) {
          fetchGame(token)
        }
        break
      case 'chat':
        setChatMessages(prev => [...prev.slice(-50), data])
        break
    }
  }, [token, fetchGame])
  
  // Find current player
  const myPlayer = currentGame?.players.find(p => p.user_id === user?.id)
  const currentTurnPlayer = currentGame?.players.find(p => p.id === currentGame.current_player_id)
  const isMyTurn = myPlayer?.id === currentGame?.current_player_id
  const isHost = myPlayer?.is_host
  const canStart = isHost && currentGame?.status === 'waiting' && (currentGame?.players.length ?? 0) >= 3
  
  const handleStartGame = async () => {
    if (token) {
      await startGame(token)
    }
  }
  
  const handleRollDice = async () => {
    if (token) {
      const result = await rollDice(token)
      if (result) {
        setLastRoll(result)
      }
    }
  }
  
  const handleBuild = async (buildingType: string, positionId: number) => {
    if (token) {
      await build(token, buildingType, positionId)
      setSelectedAction(null)
    }
  }
  
  const handleEndTurn = async () => {
    if (token) {
      await endTurn(token)
      setLastRoll(null)
    }
  }
  
  const copyToken = () => {
    if (token) {
      navigator.clipboard.writeText(token)
    }
  }
  
  if (isLoading && !currentGame) {
    return (
      <div className="game-loading">
        <div className="loading-spinner" />
        <p>Entering Teyuna...</p>
      </div>
    )
  }
  
  if (error && !currentGame) {
    return (
      <div className="game-error">
        <h2>Cannot Enter Game</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={() => navigate('/lobby')}>
          Return to Lobby
        </button>
      </div>
    )
  }
  
  if (!currentGame) {
    return null
  }
  
  // Waiting room
  if (currentGame.status === 'waiting') {
    return (
      <div className="waiting-room">
        <div className="waiting-content animate-slide-up">
          <h1>Gathering at Teyuna</h1>
          <p className="waiting-subtitle">
            Waiting for travelers to join the settlement
          </p>
          
          <div className="token-display">
            <span className="token-label">Game Token</span>
            <div className="token-value">
              <code>{currentGame.token}</code>
              <button className="copy-btn" onClick={copyToken} title="Copy token">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" />
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                </svg>
              </button>
            </div>
            <span className="token-hint">Share this token with friends to invite them</span>
          </div>
          
          <div className="players-list">
            <h3>Travelers ({currentGame.players.length}/{currentGame.board.hexes.length > 0 ? 4 : currentGame.players.length + 1})</h3>
            {currentGame.players.map((player: Player) => (
              <div key={player.id} className={`player-item ${player.color}`}>
                <div className={`player-color-dot ${player.color}`} />
                <span className="player-name">
                  {player.username}
                  {player.is_host && <span className="host-badge">Host</span>}
                  {player.user_id === user?.id && <span className="you-badge">You</span>}
                </span>
              </div>
            ))}
          </div>
          
          {canStart ? (
            <button className="btn btn-primary btn-lg" onClick={handleStartGame}>
              Begin the Journey
            </button>
          ) : isHost ? (
            <p className="waiting-hint">Need at least 3 players to start</p>
          ) : (
            <p className="waiting-hint">Waiting for host to start the game...</p>
          )}
        </div>
      </div>
    )
  }
  
  // Game over
  if (currentGame.status === 'finished') {
    const winner = currentGame.players.find(p => p.user_id === currentGame.winner_id)
    const isWinner = user?.id === currentGame.winner_id
    
    return (
      <div className="game-over">
        <div className="game-over-content animate-slide-up">
          <div className="victory-icon">
            <svg viewBox="0 0 64 64" fill="none">
              <circle cx="32" cy="32" r="28" stroke="currentColor" strokeWidth="2" />
              <path d="M32 12L38 26H52L40 36L46 52L32 42L18 52L24 36L12 26H26L32 12Z" 
                    fill="currentColor" opacity="0.3" stroke="currentColor" strokeWidth="2" />
            </svg>
          </div>
          
          <h1>{isWinner ? 'Victory!' : 'Game Over'}</h1>
          <p className="winner-text">
            {winner?.username} has built the greatest settlement in Teyuna!
          </p>
          
          <div className="final-scores">
            <h3>Final Standings</h3>
            {currentGame.players
              .sort((a, b) => b.victory_points - a.victory_points)
              .map((player, index) => (
                <div key={player.id} className={`score-row ${player.user_id === currentGame.winner_id ? 'winner' : ''}`}>
                  <span className="rank">#{index + 1}</span>
                  <div className={`player-color-dot ${player.color}`} />
                  <span className="player-name">{player.username}</span>
                  <span className="points">{player.victory_points} points</span>
                </div>
              ))}
          </div>
          
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/lobby')}>
            Return to Lobby
          </button>
        </div>
      </div>
    )
  }
  
  // Active game
  return (
    <div className="game-container">
      {/* Top Bar */}
      <div className="game-top-bar">
        <div className="turn-indicator">
          <span className="turn-label">Turn {Math.floor(currentGame.current_turn / currentGame.players.length) + 1}</span>
          <span className="current-player">
            <div className={`player-color-dot ${currentTurnPlayer?.color}`} />
            {currentTurnPlayer?.username}'s turn
            {isMyTurn && <span className="your-turn-badge">Your Turn!</span>}
          </span>
        </div>
        
        {lastRoll && (
          <div className="dice-display">
            <div className="die">{lastRoll.dice1}</div>
            <div className="die">{lastRoll.dice2}</div>
            <span className="dice-total">= {lastRoll.dice1 + lastRoll.dice2}</span>
          </div>
        )}
      </div>
      
      {/* Main Game Area */}
      <div className="game-main">
        {/* Left Panel - Players */}
        <div className="game-sidebar left">
          <h3>Settlers</h3>
          {currentGame.players.map((player: Player) => (
            <PlayerPanel 
              key={player.id} 
              player={player} 
              isCurrentTurn={player.id === currentGame.current_player_id}
              isMe={player.user_id === user?.id}
            />
          ))}
        </div>
        
        {/* Center - Board */}
        <div className="game-board-container">
          <HexBoard 
            hexes={currentGame.board.hexes}
            vertices={currentGame.board.vertices}
            edges={currentGame.board.edges}
            conquistadorPosition={currentGame.board.conquistador_position}
            players={currentGame.players}
            selectedAction={selectedAction}
            onBuild={handleBuild}
            myPlayerId={myPlayer?.id}
            isMyTurn={isMyTurn}
          />
        </div>
        
        {/* Right Panel - Actions */}
        <div className="game-sidebar right">
          <GameActions
            isMyTurn={isMyTurn}
            hasRolled={lastRoll !== null}
            onRoll={handleRollDice}
            onEndTurn={handleEndTurn}
            selectedAction={selectedAction}
            onSelectAction={setSelectedAction}
            player={myPlayer}
          />
        </div>
      </div>
      
      {/* Bottom Bar - My Resources */}
      {myPlayer && (
        <ResourceBar player={myPlayer} />
      )}
      
      {error && (
        <div className="game-toast error">
          {error}
          <button onClick={clearError}>×</button>
        </div>
      )}
    </div>
  )
}

