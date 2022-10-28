"""
==========================================================
    This is the testing framework for the pgn2data library

    All inputs for the tests are in the folder "pgn", and all
    outputs from the tests are in the folder "exports".

    The PGN files To test core functionality are in the
    folder "PGN".

    The PGN files in the "issues" folder, are tests for each
    of the issues raised on github.

    All new functionality or resolved issue needs to have an
    associated test with it (the names of the pgn files used
    for this are in the format: "report_issue_??.csv".

==========================================================
"""

import glob
import logging
import os
import unittest

import chess
import pandas as pd

from common.common import full_range
from converter.board_ref import BoardPieces
from converter.fen import FenStats
from converter.pgn_data import PGNData
from common.log_time import TimeProcess

log = logging.getLogger("pgn2data")
logging.basicConfig(level=logging.INFO)


class BoardRefTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def run_piece_at_square_test(self):
        bp = BoardPieces()
        self.__moving_piece("e2", "e4", bp)
        self.__moving_piece("e7", "e6", bp)
        self.__moving_piece("g1", "f3", bp)

    def __moving_piece(self, from_square, to_square, bp):
        from_before = bp.get_piece_at_square(from_square)
        to_before = bp.get_piece_at_square(to_square)
        bp.track_move(from_square, to_square)
        from_after = bp.get_piece_at_square(from_square)
        to_after = bp.get_piece_at_square(to_square)
        self.assertEqual(bp.get_piece_at_square(to_square), from_before)
        self.assertEqual(bp.get_piece_at_square(from_square), "")
        self.assertNotEqual(to_before, to_after)
        self.assertNotEqual(from_before, from_after)


class FenTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def run_test(self):
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR"
        fs = FenStats(fen)
        white_total, black_total = fs.get_total_piece_count()
        self.assertEqual(white_total, 16)
        self.assertEqual(black_total, 16)
        capture_white = fs.get_captured_score(chess.WHITE)
        capture_black = fs.get_captured_score(chess.BLACK)
        self.assertEqual(capture_white, 0)
        self.assertEqual(capture_black, 0)
        piece_count = fs.get_piece_count(chess.ROOK, chess.WHITE)
        self.assertEqual(piece_count, 2)
        piece_count = fs.get_piece_count(chess.QUEEN, chess.BLACK)
        self.assertEqual(piece_count, 1)

        valuations = [(8, 31, 0, 0),
                      (7, 7, 0, 0),
                      (0, 0, 0, 0),
                      (1, 1, 0, 0),
                      (0, 0, 0, 0),
                      (0, 0, 0, 0),
                      (0, 0, 8, 8),
                      (0, 0, 8, 31)]

        for r in full_range(1, 8):
            result = fs.get_piece_count_and_value_for_fen_row(r)
            self.assertEqual(result, valuations[r - 1])


