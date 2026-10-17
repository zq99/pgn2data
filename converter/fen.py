import logging
from collections import Counter
from typing import List, Tuple, NamedTuple

import chess

from common.common import (
    full_range,
    piece_fen_count,
    piece_fen_letter_to_chess_piece,
    piece_fen_letters,
    piece_fen_value,
)

log = logging.getLogger("pgn2data - fen")
logging.basicConfig(level=logging.INFO)


class FenRowStats(NamedTuple):
    white_count: int
    white_value: int
    black_count: int
    black_value: int


class FenStats:
    """Calculate piece counts and material values from a FEN position."""

    # Total starting material value per player, excluding the king.
    PIECE_VALUE_TOTAL: int = 39

    def __init__(self, fen: str) -> None:
        self.fen_position: str = fen

    @staticmethod
    def __is_valid_color(color: chess.Color) -> bool:
        """Check whether the color is white or black."""
        return color in [chess.WHITE, chess.BLACK]

    @staticmethod
    def __is_valid_piece(piece: chess.PieceType) -> bool:
        """Check whether the piece type has a recognized FEN letter."""
        return piece in piece_fen_letters

    def get_total_piece_count(self) -> Tuple[int, int]:
        """Return the total white and black piece counts, including kings."""
        pieces_to_count = [
            chess.PAWN,
            chess.QUEEN,
            chess.KNIGHT,
            chess.BISHOP,
            chess.ROOK,
            chess.KING,
        ]
        white_total = 0
        black_total = 0

        for piece in pieces_to_count:
            white_total += self.get_piece_count(piece, chess.WHITE)
            black_total += self.get_piece_count(piece, chess.BLACK)

        return white_total, black_total

    def get_piece_count(
        self,
        piece: chess.PieceType,
        color: chess.Color,
    ) -> int:
        """Count a piece type for the specified color.

        Use python-chess constants, such as chess.PAWN and chess.WHITE.
        Return zero if either parameter is invalid.
        """
        if not self.__is_valid_piece(piece):
            log.error("invalid piece parameter %s", piece)
            return 0
        elif not self.__is_valid_color(color):
            log.error("invalid color parameter %s", color)
            return 0

        piece_letter = (
            piece_fen_letters[piece].lower()
            if color == chess.BLACK
            else piece_fen_letters[piece].upper()
        )
        counts = Counter(self.fen_position)
        return counts[piece_letter]

    def get_captured_score(self, color: chess.Color) -> int:
        """Estimate captured material from the opponent's missing pieces.

        Compare the opponent's current piece counts with their starting
        counts. Promotions are not accounted for.
        """
        if not self.__is_valid_color(color):
            log.error("invalid color parameter %s", color)
            return 0

        captured_score = 0
        pieces_to_sum = [
            chess.PAWN,
            chess.QUEEN,
            chess.KNIGHT,
            chess.BISHOP,
            chess.ROOK,
        ]

        for piece in pieces_to_sum:
            count_at_start = piece_fen_count[piece]
            count_at_position = self.get_piece_count(
                piece,
                chess.WHITE if color == chess.BLACK else chess.BLACK,
            )
            captured_score += (
                count_at_start - count_at_position
            ) * piece_fen_value[piece]

        return captured_score


    def get_fen_row_counts_and_valuation(self) -> List[FenRowStats]:
        """Return a FenRowStats object for each rank, ordered from 1 to 8."""
        results: List[FenRowStats] = []

        for row in full_range(1, 8):
            results.append(self.get_piece_count_and_value_for_fen_row(row))

        return results

    def get_piece_count_and_value_for_fen_row(
        self,
        row: int,
    ) -> FenRowStats:
        """Return piece counts and material values for a rank from 1 to 8.

        Return order: white count, white value, black count, black value.
        Kings contribute to piece counts but have zero material value.
        Return four zeros if the row fails validation.
        """
        w_piece_count = 0
        w_piece_valuation = 0
        b_piece_count = 0
        b_piece_valuation = 0

        if not str(row).isnumeric() or (row < 1 or row > 8):
            log.error("invalid fen row %s", row)
            return FenRowStats(0, 0, 0, 0)

        # FEN lists ranks from 8 to 1; reverse them for rank-based indexing.
        fen_rows = self.fen_position.split("/")
        fen_rows = list(reversed(fen_rows))

        row_to_evaluate = fen_rows[row - 1]

        for value in row_to_evaluate:
            if not str(value).isnumeric():
                if str(value).lower() in piece_fen_letter_to_chess_piece:
                    chess_piece = piece_fen_letter_to_chess_piece[
                        str(value).lower()
                    ]
                    color = (
                        chess.WHITE
                        if str(value).upper() == value
                        else chess.BLACK
                    )
                    w_piece_count += 1 if color == chess.WHITE else 0
                    b_piece_count += 1 if color == chess.BLACK else 0
                    w_piece_valuation += (
                        piece_fen_value[chess_piece]
                        if color == chess.WHITE
                        else 0
                    )
                    b_piece_valuation += (
                        piece_fen_value[chess_piece]
                        if color == chess.BLACK
                        else 0
                    )

        return FenRowStats(
            white_count=w_piece_count,
            white_value=w_piece_valuation,
            black_count=b_piece_count,
            black_value=b_piece_valuation,
        )