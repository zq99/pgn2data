from timeit import default_timer as timer
from common.common import seconds_to_text
from datetime import datetime
import logging

log = logging.getLogger("pgn2data - log_time")
logging.basicConfig(level=logging.INFO)


def get_iso8061_date_format():
    return "%Y-%m-%dT%H:%M:%S%z"


def get_time_stamp():
    stamp_date = datetime.utcnow()
    return str(stamp_date.strftime(get_iso8061_date_format())) + "+0000"


class TimeProcess:

    def __init__(self):
        self.start = timer()
        self.time_started = datetime.utcnow()
        log.info("initializing at..." + str(self.time_started))

    def get_lapsed_time(self):
        end = timer()
        return end - self.start

    def print_time_taken(self):
        lapsed_time_seconds = self.get_lapsed_time()
        log.info("time taken sec: " + str(lapsed_time_seconds) + " sec")
        log.info("time taken: " + str(seconds_to_text(lapsed_time_seconds)))
        log.info("time started..." + str(self.time_started))
        log.info("time ended....." + str(datetime.utcnow()))
