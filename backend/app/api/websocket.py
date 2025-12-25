"""WebSocket API for real-time game updates."""
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.auth import AuthService
from app.services.game import GameService

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections for real-time game updates."""
    
    def __init__(self):
        # game_token -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, game_token: str):
        """Accept and register a new connection."""
        await websocket.accept()
        if game_token not in self.active_connections:
            self.active_connections[game_token] = set()
        self.active_connections[game_token].add(websocket)
    
    def disconnect(self, websocket: WebSocket, game_token: str):
        """Remove a connection."""
        if game_token in self.active_connections:
            self.active_connections[game_token].discard(websocket)
            if not self.active_connections[game_token]:
                del self.active_connections[game_token]
    
    async def broadcast_to_game(self, game_token: str, message: dict):
        """Send a message to all players in a game."""
        if game_token in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[game_token]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.add(connection)
            
            # Clean up dead connections
            for conn in dead_connections:
                self.active_connections[game_token].discard(conn)
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send a message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception:
            pass


manager = ConnectionManager()


@router.websocket("/ws/game/{game_token}")
async def game_websocket(
    websocket: WebSocket,
    game_token: str
):
    """
    WebSocket endpoint for real-time game updates.
    
    Clients should send a message with their auth token first:
    {"type": "auth", "token": "jwt_token_here"}
    
    After authentication, they receive game updates:
    - player_joined: A new player joined
    - player_left: A player disconnected
    - game_started: Game has begun
    - dice_rolled: Dice were rolled
    - build: Something was built
    - turn_ended: Turn changed
    - game_over: Game finished
    """
    await manager.connect(websocket, game_token)
    
    user_id = None
    
    try:
        # Wait for auth message
        auth_data = await websocket.receive_json()
        
        if auth_data.get("type") != "auth" or "token" not in auth_data:
            await manager.send_personal(websocket, {
                "type": "error",
                "message": "Authentication required"
            })
            await websocket.close()
            return
        
        # Validate token
        token_data = AuthService.decode_token(auth_data["token"])
        if not token_data or not token_data.user_id:
            await manager.send_personal(websocket, {
                "type": "error",
                "message": "Invalid token"
            })
            await websocket.close()
            return
        
        user_id = token_data.user_id
        
        # Send connection confirmation
        await manager.send_personal(websocket, {
            "type": "connected",
            "user_id": user_id,
            "game_token": game_token
        })
        
        # Notify others
        await manager.broadcast_to_game(game_token, {
            "type": "player_connected",
            "user_id": user_id
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            msg_type = data.get("type")
            
            if msg_type == "ping":
                await manager.send_personal(websocket, {"type": "pong"})
            
            elif msg_type == "chat":
                # Broadcast chat message to all players
                await manager.broadcast_to_game(game_token, {
                    "type": "chat",
                    "user_id": user_id,
                    "message": data.get("message", "")[:500]  # Limit length
                })
            
            # Game actions are handled via REST API,
            # but the results are broadcast here
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, game_token)
        if user_id:
            await manager.broadcast_to_game(game_token, {
                "type": "player_disconnected",
                "user_id": user_id
            })
    
    except Exception as e:
        manager.disconnect(websocket, game_token)
        if user_id:
            await manager.broadcast_to_game(game_token, {
                "type": "player_disconnected",
                "user_id": user_id
            })


async def notify_game_update(game_token: str, update_type: str, data: dict = None):
    """
    Utility function to notify all players of a game update.
    
    Called by game services after state changes.
    """
    message = {"type": update_type}
    if data:
        message.update(data)
    await manager.broadcast_to_game(game_token, message)

