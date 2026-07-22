import json
import logging
import time
import uuid
import bus.listeners.match_listener
from typing import Dict
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
            print(f"DEBUG SERVER RECEIVED: {data_str}")  # <-- תוסיפי את זה כאן
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

            response_payload = {}
            response_type = f"echo_{msg_type}"

            if msg_type == "register":
                response_payload = await handle_register(payload)
                response_type = "register_result"

            elif msg_type == "login":
                response_payload = await handle_login(payload)
                response_type = "login_result"
    
                if response_payload.get("success"):
                    user_info = response_payload.get("user", {})
                    username = user_info.get("username")
                    user_rating = user_info.get("rating", 1200)
        
                    if username and client_id in connected_clients:
                        # מעדכנים את הנתונים ושומרים תחת שם המשתמש
                        client_data = connected_clients.pop(client_id)
                        client_data["rating"] = user_rating
                        client_data["username"] = username
                        connected_clients[username] = client_data
                        client_id = username

            elif msg_type == "play":
                client_info = connected_clients.get(client_id)
                if isinstance(client_info, dict):
                    player_rating = client_info.get("rating", 1200)
                else:
                    player_rating = 1200

                await event_bus.publish(PlayerQueuedEvent(
                    client_id=client_id, 
                    rating=player_rating
                ))
                
                response_payload = {"status": "queued", "message": "Searching for match..."}
                response_type = "play_ack"

            elif msg_type == "room_menu":
                response_payload = {"status": "ok", "action": "room_menu", "message": "Room menu requested"}
                response_type = "room_menu_ack"    

            elif msg_type == "create_room":
                room_id = await room_manager.create_room(client_id)
                response_payload = {"status": "ok", "room_id": room_id, "role": "player", "player_number": 1}
                response_type = "room_created"

            elif msg_type == "join_room":
                target_room_id = payload.get("room_id", "")
                result = await room_manager.join_room(client_id, target_room_id)
                response_payload = result
                response_type = "join_room_result"

            elif msg_type == "cancel_room":
                result = await room_manager.cancel_room(client_id)
                response_payload = result
                response_type = "cancel_room_result"

            elif msg_type == "join_queue":
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
                            await connected_clients[p_id].send_text(json.dumps(match_msg))
                    response_payload = {"status": "matched", "room_id": room_id}
                else:
                    response_payload = {"status": "queued", "message": "Waiting for an opponent..."}
                response_type = "queue_result"

            elif msg_type == "leave_queue":
                matchmaking_system.remove_from_queue(client_id)
                response_payload = {"status": "left_queue"}
                response_type = "queue_result"

            else:
                response_payload = payload

            response = {
                "type": response_type,
                "payload": response_payload,
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