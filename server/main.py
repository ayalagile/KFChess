import json
import logging
import time
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from bus.event_bus import event_bus
from bus.events import ClientConnectedEvent, ClientDisconnectedEvent, MessageReceivedEvent
from bus.listeners.logging_listener import on_client_connected, on_client_disconnected, on_message_received
from server.auth import handle_login, handle_register

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    event_bus.subscribe(ClientConnectedEvent, on_client_connected)
    event_bus.subscribe(ClientDisconnectedEvent, on_client_disconnected)
    event_bus.subscribe(MessageReceivedEvent, on_message_received)
    logger.info("Event Bus initialized and listeners subscribed.")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4())[:8]
    
    await event_bus.publish(ClientConnectedEvent(client_id=client_id))
    
    try:
        while True:
            data_str = await websocket.receive_text()
            
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

            # פרסום אירוע קבלת הודעה
            await event_bus.publish(MessageReceivedEvent(
                client_id=client_id,
                msg_type=msg_type,
                payload=payload,
                request_id=request_id
            ))

            # טיפול בהודעות לפי הסוג (רישום, התחברות או ברירת מחדל)
            response_payload = {}
            response_type = f"echo_{msg_type}"

            if msg_type == "register":
                response_payload = await handle_register(payload)
                response_type = "register_result"
            elif msg_type == "login":
                response_payload = await handle_login(payload)
                response_type = "login_result"
            else:
                response_payload = payload

            response = {
                "type": response_type,
                "payload": response_payload,
                "request_id": request_id,
                "ts": int(time.time())
            }
            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        await event_bus.publish(ClientDisconnectedEvent(client_id=client_id))