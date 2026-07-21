import cv2
import time
from shared.model.board import Board
from shared.model.position import Position
from shared.model.piece import Piece 
from shared.rules.rule_engine import RuleEngine
from shared.real_time.real_time_arbiter import RealTimeArbiter
from logic.engine.game_engine import GameEngine
from client.input.board_mapper import BoardMapper
from client.input.controller import Controller
from client.ui.renderer import Renderer, CELL_SIZE
from client.ui.sprite_manager import SpriteManager

raw_click_pixels = None

def mouse_callback(event, x, y, flags, param):
    global raw_click_pixels
    if event == cv2.EVENT_LBUTTONDOWN:
        raw_click_pixels = (x, y)

def setup_initial_board_pieces(game_board: Board):
    """מציב את כל הכלים על הלוח ישירות מתוך ה-main בלי לשנות את קבצי הלוגיקה"""
    # סידור כלים שחורים (למעלה: y=0 קצינים, y=1 חיילים)
    game_board.grid[(0, 0)] = Piece("bR1", "R", "b", Position(0, 0))
    game_board.grid[(1, 0)] = Piece("bN1", "N", "b", Position(1, 0))
    game_board.grid[(2, 0)] = Piece("bB1", "B", "b", Position(2, 0))
    game_board.grid[(3, 0)] = Piece("bQ",  "Q", "b", Position(3, 0))
    game_board.grid[(4, 0)] = Piece("bK",  "K", "b", Position(4, 0))
    game_board.grid[(5, 0)] = Piece("bB2", "B", "b", Position(5, 0))
    game_board.grid[(6, 0)] = Piece("bN2", "N", "b", Position(6, 0))
    game_board.grid[(7, 0)] = Piece("bR2", "R", "b", Position(7, 0))

    for i in range(8):
        game_board.grid[(i, 1)] = Piece(f"bP{i+1}", "P", "b", Position(i, 1))

    # סידור כלים לבנים (למטה: y=7 קצינים, y=6 חיילים)
    game_board.grid[(0, 7)] = Piece("wR1", "R", "w", Position(0, 7))
    game_board.grid[(1, 7)] = Piece("wN1", "N", "w", Position(1, 7))
    game_board.grid[(2, 7)] = Piece("wB1", "B", "w", Position(2, 7))
    game_board.grid[(3, 7)] = Piece("wQ",  "Q", "w", Position(3, 7))
    game_board.grid[(4, 7)] = Piece("wK",  "K", "w", Position(4, 7))
    game_board.grid[(5, 7)] = Piece("wB2", "B", "w", Position(5, 7))
    game_board.grid[(6, 7)] = Piece("wN2", "N", "w", Position(6, 7))
    game_board.grid[(7, 7)] = Piece("wR2", "R", "w", Position(7, 7))

    for i in range(8):
        game_board.grid[(i, 6)] = Piece(f"wP{i+1}", "P", "w", Position(i, 6))


def main():
    global raw_click_pixels

    # 1. איתחול הלוח
    game_board = Board(8, 8)
    
    # סידור הכלים על הלוח במצב התחלתי
    setup_initial_board_pieces(game_board)

    rule_engine = RuleEngine()
    realtime_arbiter = RealTimeArbiter()
    engine = GameEngine(board=game_board, rule_engine=rule_engine, realtime_arbiter=realtime_arbiter)

    board_mapper = BoardMapper(square_size=CELL_SIZE)
    controller = Controller(board_mapper=board_mapper, game_engine=engine)

    sprite_manager = SpriteManager(assets_base_path="assets/pieces_mine")
    renderer = Renderer(arbiter=realtime_arbiter, sprite_manager=sprite_manager)
    window_name = "Chess Game"
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_callback)

    print("המשחק פעיל! לחצי על 'q' או סגרי את החלון כדי לצאת.")

    last_time = time.time()
    
    while True:
        current_time = time.time()
        dt_ms = int((current_time - last_time) * 1000)
        last_time = current_time

        if dt_ms > 0:
            sprite_manager.update_time(dt_ms)
            engine.handle_wait_command(dt_ms)

        # רינדור וקבלת התמונה
        frame_img = renderer.render(engine.board, selected_pos=controller.selected_pos)

        # הצגה על המסך
        cv2.imshow(window_name, frame_img.img)

        # טיפול בקלט
        if raw_click_pixels is not None:
            pixel_x, pixel_y = raw_click_pixels
            raw_click_pixels = None
            # תיקון הסטייה: הפחתת שולי הרקע כדי להביא את הפיקסלים לנקודת ה-0 של הלוח
            corrected_x = pixel_x - renderer.start_x
            corrected_y = pixel_y - renderer.start_y
            # שליחת הפיקסלים המתוקנים ל-Controller
            controller.handle_click(corrected_x, corrected_y)

        # בדיקה של מקש 'q' במקלדת
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("יציאה מהמשחק עקב לחיצה על q.")
            break

        # בדיקה האם החלון נסגר ידנית
        try:
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("החלון נסגר על ידי המשתמש.")
                break
        except Exception:
            print("חלון התצוגה נסגר.")
            break

        time.sleep(0.016)

    # סגירה מסודרת ומניעת תקיעות
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()