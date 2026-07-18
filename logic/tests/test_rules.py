import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from rules.rule_engine import RuleEngine

class TestRules(unittest.TestCase):
    def setUp(self):
        self.board = Board(width=3, height=3)
        self.engine = RuleEngine()

    def test_rook_geometry_and_blocks(self):
        rook_pos = Position(0, 0)
        rook = Piece("wR_0", "R", "w", rook_pos)
        self.board.grid[rook_pos.to_tuple()] = rook
        
        # מהלך חוקי בקו ישר
        self.assertTrue(self.engine.validate_requested_move(rook, Position(2, 0), self.board))
        # מהלך לא חוקי באלכסון
        self.assertFalse(self.engine.validate_requested_move(rook, Position(1, 1), self.board))
        
        # הוספת חוסם ידידותי
        blocker = Piece("wP_0", "P", "w", Position(1, 0))
        self.board.grid[Position(1, 0).to_tuple()] = blocker
        
        # כעת המהלך מעבר לחוסם צריך להיכשל
        self.assertFalse(self.engine.validate_requested_move(rook, Position(2, 0), self.board))

    def test_knight_jumping_ability(self):
        knight_pos = Position(0, 0)
        knight = Piece("wN_0", "N", "w", knight_pos)
        self.board.grid[knight_pos.to_tuple()] = knight
        
        # חוסם בדרך (לא אמור להפריע לסוס)
        blocker = Piece("wP_0", "P", "w", Position(1, 0))
        self.board.grid[Position(1, 0).to_tuple()] = blocker
        
        # מהלך L חוקי של סוס
        self.assertTrue(self.engine.validate_requested_move(knight, Position(1, 2), self.board))

    def test_pawn_cannot_move_backwards_or_capture_forward(self):
        pawn_pos = Position(1, 1)
        white_pawn = Piece("wP_0", "P", "w", pawn_pos)
        self.board.grid[pawn_pos.to_tuple()] = white_pawn
        
        # רגלי לבן נע למעלה (צמצום ב-Y במטריצה)
        self.assertTrue(self.engine.validate_requested_move(white_pawn, Position(1, 0), self.board))
        # אסור לזוז אחורה
        self.assertFalse(self.engine.validate_requested_move(white_pawn, Position(1, 2), self.board))
        
        # שמים אויב ישירות קדימה - אסור לאכול קדימה
        enemy = Piece("bR_0", "R", "b", Position(1, 0))
        self.board.grid[Position(1, 0).to_tuple()] = enemy
        self.assertFalse(self.engine.validate_requested_move(white_pawn, Position(1, 0), self.board))

if __name__ == '__main__':
    unittest.main()