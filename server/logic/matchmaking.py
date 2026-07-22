import asyncio
from typing import Dict, Optional
from bus.event_bus import event_bus
from bus.events import PlayerQueuedEvent, MatchFoundEvent, MatchTimeoutEvent
from server.logic.room_manager import room_manager

class QueueEntry:
    def __init__(self, client_id: str, rating: int, timeout_handle: asyncio.TimerHandle):
        self.client_id = client_id
        self.rating = rating
        self.timeout_handle = timeout_handle

class MatchmakingSystem:
    def __init__(self, elo_tolerance: int = 100, timeout_seconds: float = 60.0):
        self.queue: Dict[str, QueueEntry] = {}
        self.elo_tolerance = elo_tolerance
        self.timeout_seconds = timeout_seconds

    def setup_listeners(self):
        event_bus.subscribe(PlayerQueuedEvent, self.on_player_queued)

    async def on_player_queued(self, event: PlayerQueuedEvent):
        client_id = event.client_id
        rating = event.rating

        if client_id in self.queue:
            return

        opponent_id = self._find_opponent(client_id, rating)

        if opponent_id:
            opponent_entry = self.queue.pop(opponent_id)
            opponent_entry.timeout_handle.cancel()

            room_id = await room_manager.create_room(client_id)
            await room_manager.join_room(opponent_id, room_id)

            await event_bus.publish(MatchFoundEvent(
                room_id=room_id,
                player1_id=client_id,
                player2_id=opponent_id
            ))
        else:
            loop = asyncio.get_running_loop()
            handle = loop.call_later(
                self.timeout_seconds,
                lambda: asyncio.create_task(self._handle_timeout(client_id))
            )
            self.queue[client_id] = QueueEntry(client_id, rating, handle)

    def _find_opponent(self, client_id: str, rating: int) -> Optional[str]:
        for candidate_id, entry in self.queue.items():
            if candidate_id != client_id and abs(entry.rating - rating) <= self.elo_tolerance:
                return candidate_id
        return None

    async def _handle_timeout(self, client_id: str):
        if client_id in self.queue:
            del self.queue[client_id]
            await event_bus.publish(MatchTimeoutEvent(client_id=client_id))

    def remove_from_queue(self, client_id: str):
        if client_id in self.queue:
            entry = self.queue.pop(client_id)
            entry.timeout_handle.cancel()
    def leave_room(self, client_id: str):
        if client_id in self.queue:
            self.queue.remove(client_id)

matchmaking_system = MatchmakingSystem()
matchmaking_system.setup_listeners()