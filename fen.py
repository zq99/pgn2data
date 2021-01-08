from collections import Counter
import chess
import logging

from common import piece_fen_letters, piece_fen_count, piece_fen_value, full_range, piece_fen_letter_to_chess_piece

log = logging.getLogger("pgn2data - fen")
logging.basicConfig(level=logging.INFO)


class FenStats:
    """
    Handles all calculations performed on the fen position
    """
    # value of all player pieces at start of game
    PIECE_VALUE_TOTAL = 39

    def __init__(self, fen):
        self.fen_position = fen

    @staticmethod
    def __is_valid_color(color):
        return color in [chess.WHITE, chess.BLACK]

    @staticmethod
    def __is_valid_piece(piece):
        return piece in piece_fen_letters

    def get_total_piece_count(self):
        """
        returns a tuple with the total number of white and black pieces
        """
        pieces_to_count = [chess.PAWN, chess.QUEEN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.KING]
        white_total = 0
        black_total = 0
        for piece in pieces_to_count:
            white_total += self.get_piece_count(piece, chess.WHITE)
            black_total += self.get_piece_count(piece, chess.BLACK)
        return white_total, black_total

    def get_piece_count(self, piece, color):
        """
        the parameters "piece" and "color" are constants are from the python chess library
        color is either: chess.WHITE or chess.BLACK
        pieces: chess.PAWN, chess.QUEEN, chess.KNIGHT, chess.BISHOP, chess.ROOK
        """
        if not self.__is_valid_piece(piece):
            log.error("invalid piece parameter {}".format(str(piece)))
            return 0
        elif not self.__is_valid_color(color):
            log.error("invalid color parameter {}".format(str(color)))
            return 0
        piece_letter = piece_fen_letters[piece].lower() if color == chess.BLACK else piece_fen_letters[piece].upper()
        c = Counter(self.fen_position)
        return c[piece_letter]

    def get_captured_score(self, color):
        """
        color is the color of the player you want the score for.
        so if color= white, you need to calculate how how many black pieces captured and the total value
        of these pieces
        """
        if not self.__is_valid_color(color):
            log.error("invalid color parameter {}".format(str(color)))
            return 0

        captured_score = 0
        pieces_to_sum = [chess.PAWN, chess.QUEEN, chess.KNIGHT, chess.BISHOP, chess.ROOK]
        for piece in pieces_to_sum:
            count_at_start = piece_fen_count[piece]
            count_at_position = self.get_piece_count(piece, chess.WHITE if color == chess.BLACK else chess.BLACK)
            captured_score += (count_at_start - count_at_position) * piece_fen_value[piece]
        return captured_score

    def get_fen_row_counts_and_valuation(self):
        """
        get row counts and evaluation for all fen rows
        returns a list with 8 tuples
        each tuple has 4 values:
        white_cnt, black_cnt, white_val, black_val
        """
        results = []
        for row in full_range(1, 8):
            results.append(self.get_piece_count_and_value_for_fen_row(row))
        return results

    def get_piece_count_and_value_for_fen_row(self, row):
        """
        Returns the number of white and black pieces for a specified row in the the fen string (includes king)
        Also returns the total valuations for the white and black pieces (excludes king)
        row = fen row number between 1 and 8
        color = chess.WHITE or chess.BLACK
        """
        w_piece_count = 0
        w_piece_valuation = 0
        b_piece_count = 0
        b_piece_valuation = 0

        if not str(row).isnumeric() or (row < 1 or row > 8):
            log.error("invalid fen row {}".format(str(row)))
            return 0, 0, 0, 0

        fen_rows = self.fen_position.split("/")
        row_to_evaluate = fen_rows[row - 1]
        for value in row_to_evaluate:
            if not str(value).isnumeric():
                if str(value).lower() in piece_fen_letter_to_chess_piece:
                    chess_piece = piece_fen_letter_to_chess_piece[str(value).lower()]
                    color = chess.WHITE if str(value).upper() == value else chess.BLACK
                    w_piece_count += 1 if color == chess.WHITE else 0
                    b_piece_count += 1 if color == chess.BLACK else 0
                    w_piece_valuation += piece_fen_value[chess_piece] if color == chess.WHITE else 0
                    b_piece_valuation += piece_fen_value[chess_piece] if color == chess.BLACK else 0

        return w_piece_count, w_piece_valuation, b_piece_count, b_piece_valuation
