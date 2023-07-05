import logging
import pandas as pd
import os

log = logging.getLogger("pgn2data - process")
logging.basicConfig(level=logging.INFO)


class Result:
    """
    results of the extract are tracked here
    games_file and moves_file are ResultFile objects
    """

    def __init__(self, is_complete, games_file, moves_file):
        self.is_complete = is_complete
        self.games_file = games_file
        self.moves_file = moves_file

    @staticmethod
    def get_empty_result():
        return Result(False, ResultFile("", 0), ResultFile("", 0))

    def print_summary(self):
        """
        return a summary to console
        """
        print("is complete: {}".format(str(self.is_complete)))
        print("games file: {} | size: {}".format(self.games_file.name, self.games_file.size))
        if self.moves_file is not None:
            print("moves file: {} | size: {}".format(self.moves_file.name, self.moves_file.size))

    def get_games_df(self):
        return self.__get_as_dataframe(self.games_file.name)

    def get_moves_df(self):
        if self.moves_file is None:
            return None
        else:
            return self.__get_as_dataframe(self.moves_file.name)

    def get_combined_df(self):
        games_df = self.get_games_df()
        moves_df = self.get_moves_df()

        if (games_df is not None) and (not games_df.empty):
            if (moves_df is not None) and (not moves_df.empty):
                combined_df = pd.merge(games_df, moves_df, on='game_id')
                return combined_df
            else:
                return games_df
        else:
            log.error("games information is missing or empty")
        return None

    def create_combined_file(self, filename):
        combined_df = self.get_combined_df()
        if combined_df is not None:
            combined_df.to_csv(filename, index=False)
            return os.path.exists(filename)
        else:
            log.error("could not combine games and moves file")
            return False

    def __get_as_dataframe(self, file):
        if self.is_complete:
            return pd.read_csv(file)
        else:
            self.__display_not_found(file)
            return None

    @staticmethod
    def __display_not_found(file):
        log.error("File not found: {}".format(file))


class ResultFile:
    def __init__(self, name, size):
        self.name = name
        self.size = size
