const API_BASE = '/api'

interface RequestOptions {
  method?: string
  headers?: Record<string, string>
  body?: any
}

class ApiClient {
  private getAuthHeader(): Record<string, string> {
    const stored = localStorage.getItem('teyuna-auth')
    if (stored) {
      try {
        const { state } = JSON.parse(stored)
        if (state?.token) {
          return { 'Authorization': `Bearer ${state.token}` }
        }
      } catch {
        // Invalid stored data
      }
    }
    return {}
  }
  
  private async request<T>(endpoint: string, options: RequestOptions = {}): Promise<{ data: T }> {
    const { method = 'GET', headers = {}, body } = options
    
    const config: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeader(),
        ...headers
      }
    }
    
    if (body) {
      config.body = JSON.stringify(body)
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, config)
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw { response: { data: error, status: response.status } }
    }
    
    const data = await response.json()
    return { data }
  }
  
  async get<T = any>(endpoint: string): Promise<{ data: T }> {
    return this.request<T>(endpoint)
  }
  
  async post<T = any>(endpoint: string, body?: any): Promise<{ data: T }> {
    return this.request<T>(endpoint, { method: 'POST', body })
  }
  
  async put<T = any>(endpoint: string, body?: any): Promise<{ data: T }> {
    return this.request<T>(endpoint, { method: 'PUT', body })
  }
  
  async delete<T = any>(endpoint: string): Promise<{ data: T }> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

export const api = new ApiClient()


// WebSocket connection manager
export class GameWebSocket {
  private ws: WebSocket | null = null
  private token: string
  private gameToken: string
  private onMessage: (data: any) => void
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  
  constructor(gameToken: string, authToken: string, onMessage: (data: any) => void) {
    this.gameToken = gameToken
    this.token = authToken
    this.onMessage = onMessage
  }
  
  connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    this.ws = new WebSocket(`${protocol}//${host}/ws/game/${this.gameToken}`)
    
    this.ws.onopen = () => {
      console.log('WebSocket connected')
      // Send auth message
      this.ws?.send(JSON.stringify({ type: 'auth', token: this.token }))
      this.reconnectAttempts = 0
    }
    
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.onMessage(data)
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err)
      }
    }
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.attemptReconnect()
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
  }
  
  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000)
      console.log(`Reconnecting in ${delay}ms...`)
      setTimeout(() => this.connect(), delay)
    }
  }
  
  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
  
  disconnect() {
    this.maxReconnectAttempts = 0 // Prevent reconnection
    this.ws?.close()
  }
}

