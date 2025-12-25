"""Configuration for the AI client."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AI Client settings."""
    
    # API Configuration
    api_base_url: str = "http://localhost:8000/api"
    ws_base_url: str = "ws://localhost:8000"
    
    # AI Model Configuration
    openai_api_key: str = ""
    model_name: str = "gpt-4"
    
    # Game Configuration
    username: str = "teyuna_ai"
    password: str = "ai_player_secret"
    email: str = "ai@teyuna.game"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()

