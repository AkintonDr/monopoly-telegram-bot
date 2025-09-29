"""
FastAPI приложение для бэкенда Monopoly Telegram Bot.
Обрабатывает API запросы от Telegram бота.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

from models import Game, Player, Property
from game_engine import MonopolyEngine

app = FastAPI(title="Monopoly Telegram Bot API", version="1.0.0")

# CORS для веб-интерфейса
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальный игровой движок
game_engine = MonopolyEngine()

class GameCreateRequest(BaseModel):
    creator_username: str
    max_players: int = 6

class PlayerJoinRequest(BaseModel):
    username: str
    game_code: str

@app.get("/")
async def root():
    return {"message": "Monopoly Telegram Bot API"}

@app.post("/api/games/create")
async def create_game(request: GameCreateRequest):
    """Создать новую игру"""
    game = await game_engine.create_game(
        creator_username=request.creator_username,
        max_players=request.max_players
    )
    return {"game_id": game.id, "game_code": game.code}

@app.post("/api/games/join")
async def join_game(request: PlayerJoinRequest):
    """Присоединиться к игре"""
    result = await game_engine.join_game(
        username=request.username,
        game_code=request.game_code
    )
    return result

@app.get("/api/games/{game_id}")
async def get_game_state(game_id: str):
    """Получить состояние игры"""
    game_state = await game_engine.get_game_state(game_id)
    if not game_state:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_state

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)