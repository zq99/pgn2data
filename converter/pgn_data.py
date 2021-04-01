import logging
import ntpath
import os.path

from common.common import open_file
from common.log_time import TimeProcess
from converter.process import Process
from converter.result import ResultFile, Result

log = logging.getLogger("pgn2data - pgn_data class")
logging.basicConfig(level=logging.INFO)


class PGNData:
    """
    Main class to handle the library's methods
    examples of how to call:
        (1) p = PGNData("tal_bronstein_1982.pgn","test")
        (2) p = PGNData("tal_bronstein_1982.pgn")
        (3) p = PGNData(["tal_bronstein_1982.pgn","tal_bronstein_1982.pgn"],"myfilename")
        (4) p = PGNData(["tal_bronstein_1982.pgn","tal_bronstein_1982.pgn"])

        p.export()
    """

    def __init__(self, pgn, file_name=None):
        self._pgn = pgn
        self._file_name = file_name
        self._engine_path = None
        self._depth = 20

    def set_engine_path(self, path):
        self._engine_path = path

    def set_engine_depth(self, depth):
        if type(depth) == int:
            self._depth = depth
        else:
            log.error("Invalid engine depth specified: " + str(depth))

    def export(self):
        """
        main method to convert pgn to csv
        """
        timer = TimeProcess()
        result = Result.get_empty_result()
        if isinstance(self._pgn, list):
            if not self.__is_valid_pgn_list(self._pgn):
                log.error("no pgn files found!")
                return result
            file = self.__create_file_name(self._pgn[0]) if self._file_name is None else self._file_name
            result = self.__process_pgn_list(self._pgn, file)
        elif isinstance(self._pgn, str):
            if not os.path.isfile(self._pgn):
                log.error("no pgn files found!")
                return result
            pgn_list = [self._pgn]
            file = self.__create_file_name(self._pgn) if self._file_name is None else self._file_name
            result = self.__process_pgn_list(pgn_list, file)
        timer.print_time_taken()
        return result

    @staticmethod
    def __create_file_name(file_path):
        return ntpath.basename(file_path).replace(".pgn", "")

    def __process_pgn_list(self, file_list, output_file=None):
        """
        This takes a PGN file and creates two output files
        1. First file contains the game information
        2. Second file containing the moves
        """

        log.info("Starting process..")

        result = Result.get_empty_result()

        file_name_games = output_file + '_game_info.csv'
        file_name_moves = output_file + '_moves.csv'

        file_games = open_file(file_name_games)
        file_moves = open_file(file_name_moves)

        if file_games is None or file_moves is None:
            log.info("No data exported!")
            return result

        add_headers = True
        for file in file_list:
            process = Process(file, file_games, file_moves, self._engine_path, self._depth)
            process.parse_file(add_headers)
            add_headers = False

        file_games.close()
        file_moves.close()

        # return a result object to indicate outcome
        result = self.__get_result_of_output_files(file_name_games, file_name_moves)

        log.info("ending process..")
        return result

    @staticmethod
    def __is_valid_pgn_list(file_list):
        """
        valid = list cannot be empty and each entry must exist
        """
        if len(file_list) > 0:
            for file in file_list:
                if not os.path.isfile(file):
                    log.error("file not found:" + file)
                    return False
            return True
        return False

    def __get_result_of_output_files(self, game_file_name, moves_file_name):
        result = Result.get_empty_result()
        try:
            is_games_file_exists = os.path.isfile(game_file_name)
            is_moves_file_exists = os.path.isfile(moves_file_name)
            is_files_exists = is_games_file_exists and is_moves_file_exists
            game_size = self.__get_size(game_file_name) if is_games_file_exists else 0
            move_size = self.__get_size(moves_file_name) if is_moves_file_exists else 0
            game_result = ResultFile(game_file_name, game_size)
            move_result = ResultFile(moves_file_name, move_size)
            result = Result(is_files_exists, game_result, move_result)
        except Exception as e:
            log.error(e)
            pass
        return result

    @staticmethod
    def __get_size(filename):
        st = os.stat(filename)
        return st.st_size
