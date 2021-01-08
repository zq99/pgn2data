import logging
from datetime import datetime, timedelta

import chess

log = logging.getLogger("pgn2data - common")
logging.basicConfig(level=logging.INFO)

piece_fen_letter_to_chess_piece = {
    "p": chess.PAWN,
    "q": chess.QUEEN,
    "n": chess.KNIGHT,
    "k": chess.KING,
    "r": chess.ROOK,
    "b": chess.BISHOP
}

piece_fen_letters = {
    chess.PAWN: "p",
    chess.QUEEN: "q",
    chess.KNIGHT: "n",
    chess.KING: "k",
    chess.ROOK: "r",
    chess.BISHOP: "b"
}

piece_fen_value = {
    chess.PAWN: 1,
    chess.QUEEN: 9,
    chess.KNIGHT: 3,
    chess.KING: 0,
    chess.ROOK: 5,
    chess.BISHOP: 3
}

piece_fen_count = {
    chess.PAWN: 8,
    chess.QUEEN: 1,
    chess.KNIGHT: 2,
    chess.KING: 1,
    chess.ROOK: 2,
    chess.BISHOP: 2
}


def full_range(start, stop): return range(start, stop + 1)


def open_file(file_name):
    try:
        return open(file_name, mode='w', newline='', encoding="utf-8")
    except PermissionError:
        log.error("Could not access the file: {}".format(file_name))
        return None


def seconds_to_text(secs):
    days = secs // 86400
    hours = (secs - days * 86400) // 3600
    minutes = (secs - days * 86400 - hours * 3600) // 60
    seconds = secs - days * 86400 - hours * 3600 - minutes * 60
    result = ("{0} day{1}, ".format(days, "s" if days != 1 else "") if days else "") + \
             ("{0} hour{1}, ".format(hours, "s" if hours != 1 else "") if hours else "") + \
             ("{0} minute{1}, ".format(minutes, "s" if minutes != 1 else "") if minutes else "") + \
             ("{0} second{1}, ".format(seconds, "s" if seconds != 1 else "") if seconds else "")
    return result
