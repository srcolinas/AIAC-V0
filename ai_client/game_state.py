"""Game state models and analysis."""
from typing import Optional
from pydantic import BaseModel


class Player(BaseModel):
    """Player information."""
    id: int
    user_id: int
    username: str
    color: str
    turn_order: int
    victory_points: int
    is_host: bool
    is_active: bool
    gold: int
    stone: int
    cotton: int
    maize: int
    wood: int
    warrior_cards: int
    has_longest_path: bool
    has_largest_army: bool
    development_cards_count: int


class HexTile(BaseModel):
    """Hex tile on the board."""
    id: int
    terrain: str
    number_token: Optional[int]
    has_conquistador: bool
    q: int
    r: int


class Vertex(BaseModel):
    """Vertex (intersection) on the board."""
    id: int
    building: Optional[str]
    player_id: Optional[int]
    is_port: bool
    port_type: Optional[str]


class Edge(BaseModel):
    """Edge (road position) on the board."""
    id: int
    has_road: bool
    player_id: Optional[int]


class BoardState(BaseModel):
    """Complete board state."""
    hexes: list[HexTile]
    vertices: list[Vertex]
    edges: list[Edge]
    conquistador_position: int


class GameState(BaseModel):
    """Complete game state."""
    game_id: int
    token: str
    status: str
    current_turn: int
    current_player_id: Optional[int]
    players: list[Player]
    board: BoardState
    last_dice_roll: Optional[list[int]]
    winner_id: Optional[int]


# Building costs
BUILDING_COSTS = {
    "camino": {"stone": 1, "wood": 1},
    "bohio": {"stone": 1, "wood": 1, "cotton": 1, "maize": 1},
    "templo": {"gold": 3, "maize": 2},
}

DEVELOPMENT_CARD_COST = {"gold": 1, "cotton": 1, "maize": 1}


def can_afford(player: Player, costs: dict[str, int]) -> bool:
    """Check if player can afford a building."""
    return all(
        getattr(player, resource, 0) >= amount
        for resource, amount in costs.items()
    )


def get_available_actions(game_state: GameState, player_id: int) -> list[str]:
    """Get list of available actions for a player."""
    player = next((p for p in game_state.players if p.id == player_id), None)
    if not player:
        return []
    
    actions = []
    
    # Check what can be built
    if can_afford(player, BUILDING_COSTS["camino"]):
        actions.append("build_camino")
    
    if can_afford(player, BUILDING_COSTS["bohio"]):
        actions.append("build_bohio")
    
    if can_afford(player, BUILDING_COSTS["templo"]):
        # Check if player has any bohios to upgrade
        has_bohio = any(
            v.building == "bohio" and v.player_id == player_id
            for v in game_state.board.vertices
        )
        if has_bohio:
            actions.append("build_templo")
    
    if can_afford(player, DEVELOPMENT_CARD_COST):
        actions.append("buy_card")
    
    actions.append("end_turn")
    
    return actions


def find_valid_build_positions(
    game_state: GameState, 
    player_id: int, 
    building_type: str
) -> list[int]:
    """Find valid positions for building."""
    positions = []
    
    if building_type == "camino":
        # Find edges adjacent to player's buildings or roads
        for edge in game_state.board.edges:
            if not edge.has_road:
                # Simplified: any empty edge is valid for now
                positions.append(edge.id)
    
    elif building_type == "bohio":
        # Find empty vertices
        for vertex in game_state.board.vertices:
            if not vertex.building:
                positions.append(vertex.id)
    
    elif building_type == "templo":
        # Find player's bohios
        for vertex in game_state.board.vertices:
            if vertex.building == "bohio" and vertex.player_id == player_id:
                positions.append(vertex.id)
    
    return positions


def analyze_game_state(game_state: GameState, player_id: int) -> str:
    """Generate a human-readable analysis of the game state for the AI."""
    player = next((p for p in game_state.players if p.id == player_id), None)
    if not player:
        return "Player not found in game."
    
    analysis = []
    analysis.append(f"=== Game Analysis for {player.username} ===\n")
    
    # Current standing
    analysis.append(f"Victory Points: {player.victory_points}/10")
    
    # Resources
    analysis.append(f"\nResources:")
    analysis.append(f"  - Gold (Oro): {player.gold}")
    analysis.append(f"  - Stone (Piedra): {player.stone}")
    analysis.append(f"  - Cotton (Algodón): {player.cotton}")
    analysis.append(f"  - Maize (Maíz): {player.maize}")
    analysis.append(f"  - Wood (Madera): {player.wood}")
    
    # Available actions
    actions = get_available_actions(game_state, player_id)
    analysis.append(f"\nAvailable Actions: {', '.join(actions)}")
    
    # Other players
    analysis.append("\nOther Players:")
    for p in game_state.players:
        if p.id != player_id:
            analysis.append(f"  - {p.username}: {p.victory_points} VP")
    
    # Strategic notes
    analysis.append("\nStrategic Notes:")
    
    if player.victory_points >= 8:
        analysis.append("  - Close to winning! Focus on final points.")
    
    if can_afford(player, BUILDING_COSTS["templo"]):
        analysis.append("  - Can upgrade a bohío to templo (+1 VP).")
    
    if can_afford(player, BUILDING_COSTS["bohio"]):
        analysis.append("  - Can build a new bohío (+1 VP).")
    
    total_resources = player.gold + player.stone + player.cotton + player.maize + player.wood
    if total_resources > 7:
        analysis.append(f"  - WARNING: {total_resources} cards - will lose half on a 7!")
    
    return "\n".join(analysis)

