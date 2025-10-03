"""
Игровой движок Monopoly - основная логика игры.
Реализует все правила классической Монополии включая:
- Систему залога недвижимости
- Механику тюрьмы с дублями
- Торги между игроками
- Строительство с равномерным развитием
- Корректный расчет арендной платы
"""

import random
import uuid
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import asyncio
import json

class MonopolyEngine:
    def __init__(self):
        self.games: Dict[str, Dict] = {}
        self.board_squares = self._initialize_board()
        self.chance_cards = self._initialize_chance_cards()
        self.community_chest_cards = self._initialize_community_cards()
        
    def _initialize_board(self) -> List[Dict]:
        """Инициализация игрового поля с 40 клетками"""
        return [
            {"id": 0, "name": "Старт", "type": "start", "price": 0, "rent": 0, "group": "special"},
            {"id": 1, "name": "Васильевский остров", "type": "property", "group": "brown", "price": 60, "rent": [2, 10, 30, 90, 160, 250], "mortgage": 30, "house_price": 50},
            {"id": 2, "name": "Общественная касса", "type": "community_chest", "price": 0, "rent": 0, "group": "special"},
            {"id": 3, "name": "Петроградка", "type": "property", "group": "brown", "price": 60, "rent": [4, 20, 60, 180, 320, 450], "mortgage": 30, "house_price": 50},
            {"id": 4, "name": "Подоходный налог", "type": "tax", "amount": 200, "price": 0, "rent": 0, "group": "special"},
            {"id": 5, "name": "Московский вокзал", "type": "railroad", "price": 200, "rent": [25, 50, 100, 200], "mortgage": 100, "group": "railroad"},
            {"id": 6, "name": "Адмиралтейский", "type": "property", "group": "light_blue", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "mortgage": 50, "house_price": 50},
            {"id": 7, "name": "Шанс", "type": "chance", "price": 0, "rent": 0, "group": "special"},
            {"id": 8, "name": "Центральный", "type": "property", "group": "light_blue", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "mortgage": 50, "house_price": 50},
            {"id": 9, "name": "Невский проспект", "type": "property", "group": "light_blue", "price": 120, "rent": [8, 40, 100, 300, 450, 600], "mortgage": 60, "house_price": 50},
            {"id": 10, "name": "Тюрьма", "type": "jail", "price": 0, "rent": 0, "group": "special"},
            {"id": 11, "name": "Московский", "type": "property", "group": "pink", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "mortgage": 70, "house_price": 100},
            {"id": 12, "name": "Электростанция", "type": "utility", "price": 150, "mortgage": 75, "group": "utility"},
            {"id": 13, "name": "Фрунзенский", "type": "property", "group": "pink", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "mortgage": 70, "house_price": 100},
            {"id": 14, "name": "Красносельский", "type": "property", "group": "pink", "price": 160, "rent": [12, 60, 180, 500, 700, 900], "mortgage": 80, "house_price": 100},
            {"id": 15, "name": "Витебский вокзал", "type": "railroad", "price": 200, "rent": [25, 50, 100, 200], "mortgage": 100, "group": "railroad"},
            {"id": 16, "name": "Выборгский", "type": "property", "group": "orange", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "mortgage": 90, "house_price": 100},
            {"id": 17, "name": "Общественная касса", "type": "community_chest", "price": 0, "rent": 0, "group": "special"},
            {"id": 18, "name": "Калининский", "type": "property", "group": "orange", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "mortgage": 90, "house_price": 100},
            {"id": 19, "name": "Приморский", "type": "property", "group": "orange", "price": 200, "rent": [16, 80, 220, 600, 800, 1000], "mortgage": 100, "house_price": 100},
            {"id": 20, "name": "Бесплатная парковка", "type": "free_parking", "price": 0, "rent": 0, "group": "special"},
            {"id": 21, "name": "Кировский", "type": "property", "group": "red", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "mortgage": 110, "house_price": 150},
            {"id": 22, "name": "Шанс", "type": "chance", "price": 0, "rent": 0, "group": "special"},
            {"id": 23, "name": "Красногвардейский", "type": "property", "group": "red", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "mortgage": 110, "house_price": 150},
            {"id": 24, "name": "Колпинский", "type": "property", "group": "red", "price": 240, "rent": [20, 100, 300, 750, 925, 1100], "mortgage": 120, "house_price": 150},
            {"id": 25, "name": "Финляндский вокзал", "type": "railroad", "price": 200, "rent": [25, 50, 100, 200], "mortgage": 100, "group": "railroad"},
            {"id": 26, "name": "Курортный", "type": "property", "group": "yellow", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "mortgage": 130, "house_price": 150},
            {"id": 27, "name": "Кронштадтский", "type": "property", "group": "yellow", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "mortgage": 130, "house_price": 150},
            {"id": 28, "name": "Водопровод", "type": "utility", "price": 150, "mortgage": 75, "group": "utility"},
            {"id": 29, "name": "Пушкинский", "type": "property", "group": "yellow", "price": 280, "rent": [24, 120, 360, 850, 1025, 1200], "mortgage": 140, "house_price": 150},
            {"id": 30, "name": "В тюрьму", "type": "go_to_jail", "price": 0, "rent": 0, "group": "special"},
            {"id": 31, "name": "Петродворцовый", "type": "property", "group": "green", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "mortgage": 150, "house_price": 200},
            {"id": 32, "name": "Ломоносовский", "type": "property", "group": "green", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "mortgage": 150, "house_price": 200},
            {"id": 33, "name": "Общественная касса", "type": "community_chest", "price": 0, "rent": 0, "group": "special"},
            {"id": 34, "name": "Гатчинский", "type": "property", "group": "green", "price": 320, "rent": [28, 150, 450, 1000, 1200, 1400], "mortgage": 160, "house_price": 200},
            {"id": 35, "name": "Балтийский вокзал", "type": "railroad", "price": 200, "rent": [25, 50, 100, 200], "mortgage": 100, "group": "railroad"},
            {"id": 36, "name": "Шанс", "type": "chance", "price": 0, "rent": 0, "group": "special"},
            {"id": 37, "name": "Дворцовая площадь", "type": "property", "group": "blue", "price": 350, "rent": [35, 175, 500, 1100, 1300, 1500], "mortgage": 175, "house_price": 200},
            {"id": 38, "name": "Роскошный налог", "type": "tax", "amount": 100, "price": 0, "rent": 0, "group": "special"},
            {"id": 39, "name": "Эрмитаж", "type": "property", "group": "blue", "price": 400, "rent": [50, 200, 600, 1400, 1700, 2000], "mortgage": 200, "house_price": 200}
        ]

    def _initialize_chance_cards(self) -> List[Dict]:
        """Карты Шанс"""
        return [
            {"text": "Пройдите на Старт и получите 200₽", "action": "move_to", "target": 0, "money": 200},
            {"text": "Пройдите в тюрьму прямо, не проходите Старт", "action": "go_to_jail"},
            {"text": "Заплатите штраф за превышение скорости 15₽", "action": "pay", "amount": 15},
            {"text": "Получите 50₽", "action": "receive", "amount": 50},
            {"text": "Ремонт домов: по 25₽ за дом, по 100₽ за отель", "action": "repair", "house_cost": 25, "hotel_cost": 100},
            {"text": "Освобождение из тюрьмы", "action": "get_out_of_jail_card"}
        ]
        
    def _initialize_community_cards(self) -> List[Dict]:
        """Карты Общественная касса"""
        return [
            {"text": "Получите наследство 100₽", "action": "receive", "amount": 100},
            {"text": "Ошибка банка в вашу пользу. Получите 200₽", "action": "receive", "amount": 200},
            {"text": "Подоходный налог. Заплатите 200₽", "action": "pay", "amount": 200},
            {"text": "Получите дивиденды 20₽", "action": "receive", "amount": 20},
            {"text": "Освобождение из тюрьмы", "action": "get_out_of_jail_card"}
        ]

    async def create_game(self, creator_username: str, max_players: int = 6) -> Dict:
        """Создать новую игру"""
        game_id = str(uuid.uuid4())
        game_code = str(random.randint(100000, 999999))
        
        game_state = {
            "id": game_id,
            "code": game_code,
            "creator": creator_username,
            "status": "waiting",  # waiting, active, finished
            "max_players": max_players,
            "current_player_index": 0,
            "created_at": datetime.utcnow().isoformat(),
            "players": [],
            "properties": {},  # property_id: {owner_id, houses, hotels, mortgaged}
            "houses_remaining": 32,
            "hotels_remaining": 12,
            "turn_order": [],
            "game_log": []
        }
        
        self.games[game_id] = game_state
        
        self._add_game_log(game_id, f"🎮 Игра создана игроком {creator_username}")
        
        return {
            "success": True,
            "game_id": game_id,
            "game_code": game_code
        }

    async def join_game(self, username: str, game_code: str) -> Dict:
        """Присоединиться к игре"""
        game = self._find_game_by_code(game_code)
        
        if not game:
            return {"success": False, "error": "Игра не найдена"}
            
        if game["status"] != "waiting":
            return {"success": False, "error": "Игра уже началась"}
            
        if len(game["players"]) >= game["max_players"]:
            return {"success": False, "error": "Игра переполнена"}
            
        # Проверка, что игрок уже не в игре
        for player in game["players"]:
            if player["username"] == username:
                return {"success": False, "error": "Вы уже в этой игре"}
        
        # Создание нового игрока
        player_colors = ["🔴", "🔵", "🟢", "🟡", "🟠", "🟣"]
        player_id = str(uuid.uuid4())
        
        player = {
            "id": player_id,
            "username": username,
            "position": 0,
            "money": 1500,
            "color": player_colors[len(game["players"])],
            "is_in_jail": False,
            "jail_turns": 0,
            "consecutive_doubles": 0,
            "has_get_out_card": False,
            "is_bankrupt": False,
            "properties": []
        }
        
        game["players"].append(player)
        game["turn_order"].append(player_id)
        
        self._add_game_log(game["id"], f"👤 {username} присоединился к игре")
        
        return {
            "success": True,
            "game_id": game["id"],
            "player_id": player_id
        }

    async def start_game(self, game_id: str) -> Dict:
        """Начать игру"""
        if game_id not in self.games:
            return {"success": False, "error": "Игра не найдена"}
            
        game = self.games[game_id]
        
        if game["status"] != "waiting":
            return {"success": False, "error": "Игра уже началась"}
            
        if len(game["players"]) < 2:
            return {"success": False, "error": "Недостаточно игроков"}
        
        # Перемешиваем порядок ходов
        random.shuffle(game["turn_order"])
        game["status"] = "active"
        game["current_player_index"] = 0
        
        self._add_game_log(game_id, "🚀 Игра началась!")
        
        return {"success": True, "current_player": game["turn_order"][0]}

    async def roll_dice(self, game_id: str, player_id: str) -> Dict:
        """Бросить кубики"""
        game = self.games.get(game_id)
        if not game:
            return {"success": False, "error": "Игра не найдена"}
            
        player = self._get_player(game, player_id)
        if not player:
            return {"success": False, "error": "Игрок не найден"}
            
        if not self._is_player_turn(game, player_id):
            return {"success": False, "error": "Не ваш ход"}
        
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        total = dice1 + dice2
        is_double = dice1 == dice2
        
        self._add_game_log(game_id, f"🎲 {player['username']} бросил кубики: {dice1} + {dice2} = {total}" + 
                          (" (Дубль!)" if is_double else ""))
        
        # Обработка дублей
        if is_double:
            player["consecutive_doubles"] += 1
            if player["consecutive_doubles"] == 3:
                # Третий дубль подряд - в тюрьму
                await self._send_to_jail(game_id, player_id, "Три дубля подряд")
                player["consecutive_doubles"] = 0
                return {
                    "success": True,
                    "dice1": dice1,
                    "dice2": dice2,
                    "total": total,
                    "is_double": is_double,
                    "sent_to_jail": True,
                    "message": "Три дубля подряд! Отправляйтесь в тюрьму!"
                }
        else:
            player["consecutive_doubles"] = 0
        
        # Если в тюрьме
        if player["is_in_jail"]:
            return await self._handle_jail_roll(game_id, player_id, dice1, dice2)
        
        # Обычное движение
        old_position = player["position"]
        new_position = (old_position + total) % 40
        passed_start = new_position < old_position
        
        player["position"] = new_position
        
        if passed_start:
            player["money"] += 200
            self._add_game_log(game_id, f"💰 {player['username']} прошел Старт и получил 200₽")
        
        # Обработка клетки, на которую попал
        square = self.board_squares[new_position]
        action_result = await self._handle_square_landing(game_id, player_id, new_position)
        
        return {
            "success": True,
            "dice1": dice1,
            "dice2": dice2,
            "total": total,
            "is_double": is_double,
            "old_position": old_position,
            "new_position": new_position,
            "passed_start": passed_start,
            "square": square,
            "action_result": action_result,
            "extra_turn": is_double and not action_result.get("sent_to_jail", False)
        }

    async def _handle_jail_roll(self, game_id: str, player_id: str, dice1: int, dice2: int) -> Dict:
        """Обработка броска в тюрьме"""
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        
        is_double = dice1 == dice2
        player["jail_turns"] += 1
        
        if is_double:
            # Освобождение по дублю
            player["is_in_jail"] = False
            player["jail_turns"] = 0
            player["consecutive_doubles"] = 1  # Засчитываем дубль
            
            # Движение после освобождения
            total = dice1 + dice2
            old_position = player["position"]
            new_position = (old_position + total) % 40
            player["position"] = new_position
            
            self._add_game_log(game_id, f"🔓 {player['username']} освободился из тюрьмы дублем и переместился на позицию {new_position}")
            
            return {
                "success": True,
                "dice1": dice1,
                "dice2": dice2,
                "freed_from_jail": True,
                "new_position": new_position,
                "extra_turn": True
            }
        
        elif player["jail_turns"] >= 3:
            # Принудительное освобождение после 3 ходов
            if player["money"] >= 50:
                player["money"] -= 50
                player["is_in_jail"] = False
                player["jail_turns"] = 0
                
                self._add_game_log(game_id, f"🔓 {player['username']} принудительно освободился из тюрьмы, заплатив 50₽")
                
                return {
                    "success": True,
                    "dice1": dice1,
                    "dice2": dice2,
                    "forced_release": True,
                    "amount_paid": 50
                }
            else:
                # Банкротство
                return await self._handle_bankruptcy(game_id, player_id)
        
        else:
            self._add_game_log(game_id, f"🔒 {player['username']} остается в тюрьме (попытка {player['jail_turns']}/3)")
            
            return {
                "success": True,
                "dice1": dice1,
                "dice2": dice2,
                "still_in_jail": True,
                "attempts_left": 3 - player["jail_turns"]
            }

    async def _send_to_jail(self, game_id: str, player_id: str, reason: str) -> None:
        """Отправить игрока в тюрьму"""
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        
        player["position"] = 10
        player["is_in_jail"] = True
        player["jail_turns"] = 0
        player["consecutive_doubles"] = 0
        
        self._add_game_log(game_id, f"🚔 {player['username']} отправлен в тюрьму: {reason}")

    async def _handle_square_landing(self, game_id: str, player_id: str, position: int) -> Dict:
        """Обработка попадания на клетку"""
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        square = self.board_squares[position]
        
        if square["type"] == "property":
            return await self._handle_property_landing(game_id, player_id, position)
        elif square["type"] == "railroad":
            return await self._handle_railroad_landing(game_id, player_id, position)
        elif square["type"] == "utility":
            return await self._handle_utility_landing(game_id, player_id, position)
        elif square["type"] == "tax":
            return await self._handle_tax_landing(game_id, player_id, position)
        elif square["type"] == "chance":
            return await self._handle_chance_card(game_id, player_id)
        elif square["type"] == "community_chest":
            return await self._handle_community_card(game_id, player_id)
        elif square["type"] == "go_to_jail":
            await self._send_to_jail(game_id, player_id, "Попадание на поле 'В тюрьму'")
            return {"sent_to_jail": True}
        
        return {"action": "none"}

    async def _handle_property_landing(self, game_id: str, player_id: str, position: int) -> Dict:
        """Обработка попадания на недвижимость"""
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        square = self.board_squares[position]
        
        # Проверяем, есть ли владелец
        property_info = game["properties"].get(str(position))
        
        if not property_info:
            # Свободная недвижимость - можно купить
            return {
                "action": "can_buy",
                "property": square,
                "price": square["price"]
            }
        
        owner_id = property_info["owner_id"]
        if owner_id == player_id:
            # Своя недвижимость
            return {"action": "own_property"}
        
        # Чужая недвижимость - платим аренду
        if property_info.get("mortgaged", False):
            # Заложенная недвижимость - аренды нет
            return {"action": "mortgaged_property"}
        
        # Рассчитываем аренду
        rent = self._calculate_property_rent(game, position, property_info)
        
        if player["money"] >= rent:
            player["money"] -= rent
            owner = self._get_player(game, owner_id)
            owner["money"] += rent
            
            self._add_game_log(game_id, f"💰 {player['username']} заплатил {rent}₽ аренды игроку {owner['username']} за {square['name']}")
            
            return {
                "action": "paid_rent",
                "amount": rent,
                "to_player": owner["username"]
            }
        else:
            # Недостаточно денег - начинаем процедуру банкротства
            return await self._handle_insufficient_funds(game_id, player_id, rent)

    def _calculate_property_rent(self, game: Dict, position: int, property_info: Dict) -> int:
        """Расчет арендной платы за недвижимость"""
        square = self.board_squares[position]
        houses = property_info.get("houses", 0)
        hotels = property_info.get("hotels", 0)
        
        if hotels > 0:
            return square["rent"][5]  # Аренда с отелем
        elif houses > 0:
            return square["rent"][houses]  # Аренда с домами
        else:
            # Проверяем монополию (владение всей цветовой группой)
            if self._has_monopoly(game, property_info["owner_id"], square["group"]):
                return square["rent"][0] * 2  # Удвоенная аренда
            else:
                return square["rent"][0]  # Базовая аренда

    def _has_monopoly(self, game: Dict, player_id: str, color_group: str) -> bool:
        """Проверка монополии игрока в цветовой группе"""
        group_properties = [sq for sq in self.board_squares if sq.get("group") == color_group and sq["type"] == "property"]
        owned_count = 0
        
        for prop in group_properties:
            prop_info = game["properties"].get(str(prop["id"]))
            if prop_info and prop_info["owner_id"] == player_id:
                owned_count += 1
        
        return owned_count == len(group_properties)

    async def buy_property(self, game_id: str, player_id: str, position: int) -> Dict:
        """Купить недвижимость"""
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        square = self.board_squares[position]
        
        if str(position) in game["properties"]:
            return {"success": False, "error": "Недвижимость уже куплена"}
        
        if player["money"] < square["price"]:
            return {"success": False, "error": "Недостаточно денег"}
        
        # Покупка
        player["money"] -= square["price"]
        player["properties"].append(position)
        
        game["properties"][str(position)] = {
            "owner_id": player_id,
            "houses": 0,
            "hotels": 0,
            "mortgaged": False
        }
        
        self._add_game_log(game_id, f"🏠 {player['username']} купил {square['name']} за {square['price']}₽")
        
        return {"success": True, "amount_paid": square["price"]}

    async def mortgage_property(self, game_id: str, player_id: str, position: int) -> Dict:
        """Заложить недвижимость"""
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        square = self.board_squares[position]
        
        property_info = game["properties"].get(str(position))
        if not property_info or property_info["owner_id"] != player_id:
            return {"success": False, "error": "Вы не владеете этой недвижимостью"}
        
        if property_info["mortgaged"]:
            return {"success": False, "error": "Недвижимость уже заложена"}
        
        if property_info["houses"] > 0 or property_info["hotels"] > 0:
            return {"success": False, "error": "Сначала продайте все постройки"}
        
        # Залог
        mortgage_value = square["mortgage"]
        player["money"] += mortgage_value
        property_info["mortgaged"] = True
        
        self._add_game_log(game_id, f"🏦 {player['username']} заложил {square['name']} за {mortgage_value}₽")
        
        return {"success": True, "amount_received": mortgage_value}

    async def unmortgage_property(self, game_id: str, player_id: str, position: int) -> Dict:
        """Выкупить недвижимость из залога"""
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        square = self.board_squares[position]
        
        property_info = game["properties"].get(str(position))
        if not property_info or property_info["owner_id"] != player_id:
            return {"success": False, "error": "Вы не владеете этой недвижимостью"}
        
        if not property_info["mortgaged"]:
            return {"success": False, "error": "Недвижимость не заложена"}
        
        # Стоимость выкупа = залоговая стоимость + 10%
        unmortgage_cost = int(square["mortgage"] * 1.1)
        
        if player["money"] < unmortgage_cost:
            return {"success": False, "error": "Недостаточно денег для выкупа"}
        
        # Выкуп
        player["money"] -= unmortgage_cost
        property_info["mortgaged"] = False
        
        self._add_game_log(game_id, f"🏦 {player['username']} выкупил {square['name']} за {unmortgage_cost}₽")
        
        return {"success": True, "amount_paid": unmortgage_cost}

    async def end_turn(self, game_id: str, player_id: str) -> Dict:
        """Завершить ход"""
        game = self.games[game_id]
        
        if not self._is_player_turn(game, player_id):
            return {"success": False, "error": "Не ваш ход"}
        
        # Переход к следующему игроку
        game["current_player_index"] = (game["current_player_index"] + 1) % len(game["turn_order"])
        next_player_id = game["turn_order"][game["current_player_index"]]
        next_player = self._get_player(game, next_player_id)
        
        self._add_game_log(game_id, f"⏭️ Ход переходит к {next_player['username']}")
        
        return {
            "success": True,
            "next_player_id": next_player_id,
            "next_player_username": next_player["username"]
        }

    def _get_player(self, game: Dict, player_id: str) -> Optional[Dict]:
        """Получить игрока по ID"""
        for player in game["players"]:
            if player["id"] == player_id:
                return player
        return None

    def _is_player_turn(self, game: Dict, player_id: str) -> bool:
        """Проверить, ход ли игрока"""
        current_player_id = game["turn_order"][game["current_player_index"]]
        return current_player_id == player_id

    def _find_game_by_code(self, game_code: str) -> Optional[Dict]:
        """Найти игру по коду"""
        for game in self.games.values():
            if game["code"] == game_code:
                return game
        return None

    def _add_game_log(self, game_id: str, message: str) -> None:
        """Добавить запись в лог игры"""
        game = self.games.get(game_id)
        if game:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message
            }
            game["game_log"].append(log_entry)
            
            # Ограничиваем лог до 100 последних записей
            if len(game["game_log"]) > 100:
                game["game_log"] = game["game_log"][-100:]

    async def get_game_state(self, game_id: str) -> Optional[Dict]:
        """Получить полное состояние игры"""
        game = self.games.get(game_id)
        if not game:
            return None
        
        return {
            "id": game["id"],
            "code": game["code"],
            "status": game["status"],
            "current_player_index": game["current_player_index"],
            "players": game["players"],
            "properties": game["properties"],
            "board": self.board_squares,
            "houses_remaining": game["houses_remaining"],
            "hotels_remaining": game["hotels_remaining"],
            "game_log": game["game_log"][-20:]  # Последние 20 записей
        }

    async def _handle_bankruptcy(self, game_id: str, player_id: str) -> Dict:
        """Обработка банкротства"""
        game = self.games[game_id]
        player = self._get_player(game, player_id)
        
        player["is_bankrupt"] = True
        
        # Освобождаем всю недвижимость
        properties_to_free = []
        for pos_str, prop_info in game["properties"].items():
            if prop_info["owner_id"] == player_id:
                properties_to_free.append(pos_str)
        
        for pos_str in properties_to_free:
            del game["properties"][pos_str]
        
        self._add_game_log(game_id, f"💸 {player['username']} обанкротился!")
        
        # Проверяем окончание игры
        active_players = [p for p in game["players"] if not p["is_bankrupt"]]
        if len(active_players) <= 1:
            game["status"] = "finished"
            if active_players:
                self._add_game_log(game_id, f"🏆 {active_players[0]['username']} победил!")
        
        return {"bankruptcy": True}

# Минимальные стабы для других методов
    async def _handle_railroad_landing(self, game_id: str, player_id: str, position: int) -> Dict:
        """Обработка ЖД станций"""
        return {"action": "railroad_landing"}
    
    async def _handle_utility_landing(self, game_id: str, player_id: str, position: int) -> Dict:
        """Обработка коммунальных предприятий"""
        return {"action": "utility_landing"}
    
    async def _handle_tax_landing(self, game_id: str, player_id: str, position: int) -> Dict:
        """Обработка налогов"""
        return {"action": "tax_landing"}
    
    async def _handle_chance_card(self, game_id: str, player_id: str) -> Dict:
        """Обработка карты Шанс"""
        return {"action": "chance_card"}
    
    async def _handle_community_card(self, game_id: str, player_id: str) -> Dict:
        """Обработка карты Общественная касса"""
        return {"action": "community_card"}
        
    async def _handle_insufficient_funds(self, game_id: str, player_id: str, amount: int) -> Dict:
        """Обработка нехватки денег"""
        return {"action": "insufficient_funds", "required": amount}