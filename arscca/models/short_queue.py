from threading import Lock


class ShortQueue:
    LOCK = Lock()

    def __init__(self):
        self._empty = True

    # You may only join the queue if the queue is currently empty
    # This is useful when lots of requests come in, and you want to make sure that
    # you actually do something with the last one,
    # even though dropping intermediate requests would be fine
    def join(self):
        with self.LOCK:
            if self._empty:
                self._empty = False
                return True
            return False

    def leave(self):
        with self.LOCK:
            if self._empty:
                raise ValueError('Leaving an empty queue')
            self._empty = True
