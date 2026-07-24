import time
import uuid
import json
from server.state import server_state
from server.engine_adapter import EngineAdapter
from typing import Dict, List
from bus.event_bus import event_bus
from bus.events import RoomCreatedEvent, PlayerJoinedRoomEvent, ViewerJoinedRoomEvent
class Room:
    def __init__(self, room_id: str, creator_id: str):
        self.room_id = room_id
        self.players: List[str] = [creator_id]
        self.viewers: List[str] = []
        
        self.engine_adapter = EngineAdapter()
        self.game_state = self.engine_adapter.get_initial_state()
        self.last_activity = time.time()

    async def handle_move(self, client_id: str, move_data: dict) -> tuple[bool, dict]:
        if client_id not in self.players:
            return False, "Unauthorized player"

        is_valid, new_state, error = self.engine_adapter.validate_and_apply_move(
            self.game_state, move_data
        )

        if not is_valid:
            return False, error

        self.game_state = new_state
        self.last_activity = time.time()
        return True, self.game_state

    def remove_participant(self, client_id: str) -> bool:
        if client_id in self.players:
            self.players.remove(client_id)
        elif client_id in self.viewers:
            self.viewers.remove(client_id)
            
        return len(self.players) == 0 and len(self.viewers) == 0
    def add_participant(self, client_id: str) -> str:
        if client_id in self.players or client_id in self.viewers:
            return "already_in_room"

        if len(self.players) < 2:
            self.players.append(client_id)
            return "player"
        else:
            self.viewers.append(client_id)
            return "viewer"

class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.client_to_room: Dict[str, str] = {}

    async def create_room(self, creator_id: str) -> str:
        room_id = str(uuid.uuid4())[:6].upper()
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
            return {"success": True, "role": "viewer", "room_id": room_id, "current_state": room.game_state}

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
    
    def get_session_by_client(self, client_id: str):
        room_id = self.client_to_room.get(client_id)
        if room_id:
            return self.rooms.get(room_id)
        return None

    async def broadcast_to_room(self, room_id: str, message: dict):
        room = self.rooms.get(room_id)
        if not room:
            return
        
        all_participants = set(room.players + room.viewers)
        
        for participant_id in all_participants:
            client_data = server_state.connected_clients.get(participant_id)
            if client_data and "websocket" in client_data:
                await client_data["websocket"].send_text(json.dumps(message))

room_manager = RoomManager()