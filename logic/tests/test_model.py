import unittest
from model.position import Position
from model.piece import Piece
from model.board import Board
from model.game_state import GameState

class TestModel(unittest.TestCase):
    def setUp(self):
        self.board = Board(width=3, height=3)

    def test_position_equality(self):
        pos1 = Position(1, 2)
        pos2 = Position(1, 2)
        pos3 = Position(0, 0)
        self.assertEqual(pos1, pos2)
        self.assertNotEqual(pos1, pos3)

    def test_board_initialization_is_empty(self):
        pos = Position(0, 0)
        self.assertFalse(self.board.is_occupied(pos))
        self.assertIsNone(self.board.get_piece_at(pos))

    def test_board_mutation_move_and_remove(self):
        start_pos = Position(0, 0)
        end_pos = Position(1, 0)
        piece = Piece("wR_0", "R", "w", start_pos)
        
        # הוספה ידנית ללוח לצורך הבדיקה
        self.board.grid[start_pos.to_tuple()] = piece
        self.assertTrue(self.board.is_occupied(start_pos))
        
        # בדיקת הזזה יבשה
        self.board.move_piece(start_pos, end_pos)
        self.assertFalse(self.board.is_occupied(start_pos))
        self.assertTrue(self.board.is_occupied(end_pos))
        self.assertEqual(piece.position, end_pos)
        
        # בדיקת מחיקה
        self.board.remove_piece(end_pos)
        self.assertFalse(self.board.is_occupied(end_pos))

    def test_gamestate_game_over_guard(self):
        state = GameState()
        self.assertFalse(state.is_game_over)
        state.trigger_game_over("w")
        self.assertTrue(state.is_game_over)
        self.assertEqual(state.winner, "w")

if __name__ == '__main__':
    unittest.main()