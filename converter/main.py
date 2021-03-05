from converter.pgn_data import PGNData


def get_engine_path():
    path_dir = "C:/Users/work/Documents/stockfish/"
    engine_name = "stockfish_20090216_x64_bmi2"
    path_name = path_dir + engine_name
    return path_name


def run_test():
    file = "C:/Users/work/Documents/PycharmProjects/pgn2data/samples/caruana_carlsen_2018.pgn"
    pgn_data = PGNData(file)
    pgn_data.set_engine_path(get_engine_path())
    result = pgn_data.export()
    result.print_summary()




run_test()




