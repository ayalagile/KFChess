import uuid
from typing import Dict, List
from bus.event_bus import event_bus
from bus.events import RoomCreatedEvent, PlayerJoinedRoomEvent, ViewerJoinedRoomEvent

class Room:
    def __init__(self, room_id: str, creator_id: str):
        self.room_id = room_id
        self.players: List[str] = [creator_id]  # השחקן הראשון שיוצר את החדר
        self.viewers: List[str] = []  # צופים

    def add_participant(self, client_id: str) -> str:
        """מוסיף משתתף לחדר. מחזיר 'player' או 'viewer'."""
        if client_id in self.players or client_id in self.viewers:
            return "already_in_room"

        if len(self.players) < 2:
            self.players.append(client_id)
            return "player"
        else:
            self.viewers.append(client_id)
            return "viewer"

    def remove_participant(self, client_id: str) -> bool:
        """מסיר משתתף. מחזיר True אם החדר התרוקן לחלוטין."""
        if client_id in self.players:
            self.players.remove(client_id)
        elif client_id in self.viewers:
            self.viewers.remove(client_id)
            
        return len(self.players) == 0 and len(self.viewers) == 0

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.client_to_room: Dict[str, str] = {}

    async def create_room(self, creator_id: str) -> str:
        room_id = str(uuid.uuid4())[:6].upper()  # קוד חדר קצר
        room = Room(room_id, creator_id)
        self.rooms[room_id] = room
        self.client_to_room[creator_id] = room_id

        await event_bus.publish(RoomCreatedEvent(room_id=room_id, creator_id=creator_id))
        await event_bus.publish(PlayerJoinedRoomEvent(room_id=room_id, client_id=creator_id, player_number=1))
        
        return room_id

    async def join_room(self, client_id: str, room_id: str) -> dict:
        if room_id not in self.rooms:
            return {"success": False, "message": "Room not found"}

        room = self.rooms[room_id]
        role = room.add_participant(client_id)

        if role == "already_in_room":
            return {"success": True, "role": "player" if client_id in room.players else "viewer", "room_id": room_id}

        self.client_to_room[client_id] = room_id

        if role == "player":
            player_num = len(room.players)
            await event_bus.publish(PlayerJoinedRoomEvent(room_id=room_id, client_id=client_id, player_number=player_num))
            return {"success": True, "role": "player", "player_number": player_num, "room_id": room_id}
        else:
            await event_bus.publish(ViewerJoinedRoomEvent(room_id=room_id, client_id=client_id))
            return {"success": True, "role": "viewer", "room_id": room_id}

    async def cancel_room(self, client_id: str) -> dict:
        room_id = self.client_to_room.get(client_id)
        if not room_id or room_id not in self.rooms:
            return {"success": False, "message": "Client not in any room"}

        room = self.rooms[room_id]
        is_empty = room.remove_participant(client_id)
        del self.client_to_room[client_id]

        if is_empty:
            del self.rooms[room_id]

        return {"success": True, "message": f"Left room {room_id}"}

# יצירת המופע המרכזי של מנהל החדרים
room_manager = RoomManager()