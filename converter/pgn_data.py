import logging
import ntpath
import os.path
from typing import List, Optional, Union

import pandas as pd

from common.common import open_file
from common.log_time import TimeProcess
from converter.process import Process
from converter.result import ResultFile, Result

log = logging.getLogger("pgn2data - pgn_data class")
logging.basicConfig(level=logging.INFO)

DEFAULT_MOVES_REQUIRED: bool = True
DEFAULT_QUEUE_SIZE: int = 0
DEFAULT_COLLAPSE: bool = False
DEFAULT_ENGINE_DEPTH: int = 20


class PGNData:
    """
    Main class to handle the library's methods
    examples of how to call:
        (1) p = PGNData("tal_bronstein_1982.pgn","test")
        (2) p = PGNData("tal_bronstein_1982.pgn")
        (3) p = PGNData(["tal_bronstein_1982.pgn","tal_bronstein_1982.pgn"],"MyFilename")
        (4) p = PGNData(["tal_bronstein_1982.pgn","tal_bronstein_1982.pgn"])

        p.export()
    """

    def __init__(
            self, pgn: Union[str, List[str]], file_name: Optional[str] = None
    ) -> None:
        """Store the PGN input, optional output basename and default engine settings."""
        self._pgn = pgn
        self._file_name = file_name
        self._engine_path: Optional[str] = None
        self._engine_depth = DEFAULT_ENGINE_DEPTH

    def set_engine_path(self, path: Optional[str]) -> None:
        """Set the UCI engine path, or disable engine analysis with None."""
        self._engine_path = path

    def set_engine_depth(self, depth: int) -> None:
        """Set the analysis depth if the value is an exact int; otherwise log an error."""
        if type(depth) == int:
            self._engine_depth = depth
        else:
            log.error("Invalid engine depth specified: " + str(depth))

    def export(
        self,
        moves_required: bool = DEFAULT_MOVES_REQUIRED,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        collapse: bool = DEFAULT_COLLAPSE,
    ) -> Result:
        """
        main method to convert pgn to csv
        :parameter moves_required - if true a games and moves file is created
        :parameter queue_size - this is the max_size of the blocking queue when processing moves
        :parameter collapse - this removes any null columns from the final files
        """

        if not isinstance(moves_required, bool):
            raise TypeError("moves_required must be a bool")
        if not isinstance(queue_size, int) or queue_size < 0:
            raise ValueError("queue_size must be an int greater or equal to 0")
        if not isinstance(collapse, bool):
            raise TypeError("collapse must be a bool, when True it will remove null columns")

        timer = TimeProcess()
        result = Result.get_empty_result()

        pgn_list = self._pgn if isinstance(self._pgn, list) else [str(self._pgn)]
        file_name = self._pgn[0] if isinstance(self._pgn, list) and len(self._pgn) > 0 else str(self._pgn)

        if not self.__is_valid_pgn_list(file_list=pgn_list):
            log.error("No valid pgn file(s) found to convert to csv!")
            return result

        full_file_name = (
            self.__create_file_name(file_path=file_name) if self._file_name is None else self._file_name
        )
        result = self.__process_pgn_list(
            file_list=pgn_list,
            output_file=full_file_name,
            moves_required=moves_required,
            queue_size=queue_size,
            collapse=collapse
        )

        timer.print_time_taken()
        return result

    @staticmethod
    def __create_file_name(file_path: str) -> str:
        """Derive an output basename using the existing .pgn replacement rule."""
        return ntpath.basename(file_path).replace(".pgn", "")

    def __process_pgn_list(
        self,
        file_list: List[str],
        output_file: Optional[str] = None,
        moves_required: bool = DEFAULT_MOVES_REQUIRED,
        queue_size: int = DEFAULT_QUEUE_SIZE,
        collapse: bool = DEFAULT_COLLAPSE,
    ) -> Result:
        """
        This takes a PGN file and creates two output files
        1. First file contains the game information
        2. Second file containing the moves
        """

        log.info("Starting process..")

        result = Result.get_empty_result()

        # Both output streams are shared across all input PGN files.
        file_name_games = output_file + '_game_info.csv'
        file_games = open_file(file_name=file_name_games)

        if moves_required:
            file_name_moves = output_file + '_moves.csv'
            file_moves = open_file(file_name_moves)
            export_files_initialized = (file_games is not None) and (file_moves is not None)
        else:
            file_name_moves, file_moves = None, None
            export_files_initialized = file_games is not None

        if not export_files_initialized:
            log.info("Could not initialize the csv files to export the data into!")
            return result

        # Write headers once, even when appending multiple input files.
        add_headers = True
        for file in file_list:
            process = Process(
                pgn_file=file,
                file_games=file_games,
                file_moves=file_moves,
                engine_path=self._engine_path,
                engine_depth=self._engine_depth,
                moves_required=moves_required,
                queue_size=queue_size,
            )
            process.parse_file(add_headers)
            add_headers = False

        file_games.close()
        if moves_required:
            file_moves.close()

        # remove any null columns
        if collapse:
            self.__remove_empty_columns(file_name=file_name_games)
            self.__remove_empty_columns(file_name=file_name_moves)

        # return a result object to indicate outcome
        result = self.__get_result_of_output_files(
            game_file_name=file_name_games,
            moves_file_name=file_name_moves,
            moves_required=moves_required
        )

        log.info("ending process..")
        return result

    @staticmethod
    def __remove_empty_columns(file_name: Optional[str]) -> None:
        """Remove all-null columns from an existing CSV file."""
        if not isinstance(file_name, str) or not os.path.isfile(file_name):
            return

        df = pd.read_csv(file_name)
        df = df.dropna(axis=1, how="all")
        df.to_csv(file_name, index=False)

    @staticmethod
    def __is_valid_pgn_list(file_list: List[str]) -> bool:
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

    def __get_result_of_output_files(
        self,
        game_file_name: str,
        moves_file_name: Optional[str] = None,
        moves_required: bool = DEFAULT_MOVES_REQUIRED,
    ) -> Result:
        """Build file metadata and completion status, logging errors if inspection fails."""
        result = Result.get_empty_result()

        try:
            is_games_file_exists = os.path.isfile(game_file_name)
            game_size = self.__get_size(filename=game_file_name) if is_games_file_exists else 0
            game_result = ResultFile(game_file_name, game_size)

            if moves_required:
                is_moves_file_exists = os.path.isfile(moves_file_name) if moves_file_name is not None else False
                move_size = self.__get_size(filename=moves_file_name) if is_moves_file_exists else 0
                move_result = ResultFile(moves_file_name, move_size)
                is_files_exists = is_games_file_exists and is_moves_file_exists
            else:
                is_files_exists = is_games_file_exists
                move_result = None

            result = Result(is_files_exists, game_result, move_result)
        except Exception as e:
            log.error(e)
            pass
        return result

    @staticmethod
    def __get_size(filename: str) -> int:
        """Return the file size in bytes."""
        st = os.stat(filename)
        return st.st_size