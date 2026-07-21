import os
import json
import cv2

class SpriteManager:
    def __init__(self, assets_base_path="assets/pieces_mine"):
        self.base_path = assets_base_path
        # שמירת הגדרות ה-Config והפריימים בזיכרון כדי למנוע קריאת קבצים חוזרת ב-Render
        # מבנה: { "bB": { "idle": { "config": {...}, "frames": [img1, img2...] } } }
        self.assets_cache = {}
        
        # מעקב אחרי מצבי האנימציה בזמן אמת עבור כל כלי:
        # מבנה: { piece_id: { "state": "idle", "elapsed_ms": 0, "current_frame_idx": 0 } }
        self.pieces_anim_state = {}
        
        self._preload_assets()

    def _preload_assets(self):
        """טעינה מראש של כל התיקיות תוך התחשבות בתיקיית הביניים 'states'"""
        if not os.path.exists(self.base_path):
            print(f"[ERROR] Base path not found: {self.base_path}")
            return
            
        for piece_folder in os.listdir(self.base_path):
            piece_path = os.path.join(self.base_path, piece_folder)
            if not os.path.isdir(piece_path):
                continue
                
            self.assets_cache[piece_folder] = {}
            
            # ניקח בחשבון את תיקיית הביניים 'states' שנמצאת בתוך תיקיית הכלי
            states_base_path = os.path.join(piece_path, "states")
            if not os.path.exists(states_base_path) or not os.path.isdir(states_base_path):
                # הגנה למקרה שחלק מהכלים לא מכילים את תיקיית הביניים הזו
                states_base_path = piece_path 
                
            # מעבר על כל המצבים האמיתיים (idle, jump, move וכו') בתוך תיקיית המצבים
            for state_folder in os.listdir(states_base_path):
                state_path = os.path.join(states_base_path, state_folder)
                if not os.path.isdir(state_path):
                    continue
                    
                config_file = os.path.join(state_path, "config.json")
                sprites_dir = os.path.join(state_path, "sprites")
                
                # טעינת קובץ ההגדרות (JSON)
                config_data = {}
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                    except Exception as e:
                        print(f"[ERROR] Failed to parse JSON in {config_file}: {e}")
                
                # טעינת כל התמונות (הפריימים) בתוך תת-תיקיית הספרייטס
                frames = []
                if os.path.exists(sprites_dir):
                    # מיון לפי שם הקובץ המספרי (1.png, 2.png וכד')
                    files = sorted(
                        os.listdir(sprites_dir), 
                        key=lambda x: int(os.path.splitext(x)[0]) if os.path.splitext(x)[0].isdigit() else x
                    )
                    for file in files:
                        img_path = os.path.join(sprites_dir, file)
                        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
                        if img is not None:
                            frames.append(img)
                            
                # שמירה במטמון תחת שם המצב הנכון
                self.assets_cache[piece_folder][state_folder] = {
                    "config": config_data,
                    "frames": frames
                }
        
        print(f"[INFO] Asset preloading complete. Loaded pieces: {list(self.assets_cache.keys())}")

    def update_time(self, dt_ms: int):
        """עדכון השעון הפנימי של האנימציות - נקרא מתוך לולאת המשחק הראשית"""
        for piece_id, anim in self.pieces_anim_state.items():
            anim["elapsed_ms"] += dt_ms

    def get_piece_sprite(self, piece_id: str, logical_state: str):
        """
        מחזיר את פריים התמונה המתאים לכלי בהתאם למצבו הנוכחי והזמן שעבר.
        אם הועבר אובייקט כלי (כמו אחרי Promotion), אנו בוחרים את הספרייט לפי סוג הכלי,
        לא לפי מזהה התיקייה הישנה.
        """
        piece_ref = piece_id
        if hasattr(piece_id, 'type') and hasattr(piece_id, 'color'):
            piece_ref = piece_id

        if hasattr(piece_id, 'type') and hasattr(piece_id, 'color'):
            piece_type = str(getattr(piece_id, 'type', '')).upper()
            color = str(getattr(piece_id, 'color', '')).lower()
            if piece_type in {'P', 'N', 'B', 'R', 'Q', 'K'}:
                piece_type_key = f"{color}{piece_type}"
            else:
                piece_type_key = piece_id[:2]
        else:
            piece_type_key = piece_id[:2] if isinstance(piece_id, str) else str(piece_id)[:2]
        
        # תרגום מצב לוגי לשם תיקיית המצב
        state_key = logical_state.lower()
        if state_key == "jumping":
            state_key = "jump"
        elif state_key == "restingjump":
            state_key = "short_rest" 
        elif state_key == "moving":
            state_key = "move"
        elif state_key == "restingmove":
            state_key = "long_rest" 
        elif state_key == "idle":
            state_key = "idle"

        # הגנה למקרה שהנכס לא קים במטמון
        if piece_type_key not in self.assets_cache or state_key not in self.assets_cache[piece_type_key]:
            # חזרה ברירת מחדל ל-idle אם המצב הספציפי חסר
            state_key = "idle"
            if piece_type_key not in self.assets_cache or state_key not in self.assets_cache[piece_type_key]:
                return None

        asset = self.assets_cache[piece_type_key][state_key]
        frames = asset["frames"]
        config = asset["config"]
        
        if not frames:
            return None

        # אתחול מעקב כלי חדש אם עדיין לא קיים, או אם המצב של הכלי השתנה
        if piece_id not in self.pieces_anim_state or self.pieces_anim_state[piece_id]["current_state"] != state_key:
            self.pieces_anim_state[piece_id] = {
                "current_state": state_key,
                "elapsed_ms": 0
            }

        anim_info = self.pieces_anim_state[piece_id]
        
        # חישוב מתמטי של הפריים הנוכחי מתוך ה-Config
        fps = config.get("graphics", {}).get("frames_per_sec", 4)
        is_loop = config.get("graphics", {}).get("is_loop", True)
        
        ms_per_frame = 1000.0 / fps
        total_duration_ms = ms_per_frame * len(frames)
        
        if is_loop:
            # באנימציה מחזורית משתמשים בשארית הזמן
            current_time = anim_info["elapsed_ms"] % total_duration_ms
            frame_idx = int(current_time // ms_per_frame)
        else:
            # באנימציה חד פעמית נעצרים בפריים האחרון
            frame_idx = int(anim_info["elapsed_ms"] // ms_per_frame)
            if frame_idx >= len(frames):
                frame_idx = len(frames) - 1
                
        # הגנה על גבולות המערך
        frame_idx = max(0, min(len(frames) - 1, frame_idx))
        
        return frames[frame_idx]