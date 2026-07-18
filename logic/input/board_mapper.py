class BoardMapper:
    def __init__(self, square_size: int = 100, offset_x: int = 0, offset_y: int = 0):
        self.square_size = square_size
        self.offset_x = offset_x  # שוליים משמאל בפיקסלים
        self.offset_y = offset_y  # שוליים מלמעלה בפיקסלים

    def map_pixels_to_cell(self, x: int, y: int):
        # הפחתת השוליים לפני החישוב
        cell_x = (x - self.offset_x) // self.square_size
        cell_y = (y - self.offset_y) // self.square_size
        return (cell_x, cell_y)