from abc import ABC, abstractmethod
from logic.model.position import Position
from logic.model.board import Board

class MovementRule(ABC):
    @abstractmethod
    def get_valid_destinations(self, piece, board):
        pass

class KingRule(MovementRule):
    def get_valid_destinations(self, piece, board):
        destinations = []
        cx, cy = piece.position.x, piece.position.y
        
        # חילוץ בטוח של צבע הכלי הנוכחי
        color_str = piece.color.value.lower() if hasattr(piece.color, 'value') else piece.color.lower()
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0: continue
                tx, ty = cx + dx, cy + dy
                if 0 <= tx < board.width and 0 <= ty < board.height:
                    target_pos = Position(tx, ty)
                    target_piece = board.get_piece_at(target_pos)
                    
                    if target_piece is None:
                        destinations.append(target_pos)
                    else:
                        # חילוץ בטוח של צבע כלי היעד
                        target_color = target_piece.color.value.lower() if hasattr(target_piece.color, 'value') else target_piece.color.lower()
                        if target_color != color_str:
                            destinations.append(target_pos)
        return destinations
class RookRule(MovementRule):
    def get_valid_destinations(self, piece, board):
        destinations = []
        cx, cy = piece.position.x, piece.position.y
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            tx, ty = cx + dx, cy + dy
            while 0 <= tx < board.width and 0 <= ty < board.height:
                target_pos = Position(tx, ty)
                target_piece = board.get_piece_at(target_pos)
                if target_piece is None:
                    destinations.append(target_pos)
                else:
                    if target_piece.color != piece.color:
                        destinations.append(target_pos)
                    break
                tx, ty = tx + dx, ty + dy
        return destinations

class BishopRule(MovementRule):
    def get_valid_destinations(self, piece, board):
        destinations = []
        cx, cy = piece.position.x, piece.position.y
        for dx, dy in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            tx, ty = cx + dx, cy + dy
            while 0 <= tx < board.width and 0 <= ty < board.height:
                target_pos = Position(tx, ty)
                target_piece = board.get_piece_at(target_pos)
                if target_piece is None:
                    destinations.append(target_pos)
                else:
                    if target_piece.color != piece.color:
                        destinations.append(target_pos)
                    break
                tx, ty = tx + dx, ty + dy
        return destinations

class QueenRule(MovementRule):
    def get_valid_destinations(self, piece, board):
        return RookRule().get_valid_destinations(piece, board) + BishopRule().get_valid_destinations(piece, board)

class KnightRule(MovementRule):
    def get_valid_destinations(self, piece, board):
        destinations = []
        cx, cy = piece.position.x, piece.position.y
        for dx, dy in [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]:
            tx, ty = cx + dx, cy + dy
            if 0 <= tx < board.width and 0 <= ty < board.height:
                target_pos = Position(tx, ty)
                target_piece = board.get_piece_at(target_pos)
                if target_piece is None or target_piece.color != piece.color:
                    destinations.append(target_pos)
        return destinations

class PawnRule(MovementRule):
    def get_valid_destinations(self, piece, board: Board) -> list:
        destinations = []
        cx, cy = piece.position.x, piece.position.y
        
        color_str = piece.color.value.lower() if hasattr(piece.color, 'value') else piece.color.lower()
        direction = -1 if color_str == 'w' else 1
        
        # 1. צעד אחד קדימה
        forward_y = cy + direction
        forward_occupied = True  # דגל עזר לבדיקת חסימה
        
        if 0 <= forward_y < board.height:
            forward_pos = Position(cx, forward_y)
            if not board.is_occupied(forward_pos):
                destinations.append(forward_pos)
                forward_occupied = False  # הצעד הראשון פנוי, הדרך פתוחה לצעד כפול

            # 2. צעד כפול קדימה - מבוצע אך ורק אם הצעד הראשון אינו חסום!
            if not forward_occupied:
                start_row = 1 if direction == 1 else (board.height - 2)
                if cy == start_row:
                    double_forward_y = cy + (2 * direction)
                    if 0 <= double_forward_y < board.height:
                        double_pos = Position(cx, double_forward_y)
                        if not board.is_occupied(double_pos):
                            destinations.append(double_pos)
            
        # 3. הכאה באלכסון
        for dx in [-1, 1]:
            tx = cx + dx
            if 0 <= tx < board.width and 0 <= forward_y < board.height:
                diag_pos = Position(tx, forward_y)
                target_piece = board.get_piece_at(diag_pos)
                if target_piece:
                    target_color = target_piece.color.value.lower() if hasattr(target_piece.color, 'value') else target_piece.color.lower()
                    if target_color != color_str:
                        destinations.append(diag_pos)
                    
        return destinations