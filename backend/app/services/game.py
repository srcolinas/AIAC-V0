"""Game service for managing game logic."""
import random
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.game import Game, Player, GameState, GameStatus, PlayerColor
from app.models.user import User
from app.services.board import BoardGenerator
from app.schemas.game import (
    BuildingType, 
    ResourceType, 
    DevelopmentCardType,
    TerrainType
)


# Building costs based on Tayrona construction
BUILDING_COSTS = {
    BuildingType.CAMINO: {"stone": 1, "wood": 1},  # Stone path
    BuildingType.BOHIO: {"stone": 1, "wood": 1, "cotton": 1, "maize": 1},  # House
    BuildingType.TEMPLO: {"gold": 3, "maize": 2},  # Temple (upgrade)
}

# Development card cost
DEVELOPMENT_CARD_COST = {"gold": 1, "cotton": 1, "maize": 1}

# Development card distribution
DEVELOPMENT_CARDS = (
    [DevelopmentCardType.GUERRERO_NAOMA] * 14 +  # 14 warriors
    [DevelopmentCardType.ABUNDANCIA] * 2 +        # 2 year of plenty
    [DevelopmentCardType.SABIDURIA_MAMA] * 2 +    # 2 monopoly
    [DevelopmentCardType.NUEVOS_CAMINOS] * 2 +    # 2 road building
    [DevelopmentCardType.AVANCE_ANCESTRAL] * 5    # 5 victory points
)

AVAILABLE_COLORS = list(PlayerColor)


