import json
import time
from bus.event_bus import event_bus
from bus.events import PlayerJoinedRoomEvent, ViewerJoinedRoomEvent
from server.logic.room_manager import room_manager
from server.state import server_state

async def on_player_joined(event: PlayerJoinedRoomEvent):
    # שדר לכל השחקנים בחדר ששחקן חדש הצטרף
    msg = {
        "type": "player_joined",
        "payload": {
            "client_id": event.client_id,
            "player_number": event.player_number
        },
        "ts": int(time.time())
    }
    await room_manager.broadcast_to_room(event.room_id, msg)

event_bus.subscribe(PlayerJoinedRoomEvent, on_player_joined)