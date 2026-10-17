import logging
from datetime import datetime, timezone
from timeit import default_timer as timer

from common.common import seconds_to_text

log = logging.getLogger("pgn2data - log_time")
logging.basicConfig(level=logging.INFO)


def get_iso8061_date_format() -> str:
    """Return the timestamp format used by this module."""
    return "%Y-%m-%dT%H:%M:%S%z"


def get_time_stamp() -> str:
    """Return the current UTC timestamp with a +0000 offset."""
    stamp_date = datetime.now(timezone.utc)
    return stamp_date.strftime(get_iso8061_date_format())


class TimeProcess:
    """Measure elapsed time and log the start and end times in UTC."""

    def __init__(self) -> None:
        # Use a performance timer for elapsed time and UTC for logging.
        self.start: float = timer()
        self.time_started: datetime = datetime.now(timezone.utc)
        log.info("initializing at...%s", self.time_started)

    def get_lapsed_time(self) -> float:
        """Return the elapsed time in seconds since initialization."""
        end = timer()
        return end - self.start

    def print_time_taken(self) -> None:
        """Log the elapsed duration and the UTC start and end times."""
        lapsed_time_seconds = self.get_lapsed_time()
        log.info("time taken sec: %s sec", lapsed_time_seconds)
        log.info("time taken: %s", seconds_to_text(lapsed_time_seconds))
        log.info("time started...%s", self.time_started)
        log.info("time ended.....%s", datetime.now(timezone.utc))