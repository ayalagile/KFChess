import unittest

from client.ui.sprite_manager import SpriteManager
from shared.model.piece import Piece
from shared.model.position import Position


class TestPromotionSpriteSelection(unittest.TestCase):
    def test_promoted_piece_uses_queen_sprite_assets(self):
        sprite_manager = SpriteManager(assets_base_path="assets/pieces_mine")
        promoted_piece = Piece("wP1", "Q", "w", Position(0, 0))

        sprite = sprite_manager.get_piece_sprite(promoted_piece, "Idle")

        queen_frames = sprite_manager.assets_cache["wQ"]["idle"]["frames"]
        self.assertTrue(queen_frames)
        self.assertIsNotNone(sprite)
        self.assertEqual(sprite.shape, queen_frames[0].shape)


if __name__ == "__main__":
    unittest.main()
