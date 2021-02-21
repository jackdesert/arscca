from datetime import datetime
from datetime import timedelta


class Timer:

    MS_PER_SEC = 1e6

    def __init__(self):
        self._start = datetime.now()

    @property
    def elapsed(self):
        stop = datetime.now()
        delta = stop - self._start
        return self._display(delta)

    def _display(self, delta):
        total_seconds = delta.seconds + delta.microseconds / self.MS_PER_SEC
        return total_seconds
