"""Game API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.game import GameStatus
from app.schemas.game import (
    GameCreate,
    GameResponse,
    GameJoin,
    GameStateResponse,
    PlayerResponse,
    BuildAction,
    BoardState,
    HexTile,
    Vertex,
    Edge
)
from app.services.game import GameService
from app.api.deps import get_current_user

router = APIRouter(prefix="/games", tags=["Games"])


def _build_player_response(player) -> PlayerResponse:
    """Convert player model to response schema."""
    return PlayerResponse(
        id=player.id,
        user_id=player.user_id,
        username=player.user.username,
        color=player.color.value,
        turn_order=player.turn_order,
        victory_points=player.victory_points,
        is_host=player.is_host,
        is_active=player.is_active,
        gold=player.gold,
        stone=player.stone,
        cotton=player.cotton,
        maize=player.maize,
        wood=player.wood,
        warrior_cards=player.warrior_cards,
        has_longest_path=player.has_longest_path,
        has_largest_army=player.has_largest_army,
        development_cards_count=len(player.development_cards) if player.development_cards else 0
    )


def _build_game_state_response(game) -> GameStateResponse:
    """Convert game model to full state response."""
    board_data = game.game_state.board if game.game_state else {}
    
    # Build board state
    hexes = [HexTile(**h) for h in board_data.get("hexes", [])]
    vertices = [Vertex(**v) for v in board_data.get("vertices", [])]
    edges = [Edge(**e) for e in board_data.get("edges", [])]
    
    board = BoardState(
        hexes=hexes,
        vertices=vertices,
        edges=edges,
        conquistador_position=board_data.get("conquistador_position", 0)
    )
    
    # Find current player
    current_player_id = None
    if game.status == GameStatus.ACTIVE:
        turn_idx = game.current_turn % len(game.players)
        for p in game.players:
            if p.turn_order == turn_idx:
                current_player_id = p.id
                break
    
    return GameStateResponse(
        game_id=game.id,
        token=game.token,
        status=game.status.value,
        current_turn=game.current_turn,
        current_player_id=current_player_id,
        players=[_build_player_response(p) for p in game.players],
        board=board,
        last_dice_roll=game.game_state.last_dice_roll if game.game_state else None,
        winner_id=game.winner_id
    )


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_data: GameCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new game.
    
    Creates a game and returns a unique token for others to join.
    The creator becomes the host with the ability to start the game.
    """
    game = await GameService.create_game(db, current_user, game_data.max_players)
    
    return GameResponse(
        id=game.id,
        token=game.token,
        status=game.status.value,
        max_players=game.max_players,
        current_players=len(game.players),
        created_at=game.created_at
    )


@router.post("/join", response_model=GameStateResponse)
async def join_game(
    join_data: GameJoin,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Join an existing game using its token.
    
    Players can join games that are in 'waiting' status and have available slots.
    """
    game = await GameService.get_game_by_token(db, join_data.token)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if game.status != GameStatus.WAITING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Game has already started or finished"
        )
    
    player = await GameService.join_game(db, game, current_user)
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot join game - it may be full"
        )
    
    # Refresh game to get updated players
    game = await GameService.get_game_by_id(db, game.id)
    return _build_game_state_response(game)


@router.get("/{token}", response_model=GameStateResponse)
async def get_game(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get full game state.
    
    Returns the complete game state including board, players, and resources.
    """
    game = await GameService.get_game_by_token(db, token)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Verify user is in game
    is_player = any(p.user_id == current_user.id for p in game.players)
    if not is_player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a player in this game"
        )
    
    return _build_game_state_response(game)


@router.post("/{token}/start", response_model=GameStateResponse)
async def start_game(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start the game (host only).
    
    Requires at least 3 players. Randomizes turn order and begins the game.
    """
    game = await GameService.get_game_by_token(db, token)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    if len(game.players) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 3 players to start"
        )
    
    success = await GameService.start_game(db, game, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the host can start the game"
        )
    
    game = await GameService.get_game_by_id(db, game.id)
    return _build_game_state_response(game)


@router.post("/{token}/roll", response_model=dict)
async def roll_dice(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Roll the dice.
    
    Only the current turn's player can roll. Distributes resources on non-7 rolls.
    """
    game = await GameService.get_game_by_token(db, token)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    # Find player
    player = None
    for p in game.players:
        if p.user_id == current_user.id:
            player = p
            break
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not in this game"
        )
    
    result = await GameService.roll_dice(db, game, player.id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot roll dice - not your turn or game not active"
        )
    
    return {
        "dice1": result[0],
        "dice2": result[1],
        "total": result[0] + result[1]
    }


@router.post("/{token}/build", response_model=GameStateResponse)
async def build(
    token: str,
    build_action: BuildAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Build a structure.
    
    Build a camino (road), bohío (settlement), or templo (city).
    """
    game = await GameService.get_game_by_token(db, token)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    player = None
    for p in game.players:
        if p.user_id == current_user.id:
            player = p
            break
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not in this game"
        )
    
    success = await GameService.build(
        db, game, player.id, 
        build_action.building_type, 
        build_action.position_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot build - insufficient resources or invalid position"
        )
    
    game = await GameService.get_game_by_id(db, game.id)
    return _build_game_state_response(game)


@router.post("/{token}/buy-card", response_model=dict)
async def buy_development_card(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Buy a development card (Wisdom Card).
    
    Costs 1 gold, 1 cotton, 1 maize.
    """
    game = await GameService.get_game_by_token(db, token)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    player = None
    for p in game.players:
        if p.user_id == current_user.id:
            player = p
            break
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not in this game"
        )
    
    card = await GameService.buy_development_card(db, game, player.id)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot buy card - insufficient resources or deck empty"
        )
    
    return {"card": card}


@router.post("/{token}/end-turn", response_model=GameStateResponse)
async def end_turn(
    token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End your turn.
    
    Passes the turn to the next player.
    """
    game = await GameService.get_game_by_token(db, token)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
    
    player = None
    for p in game.players:
        if p.user_id == current_user.id:
            player = p
            break
    
    if not player:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not in this game"
        )
    
    success = await GameService.end_turn(db, game, player.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot end turn - not your turn"
        )
    
    game = await GameService.get_game_by_id(db, game.id)
    return _build_game_state_response(game)


@router.get("", response_model=list[GameResponse])
async def list_my_games(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all games for the current user.
    
    Returns both active and finished games.
    """
    games = await GameService.get_player_games(db, current_user.id)
    
    return [
        GameResponse(
            id=g.id,
            token=g.token,
            status=g.status.value,
            max_players=g.max_players,
            current_players=len(g.players),
            created_at=g.created_at
        )
        for g in games
    ]

