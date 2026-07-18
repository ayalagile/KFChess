from logic.model.board import Board
from logic.model.piece import Piece
from logic.model.position import Position

class BoardParser:
    def __init__(self):
        pass

    def parse_board_from_string(self, board_string: str) -> Board:
        """
        מקבל מחרוזת טקסט שמייצגת לוח (שורות מופרדות ב-newlines).
        למשל:
        . . bK
        . wR .
        . . .
        """
        lines = [line.strip().split() for line in board_string.strip().split('\n') if line.strip()]
        height = len(lines)
        width = len(lines[0]) if height > 0 else 0
        
        board = Board(width, height)
        piece_counts = {}  # לצורך יצירת מזהה ייחודי לכל כלי (למשל wR_0)

        for y in range(height):
            for x in range(width):
                token = lines[y][x]
                if token == '.':
                    continue  # משבצת ריקה
                
                # הטוקן מורכב מצבע (w/b) וסוג כלי (K, Q, R, B, N, P) - למשל: wR או bK
                color = token[0]
                piece_type = token[1]
                
                # יצירת מזהה ייחודי
                key = f"{color}{piece_type}"
                piece_counts[key] = piece_counts.get(key, 0) + 1
                piece_id = f"{key}_{piece_counts[key] - 1}"
                
                # יצירת הכלי והוספתו ללוח
                pos = Position(x, y)
                piece = Piece(piece_id, piece_type, color, pos)
                board.grid[pos.to_tuple()] = piece
                
        return board