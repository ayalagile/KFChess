import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.rule_engine import RuleEngine
from real_time.real_time_arbiter import RealTimeArbiter
from engine.game_engine import GameEngine
from input.board_mapper import BoardMapper
from input.controller import Controller

class TestEngineAndInputComprehensive(unittest.TestCase):
    def setUp(self):
        # 1. הקמת הלוח והכלים (לוח בגודל 3x3 לצורך הבדיקה)
        self.board = Board(width=3, height=3)
        
        # נשים צריח לבן ב-(0, 0) ומלך שחור ב-(0, 2)
        self.white_rook = Piece("wR_0", "R", "w", Position(0, 0))
        self.black_king = Piece("bK_0", "K", "b", Position(0, 2))
        
        self.board.grid[(0, 0)] = self.white_rook
        self.board.grid[(0, 2)] = self.black_king

        # 2. הקמת השכבות לפי חוקי ה-Dependency Injection באפיון
        self.rule_engine = RuleEngine()
        self.arbiter = RealTimeArbiter()
        self.game_engine = GameEngine(self.board, self.rule_engine, self.arbiter)
        
        # ה-Mapper וה-Controller תלויים רק ב-GameEngine
        self.mapper = BoardMapper(square_size=100)
        self.controller = Controller(self.mapper, self.game_engine)

    def test_complete_game_flow_via_clicks_and_time(self):
        """בדיקת זרימה מלאה: קליקים -> מנוע -> תנועה באוויר -> המתנה -> לכידת מלך וסיום משחק"""
        
        # --- שלב 1: לחיצה על הצריח הלבן (פיקסלים 50, 50 = משבצת 0,0) ---
        self.controller.handle_click(50, 50)
        self.assertEqual(self.controller.selected_pos, (0, 0), "הקונטרולר היה צריך לבחור את משבצת (0,0)")

        # --- שלב 2: לחיצה על משבצת היעד שבה נמצא המלך (פיקסלים 50, 250 = משבצת 0,2) ---
        # לחיצה זו אמורה לשלוח פקודת תנועה ל-GameEngine, שיאשר אותה ויעביר ל-Arbiter
        self.controller.handle_click(50, 250)
        
        # הבחירה בקונטרולר צריכה להתאפס מיד
        self.assertIsNone(self.controller.selected_pos)
        
        # הצריח צריך להיות במצב "Moving" (באוויר)
        self.assertEqual(self.white_rook.state, "Moving")
        self.assertEqual(len(self.arbiter.active_motions), 1, "התנועה צריכה להיות פעילה בבורר")
        
        # הלוח עדיין לא השתנה פיזית! הצריח עדיין רשום ב-(0,0) כי הוא באוויר
        self.assertEqual(self.board.get_piece_at(Position(0, 0)), self.white_rook)
        self.assertEqual(self.board.get_piece_at(Position(0, 2)), self.black_king)

# --- שלב 3: הרצת זמן מדומה חלקי (1000ms) ---
        # חצי דרך - שום דבר עדיין לא קורה בנחיתה
        events = self.game_engine.handle_wait_command(1000)  # שינוי מ-500 ל-1000
        self.assertEqual(len(events), 0)
        self.assertEqual(self.white_rook.state, "Moving")

        # --- שלב 4: הרצת יתרת הזמן (עוד 1000ms, סה"כ 2000ms) ---
        # כעת התנועה מסתיימת, ה-Arbiter קורא ל-resolve_arrival של ה-GameEngine
        events = self.game_engine.handle_wait_command(1000)  # שינוי מ-500 ל-1000        
        self.assertEqual(len(events), 1, "היה צריך להיווצר אירוע הגעה ונחיתה")
        self.assertEqual(events[0]["event"], "king_captured", "האירוע צריך לדווח על לכידת המלך")
        self.assertEqual(events[0]["captured"], self.black_king, "הכלי שנלכד צריך להיות המלך השחור")

        # --- שלב 5: בדיקת מוטציית הלוח הסופית ומצב המשחק (Game Over) ---
        # 1. הצריח חזר למצב Idle
        self.assertEqual(self.white_rook.state, "Idle")
        # 2. משבצת המקור (0,0) כעת ריקה
        self.assertFalse(self.board.is_occupied(Position(0, 0)))
        # 3. הצריח נמצא פיזית במשבצת היעד (0,2)
        self.assertEqual(self.board.get_piece_at(Position(0, 2)), self.white_rook)
        
        # 4. ה-Game-Over Guard הופעל בשלמותו!
        self.assertTrue(self.game_engine.game_state.is_game_over)
        self.assertEqual(self.game_engine.game_state.winner, "w")

    def test_game_over_guard_blocks_subsequent_moves(self):
        """בדיקה שהמנוע חוסם פקודות חדשות ברגע שהמשחק נגמר"""
        # נעביר את המשחק למצב סיום באופן ידני לצורך הבדיקה
        self.game_engine.game_state.trigger_game_over("w")
        
        # ננסה לבצע מהלך חוקי גיאומטרית דרך המנוע
        success = self.game_engine.handle_move_command(Position(0, 0), Position(0, 1))
        
        # המנוע חייב להחזיר False (לחסום) בגלל ה-Guard
        self.assertFalse(success, "המנוע לא היה צריך לאשר מהלך כשהמשחק בסטטוס Game Over")

if __name__ == '__main__':
    unittest.main()