class GameService:
    """Service for game operations."""
    
    @staticmethod
    async def create_game(db: AsyncSession, host_user: User, max_players: int = 4) -> Game:
        """Create a new game."""
        game = Game(max_players=max_players, status=GameStatus.WAITING)
        db.add(game)
        await db.flush()
        
        # Generate initial board
        board_data = BoardGenerator.generate_board()
        
        # Create development card deck
        dev_cards = list(DEVELOPMENT_CARDS)
        random.shuffle(dev_cards)
        dev_card_values = [card.value for card in dev_cards]
        
        # Create game state
        game_state = GameState(
            game_id=game.id,
            board=board_data,
            development_deck=dev_card_values,
            last_dice_roll=[],
            active_trades=[],
            game_log=[]
        )
        db.add(game_state)
        
        # Add host as first player
        player = Player(
            user_id=host_user.id,
            game_id=game.id,
            color=AVAILABLE_COLORS[0],
            turn_order=0,
            is_host=True,
            development_cards=[]
        )
        db.add(player)
        
        await db.flush()
        await db.refresh(game)
        
        return game
    
    @staticmethod
    async def get_game_by_token(db: AsyncSession, token: str) -> Optional[Game]:
        """Get a game by its token."""
        result = await db.execute(
            select(Game)
            .options(selectinload(Game.players).selectinload(Player.user))
            .options(selectinload(Game.game_state))
            .where(Game.token == token)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_game_by_id(db: AsyncSession, game_id: int) -> Optional[Game]:
        """Get a game by its ID."""
        result = await db.execute(
            select(Game)
            .options(selectinload(Game.players).selectinload(Player.user))
            .options(selectinload(Game.game_state))
            .where(Game.id == game_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def join_game(db: AsyncSession, game: Game, user: User) -> Optional[Player]:
        """Join an existing game."""
        if game.status != GameStatus.WAITING:
            return None
        
        if len(game.players) >= game.max_players:
            return None
        
        # Check if user already in game
        for player in game.players:
            if player.user_id == user.id:
                return player
        
        # Assign next available color and turn order
        used_colors = {p.color for p in game.players}
        available = [c for c in AVAILABLE_COLORS if c not in used_colors]
        
        if not available:
            return None
        
        player = Player(
            user_id=user.id,
            game_id=game.id,
            color=available[0],
            turn_order=len(game.players),
            is_host=False,
            development_cards=[]
        )
        db.add(player)
        await db.flush()
        await db.refresh(player)
        
        return player
    
    @staticmethod
    async def start_game(db: AsyncSession, game: Game, user_id: int) -> bool:
        """Start a game (host only)."""
        # Verify host
        host_player = None
        for player in game.players:
            if player.is_host and player.user_id == user_id:
                host_player = player
                break
        
        if not host_player:
            return False
        
        # Need 3-4 players
        if len(game.players) < 3:
            return False
        
        # Randomize turn order
        players = list(game.players)
        random.shuffle(players)
        for i, player in enumerate(players):
            player.turn_order = i
        
        game.status = GameStatus.ACTIVE
        game.current_turn = 0
        
        # Log game start
        if game.game_state:
            game.game_state.game_log.append({
                "type": "game_started",
                "turn_order": [p.user_id for p in sorted(players, key=lambda x: x.turn_order)]
            })
        
        await db.flush()
        return True
    
    @staticmethod
    async def roll_dice(db: AsyncSession, game: Game, player_id: int) -> Optional[tuple[int, int]]:
        """Roll dice for the current turn."""
        if game.status != GameStatus.ACTIVE:
            return None
        
        # Check it's this player's turn
        current_player = None
        for p in game.players:
            if p.turn_order == game.current_turn % len(game.players):
                current_player = p
                break
        
        if not current_player or current_player.id != player_id:
            return None
        
        # Roll dice
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        total = die1 + die2
        
        if game.game_state:
            game.game_state.last_dice_roll = [die1, die2]
            
            # Log roll
            game.game_state.game_log.append({
                "type": "dice_roll",
                "player_id": player_id,
                "dice": [die1, die2],
                "total": total
            })
        
        # If 7, conquistador must be moved (handled separately)
        if total != 7:
            # Distribute resources
            await GameService._distribute_resources(db, game, total)
        
        await db.flush()
        return (die1, die2)
    
    @staticmethod
    async def _distribute_resources(db: AsyncSession, game: Game, dice_total: int):
        """Distribute resources based on dice roll."""
        if not game.game_state:
            return
        
        board = game.game_state.board
        
        # Find hexes with matching number
        for hex_tile in board["hexes"]:
            if hex_tile["number_token"] != dice_total:
                continue
            if hex_tile["has_conquistador"]:
                continue
            
            terrain = TerrainType(hex_tile["terrain"])
            resource = BoardGenerator.get_terrain_resource(terrain)
            
            if not resource:
                continue
            
            # Find buildings adjacent to this hex
            # (Simplified - actual implementation would use proper adjacency)
            hex_id = hex_tile["id"]
            
            for vertex in board["vertices"]:
                if vertex["building"] and vertex["player_id"]:
                    # Check if vertex is adjacent to hex (simplified)
                    # In real implementation, use proper hex-vertex adjacency
                    player = None
                    for p in game.players:
                        if p.id == vertex["player_id"]:
                            player = p
                            break
                    
                    if player:
                        amount = 1 if vertex["building"] == "bohio" else 2
                        setattr(player, resource, getattr(player, resource) + amount)
    
    @staticmethod
    async def build(
        db: AsyncSession, 
        game: Game, 
        player_id: int, 
        building_type: BuildingType,
        position_id: int
    ) -> bool:
        """Build a structure."""
        if game.status != GameStatus.ACTIVE:
            return False
        
        # Find player
        player = None
        for p in game.players:
            if p.id == player_id:
                player = p
                break
        
        if not player:
            return False
        
        # Check resources
        costs = BUILDING_COSTS[building_type]
        for resource, amount in costs.items():
            if getattr(player, resource) < amount:
                return False
        
        # Deduct resources
        for resource, amount in costs.items():
            setattr(player, resource, getattr(player, resource) - amount)
        
        # Place building on board
        if game.game_state:
            board = game.game_state.board
            
            if building_type == BuildingType.CAMINO:
                # Place road on edge
                for edge in board["edges"]:
                    if edge["id"] == position_id and not edge["has_road"]:
                        edge["has_road"] = True
                        edge["player_id"] = player_id
                        break
            else:
                # Place building on vertex
                for vertex in board["vertices"]:
                    if vertex["id"] == position_id:
                        if building_type == BuildingType.BOHIO and not vertex["building"]:
                            vertex["building"] = "bohio"
                            vertex["player_id"] = player_id
                            player.victory_points += 1
                        elif building_type == BuildingType.TEMPLO and vertex["building"] == "bohio":
                            vertex["building"] = "templo"
                            player.victory_points += 1  # +1 more (total 2 for temple)
                        break
            
            # Log build
            game.game_state.game_log.append({
                "type": "build",
                "player_id": player_id,
                "building": building_type.value,
                "position": position_id
            })
        
        # Check for longest path
        await GameService._check_longest_path(db, game)
        
        # Check victory
        await GameService._check_victory(db, game)
        
        await db.flush()
        return True
    
    @staticmethod
    async def buy_development_card(db: AsyncSession, game: Game, player_id: int) -> Optional[str]:
        """Buy a development card."""
        if game.status != GameStatus.ACTIVE or not game.game_state:
            return None
        
        player = None
        for p in game.players:
            if p.id == player_id:
                player = p
                break
        
        if not player:
            return None
        
        # Check resources
        for resource, amount in DEVELOPMENT_CARD_COST.items():
            if getattr(player, resource) < amount:
                return None
        
        # Check deck
        if not game.game_state.development_deck:
            return None
        
        # Deduct resources
        for resource, amount in DEVELOPMENT_CARD_COST.items():
            setattr(player, resource, getattr(player, resource) - amount)
        
        # Draw card
        card = game.game_state.development_deck.pop()
        
        # Add to player's hand
        if player.development_cards is None:
            player.development_cards = []
        player.development_cards = player.development_cards + [card]
        
        # If victory point, add immediately
        if card == DevelopmentCardType.AVANCE_ANCESTRAL.value:
            player.victory_cards += 1
        
        game.game_state.game_log.append({
            "type": "buy_development_card",
            "player_id": player_id
        })
        
        await GameService._check_victory(db, game)
        await db.flush()
        
        return card
    
    @staticmethod
    async def end_turn(db: AsyncSession, game: Game, player_id: int) -> bool:
        """End the current player's turn."""
        if game.status != GameStatus.ACTIVE:
            return False
        
        # Check it's this player's turn
        num_players = len(game.players)
        current_idx = game.current_turn % num_players
        
        current_player = None
        for p in game.players:
            if p.turn_order == current_idx:
                current_player = p
                break
        
        if not current_player or current_player.id != player_id:
            return False
        
        game.current_turn += 1
        
        if game.game_state:
            game.game_state.last_dice_roll = []
            game.game_state.game_log.append({
                "type": "end_turn",
                "player_id": player_id,
                "new_turn": game.current_turn
            })
        
        await db.flush()
        return True
    
    @staticmethod
    async def _check_longest_path(db: AsyncSession, game: Game):
        """Check and update longest path achievement."""
        # Simplified - actual implementation would calculate road lengths
        pass
    
    @staticmethod
    async def _check_victory(db: AsyncSession, game: Game):
        """Check if any player has won."""
        for player in game.players:
            total_points = player.victory_points + player.victory_cards
            if player.has_longest_path:
                total_points += 2
            if player.has_largest_army:
                total_points += 2
            
            if total_points >= 10:
                game.status = GameStatus.FINISHED
                game.winner_id = player.user_id
                
                # Update user stats
                # (Would need to load user and update)
                
                if game.game_state:
                    game.game_state.game_log.append({
                        "type": "game_won",
                        "winner_id": player.id,
                        "points": total_points
                    })
                break
    
    @staticmethod
    async def get_player_games(db: AsyncSession, user_id: int) -> list[Game]:
        """Get all games a user is participating in."""
        result = await db.execute(
            select(Game)
            .join(Player)
            .options(selectinload(Game.players))
            .where(Player.user_id == user_id)
            .order_by(Game.created_at.desc())
        )
        return list(result.scalars().all())

