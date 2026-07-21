import logging
from bus.events import ClientConnectedEvent, ClientDisconnectedEvent, MessageReceivedEvent

logger = logging.getLogger("LoggingListener")

async def on_client_connected(event: ClientConnectedEvent):
    logger.info(f"[EventBus] Client connected: {event.client_id}")

async def on_client_disconnected(event: ClientDisconnectedEvent):
    logger.info(f"[EventBus] Client disconnected: {event.client_id}")

async def on_message_received(event: MessageReceivedEvent):
    logger.info(f"[EventBus] Message received from {event.client_id}: type={event.msg_type}")