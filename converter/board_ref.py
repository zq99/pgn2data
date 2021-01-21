import logging
from common.common import piece_fen_letter_to_chess_piece

log = logging.getLogger("pgn2data - board ref")
logging.basicConfig(level=logging.INFO)
import copy


class BoardPieces:
    """
    This is used to track where the board pieces are during a game
    """

    def __init__(self):
        self.board = {
            "a1": "R", "b1": "N", "c1": "B", "d1": "Q", "e1": "K", "f1": "B", "g1": "N", "h1": "R",
            "a2": "P", "b2": "P", "c2": "P", "d2": "P", "e2": "P", "f2": "P", "g2": "P", "h2": "P",
            "a3": "", "b3": "", "c3": "", "d3": "", "e3": "", "f3": "", "g3": "", "h3": "",
            "a4": "", "b4": "", "c4": "", "d4": "", "e4": "", "f4": "", "g4": "", "h4": "",
            "a5": "", "b5": "", "c5": "", "d5": "", "e5": "", "f5": "", "g5": "", "h5": "",
            "a6": "", "b6": "", "c6": "", "d6": "", "e6": "", "f6": "", "g6": "", "h6": "",
            "a7": "p", "b7": "p", "c7": "p", "d7": "p", "e7": "p", "f7": "p", "g7": "p", "h7": "p",
            "a8": "r", "b8": "n", "c8": "b", "d8": "q", "e8": "k", "f8": "b", "g8": "n", "h8": "r",
        }

    def get_piece_at_square(self, square):
        if square in self.board:
            return self.board[square]
        else:
            log.error("square not found: {}".format(square))
            return ""

    def track_move(self, from_square, to_square):
        """
        these inputs are string representations e.g "A1" or "H8
        """

        # TODO NEEDS TO HANDLE CASTLING
        if self.__is_valid_move(from_square, to_square):
            self.board[to_square] = copy.deepcopy(self.board[from_square])
            self.board[from_square] = ''
        else:
            log.error("invalid piece tracking from == {} and to == {}".format(from_square, to_square))

    def __is_valid_move(self, from_square, to_square):
        return from_square in self.board and to_square in self.board

    @staticmethod
    def __is_valid_piece_name(piece):
        return str(piece).lower() in piece_fen_letter_to_chess_piece

    def print_board(self):
        print(self.board)
