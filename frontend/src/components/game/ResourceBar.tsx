import { Player } from '../../store/gameStore'
import './ResourceBar.css'

interface ResourceBarProps {
  player: Player
}

const RESOURCES = [
  { key: 'gold', name: 'Oro', icon: '🥇', color: '#d4a84b' },
  { key: 'stone', name: 'Piedra', icon: '🪨', color: '#8b8378' },
  { key: 'cotton', name: 'Algodón', icon: '☁️', color: '#f5f0e6' },
  { key: 'maize', name: 'Maíz', icon: '🌽', color: '#f0c040' },
  { key: 'wood', name: 'Madera', icon: '🌳', color: '#3d7a4d' },
]

export default function ResourceBar({ player }: ResourceBarProps) {
  return (
    <div className="resource-bar">
      <div className="resource-bar-content">
        <div className="resource-label">Your Resources</div>
        
        <div className="resources-list">
          {RESOURCES.map(resource => {
            const count = player[resource.key as keyof Player] as number
            return (
              <div 
                key={resource.key} 
                className={`resource-item ${count === 0 ? 'empty' : ''}`}
                title={resource.name}
              >
                <span className="resource-icon">{resource.icon}</span>
                <span className="resource-count" style={{ color: resource.color }}>
                  {count}
                </span>
                <span className="resource-name">{resource.name}</span>
              </div>
            )
          })}
        </div>
        
        <div className="resource-divider" />
        
        <div className="cards-info">
          <div className="card-item" title="Development Cards">
            <span className="card-icon">📜</span>
            <span className="card-count">{player.development_cards_count}</span>
          </div>
          <div className="card-item" title="Warrior Cards">
            <span className="card-icon">⚔️</span>
            <span className="card-count">{player.warrior_cards}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

