import shared.rules.piece_rules as piecerules
from shared.model.board import Board

class RuleEngine:
    def __init__(self):
        self._rules = {
            'K': piecerules.KingRule(),
            'Q': piecerules.QueenRule(),
            'R': piecerules.RookRule(),
            'B': piecerules.BishopRule(),
            'N': piecerules.KnightRule(),
            'P': piecerules.PawnRule()
        }

    def validate_requested_move(self, piece, to_pos, board):
        rule = self._rules.get(piece.type)
        if not rule:
            return False
        valid_positions = rule.get_valid_destinations(piece, board)
        return to_pos in valid_positions