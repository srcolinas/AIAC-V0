import { Player } from '../../store/gameStore'
import './PlayerPanel.css'

interface PlayerPanelProps {
  player: Player
  isCurrentTurn: boolean
  isMe: boolean
}

export default function PlayerPanel({ player, isCurrentTurn, isMe }: PlayerPanelProps) {
  const totalResources = player.gold + player.stone + player.cotton + player.maize + player.wood
  
  return (
    <div className={`player-panel ${isCurrentTurn ? 'active' : ''} ${isMe ? 'is-me' : ''}`}>
      <div className="player-header">
        <div className={`player-color-indicator ${player.color}`} />
        <div className="player-info">
          <span className="player-name">
            {player.username}
            {isMe && <span className="me-badge">You</span>}
          </span>
          <span className="player-points">{player.victory_points} VP</span>
        </div>
        {isCurrentTurn && <div className="turn-arrow">◀</div>}
      </div>
      
      <div className="player-stats">
        {/* Resources (hidden from opponents) */}
        <div className="stat-row">
          <span className="stat-icon">🎴</span>
          <span className="stat-value">
            {isMe ? totalResources : '?'} resources
          </span>
        </div>
        
        {/* Development cards */}
        <div className="stat-row">
          <span className="stat-icon">📜</span>
          <span className="stat-value">
            {player.development_cards_count} cards
          </span>
        </div>
        
        {/* Warriors */}
        {player.warrior_cards > 0 && (
          <div className="stat-row">
            <span className="stat-icon">⚔️</span>
            <span className="stat-value">{player.warrior_cards} warriors</span>
          </div>
        )}
        
        {/* Achievements */}
        {player.has_longest_path && (
          <div className="achievement">
            🛤️ Longest Path (+2 VP)
          </div>
        )}
        
        {player.has_largest_army && (
          <div className="achievement">
            🏹 Largest Army (+2 VP)
          </div>
        )}
      </div>
    </div>
  )
}

