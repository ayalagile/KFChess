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