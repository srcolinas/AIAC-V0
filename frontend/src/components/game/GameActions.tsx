import { Player } from '../../store/gameStore'
import './GameActions.css'

interface GameActionsProps {
  isMyTurn: boolean
  hasRolled: boolean
  onRoll: () => void
  onEndTurn: () => void
  selectedAction: string | null
  onSelectAction: (action: string | null) => void
  player?: Player
}

const BUILDING_COSTS = {
  camino: { stone: 1, wood: 1 },
  bohio: { stone: 1, wood: 1, cotton: 1, maize: 1 },
  templo: { gold: 3, maize: 2 },
  card: { gold: 1, cotton: 1, maize: 1 }
}

const RESOURCE_ICONS: Record<string, string> = {
  gold: '🥇',
  stone: '🪨',
  cotton: '☁️',
  maize: '🌽',
  wood: '🌳'
}

export default function GameActions({
  isMyTurn,
  hasRolled,
  onRoll,
  onEndTurn,
  selectedAction,
  onSelectAction,
  player
}: GameActionsProps) {
  
  const canAfford = (costs: Record<string, number>) => {
    if (!player) return false
    return Object.entries(costs).every(([resource, amount]) => {
      return (player[resource as keyof Player] as number) >= amount
    })
  }
  
  const renderCost = (costs: Record<string, number>) => {
    return Object.entries(costs).map(([resource, amount]) => (
      <span key={resource} className="cost-item">
        {RESOURCE_ICONS[resource]} {amount}
      </span>
    ))
  }
  
  if (!isMyTurn) {
    return (
      <div className="game-actions">
        <div className="waiting-message">
          <div className="waiting-icon">⏳</div>
          <p>Waiting for your turn...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="game-actions">
      {/* Roll Dice */}
      {!hasRolled && (
        <div className="action-section">
          <button className="btn btn-primary btn-lg roll-btn" onClick={onRoll}>
            <span className="dice-icon">🎲</span>
            Roll Dice
          </button>
        </div>
      )}
      
      {/* Building Actions */}
      {hasRolled && (
        <>
          <div className="action-section">
            <h4>Build</h4>
            <div className="build-options">
              <button
                className={`build-btn ${selectedAction === 'camino' ? 'selected' : ''} ${!canAfford(BUILDING_COSTS.camino) ? 'disabled' : ''}`}
                onClick={() => onSelectAction(selectedAction === 'camino' ? null : 'camino')}
                disabled={!canAfford(BUILDING_COSTS.camino)}
              >
                <span className="build-icon">🛤️</span>
                <span className="build-name">Camino</span>
                <span className="build-cost">{renderCost(BUILDING_COSTS.camino)}</span>
              </button>
              
              <button
                className={`build-btn ${selectedAction === 'bohio' ? 'selected' : ''} ${!canAfford(BUILDING_COSTS.bohio) ? 'disabled' : ''}`}
                onClick={() => onSelectAction(selectedAction === 'bohio' ? null : 'bohio')}
                disabled={!canAfford(BUILDING_COSTS.bohio)}
              >
                <span className="build-icon">🏠</span>
                <span className="build-name">Bohío</span>
                <span className="build-cost">{renderCost(BUILDING_COSTS.bohio)}</span>
              </button>
              
              <button
                className={`build-btn ${selectedAction === 'templo' ? 'selected' : ''} ${!canAfford(BUILDING_COSTS.templo) ? 'disabled' : ''}`}
                onClick={() => onSelectAction(selectedAction === 'templo' ? null : 'templo')}
                disabled={!canAfford(BUILDING_COSTS.templo)}
              >
                <span className="build-icon">🏛️</span>
                <span className="build-name">Templo</span>
                <span className="build-cost">{renderCost(BUILDING_COSTS.templo)}</span>
              </button>
            </div>
            
            {selectedAction && (
              <p className="action-hint">
                Click on the board to place your {selectedAction}
              </p>
            )}
          </div>
          
          <div className="action-section">
            <h4>Other Actions</h4>
            <button
              className={`action-btn ${!canAfford(BUILDING_COSTS.card) ? 'disabled' : ''}`}
              disabled={!canAfford(BUILDING_COSTS.card)}
            >
              <span>📜</span>
              <span>Buy Wisdom Card</span>
              <span className="action-cost">{renderCost(BUILDING_COSTS.card)}</span>
            </button>
            
            <button className="action-btn">
              <span>🤝</span>
              <span>Trade</span>
            </button>
          </div>
          
          <div className="action-section">
            <button className="btn btn-secondary w-full" onClick={onEndTurn}>
              End Turn
            </button>
          </div>
        </>
      )}
      
      {/* Building Legend */}
      <div className="legend">
        <h4>Buildings</h4>
        <div className="legend-item">
          <span>🛤️ Camino</span>
          <span className="legend-desc">Stone path connecting settlements</span>
        </div>
        <div className="legend-item">
          <span>🏠 Bohío</span>
          <span className="legend-desc">Traditional house (1 VP)</span>
        </div>
        <div className="legend-item">
          <span>🏛️ Templo</span>
          <span className="legend-desc">Sacred temple (2 VP)</span>
        </div>
      </div>
    </div>
  )
}

