from shared.model.position import Position
from shared.real_time.motion import Motion

class RealTimeArbiter:
    def __init__(self):
        self.active_motions = []
        self.active_jumps = {}
        self.resting_cooldowns = {}

    def is_color_moving(self, color: str) -> bool:
        for motion in self.active_motions:
            if str(motion.piece.color).lower() == str(color).lower():
                return True
        return False

    def is_piece_airborne(self, piece) -> bool:
        return piece in self.active_jumps and self.active_jumps[piece] > 0

    def start_jump(self, piece) -> bool:
        if getattr(piece, 'state', 'Idle') != "Idle":
            return False
        self.active_jumps[piece] = 1000
        piece.state = "Jumping"
        return True

    def start_motion(self, piece, from_pos: Position, to_pos: Position) -> bool:
        if getattr(piece, 'state', 'Idle') != "Idle":
            return False
        if self.is_piece_airborne(piece):
            return False
        if self.is_color_moving(piece.color):
            return False 
        
        dx = abs(to_pos.x - from_pos.x)
        dy = abs(to_pos.y - from_pos.y)
        steps = max(dx, dy)
        
        duration_ms = steps * 1000
        new_motion = Motion(piece, from_pos, to_pos, duration_ms=duration_ms)
        piece.state = "Moving"
        self.active_motions.append(new_motion)
        return True

    def cancel_motion_for_piece(self, piece):
        motion_to_remove = None
        for motion in self.active_motions:
            if motion.piece == piece:
                motion_to_remove = motion
                break
        if motion_to_remove:
            self.active_motions.remove(motion_to_remove)

    def cancel_motion_by_destination(self, pos: Position):
        motions_to_cancel = [m for m in self.active_motions if m.to_pos == pos]
        for m in motions_to_cancel:
            m.piece.state = "Idle"
            self.active_motions.remove(m)

    def advance_simulated_time(self, elapsed_time_ms: int, game_engine) -> list:
        events = []
        
        # 1. מזהים וממיינים את הכלים שמגיעים ליעדם ב-Tick הנוכחי
        finished_motions_with_time = []
        for m in self.active_motions:
            if m.remaining_ms <= elapsed_time_ms:
                finished_motions_with_time.append((m.remaining_ms, m))
        
        finished_motions_with_time.sort(key=lambda x: x[0])
        
        # 2. פתרון הגעה: בדיקת לכידה מהאוויר מתבצעת בזמן שהכלים הקופצים עדיין רשומים כ-Airborne
        for original_remaining, motion in finished_motions_with_time:
            if motion in self.active_motions:
                arriving_piece = motion.piece
                target_pos = motion.to_pos
                
                # חיפוש כלי אויב שנמצא באוויר במיקומם הנוכחי (כולל כאלו שזמן הקפיצה שלהם מסתיין ב-Tick הזה)
                airborne_enemy = None
                for piece in list(self.active_jumps.keys()):
                    if piece.position.to_tuple() == target_pos.to_tuple() and \
                       piece.color != arriving_piece.color:
                        airborne_enemy = piece
                        break
                
                if airborne_enemy:
                    # חוק: הכלי שבאוויר (המלך הלבן) לוכד את הכלי שהגיע (הצריח השחור)!
                    self.active_motions.remove(motion)
                    arriving_piece.state = "Captured"
                    
                    # הסרת הכלי המגיע (הצריח השחור) מהלוח הלוגי
                    game_engine.board.remove_piece(motion.from_pos) 
                    self.cancel_motion_by_destination(target_pos)
                    
                    events.append({
                        "event": "airborne_capture",
                        "capturer": airborne_enemy,
                        "captured": arriving_piece,
                        "position": target_pos
                    })
                else:
                    # הגעה רגילה אם אין אף אחד באוויר
                    self.active_motions.remove(motion)
                    motion.piece.state = "RestingMove"
                    self.resting_cooldowns[motion.piece] = 3000
                    arrival_event = game_engine.resolve_arrival(motion)
                    if arrival_event:
                        events.append(arrival_event)
                        if arrival_event.get("event") in ["move_completed", "king_captured"]:
                            self.cancel_motion_by_destination(motion.to_pos)
        
        # 3. רק עכשיו מעדכנים ומורידים את זמני הקפיצות שהסתיימו
        finished_jumps = []
        for piece in list(self.active_jumps.keys()):
            self.active_jumps[piece] -= elapsed_time_ms
            if self.active_jumps[piece] <= 0:
                finished_jumps.append(piece)
                
        for piece in finished_jumps:
            if piece in self.active_jumps:
                del self.active_jumps[piece]
                if hasattr(piece, 'state') and piece.state == "Jumping":
                    piece.state = "RestingJump"
                    self.resting_cooldowns[piece] = 1000

        for piece in list(self.resting_cooldowns.keys()):
            self.resting_cooldowns[piece] -= elapsed_time_ms
            if self.resting_cooldowns[piece] <= 0:
                piece.state = "Idle"
                del self.resting_cooldowns[piece]

        for motion in list(self.active_motions):
            motion.tick(elapsed_time_ms)
            
        return events