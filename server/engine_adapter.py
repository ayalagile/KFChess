from typing import Tuple, Dict, Any

class EngineAdapter:
    def __init__(self):
        pass

    def get_initial_state(self) -> Dict[str, Any]:
        return {
            "board": {},  # או כל מבנה נתונים אחר שמתאים למנוע שלך
            "turn": "player1",
            "status": "active"
        }

    def validate_and_apply_move(self, current_state: Dict[str, Any], move_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:

        try:
            # כאן יושבת הבדיקה המקורית מול shared/rules או מנוע המשחק
            # לדוגמה פשוטה לצורך ההדגמה:
            
            if not move_data:
                return False, current_state, "Empty move received"

            updated_state = current_state.copy()
            
            updated_state["last_move"] = move_data
            
            updated_state["turn"] = "player2" if current_state.get("turn") == "player1" else "player1"

            return True, updated_state, ""

        except Exception as e:
            return False, current_state, str(e)