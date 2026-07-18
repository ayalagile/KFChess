from logic.model.position import Position

class Piece:
    def __init__(self, piece_id: str, piece_type: str, color: str, position: Position):
        self.id = piece_id          
        self.type = piece_type      
        self.color = color          
        self.position = position    
        self.state = "Idle"         # מצבים: "Idle", "Moving", "Jumping", "Captured"
        self.move_duration = 1000