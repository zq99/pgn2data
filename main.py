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
from process import process_file

log = logging.getLogger("pgn2data - main")
logging.basicConfig(level=logging.INFO)


def process_pgn_list(file_list, output_file=None):
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
        process_file(file, game_export_writer, move_export_writer)

    log.info("ending process..")


def is_valid_pgn_list(file_list):
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
    if isinstance(pgn, list):
        if not is_valid_pgn_list(pgn):
            log.error("no pgn files found!")
            return
        file = ntpath.basename(pgn[0]) if file_name is None else file_name
        process_pgn_list(pgn, file)
    elif isinstance(pgn, str):
        pgn_list = [pgn]
        file = pgn if file_name is None else file_name
        process_pgn_list(pgn_list, file)


if __name__ == '__main__':
    convert_pgn("data/pgn/tal_bronstein_1982.pgn", "test")

# convert_pgn(["data/pgn/lichess_damnsaltythatsport_2021-01-04.pgn",
#             "data/pgn/lichess_DannyTheDonkey_2021-01-04.pgn",
#             "data/pgn/lichess_DrDrunkenstein_2021-01-04.pgn",
#             "data/pgn/lichess_DrNykterstein_2021-01-04.pgn",
#             "data/pgn/lichess_manwithavan_2021-01-04.pgn"], "carlsen")
