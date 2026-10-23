import csv
import logging
import ntpath
import queue
import uuid
from io import TextIOWrapper
from threading import Thread
from typing import Any, Dict, List, Optional, Tuple, NamedTuple, Union

import chess
import chess.engine
import chess.pgn

from common.log_time import get_time_stamp
from converter.fen import FenRowStats, FenStats
from converter.headers import (
    file_headers_game, file_headers_moves, file_headers_stockfish
)

log = logging.getLogger("pgn2data - process")
logging.basicConfig(level=logging.INFO)


class PlayerMove:
    """
    PlayerMove = Data class to hold details of each move.
    move = Move object from python chess library
    notation = is algebraic notation of the move
    """

    def __init__(
            self,
            move: chess.Move,
            notation: str,
            clock_seconds: Optional[float] = None
    ) -> None:
        """Store the move and notation, with an initially empty piece letter."""
        self.move = move
        self.notation = notation
        self.clock_seconds = clock_seconds
        self.__piece = ""

    def get_from_square(self) -> str:
        """Return the source square, or an empty string for a short move string."""
        return str(self.move)[0:2] if self.__is_valid_move() else ""

    def get_to_square(self) -> str:
        """Return the destination square, or an empty string for a short move string."""
        return str(self.move)[2:4] if self.__is_valid_move() else ""

    def __is_valid_move(self) -> bool:
        """Check only that the move string contains at least four characters."""
        return len(str(self.move)) >= 4

    def set_piece(self, piece: str) -> None:
        """Store the moved piece letter."""
        self.__piece = piece

    def get_piece(self) -> str:
        """Return the stored piece letter."""
        return self.__piece


class MoveJob(NamedTuple):
    """A game and the settings needed to export its moves."""

    game_id: str
    game: chess.pgn.Game
    moves_writer: Any
    engine: Optional[chess.engine.SimpleEngine]
    depth: int


