import unittest
from board_io.board_parser import BoardParser
from board_io.board_printer import BoardPrinter
from model.position import Position

class TestTextIO(unittest.TestCase):
    def setUp(self):
        self.parser = BoardParser()
        self.printer = BoardPrinter()
        
        # הגדרת לוח טקסט לדוגמה (פיקסטורה)
        self.board_fixture = (
            ". . bK\n"
            ". wR .\n"
            "wP . ."
        )

    def test_board_parser_creates_correct_grid(self):
        # 1. הרצת הפארסר על הטקסט
        board = self.parser.parse_board_from_string(self.board_fixture)
        
        # 2. בדיקת מימדי הלוח
        self.assertEqual(board.width, 3)
        self.assertEqual(board.height, 3)
        
        # 3. בדיקת מיקומי וזהויות הכלים הלוגיים
        king = board.get_piece_at(Position(2, 0))
        self.assertIsNotNone(king)
        self.assertEqual(king.type, 'K')
        self.assertEqual(king.color, 'b')
        self.assertEqual(king.id, 'bK_0') # המזהה הייחודי הראשון

        rook = board.get_piece_at(Position(1, 1))
        self.assertIsNotNone(rook)
        self.assertEqual(rook.type, 'R')
        self.assertEqual(rook.color, 'w')

        pawn = board.get_piece_at(Position(0, 2))
        self.assertIsNotNone(pawn)
        self.assertEqual(pawn.type, 'P')

        # משבצת שאמורה להיות ריקה
        self.assertIsNone(board.get_piece_at(Position(0, 0)))

    def test_board_printer_outputs_matching_string(self):
        # 1. הקמת הלוח מהטקסט
        board = self.parser.parse_board_from_string(self.board_fixture)
        
        # 2. הדפסה חזרה למחרוזת
        printed_text = self.printer.board_to_string(board)
        
        # 3. וידוא שהפלט תואם לחלוטין לקלט המקורי
        self.assertEqual(printed_text, self.board_fixture)

if __name__ == '__main__':
    unittest.main()