# Repository URL: https://github.com/ayalagile/KFChess
import sys
class BoardGame:
    """
    מחלקה המנהלת את מצב הלוח והלוגיקה הבסיסית של המשחק.
    
    מוכנות לשינויים עתידיים:
    1. ייצוג בינארי: המטריצה הפנימית self._board מבודדת לחלוטין באמצעות מתודות גישה (get_piece, set_piece).
       אם נרצה לעבור לייצוג בינארי, נצטרך לשנות רק את הלוגיקה הפנימית של מתודות אלו מבלי להשפיע על שאר הקוד.
    2. חוקים מותאמים אישית: תהליך התנועה מופרד למתודת 'execute_move'. בעתיד, ניתן יהיה להזריק מחלקת RuleEngine
       לתוך ה-BoardGame שתקבע האם מהלך חוקי ואיך הכלי מתנהג (למשל שינוי כיוון תנועה).
    """
    CELL_SIZE = 100
    EMPTY_CELL = "."

    def __init__(self, board_lines):
        self._board = [row.split() for row in board_lines]
        self._height = len(self._board)
        self._width = len(self._board[0]) if self._height > 0 else 0
        self._selected_pos = None  # שומר (row, col) של הכלי הנבחר
        self._game_clock_ms = 0

    def _is_within_bounds(self, row, col):
        return 0 <= row < self._height and 0 <= col < self._width

    def get_piece(self, row, col):
        return self._board[row][col]

    def set_piece(self, row, col, value):
        self._board[row][col] = value

    def _get_color(self, piece):
        if piece == self.EMPTY_CELL:
            return None
        return piece[0]  # 'w' או 'b'

    def handle_click(self, x, y):
        col = x // self.CELL_SIZE
        row = y // self.CELL_SIZE

        if not self._is_within_bounds(row, col):
            return  # לחיצה מחוץ לגבולות הלוח מתעלמת

        clicked_piece = self.get_piece(row, col)

        if clicked_piece != self.EMPTY_CELL:
            if self._selected_pos:
                sel_row, sel_col = self._selected_pos
                selected_piece = self.get_piece(sel_row, sel_col)
                
                if self._get_color(clicked_piece) == self._get_color(selected_piece):
                    # החלפת הבחירה בכלי ידידותי אחר
                    self._selected_pos = (row, col)
                else:
                    # שליחת בקשת תנועה לעבר כלי יריב
                    self.execute_move(sel_row, sel_col, row, col)
            else:
                # בחירת כלי
                self._selected_pos = (row, col)
        else:
            # לחיצה על משבצת ריקה
            if self._selected_pos:
                sel_row, sel_col = self._selected_pos
                self.execute_move(sel_row, sel_col, row, col)

    def execute_move(self, from_row, from_col, to_row, to_col):
        # באיטרציה זו אין עדיין חוקים, התנועה מתבצעת ישירות
        piece = self.get_piece(from_row, from_col)
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, self.EMPTY_CELL)
        self._selected_pos = None

    def advance_clock(self, ms):
        self._game_clock_ms += ms

    def print_board(self):
        for row in self._board:
            print(" ".join(row))


def parse_and_validate_input():
    lines = sys.stdin.read().splitlines()
    
    board_lines = []
    command_lines = []
    reading_board = False
    reading_commands = False

    for line in lines:
        cleaned = line.strip()
        if cleaned == "Board:":
            reading_board = True
            continue
        if cleaned == "Commands:":
            reading_board = False
            reading_commands = True
            continue

        if reading_board:
            board_lines.append(line)
        elif reading_commands:
            command_lines.append(cleaned)

    # וולידציה של איטרציה 1
    valid_pieces = {"K", "Q", "R", "B", "N", "P"}
    width = None

    for line in board_lines:
        row = line.split()
        if width is None:
            width = len(row)
        elif len(row) != width:
            print("ERROR ROW_WIDTH_MISMATCH")
            sys.exit()

        for token in row:
            if token == ".":
                continue
            if len(token) != 2 or token[0] not in "wb" or token[1] not in valid_pieces:
                print("ERROR UNKNOWN_TOKEN")
                sys.exit()

    return board_lines, command_lines


def main():
    board_lines, command_lines = parse_and_validate_input()
    game = BoardGame(board_lines)

    for cmd in command_lines:
        if not cmd:
            continue
        
        parts = cmd.split()
        command_type = parts[0]

        if command_type == "click" and len(parts) == 3:
            game.handle_click(int(parts[1]), int(parts[2]))
        elif command_type == "wait" and len(parts) == 2:
            game.advance_clock(int(parts[1]))
        elif cmd == "print board":
            game.print_board()


if __name__ == "__main__":
    main()