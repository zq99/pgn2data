import logging
import os
from typing import Optional

import pandas as pd

log = logging.getLogger("pgn2data - process")
logging.basicConfig(level=logging.INFO)


class Result:
    """Track extraction status and the generated games and moves files."""

    def __init__(
        self,
        is_complete: bool,
        games_file: "ResultFile",
        moves_file: Optional["ResultFile"],
    ) -> None:
        self.is_complete: bool = is_complete
        self.games_file: ResultFile = games_file
        self.moves_file: Optional[ResultFile] = moves_file

    @staticmethod
    def get_empty_result() -> "Result":
        """Return an incomplete result with empty file details."""
        return Result(False, ResultFile("", 0), ResultFile("", 0))

    def print_summary(self) -> None:
        """Print the extraction status and output file details."""
        print(f"is complete: {self.is_complete}")
        print(
            f"games file: {self.games_file.name} | "
            f"size: {self.games_file.size}"
        )
        if self.moves_file is not None:
            print(
                f"moves file: {self.moves_file.name} | "
                f"size: {self.moves_file.size}"
            )

    def get_games_df(self) -> Optional[pd.DataFrame]:
        """Read the games file if extraction is complete."""
        return self.__get_as_dataframe(file=self.games_file.name)

    def get_moves_df(self) -> Optional[pd.DataFrame]:
        """Read the moves file if present and extraction is complete."""
        if self.moves_file is None:
            return None
        return self.__get_as_dataframe(file=self.moves_file.name)

    def get_combined_df(self) -> Optional[pd.DataFrame]:
        """Join games and moves on game_id, or return games alone.

        Return None if the games data is unavailable or empty.
        """
        games_df = self.get_games_df()
        moves_df = self.get_moves_df()

        if games_df is not None and not games_df.empty:
            if moves_df is not None and not moves_df.empty:
                return pd.merge(games_df, moves_df, on="game_id")
            return games_df

        log.error("games information is missing or empty")
        return None

    def create_combined_file(self, filename: str) -> bool:
        """Write the combined data to CSV and report whether the file exists."""
        combined_df = self.get_combined_df()

        if combined_df is not None:
            combined_df.to_csv(filename, index=False)
            return os.path.exists(filename)

        log.error("could not combine games and moves file")
        return False

    def __get_as_dataframe(self, file: str) -> Optional[pd.DataFrame]:
        """Read a CSV if extraction is complete; otherwise log and return None."""
        if self.is_complete:
            return pd.read_csv(file)

        self.__display_not_found(file=file)
        return None

    @staticmethod
    def __display_not_found(file: str) -> None:
        """Log an unavailable file."""
        log.error("File not found: %s", file)


class ResultFile:
    """Store an output file's name and size."""

    def __init__(self, name: str, size: int) -> None:
        self.name: str = name
        self.size: int = size