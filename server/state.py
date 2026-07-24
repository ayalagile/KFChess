from typing import Dict

class ServerState:
    def __init__(self):
        self.connected_clients: Dict[str, dict] = {}

server_state = ServerState()