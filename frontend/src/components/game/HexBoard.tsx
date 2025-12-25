import { HexTile, Vertex, Edge, Player } from '../../store/gameStore'
import './HexBoard.css'

interface HexBoardProps {
  hexes: HexTile[]
  vertices: Vertex[]
  edges: Edge[]
  conquistadorPosition: number
  players: Player[]
  selectedAction: string | null
  onBuild: (buildingType: string, positionId: number) => void
  myPlayerId?: number
  isMyTurn: boolean
}

// Hex dimensions
const HEX_SIZE = 60
const HEX_WIDTH = HEX_SIZE * 2
const HEX_HEIGHT = Math.sqrt(3) * HEX_SIZE

// Terrain colors
const TERRAIN_COLORS: Record<string, { fill: string; stroke: string; name: string }> = {
  sierra: { fill: '#4a6670', stroke: '#3a5560', name: 'Sierra' },
  canteras: { fill: '#8b8378', stroke: '#6b6358', name: 'Canteras' },
  tierras_altas: { fill: '#f5f0e6', stroke: '#d5d0c6', name: 'Highlands' },
  valles: { fill: '#f0c040', stroke: '#d0a020', name: 'Valles' },
  selva: { fill: '#3d7a4d', stroke: '#2d5a3d', name: 'Selva' },
  centro_ceremonial: { fill: '#c4a87c', stroke: '#a48860', name: 'Centro' }
}

// Resource icons
const TERRAIN_RESOURCES: Record<string, string> = {
  sierra: '⛰️',      // Gold
  canteras: '🪨',    // Stone
  tierras_altas: '☁️', // Cotton
  valles: '🌽',      // Maize
  selva: '🌳',       // Wood
  centro_ceremonial: '🏛️'
}

