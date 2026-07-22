from dataclasses import dataclass, field
import time

@dataclass
class Event:
    timestamp: float = field(default_factory=time.time)

@dataclass
class ClientConnectedEvent(Event):
    client_id: str = ""

@dataclass
class ClientDisconnectedEvent(Event):
    client_id: str = ""

@dataclass
class MessageReceivedEvent(Event):
    client_id: str = ""
    msg_type: str = ""
    payload: dict = field(default_factory=dict)
    request_id: str = ""
@dataclass
class RoomCreatedEvent:
    room_id: str
    creator_id: str

@dataclass
class PlayerJoinedRoomEvent:
    room_id: str
    client_id: str
    player_number: int  # 1 או 2

@dataclass
class ViewerJoinedRoomEvent:
    room_id: str
    client_id: str
@dataclass
class PlayerQueuedEvent:
    client_id: str
    rating: int

@dataclass
class MatchFoundEvent:
    room_id: str
    player1_id: str
    player2_id: str

@dataclass
class MatchTimeoutEvent:
    client_id: str