# 🏔️ Teyuna - The Lost City

A multiplayer strategy board game celebrating the ancient **Tayrona civilization** of Colombia's Sierra Nevada de Santa Marta.

![Teyuna Banner](https://img.shields.io/badge/Teyuna-The%20Lost%20City-gold?style=for-the-badge)

## 🎮 About the Game

**Teyuna** is a strategy board game inspired by Settlers of Catan, but themed around the Tayrona people who built the magnificent city of Teyuna (Ciudad Perdida) around 800 CE. Compete with 3-4 players to build the most prosperous settlement by gathering resources, constructing buildings, and earning victory points.

### The Tayrona Legacy

The Tayrona were master builders who created an extensive network of stone-paved paths, terraces, and settlements throughout the Sierra Nevada mountains. Their descendants—the Kogi, Arhuaco, Wiwa, and Kankuamo peoples—still inhabit this region, which they consider the "Heart of the World."

## ✨ Features

- 🎲 **Classic Strategy Gameplay** - Familiar mechanics with original Tayrona theming
- 👥 **Multiplayer Support** - Play with 3-4 players
- 🌐 **Web-Based** - Play in your browser with a beautiful, responsive UI
- 🤖 **AI Opponents** - Challenge AI players powered by LLMs
- 🔐 **User Accounts** - Track your stats and game history
- 📱 **Real-time Updates** - WebSocket-powered live game state

## 🏛️ Game Elements

### Resources
| Resource | Name | Source | Icon |
|----------|------|--------|------|
| Gold | Oro | Sierra (Mountains) | 🥇 |
| Stone | Piedra | Canteras (Quarries) | 🪨 |
| Cotton | Algodón | Tierras Altas (Highlands) | ☁️ |
| Maize | Maíz | Valles (Valleys) | 🌽 |
| Wood | Madera | Selva (Jungle) | 🌳 |

### Buildings
| Building | Name | Cost | Victory Points |
|----------|------|------|----------------|
| 🛤️ | Camino de Piedra (Stone Path) | 1 Stone + 1 Wood | 0 |
| 🏠 | Bohío (Traditional House) | 1 Stone + 1 Wood + 1 Cotton + 1 Maize | 1 |
| 🏛️ | Templo (Temple) | 3 Gold + 2 Maize | 2 |

### Special Cards
- ⚔️ **Guerrero Naoma** - Warrior cards (move the Conquistador)
- 🌾 **Abundancia de la Tierra** - Take 2 resources
- 🔮 **Sabiduría del Mama** - Monopoly on a resource
- 🛤️ **Nuevos Caminos** - Build 2 free roads
- 🏆 **Avance Ancestral** - Victory point

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI |
| Frontend | React, TypeScript, Vite |
| Database | PostgreSQL |
| AI Client | Python, Pydantic AI |
| Real-time | WebSockets |
| Styling | CSS Variables, Custom Design System |

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Docker (optional)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/yourusername/teyuna.git
cd teyuna

# Start all services
docker-compose up -d

# Access the game
open http://localhost:3000
```

### Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### AI Client

```bash
cd ai_client

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key (optional, falls back to heuristics)
export OPENAI_API_KEY=your-api-key

# Join a game
python main.py join <game-token>

# Or create a new game
python main.py create --players 4
```

## 📖 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create new account |
| POST | `/api/auth/login` | Get access token |
| POST | `/api/games` | Create new game |
| POST | `/api/games/join` | Join existing game |
| GET | `/api/games/{token}` | Get game state |
| POST | `/api/games/{token}/roll` | Roll dice |
| POST | `/api/games/{token}/build` | Build structure |
| POST | `/api/games/{token}/end-turn` | End turn |

## 🎯 Game Rules

### Objective
Be the first player to reach **10 Victory Points**.

### Turn Structure
1. **Roll Dice** - Determine which hexes produce resources
2. **Collect Resources** - All players collect from matching hexes
3. **Trade & Build** - Construct buildings, buy cards, trade with players
4. **End Turn** - Pass to the next player

### Victory Points
- Each Bohío = 1 VP
- Each Templo = 2 VP
- Longest Path (5+ roads) = 2 VP
- Largest Army (3+ warriors) = 2 VP
- Certain Wisdom Cards = 1 VP each

### The Conquistador
When a 7 is rolled:
1. Players with >7 cards discard half
2. Active player moves the Conquistador
3. Steal 1 resource from an adjacent player
4. The blocked hex produces no resources

## 🌍 Cultural Note

This game is created with deep respect for the Tayrona civilization and their descendants. The Tayrona were remarkable engineers and artists whose legacy lives on in the Sierra Nevada de Santa Marta. We encourage players to learn more about this culture and support indigenous communities in Colombia.

**Learn more:**
- [Ciudad Perdida (Lost City)](https://en.wikipedia.org/wiki/Ciudad_Perdida)
- [Tayrona People](https://en.wikipedia.org/wiki/Tairona)
- [Sierra Nevada de Santa Marta](https://en.wikipedia.org/wiki/Sierra_Nevada_de_Santa_Marta)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

---

<p align="center">
  <strong>Teyuna</strong> — Honoring the legacy of the Tayrona people<br>
  <em>Sierra Nevada de Santa Marta, Colombia</em>
</p>
