from client.input.board_mapper import BoardMapper
from logic.engine.game_engine import GameEngine
from shared.model.position import Position

class Controller:
    def __init__(self, board_mapper: BoardMapper, game_engine: GameEngine):
        self.board_mapper = board_mapper
        self.game_engine = game_engine
        self.selected_pos = None  # ישמור טאפל של (x, y) עבור המיקום שנבחר

    def handle_click(self, pixel_x: int, pixel_y: int):
        # 1. תרגום הפיקסלים למיקום לוגי בעזרת המפר
        current_pos = self.board_mapper.map_pixels_to_cell(pixel_x, pixel_y)
        cx, cy = current_pos
        
        # גישה ללוח דרך ה-GameEngine בלבד
        board = self.game_engine.board
        
        # הגנה מפני לחיצה מחוץ לגבולות הלוח
        if not (0 <= cx < board.width and 0 <= cy < board.height):
            return
        
        # --- הוספת זיהוי הקפיצה בתוך הקונטרולר ---
        if self.selected_pos == current_pos:
            # הפעלת פקודת הקפיצה הלוגית במנוע
            self.game_engine.handle_jump_command(current_pos)
            self.selected_pos = None  # איפוס הבחירה
            return
        # ------------------------------------------

        # בדיקה האם יש כלי במשבצת שנלחצה (מתוך הלוח שבמנוע)
        pos_obj = Position(cx, cy)
        clicked_piece = board.get_piece_at(pos_obj)
        # מקרה א': אין בחירה קודמת, ולחצו על משבצת עם כלי
        if self.selected_pos is None:
            if clicked_piece:
                self.selected_pos = current_pos
            return

        # חילוץ מיקומי המקור הלוגיים
        sx, sy = self.selected_pos
        selected_piece = board.get_piece_at(Position(sx, sy))
        # מקרה ב': יש בחירה קודמת, ולחצו על כלי אחר מאותו הצבע (החלפת בחירה)
        if clicked_piece and selected_piece and clicked_piece.color == selected_piece.color:
            self.selected_pos = current_pos
            return

        # מקרה ג': יש בחירה קודמת ולחצו על משבצת ריקה או אויב -> שליחת פקודה למנוע!
        from_pos = self.selected_pos
        self.selected_pos = None  # איפוס הבחירה לקראת הלחיצה הבאה
        
        # הפעלת מסלול הפקודות הציבורי במנוע – שליחת מיקום מקור ומיקום יעד בלבד
        self.game_engine.handle_move_command(from_pos, current_pos)
