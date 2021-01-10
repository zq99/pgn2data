"""
This has been tested using the Lichess API
lichess.org/games/export/[user_name]
lichess.org/games/export/[user_name]?since=1525132800000
"""

import logging

from pgn_data import PgnData

log = logging.getLogger("pgn2data - main")
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # r = convert_pgn("data/pgn/tal_bronstein_1982.pgn", "test")
    # r = convert_pgn("data/pgn/lichess_DrNykterstein_2021-01-04.pgn","test2")
    #    print(r.is_complete)
    #    print(r.games_file.size)
    #    print(r.moves_file.size)

    # convert_pgn(["data/pgn/lichess_damnsaltythatsport_2021-01-04.pgn",
    #             "data/pgn/lichess_DannyTheDonkey_2021-01-04.pgn",
    #             "data/pgn/lichess_DrDrunkenstein_2021-01-04.pgn",
    #             "data/pgn/lichess_DrNykterstein_2021-01-04.pgn",
    #             "data/pgn/lichess_manwithavan_2021-01-04.pgn"], "carlsen")

    pgn_data = PgnData("data/pgn/tal_bronstein_1982.pgn", "testyyy")
    result = pgn_data.export()
