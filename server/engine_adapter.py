from typing import Tuple, Dict, Any

class EngineAdapter:
    def __init__(self):
        # כאן אפשר לאתחול את מבנה הנתונים ההתחלתי של המשחק או את חוקי המנוע
        pass

    def get_initial_state(self) -> Dict[str, Any]:
        """מחזיר את מצב המשחק ההתחלתי כאשר חדר חדש נפתח"""
        return {
            "board": {},  # או כל מבנה נתונים אחר שמתאים למנוע שלך
            "turn": "player1",
            "status": "active"
        }

    def validate_and_apply_move(self, current_state: Dict[str, Any], move_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
        """
        בודק את תקינות המהלך מול חוקי המנוע ומעדכן את המצב במידה והוא חוקי.
        מחזיר: (is_valid, new_state, error_message)
        """
        try:
            # כאן יושבת הבדיקה המקורית מול shared/rules או מנוע המשחק
            # לדוגמה פשוטה לצורך ההדגמה:
            
            if not move_data:
                return False, current_state, "Empty move received"

            # יצירת עותק של המצב הנוכחי לצורך עדכון
            updated_state = current_state.copy()
            
            # ביצוע שינוי במצב המשחק בהתאם למהלך
            updated_state["last_move"] = move_data
            
            # החלפת תור לדוגמה (אם רלוונטי)
            updated_state["turn"] = "player2" if current_state.get("turn") == "player1" else "player1"

            return True, updated_state, ""

        except Exception as e:
            return False, current_state, str(e)