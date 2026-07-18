from logic.model.board import Board
from logic.model.position import Position

class BoardPrinter:
    def __init__(self):
        pass

    def board_to_string(self, board: Board) -> str:
        """
        הופך אובייקט לוח למחרוזת טקסט הניתנת להדפסה.
        """
        output_lines = []
        for y in range(board.height):
            row_tokens = []
            for x in range(board.width):
                piece = board.get_piece_at(Position(x, y))
                if piece:
                    # מדפיס את הצבע וסוג הכלי (למשל wR)
                    row_tokens.append(f"{piece.color}{piece.type}")
                else:
                    row_tokens.append(".")
            output_lines.append(" ".join(row_tokens))
        return "\n".join(output_lines)