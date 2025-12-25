import { create } from 'zustand'
import { api } from '../services/api'

// Types
export interface Player {
  id: number
  user_id: number
  username: string
  color: string
  turn_order: number
  victory_points: number
  is_host: boolean
  is_active: boolean
  gold: number
  stone: number
  cotton: number
  maize: number
  wood: number
  warrior_cards: number
  has_longest_path: boolean
  has_largest_army: boolean
  development_cards_count: number
}

export interface HexTile {
  id: number
  terrain: string
  number_token: number | null
  has_conquistador: boolean
  q: number
  r: number
}

export interface Vertex {
  id: number
  building: string | null
  player_id: number | null
  is_port: boolean
  port_type: string | null
}

export interface Edge {
  id: number
  has_road: boolean
  player_id: number | null
}

export interface BoardState {
  hexes: HexTile[]
  vertices: Vertex[]
  edges: Edge[]
  conquistador_position: number
}

export interface GameState {
  game_id: number
  token: string
  status: string
  current_turn: number
  current_player_id: number | null
  players: Player[]
  board: BoardState
  last_dice_roll: number[] | null
  winner_id: number | null
}

export interface GameSummary {
  id: number
  token: string
  status: string
  max_players: number
  current_players: number
  created_at: string
}

interface GameStoreState {
  currentGame: GameState | null
  myGames: GameSummary[]
  isLoading: boolean
  error: string | null
  
  // Actions
  createGame: (maxPlayers: number) => Promise<string | null>
  joinGame: (token: string) => Promise<boolean>
  fetchGame: (token: string) => Promise<void>
  fetchMyGames: () => Promise<void>
  startGame: (token: string) => Promise<boolean>
  rollDice: (token: string) => Promise<{ dice1: number; dice2: number } | null>
  build: (token: string, buildingType: string, positionId: number) => Promise<boolean>
  endTurn: (token: string) => Promise<boolean>
  clearError: () => void
  clearGame: () => void
}

export const useGameStore = create<GameStoreState>((set, get) => ({
  currentGame: null,
  myGames: [],
  isLoading: false,
  error: null,
  
  createGame: async (maxPlayers: number) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.post('/games', { max_players: maxPlayers })
      set({ isLoading: false })
      return response.data.token
    } catch (err: any) {
      set({ 
        isLoading: false, 
        error: err.response?.data?.detail || 'Failed to create game'
      })
      return null
    }
  },
  
  joinGame: async (token: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.post('/games/join', { token })
      set({ currentGame: response.data, isLoading: false })
      return true
    } catch (err: any) {
      set({ 
        isLoading: false, 
        error: err.response?.data?.detail || 'Failed to join game'
      })
      return false
    }
  },
  
  fetchGame: async (token: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.get(`/games/${token}`)
      set({ currentGame: response.data, isLoading: false })
    } catch (err: any) {
      set({ 
        isLoading: false, 
        error: err.response?.data?.detail || 'Failed to fetch game'
      })
    }
  },
  
  fetchMyGames: async () => {
    try {
      const response = await api.get('/games')
      set({ myGames: response.data })
    } catch (err: any) {
      console.error('Failed to fetch games:', err)
    }
  },
  
  startGame: async (token: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await api.post(`/games/${token}/start`)
      set({ currentGame: response.data, isLoading: false })
      return true
    } catch (err: any) {
      set({ 
        isLoading: false, 
        error: err.response?.data?.detail || 'Failed to start game'
      })
      return false
    }
  },
  
  rollDice: async (token: string) => {
    try {
      const response = await api.post(`/games/${token}/roll`)
      // Refresh game state
      await get().fetchGame(token)
      return response.data
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Failed to roll dice' })
      return null
    }
  },
  
  build: async (token: string, buildingType: string, positionId: number) => {
    try {
      const response = await api.post(`/games/${token}/build`, {
        building_type: buildingType,
        position_id: positionId
      })
      set({ currentGame: response.data })
      return true
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Failed to build' })
      return false
    }
  },
  
  endTurn: async (token: string) => {
    try {
      const response = await api.post(`/games/${token}/end-turn`)
      set({ currentGame: response.data })
      return true
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Failed to end turn' })
      return false
    }
  },
  
  clearError: () => set({ error: null }),
  clearGame: () => set({ currentGame: null })
}))

