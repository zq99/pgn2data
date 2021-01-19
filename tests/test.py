import unittest
from converter.board_ref import BoardPieces


class BoardRefTestCase(unittest.TestCase):
    def card_deck_creation_test(self):
        bp = BoardPieces()
        bp.print_board()
        e2 = bp.get_piece_at_square("e2")
        e4_before = bp.get_piece_at_square("e4")
        bp.track_move("e2", "e4")
        self.assertTrue(bp.get_piece_at_square("e4"), e2)
        self.assertTrue(bp.get_piece_at_square("e2"), "")
        ef4_after = bp.get_piece_at_square("e4")
        self.assertFalse(e4_before,ef4_after)

