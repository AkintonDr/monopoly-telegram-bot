"""
Модели данных для Monopoly Bot.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
import json

Base = declarative_base()

class Game(Base):
    __tablename__ = "games"
    
    id = Column(String, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    creator_id = Column(String, nullable=False)
    status = Column(String, default="waiting")  # waiting, active, finished
    current_player_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    max_players = Column(Integer, default=6)
    
    # Связи
    players = relationship("Player", back_populates="game", cascade="all, delete-orphan")
    properties = relationship("PropertyOwnership", back_populates="game")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    telegram_id = Column(String, nullable=False)
    game_id = Column(String, ForeignKey("games.id"))
    position = Column(Integer, default=0)
    money = Column(Integer, default=1500)
    is_in_jail = Column(Boolean, default=False)
    jail_turns = Column(Integer, default=0)
    consecutive_doubles = Column(Integer, default=0)
    has_get_out_card = Column(Boolean, default=False)
    color = Column(String)  # Цвет игрока для отображения
    is_bankrupt = Column(Boolean, default=False)
    
    # Связи
    game = relationship("Game", back_populates="players")
    owned_properties = relationship("PropertyOwnership", back_populates="owner")

class PropertyOwnership(Base):
    __tablename__ = "property_ownership"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey("games.id"))
    property_id = Column(Integer, nullable=False)  # ID клетки на поле
    owner_id = Column(String, ForeignKey("players.id"))
    houses = Column(Integer, default=0)
    hotels = Column(Integer, default=0)
    is_mortgaged = Column(Boolean, default=False)
    mortgage_date = Column(DateTime)
    
    # Связи
    game = relationship("Game", back_populates="properties")
    owner = relationship("Player", back_populates="owned_properties")

class TradeOffer(Base):
    __tablename__ = "trade_offers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey("games.id"))
    from_player_id = Column(String, ForeignKey("players.id"))
    to_player_id = Column(String, ForeignKey("players.id"))
    offered_money = Column(Integer, default=0)
    offered_properties = Column(Text)  # JSON список property_id
    requested_money = Column(Integer, default=0)
    requested_properties = Column(Text)  # JSON список property_id
    status = Column(String, default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

class GameAction(Base):
    __tablename__ = "game_actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(String, ForeignKey("games.id"))
    player_id = Column(String, ForeignKey("players.id"))
    action_type = Column(String, nullable=False)  # move, buy, sell, mortgage, etc.
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(Text)  # JSON с дополнительными данными

# Pydantic модели для API
class PlayerResponse(BaseModel):
    id: str
    username: str
    position: int
    money: int
    is_in_jail: bool
    jail_turns: int
    consecutive_doubles: int
    has_get_out_card: bool
    color: str
    is_bankrupt: bool
    properties: List[Dict]

class GameResponse(BaseModel):
    id: str
    code: str
    status: str
    current_player_index: int
    players: List[PlayerResponse]
    board_state: Dict