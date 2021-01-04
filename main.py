"""
This has been tested using the Lichess API
lichess.org/games/export/[user_name]
lichess.org/games/export/[user_name]?since=1525132800000
"""

import logging
import csv
from datetime import datetime
import uuid
import ntpath

import chess.pgn

file_headers_game = ["game_id", "event", "site", "date_played", "round", "white", "black", "result", "winner",
                     "black_elo", "black_rating_diff", "eco", "termination", "time_control", "utc_date",
                     "utc_time", "variant", "white_elo", "white_rating_diff", "date_extracted", "file_name"]

file_headers_moves = ["game_id", "order_no", "move", "is_check", "is_check_mate", "is_fifty_moves",
                      "is_fivefold_repetition", "is_game_over", "is_insufficient_material", "move_sequence"]

log = logging.getLogger("pgn to dataset")
logging.basicConfig(level=logging.INFO)


def __get_game_row_data(game, row_number, file_name):
    """
    takes a "game" object and converts it into a list with the data for each column
    """
    return [row_number,
            game.headers["Event"] if "Event" in game.headers else "",
            game.headers["Site"] if "Site" in game.headers else "",
            game.headers["Date"] if "Date" in game.headers else "",
            game.headers["Round"] if "Round" in game.headers else "",
            game.headers["White"] if "White" in game.headers else "",
            game.headers["Black"] if "Black" in game.headers else "",
            game.headers["Result"] if "Result" in game.headers else "",
            __get_winner(game),
            game.headers["BlackElo"] if "BlackElo" in game.headers else "",
            game.headers["BlackRatingDiff"] if "BlackRatingDiff" in game.headers else "",
            game.headers["ECO"] if "ECO" in game.headers else "",
            game.headers["Termination"] if "Termination" in game.headers else "",
            game.headers["TimeControl"] if "TimeControl" in game.headers else "",
            game.headers["UTCDate"] if "UTCDate" in game.headers else "",
            game.headers["UTCTime"] if "UTCTime" in game.headers else "",
            game.headers["Variant"] if "Variant" in game.headers else "",
            game.headers["WhiteElo"] if "WhiteElo" in game.headers else "",
            game.headers["WhiteRatingDiff"] if "WhiteRatingDiff" in game.headers else "",
            __get_time_stamp(), ntpath.basename(file_name)]


def __get_move_row_data(move, board, game_id, order_number, sequence):
    return [game_id, order_number, move,
            1 if board.is_check() else 0,
            1 if board.is_checkmate() else 0,
            1 if board.is_fifty_moves() else 0,
            1 if board.is_fivefold_repetition() else 0,
            1 if board.is_game_over() else 0,
            1 if board.is_insufficient_material() else 0,
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
    return len(file_list) > 0


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
    files = ["data/pgn/lichess_damnsaltythatsport_2021-01-04.pgn",
             "data/pgn/lichess_DannyTheDonkey_2021-01-04.pgn",
             "data/pgn/lichess_DrDrunkenstein_2021-01-04.pgn",
             "data/pgn/lichess_DrNykterstein_2021-01-04.pgn",
             "data/pgn/lichess_manwithavan_2021-01-04.pgn"]

    process_pgn(files, "carlsen")
