"""
This has been tested using the Lichess API
lichess.org/games/export/[user_name]
lichess.org/games/export/[user_name]?since=1525132800000
"""

import logging
import csv
from collections import Counter
from datetime import datetime
import uuid
import ntpath
import os.path

import chess.pgn

file_headers_game = ["game_id", "event", "site", "date_played", "round", "white", "black", "result", "white_elo",
                     "white_rating_diff",
                     "black_elo", "black_rating_diff", "winner", "winner_elo", "loser", "loser_elo",
                     "winner_loser_elo_diff", "eco", "termination", "time_control", "utc_date",
                     "utc_time", "variant", "ply_count", "date_created", "file_name"]

file_headers_moves = ["game_id", "move_no", "move", "fen", "is_check", "is_check_mate", "is_fifty_moves",
                      "is_fivefold_repetition", "is_game_over", "is_insufficient_material",
                      "w_count", "b_count",
                      "wp_count", "bp_count", "wq_count", "bq_count", "wb_count", "bb_count", "wn_count", "bn_count",
                      "wr_count", "br_count",
                      "captured_score_for_white", "captured_score_for_black",
                      "fen_row1_w_count", "fen_row2_w_count", "fen_row3_w_count", "fen_row4_w_count",
                      "fen_row5_w_count", "fen_row6_w_count", "fen_row7_w_count", "fen_row8_w_count",
                      "fen_row1_b_count", "fen_row2_b_count", "fen_row3_b_count", "fen_row4_b_count",
                      "fen_row5_b_count", "fen_row6_b_count", "fen_row7_b_count", "fen_row8_b_count",
                      "fen_row1_w_value", "fen_row2_w_value", "fen_row3_w_value", "fen_row4_w_value",
                      "fen_row5_w_value", "fen_row6_w_value", "fen_row7_w_value", "fen_row8_w_value",
                      "fen_row1_b_value", "fen_row2_b_value", "fen_row3_b_value", "fen_row4_b_value",
                      "fen_row5_b_value", "fen_row6_b_value", "fen_row7_b_value", "fen_row8_b_value",
                      "move_sequence"]

log = logging.getLogger("pgn to dataset")
logging.basicConfig(level=logging.INFO)


def full_range(start, stop): return range(start, stop + 1)


def __get_game_row_data(game, row_number, file_name):
    """
    takes a "game" object and converts it into a list with the data for each column
    """
    winner = __get_winner(game)
    loser = game.headers["White"] if winner == game.headers["Black"] else (
        game.headers["Black"] if winner == game.headers["White"] else winner)
    winner_elo = game.headers["WhiteElo"] if winner == game.headers["White"] else (
        game.headers["BlackElo"] if winner == game.headers["Black"] else "")
    loser_elo = game.headers["WhiteElo"] if winner == game.headers["Black"] else (
        game.headers["BlackElo"] if winner == game.headers["White"] else "")
    winner_loser_elo_diff = 0 if not (str(winner_elo).isnumeric() and str(loser_elo).isnumeric()) else int(
        winner_elo) - int(loser_elo)
    return [row_number,
            game.headers["Event"] if "Event" in game.headers else "",
            game.headers["Site"] if "Site" in game.headers else "",
            game.headers["Date"] if "Date" in game.headers else "",
            game.headers["Round"] if "Round" in game.headers else "",
            game.headers["White"] if "White" in game.headers else "",
            game.headers["Black"] if "Black" in game.headers else "",
            game.headers["Result"] if "Result" in game.headers else "",
            game.headers["WhiteElo"] if "WhiteElo" in game.headers else "",
            game.headers["WhiteRatingDiff"] if "WhiteRatingDiff" in game.headers else "",
            game.headers["BlackElo"] if "BlackElo" in game.headers else "",
            game.headers["BlackRatingDiff"] if "BlackRatingDiff" in game.headers else "",
            winner,
            winner_elo,
            loser,
            loser_elo,
            winner_loser_elo_diff,
            game.headers["ECO"] if "ECO" in game.headers else "",
            game.headers["Termination"] if "Termination" in game.headers else "",
            game.headers["TimeControl"] if "TimeControl" in game.headers else "",
            game.headers["UTCDate"] if "UTCDate" in game.headers else "",
            game.headers["UTCTime"] if "UTCTime" in game.headers else "",
            game.headers["Variant"] if "Variant" in game.headers else "",
            game.headers["PlyCount"] if "PlyCount" in game.headers else "",
            __get_time_stamp(), ntpath.basename(file_name)]


