"""AI Agent for playing Teyuna using Pydantic AI."""
from pydantic_ai import Agent
from pydantic import BaseModel
from typing import Optional
import json

from game_state import (
    GameState, 
    Player,
    analyze_game_state, 
    get_available_actions,
    find_valid_build_positions,
    can_afford,
    BUILDING_COSTS,
    DEVELOPMENT_CARD_COST
)


class GameAction(BaseModel):
    """An action to take in the game."""
    action_type: str  # roll, build, buy_card, end_turn
    building_type: Optional[str] = None  # camino, bohio, templo
    position_id: Optional[int] = None
    reasoning: str


SYSTEM_PROMPT = """You are an expert AI player of Teyuna, a strategy board game inspired by the ancient Tayrona civilization of Colombia.

## Game Overview
- Goal: Be the first to reach 10 Victory Points
- Resources: Gold (Oro), Stone (Piedra), Cotton (Algodón), Maize (Maíz), Wood (Madera)
- Buildings:
  - Camino (Stone Path): 1 Stone + 1 Wood
  - Bohío (House): 1 Stone + 1 Wood + 1 Cotton + 1 Maize = 1 VP
  - Templo (Temple): 3 Gold + 2 Maize = 2 VP (upgrades a Bohío)

## Your Strategy
1. Early game: Build paths and bohíos to establish resource collection
2. Mid game: Expand territory and accumulate resources
3. Late game: Build temples and push for victory

## Decision Making
When choosing an action:
1. Analyze your current resources and what you can afford
2. Consider victory point opportunities
3. Avoid holding more than 7 cards (you lose half on a 7 roll)
4. Build strategically to maximize resource production

Always respond with a clear action and brief reasoning.
"""


def create_agent(model_name: str = "openai:gpt-4") -> Agent:
    """Create and configure the game agent."""
    return Agent(
        model_name,
        system_prompt=SYSTEM_PROMPT,
        result_type=GameAction,
    )


async def decide_action(
    agent: Agent,
    game_state: GameState,
    player_id: int,
    has_rolled: bool = False
) -> GameAction:
    """Use the AI agent to decide the next action."""
    player = next((p for p in game_state.players if p.id == player_id), None)
    if not player:
        return GameAction(
            action_type="end_turn",
            reasoning="Player not found"
        )
    
    # If we haven't rolled yet, must roll first
    if not has_rolled:
        return GameAction(
            action_type="roll",
            reasoning="Must roll dice at the start of turn"
        )
    
    # Get game analysis for context
    analysis = analyze_game_state(game_state, player_id)
    available_actions = get_available_actions(game_state, player_id)
    
    # Build the prompt
    prompt = f"""
Current Game State:
{analysis}

It's your turn. You have already rolled the dice.
Available actions: {', '.join(available_actions)}

Based on the current situation, what action should you take?
Consider:
1. Can you build something that gives victory points?
2. Should you expand your road network?
3. Is it better to save resources for next turn?

Choose ONE action and explain your reasoning.
"""
    
    try:
        result = await agent.run(prompt)
        return result.data
    except Exception as e:
        # Fallback to simple heuristic
        return heuristic_action(player, game_state, available_actions)


def heuristic_action(
    player: Player,
    game_state: GameState,
    available_actions: list[str]
) -> GameAction:
    """Simple heuristic fallback when AI is unavailable."""
    
    # Priority 1: Build templo if possible (most VP)
    if "build_templo" in available_actions:
        positions = find_valid_build_positions(game_state, player.id, "templo")
        if positions:
            return GameAction(
                action_type="build",
                building_type="templo",
                position_id=positions[0],
                reasoning="Building temple for 2 victory points"
            )
    
    # Priority 2: Build bohío if possible
    if "build_bohio" in available_actions:
        positions = find_valid_build_positions(game_state, player.id, "bohio")
        if positions:
            return GameAction(
                action_type="build",
                building_type="bohio",
                position_id=positions[0],
                reasoning="Building bohío for 1 victory point"
            )
    
    # Priority 3: Build camino for expansion
    if "build_camino" in available_actions:
        positions = find_valid_build_positions(game_state, player.id, "camino")
        if positions:
            return GameAction(
                action_type="build",
                building_type="camino",
                position_id=positions[0],
                reasoning="Building path for expansion"
            )
    
    # Priority 4: Buy development card
    if "buy_card" in available_actions:
        total = player.gold + player.stone + player.cotton + player.maize + player.wood
        if total > 7:  # Prevent losing cards on a 7
            return GameAction(
                action_type="buy_card",
                reasoning="Buying card to reduce hand size and gain potential VP"
            )
    
    # Default: End turn
    return GameAction(
        action_type="end_turn",
        reasoning="No beneficial actions available, ending turn"
    )

