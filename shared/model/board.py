from typing import Dict, Tuple, Optional
from shared.model.position import Position
from shared.model.piece import Piece

class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = {}  # type: Dict[Tuple[int, int], Optional[Piece]]
        
        # אתחול לוח ריק
        for y in range(height):
            for x in range(width):
                self.grid[(x, y)] = None

    def get_piece_at(self, pos: Position) -> Optional[Piece]:
        return self.grid.get(pos.to_tuple())

    def is_occupied(self, pos: Position) -> bool:
        return self.grid.get(pos.to_tuple()) is not None

    def move_piece(self, from_pos: Position, to_pos: Position):
        from_tup = from_pos.to_tuple()
        to_tup = to_pos.to_tuple()
        
        if from_tup in self.grid and self.grid[from_tup]:
            piece = self.grid[from_tup]
            self.grid[from_tup] = None
            self.grid[to_tup] = piece
            if piece:
                piece.position = to_pos

    def remove_piece(self, pos_or_piece):
        """מסיר כלי מהלוח לפי מיקום או לפי התייחסות לכלי עצמו"""
        if isinstance(pos_or_piece, Position):
            self.grid[pos_or_piece.to_tuple()] = None
        elif hasattr(pos_or_piece, 'position'):
            self.grid[pos_or_piece.position.to_tuple()] = None