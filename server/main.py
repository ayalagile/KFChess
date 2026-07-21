import json
import logging
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Server")

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Client connected")
    try:
        while True:
            data_str = await websocket.receive_text()
            logger.info(f"Received raw data: {data_str}")
            
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

            echo_response = {
                "type": f"echo_{data.get('type', 'unknown')}",
                "payload": data.get("payload", {}),
                "request_id": data.get("request_id"),
                "ts": int(time.time())
            }
            
            await websocket.send_text(json.dumps(echo_response))
            logger.info(f"Sent Echo: {echo_response}")

    except WebSocketDisconnect:
        logger.info("Client disconnected")