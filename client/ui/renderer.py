import cv2
from client.ui.img import Img
from client.ui.sprite_manager import SpriteManager

CELL_SIZE = 80

class Renderer:
    def __init__(self, arbiter, sprite_manager: SpriteManager):
        self.arbiter = arbiter
        self.sprite_manager = sprite_manager
        self.background = Img().read("assets/background.png")
        # טעינת הלוח ושינוי גודלו בהתאם ל-CELL_SIZE החדש (8 משבצות)
        raw_board = Img().read("assets/board.png")
        board_new_size = CELL_SIZE * 8
        
        self.board = Img()
        self.board.img = cv2.resize(
            raw_board.img, 
            (board_new_size, board_new_size), 
            interpolation=cv2.INTER_AREA
        )
        bg_h, bg_w = self.background.img.shape[:2]
        board_h, board_w = self.board.img.shape[:2]
        
        # חישוב המרכז המדויק
        self.start_x = (bg_w - board_w) // 2
        self.start_y = (bg_h - board_h) // 2

    def render(self, board_obj, selected_pos=None):
        frame = Img()
        frame.img = self.background.img.copy()

        # הדבקת הלוח הריק במרכז הרקע
        board_h, board_w = self.board.img.shape[:2]
        frame.img[self.start_y:self.start_y+board_h, self.start_x:self.start_x+board_w] = self.board.img
        
        # 1. ציור ריבוע בחירה (צהוב) אם קיים
        if selected_pos:
            sel_x, sel_y = selected_pos
            cv_start_x = self.start_x + (sel_x * CELL_SIZE)
            cv_start_y = self.start_y + (sel_y * CELL_SIZE)
            cv2.rectangle(
                frame.img, 
                (cv_start_x, cv_start_y), 
                (cv_start_x + CELL_SIZE, cv_start_y + CELL_SIZE), 
                (0, 255, 255), 
                3
            )

        # 2. מעבר בלולאה על כל הכלים וחישוב מיקומי ציור
        for piece_obj in board_obj.grid.values():
            if piece_obj is None or getattr(piece_obj, 'state', None) == "Captured":
                continue

            # קביעת קואורדינטות בסיס בפיקסלים
            x_pixel = self.start_x + (piece_obj.position.x * CELL_SIZE)
            y_pixel = self.start_y + (piece_obj.position.y * CELL_SIZE)
            y_offset = 0

            # א. בדיקה האם הכלי בתנועה אקטיבית (מעבר חלק בין משבצות)
            active_motion = None
            for motion in self.arbiter.active_motions:
                if motion.piece == piece_obj:
                    active_motion = motion
                    break

            if active_motion:
                dx = abs(active_motion.to_pos.x - active_motion.from_pos.x)
                dy = abs(active_motion.to_pos.y - active_motion.from_pos.y)
                total_duration = max(dx, dy) * 1000
                
                if total_duration > 0:
                    t = 1.0 - (active_motion.remaining_ms / total_duration)
                    t = max(0.0, min(1.0, t))
                    
                    start_x = self.start_x + (active_motion.from_pos.x * CELL_SIZE)
                    start_y = self.start_y + (active_motion.from_pos.y * CELL_SIZE)
                    end_x = self.start_x + (active_motion.to_pos.x * CELL_SIZE)
                    end_y = self.start_y + (active_motion.to_pos.y * CELL_SIZE)
                    
                    x_pixel = int(start_x + t * (end_x - start_x))
                    y_pixel = int(start_y + t * (end_y - start_y))

            # ב. בדיקה האם הכלי באנימציית קפיצה (פרבולה אנכית)
            elif piece_obj in self.arbiter.active_jumps:
                remaining_jump = self.arbiter.active_jumps[piece_obj]
                t = 1.0 - (remaining_jump / 1000.0)
                t = max(0.0, min(1.0, t))
                
                max_jump_height = 40
                y_offset = -int(4 * max_jump_height * t * (1.0 - t))

            # ג. שליפת הפריים המעודכן מתוך ה-SpriteManager
            current_state = getattr(piece_obj, 'state', 'Idle')
            piece_sprite_np = self.sprite_manager.get_piece_sprite(piece_obj, current_state)

            if piece_sprite_np is not None:
                # יצירת אובייקט Img זמני ועטיפת מערך הפיקסלים שחזר מהמנהל
                sprite_img = Img()
                
                # שינוי גודל דינמי ל-(100, 100) כדי למנוע את עיוות/דחיסת הכלים
                sprite_img.img = cv2.resize(piece_sprite_np, (CELL_SIZE, CELL_SIZE), interpolation=cv2.INTER_AREA)
                
                # שימוש במתודת הציור המקורית שלכם השומרת על מיקומים ושקופיות כראוי
                sprite_img.draw_on(frame, x_pixel, y_pixel + y_offset)

        return frame