class Process:
    """
    Handles the pgn to data conversion
    """

    def __init__(
            self,
            pgn_file: str,
            file_games: TextIOWrapper,
            file_moves: Optional[TextIOWrapper],
            engine_path: Optional[str],
            engine_depth: int,
            moves_required: bool,
            queue_size: int = 0,
    ) -> None:
        """Store input, output, engine and queue settings for one PGN file."""
        self.pgn_file = pgn_file
        self.file_games = file_games
        self.file_moves = file_moves
        self.engine_path = engine_path
        self.engine_depth = engine_depth
        self.max_queue_size = queue_size
        self.moves_required = moves_required

    def parse_file(self, add_headers_flag: bool = True) -> None:
        """
        This is the main method of the class for invoking the file processing
        """

        if self.moves_required:
            self.__parse_file_games_and_moves(add_headers_flag=add_headers_flag)
        else:
            self.__parse_file_games(add_headers_flag=add_headers_flag)

    def __parse_file_games(self, add_headers_flag: bool = True) -> None:
        """
        processes the pgn file and then exports game information
        into the game csv file, moves are ignored
        """

        log.info("Processing games only in file:{}".format(self.pgn_file))
        pgn = open(self.pgn_file, encoding="UTF-8")

        game_writer = csv.writer(self.file_games, delimiter=',')
        if add_headers_flag:
            game_writer.writerow(file_headers_game)

        order = 1
        while True:
            game_id = str(uuid.uuid4())
            game = chess.pgn.read_game(pgn)
            if game is None:
                break  # end of file

            game_writer.writerow(
                self.__get_game_row_data(
                    game=game,
                    game_id=game_id,
                    order=order,
                    file_name=self.pgn_file
                )
            )
            order += 1

    def __parse_file_games_and_moves(self, add_headers_flag: bool = True) -> None:
        """
        processes the pgn file and then exports game information
        into the game csv file, and the moves into the moves csv file
        """

        log.info("Processing games and moves in file:{}".format(self.pgn_file))
        pgn = open(self.pgn_file, encoding="UTF-8")

        engine = None
        if self.engine_path is not None:
            engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

        # The producer queues games; a single worker writes their move rows.
        q: queue.Queue[MoveJob] = queue.Queue(maxsize=self.max_queue_size)

        worker = Thread(
            target=self.__process_move_queue,
            args=(q,),
            daemon=True,
        )
        worker.start()

        move_writer = csv.writer(self.file_moves, delimiter=',')
        if add_headers_flag:
            headers = file_headers_moves.copy()
            if engine is not None:
                headers.extend(file_headers_stockfish)
            move_writer.writerow(headers)

        game_writer = csv.writer(self.file_games, delimiter=',')
        if add_headers_flag:
            game_writer.writerow(file_headers_game)

        order = 1
        while True:
            game_id = str(uuid.uuid4())
            game = chess.pgn.read_game(pgn)
            if game is None:
                break  # end of file

            game_writer.writerow(
                self.__get_game_row_data(
                    game=game,
                    game_id=game_id,
                    order=order,
                    file_name=self.pgn_file
                )
            )
            q.put(
                MoveJob(
                    game_id=game_id,
                    game=game,
                    moves_writer=move_writer,
                    engine=engine,
                    depth=self.engine_depth,
                )
            )
            order += 1

        # Wait for every queued game before closing the engine.
        q.join()

        if engine is not None:
            engine.quit()

    def __process_move_queue(self, q: queue.Queue[MoveJob]) -> None:
        """Process queued games as they become available."""
        while True:
            job = q.get()
            self.__process_move(
                game_id=job.game_id,
                game=job.game,
                moves_writer=job.moves_writer,
                engine=job.engine,
                depth=job.depth,
            )
            q.task_done()

    def __process_move(
            self,
            game_id: str,
            game: chess.pgn.Game,
            moves_writer: Any,
            engine: Optional[chess.engine.SimpleEngine],
            depth: int,
    ) -> None:
        """
        process all the moves in a game
        """
        board = game.board()
        order_number = 1
        players_order_number = 1
        sequence = ""

        # track stockfish evaluation
        white_eval = 0
        black_eval = 0

        for node in game.mainline():
            move = node.move
            notation = board.san(move)
            board.push(move)
            player_move = PlayerMove(
                move=move,
                notation=notation,
                clock_seconds=node.clock(),
            )

            # this gets the name of the piece that was moved
            try:
                index = chess.SQUARE_NAMES.index(player_move.get_to_square())
            except ValueError as exc:
                log.error(
                    "Cannot resolve destination square for move %s: %s",
                    notation,
                    exc,
                )
                break
            p = board.piece_at(chess.SQUARES[index])

            player_move.set_piece(str(p))
            sequence += ("|" if len(sequence) > 0 else "") + str(notation)

            # output the data about the move to the file
            row_data, prev_eval, is_white = self.__get_move_row_data(
                player_move=player_move, board=board,
                game_id=game_id, game=game, order_number=order_number,
                players_order_number=players_order_number, sequence=sequence,
                engine=engine, depth=depth,
                white_eval=white_eval, black_eval=black_eval
            )
            moves_writer.writerow(row_data)

            # this is tracking the move numbers in the game
            players_order_number += 1 if (order_number % 2) == 0 else 0
            order_number += 1

            # this is tracking what the previous evaluation is for each move
            # so it can be inserted alongside the current row
            white_eval = prev_eval if is_white else white_eval
            black_eval = prev_eval if not is_white else black_eval

    def __get_game_row_data(
            self,
            game: chess.pgn.Game,
            game_id: str,
            order: int,
            file_name: str
    ) -> List[Any]:
        """
        takes a "game" object and converts it into a list with the data for each column
        """

        winner = self.__get_winner(game=game)

        loser, winner_elo, loser_elo, winner_loser_elo_diff = (
            self.__get_winner_loser_details(game=game, winner=winner)
        )

        # Keep column order aligned with file_headers_game.
        return [
            game_id,
            order,
            game.headers.get("Event", ""),
            game.headers.get("Site", ""),
            game.headers.get("Date", ""),
            game.headers.get("Round", ""),
            game.headers.get("White", ""),
            game.headers.get("Black", ""),
            game.headers.get("Result", ""),
            game.headers.get("WhiteElo", ""),
            game.headers.get("WhiteRatingDiff", ""),
            game.headers.get("BlackElo", ""),
            game.headers.get("BlackRatingDiff", ""),
            game.headers.get("WhiteTitle", ""),
            game.headers.get("BlackTitle", ""),
            winner,
            winner_elo,
            loser,
            loser_elo,
            winner_loser_elo_diff,
            game.headers.get("ECO", ""),
            game.headers.get("Termination", ""),
            game.headers.get("TimeControl", ""),
            game.headers.get("UTCDate", ""),
            game.headers.get("UTCTime", ""),
            game.headers.get("Variant", ""),
            game.headers.get("PlyCount", ""),
            get_time_stamp(),
            ntpath.basename(file_name),
        ]

    @staticmethod
    def __get_winner_loser_details(
            game: chess.pgn.Game,
            winner: str,
    ) -> Tuple[str, str, str, Union[int, str]]:
        """Return loser, winner rating, loser rating and rating difference."""
        headers = game.headers
        loser = ""
        winner_elo = ""
        loser_elo = ""
        rating_diff: Union[int, str] = ""

        if "White" in headers and "Black" in headers:
            if winner == headers["Black"]:
                loser = headers["White"]
            elif winner == headers["White"]:
                loser = headers["Black"]
            else:
                loser = winner

        if "WhiteElo" in headers and "BlackElo" in headers:
            if winner == headers["White"]:
                winner_elo = headers["WhiteElo"]
            elif winner == headers["Black"]:
                winner_elo = headers["BlackElo"]

            if winner == headers["Black"]:
                loser_elo = headers["WhiteElo"]
            elif winner == headers["White"]:
                loser_elo = headers["BlackElo"]

            if str(winner_elo).isnumeric() and str(loser_elo).isnumeric():
                rating_diff = int(winner_elo) - int(loser_elo)
            else:
                rating_diff = 0

        return loser, winner_elo, loser_elo, rating_diff

    # Share cached rank statistics across Process instances.
    __fen_row_counts_and_valuation_dict: Dict[str, List[FenRowStats]] = {}

    def __get_move_row_data(
            self,
            player_move: PlayerMove,
            board: chess.Board,
            game_id: str,
            game: chess.pgn.Game,
            order_number: int,
            players_order_number: int,
            sequence: str,
            engine: Optional[chess.engine.SimpleEngine],
            depth: int,
            white_eval: Optional[int],
            black_eval: Optional[int],
    ) -> Tuple[List[Any], Optional[int], bool]:
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

        is_white_move = not self.__is_number_even(number=order_number)

        player_name = game.headers["White"] if is_white_move else game.headers["Black"]
        player_colour = "White" if is_white_move else "Black"

        # this calculates engine evaluation but only an engine has been specified
        evaluation = 0
        if engine is not None:
            evaluation = self.__get_evaluation_from_board(
                board=board, depth=depth, engine=engine, is_white_move=is_white_move
            )

        # Keep column order aligned with file_headers_moves.
        # FenRowStats retains tuple indexing for the existing CSV layout.
        data = [game_id,
                order_number,
                players_order_number,
                player_name,
                player_move.notation,
                player_move.move,
                player_move.get_from_square(),
                player_move.get_to_square(),
                player_move.get_piece().upper(),
                player_colour,
                player_move.clock_seconds,
                board.board_fen(),
                int(board.is_check()),
                int(board.is_checkmate()),
                int(board.is_fifty_moves()),
                int(board.is_fivefold_repetition()),
                int(board.is_game_over()),
                int(board.is_insufficient_material()),
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
                *(row.white_count for row in fen_row_valuations),
                *(row.white_value for row in fen_row_valuations),
                *(row.black_count for row in fen_row_valuations),
                *(row.black_value for row in fen_row_valuations),
                sequence]

        if engine is not None:
            prev_value = white_eval if is_white_move else black_eval

            data.append(evaluation / 100.0 if evaluation is not None else None)
            data.append(prev_value / 100.0 if prev_value is not None else None)

            if evaluation is not None and prev_value is not None:
                data.append((evaluation - prev_value) / 100.0)
            else:
                data.append(None)

            data.append(depth)

        return data, evaluation, is_white_move

    @staticmethod
    def __get_evaluation_from_board(
            board: chess.Board,
            depth: int,
            engine: chess.engine.SimpleEngine,
            is_white_move: bool,
    ) -> Optional[int]:
        # this wrapped in a function because engine.analyse is not able to
        # parse the board object without errors
        """Return the moving side's score in centipawns, or None for a mate score.

        Log analysis errors and retain the default score of zero."""
        evaluation = 0
        try:
            info = engine.analyse(board=board, limit=chess.engine.Limit(depth=depth))
            pov_score = info["score"]
            evaluation = pov_score.white().score() if is_white_move else pov_score.black().score()
        except Exception as ex:
            log.error(ex)
        return evaluation

    @staticmethod
    def __is_number_even(number: int) -> bool:
        """Return whether the number is even."""
        return number % 2 == 0

    @staticmethod
    def __get_winner(game: chess.pgn.Game) -> str:
        """Return the winner, 'draw', or an empty string for an unknown result."""
        result = game.headers.get("Result")

        if result == "1-0":
            return game.headers.get("White", "")
        if result == "0-1":
            return game.headers.get("Black", "")
        if result == "1/2-1/2":
            return "draw"

        return ""