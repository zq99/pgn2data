"""
This has been tested using the Lichess API
lichess.org/games/export/[user_name]
lichess.org/games/export/[user_name]?since=1525132800000
"""

import csv
import logging
import ntpath
import os.path

from headers import file_headers_game, file_headers_moves
from common import open_file
from process import __process_file
from log_time import TimeProcess
from result import ResultFile, Result

log = logging.getLogger("pgn2data - main")
logging.basicConfig(level=logging.INFO)


def __process_pgn_list(file_list, output_file=None):
    """
    This takes a PGN file and creates two output files
    1. First file contains the game information
    2. Second file containing the moves
    """

    log.info("Starting process..")

    file_name_games = output_file + '_game_info.csv'
    file_name_moves = output_file + '_moves.csv'

    file_games = open_file(file_name_games)
    file_moves = open_file(file_name_moves)

    if file_games is None or file_moves is None:
        log.info("No data exported!")
        return

    game_export_writer = csv.writer(file_games, delimiter=',')
    game_export_writer.writerow(file_headers_game)
    move_export_writer = csv.writer(file_moves, delimiter=',')
    move_export_writer.writerow(file_headers_moves)

    for file in file_list:
        __process_file(file, game_export_writer, move_export_writer)

    # return a result object to indicate outcome

    result = get_result_of_output_files(file_name_games, file_name_moves)

    log.info("ending process..")

    return result


def get_result_of_output_files(game_file_name, moves_file_name):
    is_games_file_exists = os.path.isfile(game_file_name)
    is_moves_file_exists = os.path.isfile(moves_file_name)
    is_files_exists = is_games_file_exists and is_moves_file_exists
    game_size = __get_size(game_file_name) if is_games_file_exists else 0
    move_size = __get_size(moves_file_name) if is_moves_file_exists else 0
    game_result = ResultFile(game_file_name, game_size)
    move_result = ResultFile(moves_file_name, move_size)
    return Result(is_files_exists, game_result, move_result)


def __get_size(filename):
    st = os.stat(filename)
    return st.st_size


def __is_valid_pgn_list(file_list):
    """
    valid = list cannot be empty and each entry must exist
    """
    if len(file_list) > 0:
        for file in file_list:
            if not os.path.isfile(file):
                return False
        return True
    return False


def convert_pgn(pgn, file_name=None):
    """
    main method to convert pgn to csv
    examples of how to call:
    (1) convert_pgn("data/pgn/tal_bronstein_1982.pgn","test")
    (2) convert_pgn("data/pgn/tal_bronstein_1982.pgn")
    (3) convert_pgn(["data/pgn/tal_bronstein_1982.pgn","data/pgn/tal_bronstein_1982.pgn"])
    (4) convert_pgn(["data/pgn/tal_bronstein_1982.pgn","data/pgn/tal_bronstein_1982.pgn"])
    """
    timer = TimeProcess()
    result = Result.get_empty_result()
    if isinstance(pgn, list):
        if not __is_valid_pgn_list(pgn):
            log.error("no pgn files found!")
            return
        file = ntpath.basename(pgn[0]) if file_name is None else file_name
        result = __process_pgn_list(pgn, file)
    elif isinstance(pgn, str):
        if not os.path.isfile(pgn):
            log.error("no pgn files found!")
            return
        pgn_list = [pgn]
        file = pgn if file_name is None else file_name
        result = __process_pgn_list(pgn_list, file)
    timer.print_time_taken()
    return result


if __name__ == '__main__':
    # r = convert_pgn("data/pgn/tal_bronstein_1982.pgn", "test")
     r = convert_pgn("data/pgn/lichess_DrNykterstein_2021-01-04.pgn","test2")
    #    print(r.is_complete)
    #    print(r.games_file.size)
    #    print(r.moves_file.size)

    #convert_pgn(["data/pgn/lichess_damnsaltythatsport_2021-01-04.pgn",
    #             "data/pgn/lichess_DannyTheDonkey_2021-01-04.pgn",
    #             "data/pgn/lichess_DrDrunkenstein_2021-01-04.pgn",
    #             "data/pgn/lichess_DrNykterstein_2021-01-04.pgn",
    #             "data/pgn/lichess_manwithavan_2021-01-04.pgn"], "carlsen")
