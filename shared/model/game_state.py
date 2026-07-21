class GameState:
    def __init__(self):
        self.is_game_over = False
        self.winner = None  # 'w' או 'b'

    def trigger_game_over(self, winner_color: str):
        self.is_game_over = True
        self.winner = winner_color