"""
Teyuna - A Strategy Board Game

A multiplayer strategy board game inspired by the Tayrona civilization
of the Sierra Nevada de Santa Marta, Colombia.

Build bohíos (houses), templos (temples), and caminos (stone paths) to
develop your community and honor the ancient traditions of Teyuna.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, close_db
from app.api import auth_router, games_router, ws_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="Teyuna",
    description="""
## 🏔️ Teyuna - The Lost City Strategy Game

A multiplayer strategy board game celebrating the ancient Tayrona civilization
of Colombia's Sierra Nevada de Santa Marta.

### 🎮 Game Overview

Compete with 3-4 players to build the most prosperous community inspired by 
the legendary city of Teyuna (Ciudad Perdida). Gather resources, construct 
buildings, and earn victory points to win.

### 🏛️ Buildings

- **Camino de Piedra** (Stone Path) - Connect your settlements
- **Bohío** (Traditional House) - Circular dwellings that earn resources
- **Templo** (Temple) - Sacred ceremonial structures

### 💎 Resources

- **Oro** (Gold) - From the Sierra mountains
- **Piedra** (Stone) - From the quarries
- **Algodón** (Cotton) - From the highlands
- **Maíz** (Maize) - From the fertile valleys
- **Madera** (Wood) - From the jungle

### 📜 API Endpoints

Use the endpoints below to register, authenticate, and play!
    """,
    version=settings.app_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(games_router, prefix="/api")
app.include_router(ws_router)


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint."""
    return {
        "name": "Teyuna",
        "description": "A strategy board game inspired by the Tayrona civilization",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

