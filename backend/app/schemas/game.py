"""Game-related Pydantic schemas."""
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ResourceType(str, Enum):
    """Resource types in the game - based on Tayrona economy."""
    GOLD = "gold"       # Ore equivalent - from mountains (Sierra)
    STONE = "stone"     # Brick equivalent - from quarries (Canteras)
    COTTON = "cotton"   # Wool equivalent - from highlands (Tierras Altas)
    MAIZE = "maize"     # Grain equivalent - from valleys (Valles)
    WOOD = "wood"       # Lumber equivalent - from jungle (Selva)


class TerrainType(str, Enum):
    """Terrain types on the board."""
    SIERRA = "sierra"           # Mountains - produces Gold
    CANTERAS = "canteras"       # Quarries - produces Stone
    TIERRAS_ALTAS = "tierras_altas"  # Highlands - produces Cotton
    VALLES = "valles"           # Valleys - produces Maize
    SELVA = "selva"             # Jungle - produces Wood
    CENTRO_CEREMONIAL = "centro_ceremonial"  # Desert/Robber - no production


class BuildingType(str, Enum):
    """Building types - based on Tayrona architecture."""
    CAMINO = "camino"   # Stone Path - Road equivalent
    BOHIO = "bohio"     # Circular House - Settlement equivalent
    TEMPLO = "templo"   # Temple - City equivalent


class DevelopmentCardType(str, Enum):
    """Development card types - based on Tayrona culture."""
    GUERRERO_NAOMA = "guerrero_naoma"       # Knight - Naoma Warrior
    ABUNDANCIA = "abundancia"                # Year of Plenty - Earth's Abundance
    SABIDURIA_MAMA = "sabiduria_mama"       # Monopoly - Mama's Wisdom
    NUEVOS_CAMINOS = "nuevos_caminos"       # Road Building - New Paths
    AVANCE_ANCESTRAL = "avance_ancestral"   # Victory Point - Ancestral Advancement


class PortType(str, Enum):
    """Port types for maritime trade."""
    GENERAL = "general"     # 3:1 any resource
    GOLD = "gold"           # 2:1 gold
    STONE = "stone"         # 2:1 stone
    COTTON = "cotton"       # 2:1 cotton
    MAIZE = "maize"         # 2:1 maize
    WOOD = "wood"           # 2:1 wood


class GameCreate(BaseModel):
    """Schema for creating a new game."""
    max_players: int = Field(default=4, ge=3, le=4)


class GameJoin(BaseModel):
    """Schema for joining an existing game."""
    token: str = Field(..., min_length=32, max_length=32)


class PlayerResponse(BaseModel):
    """Schema for player information."""
    id: int
    user_id: int
    username: str
    color: str
    turn_order: int
    victory_points: int
    is_host: bool
    is_active: bool
    
    # Resources
    gold: int
    stone: int
    cotton: int
    maize: int
    wood: int
    
    # Cards and achievements
    warrior_cards: int
    has_longest_path: bool
    has_largest_army: bool
    development_cards_count: int
    
    class Config:
        from_attributes = True


class HexTile(BaseModel):
    """Schema for a hex tile on the board."""
    id: int
    terrain: TerrainType
    number_token: Optional[int] = None  # 2-12, None for ceremonial center
    has_conquistador: bool = False
    q: int  # Axial coordinate
    r: int  # Axial coordinate


class Vertex(BaseModel):
    """Schema for a vertex (intersection) on the board."""
    id: int
    building: Optional[BuildingType] = None
    player_id: Optional[int] = None
    is_port: bool = False
    port_type: Optional[PortType] = None


class Edge(BaseModel):
    """Schema for an edge (road position) on the board."""
    id: int
    has_road: bool = False
    player_id: Optional[int] = None


class BoardState(BaseModel):
    """Schema for the complete board state."""
    hexes: list[HexTile]
    vertices: list[Vertex]
    edges: list[Edge]
    conquistador_position: int  # Hex ID where conquistador is


class GameStateResponse(BaseModel):
    """Schema for complete game state response."""
    game_id: int
    token: str
    status: str
    current_turn: int
    current_player_id: Optional[int]
    players: list[PlayerResponse]
    board: BoardState
    last_dice_roll: Optional[list[int]]
    winner_id: Optional[int]
    
    class Config:
        from_attributes = True


class GameResponse(BaseModel):
    """Schema for basic game information."""
    id: int
    token: str
    status: str
    max_players: int
    current_players: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Game Actions

class DiceRoll(BaseModel):
    """Schema for dice roll result."""
    dice1: int = Field(..., ge=1, le=6)
    dice2: int = Field(..., ge=1, le=6)
    total: int = Field(..., ge=2, le=12)


class BuildAction(BaseModel):
    """Schema for building action."""
    building_type: BuildingType
    position_id: int  # Vertex ID for bohio/templo, Edge ID for camino


class TradeOffer(BaseModel):
    """Schema for trade offer."""
    offering: dict[ResourceType, int]
    requesting: dict[ResourceType, int]
    target_player_id: Optional[int] = None  # None for bank/port trade


class MoveConquistador(BaseModel):
    """Schema for moving the conquistador."""
    target_hex_id: int
    steal_from_player_id: Optional[int] = None


class PlayDevelopmentCard(BaseModel):
    """Schema for playing a development card."""
    card_type: DevelopmentCardType
    # Additional data based on card type
    target_resource: Optional[ResourceType] = None  # For monopoly
    resources: Optional[list[ResourceType]] = None  # For year of plenty


class GameAction(BaseModel):
    """Union schema for all game actions."""
    action_type: str
    build: Optional[BuildAction] = None
    trade: Optional[TradeOffer] = None
    move_conquistador: Optional[MoveConquistador] = None
    play_card: Optional[PlayDevelopmentCard] = None

