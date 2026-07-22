from server.engine_adapter import EngineAdapter


class GameSession:
    def __init__(self, room_id: str, player1_id: str, player2_id: str):
        self.room_id = room_id
        self.players = [player1_id, player2_id]
        self.viewers = set()
        self.game_state = {}
        self.engine_adapter = EngineAdapter()

    async def handle_move(self, client_id: str, move_data: dict):
        if client_id not in self.players:
            return False, "Unauthorized player"

        is_valid, new_state, error = self.engine_adapter.validate_and_apply_move(
            self.game_state, move_data
        )

        if not is_valid:
            return False, error

        self.game_state = new_state
        return True, self.game_state