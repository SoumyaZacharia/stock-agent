import threading
import time


class TokenBucket:
    """Allows `rate_per_sec` calls per second, with bursts up to `capacity`."""

    def __init__(self, rate_per_sec, capacity, clock=time.monotonic, sleep=time.sleep):
        self.rate = rate_per_sec
        self.capacity = capacity
        self.tokens = float(capacity)
        self.clock = clock
        self.sleep = sleep
        self.updated = clock()
        self.lock = threading.Lock()

    def acquire(self):
        while True:
            with self.lock:
                now = self.clock()
                self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
                self.updated = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                wait = (1 - self.tokens) / self.rate
            self.sleep(wait)