export default function HexBoard({ 
  hexes, 
  vertices, 
  edges, 
  conquistadorPosition,
  players,
  selectedAction,
  onBuild,
  myPlayerId,
  isMyTurn
}: HexBoardProps) {
  
  // Convert axial coordinates to pixel position
  const axialToPixel = (q: number, r: number) => {
    const x = HEX_SIZE * (3/2 * q)
    const y = HEX_SIZE * (Math.sqrt(3)/2 * q + Math.sqrt(3) * r)
    return { x: x + 400, y: y + 300 } // Center offset
  }
  
  // Generate hex points for SVG polygon
  const getHexPoints = (cx: number, cy: number) => {
    const points = []
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 6
      const x = cx + HEX_SIZE * Math.cos(angle)
      const y = cy + HEX_SIZE * Math.sin(angle)
      points.push(`${x},${y}`)
    }
    return points.join(' ')
  }
  
  // Get player color
  const getPlayerColor = (playerId: number | null) => {
    if (!playerId) return 'transparent'
    const player = players.find(p => p.id === playerId)
    if (!player) return 'transparent'
    
    const colors: Record<string, string> = {
      gold: '#d4a84b',
      terracotta: '#8b4513',
      jade: '#00a36c',
      obsidian: '#1c1c1c'
    }
    return colors[player.color] || 'transparent'
  }
  
  const handleVertexClick = (vertex: Vertex) => {
    if (!isMyTurn || !selectedAction) return
    
    if (selectedAction === 'bohio' && !vertex.building) {
      onBuild('bohio', vertex.id)
    } else if (selectedAction === 'templo' && vertex.building === 'bohio' && vertex.player_id === myPlayerId) {
      onBuild('templo', vertex.id)
    }
  }
  
  const handleEdgeClick = (edge: Edge) => {
    if (!isMyTurn || selectedAction !== 'camino' || edge.has_road) return
    onBuild('camino', edge.id)
  }
  
  return (
    <svg className="hex-board" viewBox="0 0 800 600" preserveAspectRatio="xMidYMid meet">
      <defs>
        {/* Filters and gradients */}
        <filter id="hex-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="2" dy="4" stdDeviation="3" floodOpacity="0.3" />
        </filter>
        
        <pattern id="conquistador-pattern" width="10" height="10" patternUnits="userSpaceOnUse">
          <circle cx="5" cy="5" r="2" fill="#8b0000" opacity="0.5" />
        </pattern>
      </defs>
      
      {/* Hex tiles */}
      <g className="hexes">
        {hexes.map((hex) => {
          const { x, y } = axialToPixel(hex.q, hex.r)
          const terrain = TERRAIN_COLORS[hex.terrain] || TERRAIN_COLORS.centro_ceremonial
          const hasConquistador = hex.id === conquistadorPosition
          
          return (
            <g key={hex.id} className="hex-group">
              {/* Hex shape */}
              <polygon
                points={getHexPoints(x, y)}
                fill={terrain.fill}
                stroke={terrain.stroke}
                strokeWidth="3"
                filter="url(#hex-shadow)"
                className="hex-tile"
              />
              
              {/* Conquistador overlay */}
              {hasConquistador && (
                <polygon
                  points={getHexPoints(x, y)}
                  fill="url(#conquistador-pattern)"
                  className="conquistador-overlay"
                />
              )}
              
              {/* Resource icon */}
              <text
                x={x}
                y={y - 15}
                textAnchor="middle"
                className="hex-resource"
                fontSize="20"
              >
                {TERRAIN_RESOURCES[hex.terrain]}
              </text>
              
              {/* Number token */}
              {hex.number_token && (
                <g className="number-token">
                  <circle
                    cx={x}
                    cy={y + 15}
                    r="18"
                    fill="#f5f0e6"
                    stroke="#2d261f"
                    strokeWidth="2"
                  />
                  <text
                    x={x}
                    y={y + 21}
                    textAnchor="middle"
                    className={`number-text ${hex.number_token === 6 || hex.number_token === 8 ? 'hot' : ''}`}
                  >
                    {hex.number_token}
                  </text>
                  {/* Probability dots */}
                  <text
                    x={x}
                    y={y + 30}
                    textAnchor="middle"
                    className="probability-dots"
                  >
                    {getProbabilityDots(hex.number_token)}
                  </text>
                </g>
              )}
              
              {/* Conquistador icon */}
              {hasConquistador && (
                <text
                  x={x}
                  y={y + 5}
                  textAnchor="middle"
                  fontSize="24"
                  className="conquistador-icon"
                >
                  ⚔️
                </text>
              )}
            </g>
          )
        })}
      </g>
      
      {/* Edges (roads) */}
      <g className="edges">
        {edges.map((edge) => {
          // Simplified edge rendering
          const angle = (edge.direction || 0) * 60 * Math.PI / 180
          const cx = 400 + edge.q * 30
          const cy = 300 + edge.r * 30
          
          const x1 = cx - 15 * Math.cos(angle)
          const y1 = cy - 15 * Math.sin(angle)
          const x2 = cx + 15 * Math.cos(angle)
          const y2 = cy + 15 * Math.sin(angle)
          
          const canBuild = isMyTurn && selectedAction === 'camino' && !edge.has_road
          
          return (
            <g key={edge.id}>
              {edge.has_road && (
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={getPlayerColor(edge.player_id)}
                  strokeWidth="6"
                  strokeLinecap="round"
                  className="road"
                />
              )}
              {canBuild && (
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="transparent"
                  strokeWidth="12"
                  className="edge-hitbox"
                  onClick={() => handleEdgeClick(edge)}
                />
              )}
            </g>
          )
        })}
      </g>
      
      {/* Vertices (buildings) */}
      <g className="vertices">
        {vertices.map((vertex) => {
          const vx = 400 + vertex.q * 10
          const vy = 300 + vertex.r * 10
          
          const canBuildBohio = isMyTurn && selectedAction === 'bohio' && !vertex.building
          const canBuildTemplo = isMyTurn && selectedAction === 'templo' && 
                                  vertex.building === 'bohio' && vertex.player_id === myPlayerId
          const canBuild = canBuildBohio || canBuildTemplo
          
          return (
            <g key={vertex.id}>
              {/* Building */}
              {vertex.building === 'bohio' && (
                <g className="bohio" transform={`translate(${vx}, ${vy})`}>
                  <circle
                    r="12"
                    fill={getPlayerColor(vertex.player_id)}
                    stroke="#2d261f"
                    strokeWidth="2"
                  />
                  <circle r="5" fill="#2d261f" opacity="0.3" />
                </g>
              )}
              
              {vertex.building === 'templo' && (
                <g className="templo" transform={`translate(${vx}, ${vy})`}>
                  <polygon
                    points="0,-16 14,8 -14,8"
                    fill={getPlayerColor(vertex.player_id)}
                    stroke="#2d261f"
                    strokeWidth="2"
                  />
                  <rect x="-6" y="8" width="12" height="8" fill={getPlayerColor(vertex.player_id)} stroke="#2d261f" strokeWidth="2" />
                </g>
              )}
              
              {/* Build spot indicator */}
              {canBuild && (
                <circle
                  cx={vx}
                  cy={vy}
                  r="15"
                  fill="transparent"
                  stroke="#d4a84b"
                  strokeWidth="2"
                  strokeDasharray="4"
                  className="build-spot"
                  onClick={() => handleVertexClick(vertex)}
                />
              )}
              
              {/* Port indicator */}
              {vertex.is_port && (
                <text
                  x={vx}
                  y={vy - 20}
                  textAnchor="middle"
                  fontSize="12"
                  className="port-indicator"
                >
                  ⚓
                </text>
              )}
            </g>
          )
        })}
      </g>
    </svg>
  )
}

function getProbabilityDots(num: number): string {
  const probabilities: Record<number, number> = {
    2: 1, 3: 2, 4: 3, 5: 4, 6: 5,
    8: 5, 9: 4, 10: 3, 11: 2, 12: 1
  }
  return '•'.repeat(probabilities[num] || 0)
}

