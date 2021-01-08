import logging
import chess
import uuid
import chess.pgn
import ntpath
from log_time import get_time_stamp
from fen import FenStats


log = logging.getLogger("pgn2data - process")
logging.basicConfig(level=logging.INFO)


class PlayerMove:
    """
    data class to hold details of each move
    move = Move object from python chess library
    notation = is algebraic notation of the move
    """

    def __init__(self, move, notation):
        self.move = move
        self.notation = notation

    def get_from_square(self):
        return str(self.move)[:2] if self.__is_valid_move() else ""

    def get_to_square(self):
        return str(self.move)[2:] if self.__is_valid_move() else ""

    def __is_valid_move(self):
        return len(str(self.move)) == 4


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
            notation = board.san(move)
            board.push(move)
            player_move = PlayerMove(move, notation)
            sequence += ("|" if len(notation) > 0 else "") + str(notation)
            moves_writer.writerow(__get_move_row_data(player_move, board, game_id, order_number, sequence))
            order_number += 1


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
            get_time_stamp(), ntpath.basename(file_name)]


def __get_move_row_data(player_move, board, game_id, order_number, sequence):
    """
    process each move in a game
    """

    fen_stats = FenStats(board.board_fen())
    white_count, black_count = fen_stats.get_total_piece_count()
    fen_row_valuations = fen_stats.get_fen_row_counts_and_valuation()

    return [game_id, order_number,
            player_move.notation,
            player_move.move,
            player_move.get_from_square(),
            player_move.get_to_square(),
            # player_move.get_piece(),
            board.board_fen(),
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
