#!/usr/bin/env python3
"""
Teyuna AI Client - Terminal-based AI player for the Teyuna board game.

This client uses Pydantic AI to make strategic decisions while playing
the Teyuna board game against human players.
"""
import asyncio
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.spinner import Spinner
import typer

from config import get_settings
from api_client import GameClient
from game_state import GameState, analyze_game_state
from agent import create_agent, decide_action, heuristic_action

app = typer.Typer(help="Teyuna AI Client - Play Teyuna with an AI agent")
console = Console()
settings = get_settings()


def display_welcome():
    """Display welcome banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ████████╗███████╗██╗   ██╗██╗   ██╗███╗   ██╗ █████╗       ║
║   ╚══██╔══╝██╔════╝╚██╗ ██╔╝██║   ██║████╗  ██║██╔══██╗      ║
║      ██║   █████╗   ╚████╔╝ ██║   ██║██╔██╗ ██║███████║      ║
║      ██║   ██╔══╝    ╚██╔╝  ██║   ██║██║╚██╗██║██╔══██║      ║
║      ██║   ███████╗   ██║   ╚██████╔╝██║ ╚████║██║  ██║      ║
║      ╚═╝   ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝      ║
║                                                               ║
║              🏔️  AI Client - The Lost City  🏔️               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bold gold1")


def display_game_state(game_state: GameState, my_player_id: int):
    """Display current game state in a formatted table."""
    # Players table
    table = Table(title="🎮 Players", show_header=True, header_style="bold gold1")
    table.add_column("Player", style="cyan")
    table.add_column("Color", style="white")
    table.add_column("VP", justify="right", style="yellow")
    table.add_column("Resources", justify="right")
    table.add_column("Cards", justify="right")
    
    for player in game_state.players:
        is_me = "⭐ " if player.id == my_player_id else ""
        is_current = "🎲 " if player.id == game_state.current_player_id else ""
        
        resources = f"🥇{player.gold} 🪨{player.stone} ☁️{player.cotton} 🌽{player.maize} 🌳{player.wood}"
        cards = f"📜{player.development_cards_count} ⚔️{player.warrior_cards}"
        
        table.add_row(
            f"{is_current}{is_me}{player.username}",
            player.color.upper(),
            str(player.victory_points),
            resources,
            cards
        )
    
    console.print(table)
    
    # Turn info
    if game_state.last_dice_roll:
        dice_sum = sum(game_state.last_dice_roll)
        console.print(f"🎲 Last roll: {game_state.last_dice_roll[0]} + {game_state.last_dice_roll[1]} = {dice_sum}")


async def play_turn(client: GameClient, game_token: str, agent, my_player_id: int):
    """Play a single turn."""
    # Get current game state
    game_data = client.get_game(game_token)
    if not game_data:
        console.print("[red]Failed to get game state[/red]")
        return False
    
    game_state = GameState(**game_data)
    
    # Check if it's our turn
    if game_state.current_player_id != my_player_id:
        return True  # Not our turn, continue waiting
    
    console.print("\n[bold green]🎯 It's our turn![/bold green]\n")
    display_game_state(game_state, my_player_id)
    
    has_rolled = False
    
    while True:
        # Decide action
        with console.status("[bold gold1]AI is thinking..."):
            if agent:
                action = await decide_action(agent, game_state, my_player_id, has_rolled)
            else:
                # Fallback to heuristic
                my_player = next((p for p in game_state.players if p.id == my_player_id), None)
                if not my_player:
                    break
                if not has_rolled:
                    from agent import GameAction
                    action = GameAction(action_type="roll", reasoning="Must roll dice first")
                else:
                    from game_state import get_available_actions
                    available = get_available_actions(game_state, my_player_id)
                    action = heuristic_action(my_player, game_state, available)
        
        console.print(f"\n[cyan]Decision:[/cyan] {action.action_type}")
        console.print(f"[dim]Reasoning: {action.reasoning}[/dim]\n")
        
        # Execute action
        if action.action_type == "roll":
            result = client.roll_dice(game_token)
            if result:
                console.print(f"🎲 Rolled: {result['dice1']} + {result['dice2']} = {result['total']}")
                has_rolled = True
                
                # Refresh game state
                game_data = client.get_game(game_token)
                if game_data:
                    game_state = GameState(**game_data)
            else:
                console.print("[red]Failed to roll dice[/red]")
                break
        
        elif action.action_type == "build":
            if action.building_type and action.position_id is not None:
                result = client.build(game_token, action.building_type, action.position_id)
                if result:
                    console.print(f"🏗️ Built {action.building_type} at position {action.position_id}")
                    game_state = GameState(**result)
                else:
                    console.print(f"[yellow]Failed to build {action.building_type}[/yellow]")
        
        elif action.action_type == "buy_card":
            result = client.buy_card(game_token)
            if result:
                console.print(f"📜 Bought wisdom card: {result.get('card', 'unknown')}")
            else:
                console.print("[yellow]Failed to buy card[/yellow]")
        
        elif action.action_type == "end_turn":
            result = client.end_turn(game_token)
            if result:
                console.print("✅ Turn ended")
                return True
            else:
                console.print("[red]Failed to end turn[/red]")
                break
        
        # Small delay between actions
        await asyncio.sleep(1)
    
    return True


async def game_loop(client: GameClient, game_token: str, my_player_id: int, use_ai: bool = True):
    """Main game loop."""
    console.print(f"\n[bold]Entering game: {game_token}[/bold]\n")
    
    # Create AI agent if enabled
    agent = None
    if use_ai and settings.openai_api_key:
        try:
            agent = create_agent(f"openai:{settings.model_name}")
            console.print("[green]✓ AI agent initialized[/green]")
        except Exception as e:
            console.print(f"[yellow]AI unavailable, using heuristics: {e}[/yellow]")
    else:
        console.print("[yellow]Using heuristic player (no AI key configured)[/yellow]")
    
    while True:
        # Get game state
        game_data = client.get_game(game_token)
        if not game_data:
            console.print("[red]Lost connection to game[/red]")
            break
        
        game_state = GameState(**game_data)
        
        # Check game status
        if game_state.status == "finished":
            console.print("\n[bold]🏆 GAME OVER![/bold]")
            winner = next((p for p in game_state.players if p.user_id == game_state.winner_id), None)
            if winner:
                if winner.id == my_player_id:
                    console.print("[bold green]🎉 WE WON! 🎉[/bold green]")
                else:
                    console.print(f"[yellow]Winner: {winner.username}[/yellow]")
            break
        
        if game_state.status == "waiting":
            console.print("[dim]Waiting for game to start...[/dim]")
            await asyncio.sleep(3)
            continue
        
        # Check if it's our turn
        if game_state.current_player_id == my_player_id:
            await play_turn(client, game_token, agent, my_player_id)
        else:
            # Show whose turn it is
            current = next((p for p in game_state.players if p.id == game_state.current_player_id), None)
            if current:
                console.print(f"[dim]Waiting for {current.username}'s turn...[/dim]")
        
        await asyncio.sleep(2)


@app.command()
def join(
    token: str = typer.Argument(..., help="Game token to join"),
    use_ai: bool = typer.Option(True, "--ai/--no-ai", help="Use AI for decisions")
):
    """Join an existing game with the AI client."""
    display_welcome()
    
    client = GameClient(settings.api_base_url)
    
    # Login or register
    console.print("\n[bold]Authenticating...[/bold]")
    
    if not client.login(settings.username, settings.password):
        console.print("[yellow]User not found, registering...[/yellow]")
        if not client.register(settings.username, settings.email, settings.password):
            console.print("[red]Failed to register[/red]")
            return
        if not client.login(settings.username, settings.password):
            console.print("[red]Failed to login after registration[/red]")
            return
    
    console.print(f"[green]✓ Logged in as {settings.username}[/green]")
    
    # Join game
    result = client.join_game(token)
    if not result:
        console.print(f"[red]Failed to join game: {token}[/red]")
        return
    
    game_state = GameState(**result)
    my_player = next((p for p in game_state.players if p.username == settings.username), None)
    
    if not my_player:
        console.print("[red]Failed to find our player in game[/red]")
        return
    
    console.print(f"[green]✓ Joined game as {my_player.color} player[/green]")
    
    # Start game loop
    asyncio.run(game_loop(client, token, my_player.id, use_ai))
    
    client.close()


@app.command()
def create(
    max_players: int = typer.Option(4, "--players", "-p", help="Maximum players (3-4)"),
    use_ai: bool = typer.Option(True, "--ai/--no-ai", help="Use AI for decisions")
):
    """Create a new game and wait for players to join."""
    display_welcome()
    
    client = GameClient(settings.api_base_url)
    
    # Login or register
    console.print("\n[bold]Authenticating...[/bold]")
    
    if not client.login(settings.username, settings.password):
        console.print("[yellow]User not found, registering...[/yellow]")
        if not client.register(settings.username, settings.email, settings.password):
            console.print("[red]Failed to register[/red]")
            return
        if not client.login(settings.username, settings.password):
            console.print("[red]Failed to login after registration[/red]")
            return
    
    console.print(f"[green]✓ Logged in as {settings.username}[/green]")
    
    # Create game
    console.print(f"\n[bold]Creating {max_players}-player game...[/bold]")
    game_token = client.create_game(max_players)
    
    if not game_token:
        console.print("[red]Failed to create game[/red]")
        return
    
    console.print(Panel(
        f"[bold gold1]{game_token}[/bold gold1]",
        title="🎮 Game Created!",
        subtitle="Share this token with other players"
    ))
    
    # Get game state
    game_data = client.get_game(game_token)
    if not game_data:
        console.print("[red]Failed to get game state[/red]")
        return
    
    game_state = GameState(**game_data)
    my_player = next((p for p in game_state.players if p.username == settings.username), None)
    
    if not my_player:
        console.print("[red]Failed to find our player[/red]")
        return
    
    # Wait for players and start
    console.print("\n[bold]Waiting for players to join...[/bold]")
    console.print("[dim]Press Ctrl+C to cancel[/dim]\n")
    
    try:
        while True:
            game_data = client.get_game(game_token)
            if game_data:
                game_state = GameState(**game_data)
                player_count = len(game_state.players)
                console.print(f"Players: {player_count}/{max_players}")
                
                if player_count >= 3:
                    if Confirm.ask("Start game now?"):
                        result = client.start_game(game_token)
                        if result:
                            console.print("[green]✓ Game started![/green]")
                            break
                        else:
                            console.print("[red]Failed to start game[/red]")
            
            time.sleep(3)
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        return
    
    # Start game loop
    asyncio.run(game_loop(client, game_token, my_player.id, use_ai))
    
    client.close()


@app.command()
def list_games():
    """List all games for the AI player."""
    display_welcome()
    
    client = GameClient(settings.api_base_url)
    
    if not client.login(settings.username, settings.password):
        console.print("[red]Failed to login[/red]")
        return
    
    games = client.get_my_games()
    
    if not games:
        console.print("[dim]No games found[/dim]")
        return
    
    table = Table(title="Your Games", show_header=True, header_style="bold gold1")
    table.add_column("Token", style="cyan")
    table.add_column("Status", style="white")
    table.add_column("Players")
    
    for game in games:
        table.add_row(
            game["token"],
            game["status"].upper(),
            f"{game['current_players']}/{game['max_players']}"
        )
    
    console.print(table)
    client.close()


if __name__ == "__main__":
    app()

