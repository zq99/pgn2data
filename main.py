"""
This has been tested using the Lichess API
lichess.org/games/export/[user_name]
lichess.org/games/export/[user_name]?since=1525132800000
"""

import logging

from converter.pgn_data import PGNData

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
    #             "data/pgn/lichess_DrNykterstein_2021-01-13.pgn",
    #             "data/pgn/lichess_manwithavan_2021-01-04.pgn"], "carlsen")

    import logging

    pgn_data = PGNData(["data/pgn/spassky_petrosian_1966.pgn"],"yyyy")
    #pgn_data = PGNData(["data/pgn/tal_bronstein_1982.pgn"])

    #pgn_data = PGNData(["data/pgn/lichess_damnsaltythatsport_2021-01-04.pgn",
    #                    "data/pgn/lichess_DannyTheDonkey_2021-01-04.pgn",
    #                    "data/pgn/lichess_DrDrunkenstein_2021-01-04.pgn",
    #                    "data/pgn/lichess_DrNykterstein_2021-01-13.pgn",
    #                    "data/pgn/lichess_manwithavan_2021-01-04.pgn"])

    #result = pgn_data.export()
    #result.print_summary()

    import testing.test as t

    t.run_all_tests()
