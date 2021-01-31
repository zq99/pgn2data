import unittest
from converter.board_ref import BoardPieces
import logging


class BoardRefTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def run_piece_at_square_test(self):
        bp = BoardPieces()
        bp.print_board()
        self.__moving_piece("e2", "e4", bp)
        self.__moving_piece("e7", "e6", bp)
        self.__moving_piece("g1", "f3", bp)
        bp.print_board()

    def __moving_piece(self, from_square, to_square, bp):
        from_before = bp.get_piece_at_square(from_square)
        to_before = bp.get_piece_at_square(to_square)
        bp.track_move(from_square, to_square)
        from_after = bp.get_piece_at_square(from_square)
        to_after = bp.get_piece_at_square(to_square)
        self.assertEqual(bp.get_piece_at_square(to_square), from_before)
        self.assertEqual(bp.get_piece_at_square(from_square), "")
        self.assertNotEqual(to_before, to_after)
        self.assertNotEqual(from_before, from_after)


def board_test():
    test_board_ref = BoardRefTestCase()
    test_board_ref.run_piece_at_square_test()

def fen_stat_tests():
    pass



def run_all_tests():
    log = logging.getLogger("pgn2data")
    logging.basicConfig(level=logging.INFO)

    log.info("Start testing")
    board_test()
    log.info("End testing")
