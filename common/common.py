import logging
from typing import Dict, Optional
from io import TextIOWrapper

import chess

log = logging.getLogger("pgn2data - common")
logging.basicConfig(level=logging.INFO)

# Map lowercase FEN piece letters to python-chess piece types.
piece_fen_letter_to_chess_piece: Dict[str, chess.PieceType] = {
    "p": chess.PAWN,
    "q": chess.QUEEN,
    "n": chess.KNIGHT,
    "k": chess.KING,
    "r": chess.ROOK,
    "b": chess.BISHOP,
}

# Map python-chess piece types to lowercase FEN piece letters.
piece_fen_letters: Dict[chess.PieceType, str] = {
    chess.PAWN: "p",
    chess.QUEEN: "q",
    chess.KNIGHT: "n",
    chess.KING: "k",
    chess.ROOK: "r",
    chess.BISHOP: "b",
}

# Conventional material values; the king has no exchange value.
piece_fen_value: Dict[chess.PieceType, int] = {
    chess.PAWN: 1,
    chess.QUEEN: 9,
    chess.KNIGHT: 3,
    chess.KING: 0,
    chess.ROOK: 5,
    chess.BISHOP: 3,
}

# Starting number of each piece type per player.
piece_fen_count: Dict[chess.PieceType, int] = {
    chess.PAWN: 8,
    chess.QUEEN: 1,
    chess.KNIGHT: 2,
    chess.KING: 1,
    chess.ROOK: 2,
    chess.BISHOP: 2,
}

# Starting squares and piece letters, without distinguishing piece color.
board_reference: Dict[str, str] = {
    "A1": "R", "B1": "N", "C1": "B", "D1": "Q",
    "E1": "K", "F1": "B", "G1": "N", "H1": "R",
    "A2": "P", "B2": "P", "C2": "P", "D2": "P",
    "E2": "P", "F2": "P", "G2": "P", "H2": "P",
    "A8": "R", "B8": "N", "C8": "B", "D8": "Q",
    "E8": "K", "F8": "B", "G8": "N", "H8": "R",
    "A7": "P", "B7": "P", "C7": "P", "D7": "P",
    "E7": "P", "F7": "P", "G7": "P", "H7": "P",
}


def full_range(start: int, stop: int) -> range:
    """Return a range including both start and stop."""
    return range(start, stop + 1)


def open_file(file_name: str) -> Optional[TextIOWrapper]:
    """Open a UTF-8 file for writing, returning None if permission is denied.

    An existing file is overwritten. The caller must close the returned file.
    Other file-opening errors propagate to the caller.
    """
    try:
        return open(file_name, mode="w", newline="", encoding="utf-8")
    except PermissionError:
        log.error("Could not access the file: %s", file_name)
        return None


def seconds_to_text(secs: int | float) -> str:
    """Format whole seconds as days, hours, minutes and seconds.

    Omit zero-valued units and retain a trailing comma and space.
    Return an empty string for zero seconds.
    """
    days, remainder = divmod(secs, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    units = (
        (days, "day"),
        (hours, "hour"),
        (minutes, "minute"),
        (seconds, "second"),
    )

    return "".join(
        f"{value} {unit}{'s' if value != 1 else ''}, "
        for value, unit in units
        if value
    )