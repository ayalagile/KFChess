from logic.model.position import Position

class Motion:
    def __init__(self, piece, from_pos: Position, to_pos: Position, duration_ms: int = 1000):
        self.piece = piece
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.remaining_ms = duration_ms  # שינוי השם ל-remaining_ms לצורך תאימות מלאה ל-Arbiter

    def tick(self, elapsed_time_ms: int) -> bool:
        """
        מפחית את הזמן שנותר לתנועה בצורה מבוקרת.
        מחזיר True אך ורק אם התנועה הגיעה לסיומה המלא.
        """
        self.remaining_ms -= elapsed_time_ms
        if self.remaining_ms <= 0:
            self.remaining_ms = 0
            return True
        return False