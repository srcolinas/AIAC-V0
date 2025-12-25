"""Game-related database models."""
import secrets
from enum import Enum
from sqlalchemy import String, Integer, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class GameStatus(str, Enum):
    """Game status enumeration."""
    WAITING = "waiting"  # Waiting for players to join
    ACTIVE = "active"    # Game in progress
    FINISHED = "finished"  # Game completed


class PlayerColor(str, Enum):
    """Player colors based on Tayrona cultural elements."""
    GOLD = "gold"           # Represents their famous goldwork
    TERRACOTTA = "terracotta"  # Earth tones of their pottery
    JADE = "jade"           # Precious stones they traded
    OBSIDIAN = "obsidian"   # Dark volcanic glass used in tools


class Game(Base, TimestampMixin):
    """Game model representing a Teyuna game session."""
    
    __tablename__ = "games"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token: Mapped[str] = mapped_column(
        String(32), 
        unique=True, 
        nullable=False, 
        index=True,
        default=lambda: secrets.token_hex(16)
    )
    
    # Game settings
    max_players: Mapped[int] = mapped_column(Integer, default=4)
    status: Mapped[GameStatus] = mapped_column(
        SQLEnum(GameStatus),
        default=GameStatus.WAITING
    )
    
    # Game progress
    current_turn: Mapped[int] = mapped_column(Integer, default=0)
    winner_id: Mapped[int | None] = mapped_column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=True
    )
    
    # Relationships
    players: Mapped[list["Player"]] = relationship(
        "Player",
        back_populates="game",
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    game_state: Mapped["GameState | None"] = relationship(
        "GameState",
        back_populates="game",
        uselist=False,
        lazy="selectin",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Game(id={self.id}, token='{self.token}', status={self.status})>"


class Player(Base, TimestampMixin):
    """Player model linking users to games."""
    
    __tablename__ = "players"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    
    # Player game state
    color: Mapped[PlayerColor] = mapped_column(SQLEnum(PlayerColor), nullable=False)
    turn_order: Mapped[int] = mapped_column(Integer, nullable=False)
    victory_points: Mapped[int] = mapped_column(Integer, default=0)
    is_host: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Resources - named after Tayrona economy
    gold: Mapped[int] = mapped_column(Integer, default=0)      # Ore equivalent
    stone: Mapped[int] = mapped_column(Integer, default=0)     # Brick equivalent
    cotton: Mapped[int] = mapped_column(Integer, default=0)    # Wool equivalent
    maize: Mapped[int] = mapped_column(Integer, default=0)     # Grain equivalent
    wood: Mapped[int] = mapped_column(Integer, default=0)      # Lumber equivalent
    
    # Special cards/achievements
    warrior_cards: Mapped[int] = mapped_column(Integer, default=0)  # Knight equivalent
    victory_cards: Mapped[int] = mapped_column(Integer, default=0)
    has_longest_path: Mapped[bool] = mapped_column(default=False)
    has_largest_army: Mapped[bool] = mapped_column(default=False)
    
    # Development cards in hand (JSON array)
    development_cards: Mapped[dict] = mapped_column(JSON, default=list)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="players")
    game: Mapped["Game"] = relationship("Game", back_populates="players")
    
    def __repr__(self) -> str:
        return f"<Player(id={self.id}, user_id={self.user_id}, color={self.color})>"


class GameState(Base, TimestampMixin):
    """Stores the complete game board state as JSON."""
    
    __tablename__ = "game_states"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id"), 
        unique=True, 
        nullable=False
    )
    
    # Board state stored as JSON for flexibility
    # Contains: hexes, vertices, edges, ports, conquistador position
    board: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    
    # Development card deck
    development_deck: Mapped[list] = mapped_column(JSON, default=list)
    
    # Current dice roll
    last_dice_roll: Mapped[list] = mapped_column(JSON, default=list)
    
    # Trade offers currently active
    active_trades: Mapped[list] = mapped_column(JSON, default=list)
    
    # Game log for replay/history
    game_log: Mapped[list] = mapped_column(JSON, default=list)
    
    # Relationship
    game: Mapped["Game"] = relationship("Game", back_populates="game_state")
    
    def __repr__(self) -> str:
        return f"<GameState(id={self.id}, game_id={self.game_id})>"


# Import at end to avoid circular imports
from app.models.user import User