class FileCreationTestCase(unittest.TestCase):
    exports_folder_name = "exports"
    pgn_folder_name = "pgn"
    issues_folder_name = "issues"
    issues_name = 'reported_issue_*.pgn'

    def __init__(self):
        super().__init__()
        self.setUp()

    def setUp(self):
        self.folder = os.path.dirname(os.path.realpath(__file__))
        self.check_folders_exist()
        self.delete_old_test_exports()

    def check_folders_exist(self):
        folders = [self.get_output_filepath(None), self.get_source_filepath(None),
                   self.get_source_issues_filepath(None)]
        for folder in folders:
            self.assertTrue(os.path.isdir(folder))

    def delete_old_test_exports(self):
        output_path = self.get_output_filepath(None)
        os.chdir(output_path)
        all_files = os.listdir()
        if len(all_files) > 0:
            for f in all_files:
                log.info("removing old export: {}".format(f))
                os.remove(f)
        self.assertTrue(len(os.listdir()) == 0)

    def run_tests(self):
        self.run_basic_pgn_format_test()
        self.run_single_file_test()
        self.run_multiple_files_test()
        self.run_reported_github_issues_test()
        self.run_pandas_dataframe_test()
        self.run_content_test()

    def run_content_test(self):
        f = self.get_source_filepath("content_test.pgn")
        o = self.get_output_filepath("content_test")
        pgn_data = PGNData(f, o)
        result = pgn_data.export()
        self.assertTrue(result.is_complete)
        games_df = result.get_games_df()
        moves_df = result.get_moves_df()
        self.assertFalse(games_df.empty)
        self.assertFalse(moves_df.empty)
        ids_from_games_file = list(set(games_df['game_id'].values.tolist()))
        ids_from_moves_file = list(set(moves_df['game_id'].values.tolist()))
        ids_from_games_file.sort()
        ids_from_moves_file.sort()
        self.assertTrue(len(ids_from_games_file) == len(ids_from_moves_file))
        self.assertTrue(ids_from_games_file == ids_from_moves_file)
        colors = list(set(moves_df['color'].values.tolist()))
        self.assertTrue(len(colors) == 2)
        pieces = list(set(moves_df['piece'].values.tolist()))
        pieces.sort()
        self.assertTrue(pieces == ['B', 'K', 'N', 'P', 'Q', 'R'])
        players1 = list(set(moves_df['player'].values.tolist()))
        players2 = list(set(games_df['white'].values.tolist() + games_df['black'].values.tolist()))
        players1.sort()
        players2.sort()
        self.assertTrue(players1 == players2)

    def run_basic_pgn_format_test(self):
        f = self.get_source_filepath("basic_format_test.pgn")
        o = self.get_output_filepath("basic_format_test")
        pgn_data = PGNData(f, o)
        result = pgn_data.export()
        result.print_summary()
        self.assertTrue(result.is_complete)

    def run_single_file_test(self):

        f = self.get_source_filepath("pgn_test1.pgn")
        o = self.get_output_filepath("single_file_test")
        pgn_data = PGNData(f, o)
        result = pgn_data.export()
        result.print_summary()
        self.assertTrue(result.is_complete)

    def run_multiple_files_test(self):

        f1 = self.get_source_filepath("pgn_test1.pgn")
        f2 = self.get_source_filepath("pgn_test2.pgn")
        o = self.get_output_filepath("multiple_file_test")
        pgn_data = PGNData([f1, f2], o)
        result = pgn_data.export()
        result.print_summary()
        self.assertTrue(result.is_complete)

    def run_reported_github_issues_test(self):

        """
        Every issue on issues that is resolved should
        have a test pgn file that is added here to
        demonstrate an issue has been fixed. The name
        of the pgn file should be:

        "reported_issue_[issue number].pgn"

        Add each file to the path "/testing/pgn/issues/"
        """

        files = self.get_github_issues_test_files()

        for file in files:
            file_name = self.get_source_issues_filepath(file)
            output_name = self.get_output_filepath(file.replace(".pgn", ""))
            pgn_data = PGNData(file_name, output_name)
            result = pgn_data.export()
            self.assertTrue(result.is_complete)

    def get_github_issues_test_files(self):
        files = []
        path = self.get_source_issues_filepath(self.issues_name)
        for file in glob.glob(path):
            name = os.path.basename(file)
            files.append(name)
        return files

    def get_source_issues_filepath(self, file=None):
        name_format = '{}/{}/{}/{}' if file is not None else '{}/{}/{}'
        return name_format.format(self.folder, self.pgn_folder_name, self.issues_folder_name, file)

    def get_source_filepath(self, file):
        name_format = '{}/{}/{}' if file is not None else '{}/{}'
        return name_format.format(self.folder, self.pgn_folder_name, file)

    def get_output_filepath(self, output_name):
        name_format = '{}/{}/{}' if output_name is not None else '{}/{}'
        return name_format.format(self.folder, self.exports_folder_name, output_name)

    def run_pandas_dataframe_test(self):
        f = self.get_source_filepath("pandas_test.pgn")
        o = self.get_output_filepath("pandas_test")
        pgn_data = PGNData(f, o)
        result = pgn_data.export()

        log.info("check source file for dataframe has been created")
        self.assertTrue(result.is_complete)
        games_df = result.get_games_df()
        moves_df = result.get_moves_df()
        combined_df = result.get_combined_df()

        log.info("check 3 dataframes are created and they are valid")
        df_list = [games_df, moves_df, combined_df]
        for df in df_list:
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertFalse(df.empty)
            self.assertFalse(len(df) == 0)
            self.assertFalse(len(df.columns) == 0)

        log.info("check correct number of columns in combined df")
        # exclude the "game_id" to prevent double counting
        self.assertTrue(len(combined_df.columns) - 1 == (len(games_df.columns) - 1) + (len(moves_df.columns) - 1))

        log.info("check combined has all the columns in games and moves")
        combined_column_list = list(combined_df.columns.values)
        for df in [games_df, moves_df]:
            columns = list(df.columns.values)
            for col in columns:
                self.assertTrue(col in combined_column_list)

        log.info("check correct number of rows in combined df")
        self.assertTrue(len(moves_df) == len(combined_df))

        log.info("perform basic pandas operation")
        self.assertTrue(len(moves_df.head(3)) == 3)
        self.assertTrue(len(games_df.head(1)) == 1)
        self.assertTrue(len(combined_df.head(5)) == 5)

        log.info("export combined dataframe as a csv")
        combined_file1 = self.get_output_filepath("pandas_test_export1.csv")
        combined_df.to_csv(combined_file1, index=False)
        self.assertTrue(os.path.exists(combined_file1))

        combined_file2 = self.get_output_filepath("pandas_test_export2.csv")
        is_exists = result.create_combined_file(combined_file2)
        self.assertTrue(os.path.exists(combined_file2))
        self.assertTrue(is_exists)


def board_test():
    test_board_ref = BoardRefTestCase()
    test_board_ref.run_piece_at_square_test()


def fen_stat_tests():
    test_fen = FenTestCase()
    test_fen.run_test()


def file_creation_tests():
    test_creation = FileCreationTestCase()
    test_creation.run_tests()


def log_output_as_headline(message, length=50):

    log.info("#" * length)
    log.info(" {} ".format(message))
    log.info("#" * length)


def run_all_tests():
    """
    This is the main method to run to check the API output

    >> from testing.test import run_all_tests
    >> run_all_tests()
    """

    t = TimeProcess()
    log_output_as_headline("Start testing")
    board_test()
    fen_stat_tests()
    file_creation_tests()
    log_output_as_headline("end testing")
    t.print_time_taken()
