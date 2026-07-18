# kungfu_chess/texttests/script_runner.py
import sys
from logic.board_io.board_parser import BoardParser
from logic.board_io.board_printer import BoardPrinter
from logic.rules.rule_engine import RuleEngine
from logic.real_time.real_time_arbiter import RealTimeArbiter
from logic.engine.game_engine import GameEngine
from logic.input.board_mapper import BoardMapper
from logic.input.controller import Controller

def run_script(lines: list):
    board_lines = []
    commands = []
    reading_board = False
    reading_commands = False
    
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
        if cleaned.startswith("Board:"):
            reading_board = True
            reading_commands = False
            continue
        if cleaned.startswith("Commands:"):
            reading_board = False
            reading_commands = True
            continue
            
        if reading_board:
            board_lines.append(cleaned)
        elif reading_commands:
            commands.append(cleaned)
            
    if not board_lines:
        return None

    # 1. ולידציות תקינות הלוח (פותר את טסטים 4, 5, 10, 11)
    first_row_width = len(board_lines[0].split())
    for row_str in board_lines:
        tokens = row_str.split()
        if len(tokens) != first_row_width:
            print("ERROR ROW_WIDTH_MISMATCH")
            return None
        for token in tokens:
            if token != '.' and (len(token) != 2 or token[0] not in 'wb' or token[1] not in 'KQRBNP'):
                print("ERROR UNKNOWN_TOKEN")
                return None

    # אתחול רכיבי המשחק
    board_str = "\n".join(board_lines)
    parser = BoardParser()
    printer = BoardPrinter()
    
    board = parser.parse_board_from_string(board_str)
    rule_engine = RuleEngine()
    arbiter = RealTimeArbiter()
    game_engine = GameEngine(board, rule_engine, arbiter)
    
    mapper = BoardMapper(100)
    controller = Controller(mapper, game_engine)
    
    # הרצת הפקודות והדפסת הפלט
    for cmd_str in commands:
        parts = cmd_str.split()
        if not parts:
            continue
            
        action = parts[0]
        
        if action == "print" and parts[1] == "board":
            print(printer.board_to_string(game_engine.board))
            
        elif action == "click":
            x = int(parts[1])
            y = int(parts[2])
            controller.handle_click(x, y)
            
        elif action == "wait":
            duration = int(parts[1])
            # מריצים את ה-wait במנוע המשחק, אך לא מדפיסים את הלוגים הפנימיים (פותר את טסטי התנועה והתנגשויות)
            game_engine.handle_wait_command(duration)

    # החזרת מנוע המשחק לצורך תשאול ישיר בטסטים
    return game_engine