import logging
from enum import Enum
from typing import Dict

from common.common import piece_fen_letter_to_chess_piece

log = logging.getLogger("pgn2data - board ref")
logging.basicConfig(level=logging.INFO)


class MoveType(Enum):
    """Distinguish castling moves from regular moves."""

    white_kingside = 1
    white_queenside = 2
    black_kingside = 3
    black_queenside = 4
    regular = 5


class PieceColor(Enum):
    """Represent a piece's colour."""

    white = 1
    black = 2
    unknown = 3


class BoardPieces:
    """Track pieces from the standard chess starting position.

    Uppercase letters represent white pieces, lowercase letters represent
    black pieces, and empty strings represent unoccupied squares.

    This class is currently unused and has been replaced by python-chess
    piece tracking.
    """

    def __init__(self) -> None:
        self.board: Dict[str, str] = {
            "a1": "R", "b1": "N", "c1": "B", "d1": "Q",
            "e1": "K", "f1": "B", "g1": "N", "h1": "R",
            "a2": "P", "b2": "P", "c2": "P", "d2": "P",
            "e2": "P", "f2": "P", "g2": "P", "h2": "P",
            "a3": "", "b3": "", "c3": "", "d3": "",
            "e3": "", "f3": "", "g3": "", "h3": "",
            "a4": "", "b4": "", "c4": "", "d4": "",
            "e4": "", "f4": "", "g4": "", "h4": "",
            "a5": "", "b5": "", "c5": "", "d5": "",
            "e5": "", "f5": "", "g5": "", "h5": "",
            "a6": "", "b6": "", "c6": "", "d6": "",
            "e6": "", "f6": "", "g6": "", "h6": "",
            "a7": "p", "b7": "p", "c7": "p", "d7": "p",
            "e7": "p", "f7": "p", "g7": "p", "h7": "p",
            "a8": "r", "b8": "n", "c8": "b", "d8": "q",
            "e8": "k", "f8": "b", "g8": "n", "h8": "r",
        }

    def get_piece_at_square(self, square: str) -> str:
        """Return the piece letter, or an empty string if empty or unknown."""
        if square in self.board:
            return self.board[square]

        log.error("square not found: %s", square)
        return ""

    def track_move(self, from_square: str, to_square: str) -> None:
        """Update piece positions using lowercase squares, such as 'a1'.

        Handle rook movement when castling. Only square names are validated;
        this method does not check chess legality or handle promotion or
        en passant captures.
        """
        if self.__is_valid_move(from_square, to_square):
            move_type = self.__get_move_type(from_square, to_square)

            # Moving onto an occupied square replaces the captured piece.
            self.board[to_square] = self.board[from_square]
            self.board[from_square] = ""

            # Castling also moves the rook.
            if move_type == MoveType.white_kingside:
                self.board["f1"] = self.board["h1"]
                self.board["h1"] = ""
            elif move_type == MoveType.white_queenside:
                self.board["d1"] = self.board["a1"]
                self.board["a1"] = ""
            elif move_type == MoveType.black_kingside:
                self.board["f8"] = self.board["h8"]
                self.board["h8"] = ""
            elif move_type == MoveType.black_queenside:
                self.board["d8"] = self.board["a8"]
                self.board["a8"] = ""
        else:
            log.error(
                "invalid piece tracking from == %s and to == %s",
                from_square,
                to_square,
            )

    def __is_valid_move(self, from_square: str, to_square: str) -> bool:
        """Check that both square names exist on the board."""
        return from_square in self.board and to_square in self.board

    def __get_move_type(self, from_sq: str, to_sq: str) -> MoveType:
        """Identify castling from the piece and its source and destination."""
        piece = self.get_piece_at_square(from_sq)
        is_king = piece.upper() == "K"

        if is_king:
            if from_sq == "e1" and to_sq == "g1":
                return MoveType.white_kingside
            elif from_sq == "e8" and to_sq == "g8":
                return MoveType.black_kingside
            elif from_sq == "e1" and to_sq == "c1":
                return MoveType.white_queenside
            elif from_sq == "e8" and to_sq == "c8":
                return MoveType.black_queenside

        return MoveType.regular

    @staticmethod
    def __is_valid_piece_name(piece: str) -> bool:
        """Check whether the piece letter is recognized, ignoring case."""
        return str(piece).lower() in piece_fen_letter_to_chess_piece

    def print_board(self) -> None:
        """Print the square-to-piece dictionary."""
        print(self.board)