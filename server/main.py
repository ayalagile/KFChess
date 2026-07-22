import json
import logging
import time
import uuid
from typing import Dict, Callable, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from bus.event_bus import event_bus
from bus.events import ClientConnectedEvent, ClientDisconnectedEvent, MessageReceivedEvent, PlayerQueuedEvent
from bus.listeners.logging_listener import on_client_connected, on_client_disconnected, on_message_received
from server.auth import handle_login, handle_register
from server.logic.matchmaking import matchmaking_system
from server.logic.room_manager import room_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

app = FastAPI()

connected_clients: Dict[str, dict] = {}

@app.on_event("startup")
async def startup_event():
    event_bus.subscribe(ClientConnectedEvent, on_client_connected)
    event_bus.subscribe(ClientDisconnectedEvent, on_client_disconnected)
    event_bus.subscribe(MessageReceivedEvent, on_message_received)
    logger.info("Event Bus initialized and listeners subscribed.")
    matchmaking_system.setup_listeners()

# --- מנהלי הודעות (Message Handlers) ---

async def handle_register_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    response_payload = await handle_register(payload)
    return "register_result", response_payload

async def handle_login_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    global client_id_ref  # לטיפול בעדכון מזהה הלקוח מול connected_clients אם נדרש
    response_payload = await handle_login(payload)
    
    if response_payload.get("success"):
        user_info = response_payload.get("user", {})
        username = user_info.get("username")
        user_rating = user_info.get("rating", 1200)

        if username and client_id in connected_clients:
            client_data = connected_clients.pop(client_id)
            client_data["rating"] = user_rating
            client_data["username"] = username
            connected_clients[username] = client_data
            
    return "login_result", response_payload

async def handle_play_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    client_info = connected_clients.get(client_id)
    player_rating = client_info.get("rating", 1200) if isinstance(client_info, dict) else 1200

    await event_bus.publish(PlayerQueuedEvent(
        client_id=client_id, 
        rating=player_rating
    ))
    return "play_ack", {"status": "queued", "message": "Searching for match..."}

async def handle_room_menu_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    return "room_menu_ack", {"status": "ok", "action": "room_menu", "message": "Room menu requested"}

async def handle_create_room_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    room_id = await room_manager.create_room(client_id)
    return "room_created", {"status": "ok", "room_id": room_id, "role": "player", "player_number": 1}

async def handle_join_room_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    target_room_id = payload.get("room_id", "")
    result = await room_manager.join_room(client_id, target_room_id)
    return "join_room_result", result

async def handle_cancel_room_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    result = await room_manager.cancel_room(client_id)
    return "cancel_room_result", result

async def handle_join_queue_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    room_id = matchmaking_system.add_to_queue(client_id)
    if room_id:
        players = matchmaking_system.active_rooms.get(room_id, [])
        for p_id in players:
            if p_id in connected_clients:
                match_msg = {
                    "type": "match_found",
                    "payload": {"room_id": room_id, "opponent_id": [p for p in players if p != p_id][0]},
                    "ts": int(time.time())
                }
                await connected_clients[p_id]["websocket"].send_text(json.dumps(match_msg))
        return "queue_result", {"status": "matched", "room_id": room_id}
    else:
        return "queue_result", {"status": "queued", "message": "Waiting for an opponent..."}

async def handle_leave_queue_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    matchmaking_system.remove_from_queue(client_id)
    return "queue_result", {"status": "left_queue"}

async def handle_move_msg(client_id: str, payload: dict, websocket: WebSocket) -> tuple[str, dict]:
    move_data = payload.get("move", {})
    session = room_manager.get_session_by_client(client_id)
    
    if not session:
        await websocket.send_json({
            "type": "error",
            "payload": {"message": "You are not in an active game session."},
            "ts": int(time.time())
        })
        return "", {}

    success, result = await session.handle_move(client_id, move_data)
    
    if not success:
        await websocket.send_json({
            "type": "move_error",
            "payload": {"message": result},
            "ts": int(time.time())
        })
        return "", {}
    else:
        broadcast_message = {
            "type": "game_state_update",
            "payload": {
                "room_id": session.room_id,
                "last_move": move_data,
                "state": result
            },
            "ts": int(time.time())
        }
        await room_manager.broadcast_to_room(session.room_id, broadcast_message)
        return "", {}

# מילון הנתבים המרכזי (Dispatcher)
MESSAGE_HANDLERS: Dict[str, Callable[[str, dict, WebSocket], Any]] = {
    "register": handle_register_msg,
    "login": handle_login_msg,
    "play": handle_play_msg,
    "room_menu": handle_room_menu_msg,
    "create_room": handle_create_room_msg,
    "join_room": handle_join_room_msg,
    "cancel_room": handle_cancel_room_msg,
    "join_queue": handle_join_queue_msg,
    "leave_queue": handle_leave_queue_msg,
    "move": handle_move_msg,
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4())[:8]
    connected_clients[client_id] = {
        "websocket": websocket,
        "rating": 1200,
        "username": None
    }
    
    await event_bus.publish(ClientConnectedEvent(client_id=client_id))
    
    try:
        while True:
            data_str = await websocket.receive_text()
            print(f"DEBUG SERVER RECEIVED: {data_str}")
            
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                error_response = {
                    "type": "error",
                    "payload": {"message": "Invalid JSON format"},
                    "ts": int(time.time())
                }
                await websocket.send_text(json.dumps(error_response))
                continue

            msg_type = data.get("type", "unknown")
            payload = data.get("payload", {})
            request_id = data.get("request_id", "")

            await event_bus.publish(MessageReceivedEvent(
                client_id=client_id,
                msg_type=msg_type,
                payload=payload,
                request_id=request_id
            ))

            handler = MESSAGE_HANDLERS.get(msg_type)
            if handler:
                response_type, response_payload = await handler(client_id, payload, websocket)
                
                # אם הוחזר סוג תגובה ריק (כמו ב־move שנשלח דרך Broadcast), נדלג על שליחת התגובה הרגילה
                if not response_type:
                    continue

                response = {
                    "type": response_type,
                    "payload": response_payload,
                    "request_id": request_id,
                    "ts": int(time.time())
                }
            else:
                response = {
                    "type": f"echo_{msg_type}",
                    "payload": payload,
                    "request_id": request_id,
                    "ts": int(time.time())
                }

            client_data = connected_clients.get(client_id)
            if client_data:
                await client_data["websocket"].send_text(json.dumps(response))

    except WebSocketDisconnect:
        matchmaking_system.remove_from_queue(client_id)
        matchmaking_system.leave_room(client_id)
        if client_id in connected_clients:
            del connected_clients[client_id]
            
        await event_bus.publish(ClientDisconnectedEvent(client_id=client_id))