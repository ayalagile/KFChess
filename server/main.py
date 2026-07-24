# import json
# import logging
# import time
# import uuid
# from typing import Dict, Callable, Any
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect

# from bus.event_bus import event_bus
# from bus.events import ClientConnectedEvent, ClientDisconnectedEvent, MessageReceivedEvent, PlayerQueuedEvent
# from bus.listeners.logging_listener import on_client_connected, on_client_disconnected, on_message_received
# from server.auth import handle_login, handle_register
# from server.logic.matchmaking import matchmaking_system
# from server.logic.room_manager import room_manager

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger("Server")

# app = FastAPI()

# connected_clients: Dict[str, dict] = {}

# @app.on_event("startup")
# async def startup_event():
#     event_bus.subscribe(ClientConnectedEvent, on_client_connected)
#     event_bus.subscribe(ClientDisconnectedEvent, on_client_disconnected)
#     event_bus.subscribe(MessageReceivedEvent, on_message_received)
#     logger.info("Event Bus initialized and listeners subscribed.")
#     matchmaking_system.setup_listeners()





# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     client_id = str(uuid.uuid4())[:8]
#     connected_clients[client_id] = {
#         "websocket": websocket,
#         "rating": 1200,
#         "username": None
#     }
    
#     await event_bus.publish(ClientConnectedEvent(client_id=client_id))
    
#     try:
#         while True:
#             data_str = await websocket.receive_text()
#             print(f"DEBUG SERVER RECEIVED: {data_str}")
            
#             try:
#                 data = json.loads(data_str)
#             except json.JSONDecodeError:
#                 error_response = {
#                     "type": "error",
#                     "payload": {"message": "Invalid JSON format"},
#                     "ts": int(time.time())
#                 }
#                 await websocket.send_text(json.dumps(error_response))
#                 continue

#             msg_type = data.get("type", "unknown")
#             payload = data.get("payload", {})
#             request_id = data.get("request_id", "")

#             await event_bus.publish(MessageReceivedEvent(
#                 client_id=client_id,
#                 msg_type=msg_type,
#                 payload=payload,
#                 request_id=request_id
#             ))

#             handler = MESSAGE_HANDLERS.get(msg_type)
#             if handler:
#                 response_type, response_payload = await handler(client_id, payload, websocket)
                
#                 # אם הוחזר סוג תגובה ריק (כמו ב־move שנשלח דרך Broadcast), נדלג על שליחת התגובה הרגילה
#                 if not response_type:
#                     continue

#                 response = {
#                     "type": response_type,
#                     "payload": response_payload,
#                     "request_id": request_id,
#                     "ts": int(time.time())
#                 }
#             else:
#                 response = {
#                     "type": f"echo_{msg_type}",
#                     "payload": payload,
#                     "request_id": request_id,
#                     "ts": int(time.time())
#                 }

#             client_data = connected_clients.get(client_id)
#             if client_data:
#                 await client_data["websocket"].send_text(json.dumps(response))

#     except WebSocketDisconnect:
#         session = room_manager.get_session_by_client(client_id)
#         if session:
#             for player in session.players:
#                 if player != client_id:
#                     from server.main import connected_clients
#                     opponent_data = connected_clients.get(player)
#                     if opponent_data and "websocket" in opponent_data:
#                         resign_msg = {
#                             "type": "opponent_disconnected",
#                             "payload": {"message": "Opponent disconnected. You win by default."},
#                             "ts": int(time.time())
#                         }
#                         await opponent_data["websocket"].send_text(json.dumps(resign_msg))
            
#             await room_manager.cancel_room(client_id)
#         matchmaking_system.remove_from_queue(client_id)
#         matchmaking_system.leave_room(client_id)
#         if client_id in connected_clients:
#             del connected_clients[client_id]
            
#         await event_bus.publish(ClientDisconnectedEvent(client_id=client_id))

import json
import logging
import time
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from bus.event_bus import event_bus
from bus.events import ClientConnectedEvent, ClientDisconnectedEvent, MessageReceivedEvent
from server.logic.matchmaking import matchmaking_system
from server.logic.room_manager import room_manager
from server.state import server_state
from server.handlers import MESSAGE_HANDLERS
from bus.listeners.logging_listener import on_client_connected, on_client_disconnected, on_message_received
from bus.listeners.match_listener import on_match_found
from bus.listeners.room_listeners import on_player_joined
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

app = FastAPI()

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
    server_state.connected_clients[client_id] = {
        "websocket": websocket,
        "rating": 1200,
        "username": None
    }
    
    await event_bus.publish(ClientConnectedEvent(client_id=client_id))
    
    try:
        while True:
            data_str = await websocket.receive_text()
            try:
                data = json.loads(data_str)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "payload": {"message": "Invalid JSON format"},
                    "ts": int(time.time())
                }))
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

            client_data = server_state.connected_clients.get(client_id)
            if client_data:
                await client_data["websocket"].send_text(json.dumps(response))

    except WebSocketDisconnect:
        session = room_manager.get_session_by_client(client_id)
        if session:
            for player in session.players:
                if player != client_id:
                    opponent_data = server_state.connected_clients.get(player)
                    if opponent_data and "websocket" in opponent_data:
                        resign_msg = {
                            "type": "opponent_disconnected",
                            "payload": {"message": "Opponent disconnected. You win by default."},
                            "ts": int(time.time())
                        }
                        await opponent_data["websocket"].send_text(json.dumps(resign_msg))
            
            await room_manager.cancel_room(client_id)
            
        matchmaking_system.remove_from_queue(client_id)
        matchmaking_system.leave_room(client_id)
        if client_id in server_state.connected_clients:
            del server_state.connected_clients[client_id]
            
        await event_bus.publish(ClientDisconnectedEvent(client_id=client_id))