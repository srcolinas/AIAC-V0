"""HTTP client for Teyuna game API."""
import httpx
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GameClient:
    """Client for interacting with the Teyuna API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.client = httpx.Client(timeout=30.0)
    
    def _headers(self) -> dict:
        """Get request headers with auth token."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, username: str, email: str, password: str) -> bool:
        """Register a new user."""
        try:
            response = self.client.post(
                f"{self.base_url}/auth/register",
                json={"username": username, "email": email, "password": password},
                headers=self._headers()
            )
            return response.status_code == 201
        except Exception:
            return False
    
    def login(self, username: str, password: str) -> bool:
        """Login and store the access token."""
        try:
            response = self.client.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password},
                headers=self._headers()
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                return True
            return False
        except Exception:
            return False
    
    def get_me(self) -> Optional[dict]:
        """Get current user info."""
        try:
            response = self.client.get(
                f"{self.base_url}/auth/me",
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def create_game(self, max_players: int = 4) -> Optional[str]:
        """Create a new game and return its token."""
        try:
            response = self.client.post(
                f"{self.base_url}/games",
                json={"max_players": max_players},
                headers=self._headers()
            )
            if response.status_code == 201:
                return response.json()["token"]
            return None
        except Exception:
            return None
    
    def join_game(self, game_token: str) -> Optional[dict]:
        """Join an existing game."""
        try:
            response = self.client.post(
                f"{self.base_url}/games/join",
                json={"token": game_token},
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def get_game(self, game_token: str) -> Optional[dict]:
        """Get current game state."""
        try:
            response = self.client.get(
                f"{self.base_url}/games/{game_token}",
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def start_game(self, game_token: str) -> Optional[dict]:
        """Start a game (host only)."""
        try:
            response = self.client.post(
                f"{self.base_url}/games/{game_token}/start",
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def roll_dice(self, game_token: str) -> Optional[dict]:
        """Roll dice for current turn."""
        try:
            response = self.client.post(
                f"{self.base_url}/games/{game_token}/roll",
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def build(self, game_token: str, building_type: str, position_id: int) -> Optional[dict]:
        """Build a structure."""
        try:
            response = self.client.post(
                f"{self.base_url}/games/{game_token}/build",
                json={"building_type": building_type, "position_id": position_id},
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def buy_card(self, game_token: str) -> Optional[dict]:
        """Buy a development card."""
        try:
            response = self.client.post(
                f"{self.base_url}/games/{game_token}/buy-card",
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def end_turn(self, game_token: str) -> Optional[dict]:
        """End current turn."""
        try:
            response = self.client.post(
                f"{self.base_url}/games/{game_token}/end-turn",
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def get_my_games(self) -> list[dict]:
        """Get all games for current user."""
        try:
            response = self.client.get(
                f"{self.base_url}/games",
                headers=self._headers()
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()

