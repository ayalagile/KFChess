import unittest
from board_io.board_parser import BoardParser
from board_io.board_printer import BoardPrinter
from rules.rule_engine import RuleEngine
from real_time.real_time_arbiter import RealTimeArbiter
from engine.game_engine import GameEngine
from text_test.script_runner import ScriptRunner

class TestScriptScenario(unittest.TestCase):
    def test_complete_text_script_scenario(self):
        # 1. הגדרת לוח משחק ראשוני בטקסט
        initial_board_str = (
            ". . bK\n"
            ". . .\n"
            "wR . ."
        )
        
        # 2. הקמת השכבות (Dependency Injection)
        parser = BoardParser()
        printer = BoardPrinter()
        board = parser.parse_board_from_string(initial_board_str)
        
        rule_engine = RuleEngine()
        arbiter = RealTimeArbiter()
        game_engine = GameEngine(board, rule_engine, arbiter)
        
        runner = ScriptRunner(game_engine, printer)
        
        # 3. תרחיש הפקודות: הצריח נע ל-(0,0) - משבצת ריקה
        game_script = [
            {"action": "move", "from": (0, 2), "to": (0, 0)},
            {"action": "wait", "duration": 1000},
            {"action": "wait", "duration": 1000}
        ]
        
        # 4. הרצת הסקריפט
        runner.run_commands(game_script)
        
        # 5. בדיקות התאמה בזמן אמת (Assertions) - המשחק ממשיך!
        # המשחק לא צריך להיות ב-Game Over, כי המלך עדיין חי ב-(2,0)
        self.assertFalse(game_engine.game_state.is_game_over)
        self.assertIsNone(game_engine.game_state.winner)
        
        # וידוא שהלוח הסופי מציג את הצריח ב-(0,0) והמלך נותר ב-(2,0)
        expected_final_board = (
            "wR . bK\n"
            ". . .\n"
            ". . ."
        )
        self.assertEqual(printer.board_to_string(board), expected_final_board)

if __name__ == '__main__':
    unittest.main()