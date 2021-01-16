import logging
import ntpath
import queue
import uuid
from threading import Thread
from converter.board_ref import BoardPieces

import chess
import chess.pgn

from converter.fen import FenStats
from common.log_time import get_time_stamp

log = logging.getLogger("pgn2data - process")
logging.basicConfig(level=logging.INFO)


class PlayerMove:
    """
    data class to hold details of each move
    move = Move object from python chess library
    notation = is algebraic notation of the move
    """

    def __init__(self, move, notation):
        self.move = move
        self.notation = notation
        self.__piece = ""

    def get_from_square(self):
        return str(self.move)[0:2] if self.__is_valid_move() else ""

    def get_to_square(self):
        return str(self.move)[2:4] if self.__is_valid_move() else ""

    def __is_valid_move(self):
        return len(str(self.move)) >= 4

    def set_piece(self, piece):
        self.__piece = piece

    def get_piece(self):
        return self.__piece


class Process:
    """
    Handles the pgn to data conversion
    """

    def __init__(self, pgn_file, games_writer, moves_writer):
        self.pgn_file = pgn_file
        self.games_writer = games_writer
        self.moves_writer = moves_writer

    def generate(self):
        """
        processes on pgn file and then exports game information
        into the game csv file, and the moves into the moves csv file
        """

        print("hello there")

        log.info("Processing file:{}".format(self.pgn_file))
        pgn = open(self.pgn_file)

        q = queue.Queue(maxsize=0)
        worker = Thread(target=self.__process_move_queue, args=(q,))
        worker.setDaemon(True)
        worker.start()

        while True:
            game_id = str(uuid.uuid4())
            game = chess.pgn.read_game(pgn)
            if game is None:
                break  # end of file
            # self.games_writer.writerow(self.__get_game_row_data(game, game_id, self.pgn_file))
            self.games_writer.writerow(self.__get_game_row_data(game, game_id, self.pgn_file))
            q.put((game_id, game, self.moves_writer))

        q.join()


    def __process_move_queue(self, q):
        """
        process moves in the blocking queue as they are added
        """
        while True:
            item = q.get()
            self.__process_move(item[0], item[1], item[2])
            q.task_done()


    def __process_move(self, game_id, game, moves_writer):
        """
        process all the moves in a game
        """
        board_pieces = BoardPieces()
        board = game.board()
        order_number = 1
        sequence = ""
        for move in game.mainline_moves():
            notation = board.san(move)
            board.push(move)
            player_move = PlayerMove(move, notation)
            board_pieces.track_move(player_move.get_from_square(), player_move.get_to_square())
            piece = board_pieces.get_piece_at_square(player_move.get_from_square())
            player_move.set_piece(piece)
            sequence += ("|" if len(sequence) > 0 else "") + str(notation)
            moves_writer.writerow(self.__get_move_row_data(player_move, board, game_id, game, order_number, sequence))
            order_number += 1


    def __get_game_row_data(self, game, row_number, file_name):
        """
        takes a "game" object and converts it into a list with the data for each column
        """

        winner = self.__get_winner(game)
        loser = game.headers["White"] if winner == game.headers["Black"] else (
            game.headers["Black"] if winner == game.headers["White"] else winner)
        winner_elo = game.headers["WhiteElo"] if winner == game.headers["White"] else (
            game.headers["BlackElo"] if winner == game.headers["Black"] else "")
        loser_elo = game.headers["WhiteElo"] if winner == game.headers["Black"] else (
            game.headers["BlackElo"] if winner == game.headers["White"] else "")
        winner_loser_elo_diff = 0 if not (str(winner_elo).isnumeric() and str(loser_elo).isnumeric()) else int(
            winner_elo) - int(loser_elo)

        return [row_number,
                game.headers["Event"] if "Event" in game.headers else "",
                game.headers["Site"] if "Site" in game.headers else "",
                game.headers["Date"] if "Date" in game.headers else "",
                game.headers["Round"] if "Round" in game.headers else "",
                game.headers["White"] if "White" in game.headers else "",
                game.headers["Black"] if "Black" in game.headers else "",
                game.headers["Result"] if "Result" in game.headers else "",
                game.headers["WhiteElo"] if "WhiteElo" in game.headers else "",
                game.headers["WhiteRatingDiff"] if "WhiteRatingDiff" in game.headers else "",
                game.headers["BlackElo"] if "BlackElo" in game.headers else "",
                game.headers["BlackRatingDiff"] if "BlackRatingDiff" in game.headers else "",
                winner,
                winner_elo,
                loser,
                loser_elo,
                winner_loser_elo_diff,
                game.headers["ECO"] if "ECO" in game.headers else "",
                game.headers["Termination"] if "Termination" in game.headers else "",
                game.headers["TimeControl"] if "TimeControl" in game.headers else "",
                game.headers["UTCDate"] if "UTCDate" in game.headers else "",
                game.headers["UTCTime"] if "UTCTime" in game.headers else "",
                game.headers["Variant"] if "Variant" in game.headers else "",
                game.headers["PlyCount"] if "PlyCount" in game.headers else "",
                get_time_stamp(), ntpath.basename(file_name)]


    __fen_row_counts_and_valuation_dict = {}


    def __get_move_row_data(self, player_move, board, game_id, game, order_number, sequence):
        """
        process each move in a game
        """

        fen_stats = FenStats(board.board_fen())
        white_count, black_count = fen_stats.get_total_piece_count()

        if fen_stats.fen_position in self.__fen_row_counts_and_valuation_dict:
            fen_row_valuations = self.__fen_row_counts_and_valuation_dict[fen_stats.fen_position]
        else:
            fen_row_valuations = fen_stats.get_fen_row_counts_and_valuation()
            self.__fen_row_counts_and_valuation_dict[fen_stats.fen_position] = fen_row_valuations

        is_white_move = not self.__is_number_even(order_number)

        player_name = game.headers["White"] if is_white_move else game.headers["Black"]
        player_colour = "White" if is_white_move else "Black"

        return [game_id,
                order_number,
                player_name,
                player_move.notation,
                player_move.move,
                player_move.get_from_square(),
                player_move.get_to_square(),
                player_move.get_piece().upper(),
                player_colour,
                board.board_fen(),
                1 if board.is_check() else 0,
                1 if board.is_checkmate() else 0,
                1 if board.is_fifty_moves() else 0,
                1 if board.is_fivefold_repetition() else 0,
                1 if board.is_game_over() else 0,
                1 if board.is_insufficient_material() else 0,
                white_count,
                black_count,
                fen_stats.get_piece_count(chess.PAWN, chess.WHITE),
                fen_stats.get_piece_count(chess.PAWN, chess.BLACK),
                fen_stats.get_piece_count(chess.QUEEN, chess.WHITE),
                fen_stats.get_piece_count(chess.QUEEN, chess.BLACK),
                fen_stats.get_piece_count(chess.BISHOP, chess.WHITE),
                fen_stats.get_piece_count(chess.BISHOP, chess.BLACK),
                fen_stats.get_piece_count(chess.KNIGHT, chess.WHITE),
                fen_stats.get_piece_count(chess.KNIGHT, chess.BLACK),
                fen_stats.get_piece_count(chess.ROOK, chess.WHITE),
                fen_stats.get_piece_count(chess.ROOK, chess.BLACK),
                fen_stats.get_captured_score(chess.WHITE),
                fen_stats.get_captured_score(chess.BLACK),
                fen_row_valuations[0][0], fen_row_valuations[1][0], fen_row_valuations[2][0], fen_row_valuations[3][0],
                fen_row_valuations[4][0], fen_row_valuations[5][0], fen_row_valuations[6][0], fen_row_valuations[7][0],
                fen_row_valuations[0][1], fen_row_valuations[1][1], fen_row_valuations[2][1], fen_row_valuations[3][1],
                fen_row_valuations[4][1], fen_row_valuations[5][1], fen_row_valuations[6][1], fen_row_valuations[7][1],
                fen_row_valuations[0][2], fen_row_valuations[1][2], fen_row_valuations[2][2], fen_row_valuations[3][2],
                fen_row_valuations[4][2], fen_row_valuations[5][2], fen_row_valuations[6][2], fen_row_valuations[7][2],
                fen_row_valuations[0][3], fen_row_valuations[1][3], fen_row_valuations[2][3], fen_row_valuations[3][3],
                fen_row_valuations[4][3], fen_row_valuations[5][3], fen_row_valuations[6][3], fen_row_valuations[7][3],
                sequence]


    @staticmethod
    def __is_number_even(number):
        return number % 2 == 0


    @staticmethod
    def __get_winner(game):
        info = game.headers
        if "White" in info and "Black" in info and "Result" in info:
            if game.headers["Result"] == "1/2-1/2":
                return "draw"
            return game.headers["White"] if game.headers["Result"] == "1-0" else game.headers["Black"]
        else:
            return ""