def __get_move_row_data(move, board, game_id, order_number, sequence):
    fen_stats = FenStats(board.board_fen())
    white_count, black_count = fen_stats.get_total_piece_count()
    fen_row_valuations = fen_stats.get_fen_row_counts_and_valuation()
    return [game_id, order_number, move, board.board_fen(),
            1 if board.is_check() else 0,
            1 if board.is_checkmate() else 0,
            1 if board.is_fifty_moves() else 0,
            1 if board.is_fivefold_repetition() else 0,
            1 if board.is_game_over() else 0,
            1 if board.is_insufficient_material() else 0,
            white_count,
            black_count,
            fen_stats.get_piece_count(chess.PAWN, chess.WHITE),
            fen_stats.get_piece_count(chess.PAWN, chess.BLACK),
            fen_stats.get_piece_count(chess.QUEEN, chess.WHITE),
            fen_stats.get_piece_count(chess.QUEEN, chess.BLACK),
            fen_stats.get_piece_count(chess.BISHOP, chess.WHITE),
            fen_stats.get_piece_count(chess.BISHOP, chess.BLACK),
            fen_stats.get_piece_count(chess.KNIGHT, chess.WHITE),
            fen_stats.get_piece_count(chess.KNIGHT, chess.BLACK),
            fen_stats.get_piece_count(chess.ROOK, chess.WHITE),
            fen_stats.get_piece_count(chess.ROOK, chess.BLACK),
            fen_stats.get_captured_score(chess.WHITE),
            fen_stats.get_captured_score(chess.BLACK),
            fen_row_valuations[0][0], fen_row_valuations[1][0], fen_row_valuations[2][0], fen_row_valuations[3][0],
            fen_row_valuations[4][0], fen_row_valuations[5][0], fen_row_valuations[6][0], fen_row_valuations[7][0],
            fen_row_valuations[0][1], fen_row_valuations[1][1], fen_row_valuations[2][1], fen_row_valuations[3][1],
            fen_row_valuations[4][1], fen_row_valuations[5][1], fen_row_valuations[6][1], fen_row_valuations[7][1],
            fen_row_valuations[0][2], fen_row_valuations[1][2], fen_row_valuations[2][2], fen_row_valuations[3][2],
            fen_row_valuations[4][2], fen_row_valuations[5][2], fen_row_valuations[6][2], fen_row_valuations[7][2],
            fen_row_valuations[0][3], fen_row_valuations[1][3], fen_row_valuations[2][3], fen_row_valuations[3][3],
            fen_row_valuations[4][3], fen_row_valuations[5][3], fen_row_valuations[6][3], fen_row_valuations[7][3],
            sequence]


def __get_winner(game):
    info = game.headers
    if "White" in info and "Black" in info and "Result" in info:
        if game.headers["Result"] == "1/2-1/2":
            return "draw"
        return game.headers["White"] if game.headers["Result"] == "1-0" else game.headers["Black"]
    else:
        return ""


def __get_time_stamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def __open_file(file_name):
    try:
        return open(file_name, mode='w', newline='', encoding="utf-8")
    except PermissionError:
        log.error("Could not access the file: {}".format(file_name))
        return None


piece_fen_letter_to_chess_piece = {
    "p": chess.PAWN,
    "q": chess.QUEEN,
    "n": chess.KNIGHT,
    "k": chess.KING,
    "r": chess.ROOK,
    "b": chess.BISHOP
}

piece_fen_letters = {
    chess.PAWN: "p",
    chess.QUEEN: "q",
    chess.KNIGHT: "n",
    chess.KING: "k",
    chess.ROOK: "r",
    chess.BISHOP: "b"
}

piece_fen_value = {
    chess.PAWN: 1,
    chess.QUEEN: 9,
    chess.KNIGHT: 3,
    chess.KING: 0,
    chess.ROOK: 5,
    chess.BISHOP: 3
}

piece_fen_count = {
    chess.PAWN: 8,
    chess.QUEEN: 1,
    chess.KNIGHT: 2,
    chess.KING: 1,
    chess.ROOK: 2,
    chess.BISHOP: 2
}


class FenStats:
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


def process_file(pgn_file, games_writer, moves_writer):
    """
    processes on pgn file and then exports game information
    into the game csv file, and the moves into the moves csv file
    """

    log.info("Processing file:{}".format(pgn_file))
    pgn = open(pgn_file)

    while True:
        game_id = uuid.uuid4()
        game = chess.pgn.read_game(pgn)
        if game is None:
            break  # end of file
        games_writer.writerow(__get_game_row_data(game, game_id, pgn_file))
        board = game.board()
        order_number = 1
        sequence = ""
        for move in game.mainline_moves():
            sequence += ("|" if len(sequence) > 0 else "") + str(move)
            board.push(move)
            moves_writer.writerow(__get_move_row_data(move, board, game_id, order_number, sequence))
            order_number += 1


def is_valid_pgn_list(file_list):
    if len(file_list) > 0:
        for file in file_list:
            if not os.path.isfile(file):
                return False
        return True
    return False


def process_pgn(file_list, output_file=None):
    """
    This takes a PGN file and creates two output files
    1. First file contains the game information
    2. Second file containing the moves
    """

    log.info("Starting process..")

    if not is_valid_pgn_list(file_list):
        log.error("no pgn files found!")
        return

    output_file = ntpath.basename(file_list[0]) if output_file is None else output_file

    file_name_games = output_file + '_game_info.csv'
    file_name_moves = output_file + '_moves.csv'

    file_games = __open_file(file_name_games)
    file_moves = __open_file(file_name_moves)

    if file_games is None or file_moves is None:
        log.info("No data exported!")
        return

    game_export_writer = csv.writer(file_games, delimiter=',')
    game_export_writer.writerow(file_headers_game)
    move_export_writer = csv.writer(file_moves, delimiter=',')
    move_export_writer.writerow(file_headers_moves)

    for file in file_list:
        process_file(file, game_export_writer, move_export_writer)

    log.info("ending process..")


if __name__ == '__main__':
    files = ["data/pgn/tal_bronstein_1982.pgn"]
    # files = ["data/pgn/lichess_damnsaltythatsport_2021-01-04.pgn",
    #         "data/pgn/lichess_DannyTheDonkey_2021-01-04.pgn",
    #         "data/pgn/lichess_DrDrunkenstein_2021-01-04.pgn",
    #         "data/pgn/lichess_DrNykterstein_2021-01-04.pgn",
    #        "data/pgn/lichess_manwithavan_2021-01-04.pgn"]

    process_pgn(files, "bronstein")
