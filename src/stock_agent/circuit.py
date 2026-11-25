import time


class CircuitBreaker:
    def __init__(self, failure_threshold=3, reset_after=300, clock=time.monotonic):
        self.threshold = failure_threshold
        self.reset_after = reset_after
        self.clock = clock
        self.failures = 0
        self.opened_at = None

    def allow(self) -> bool:
        if self.opened_at is None:
            return True
        # after the cool-down, let one trial call through ("half-open")
        return self.clock() - self.opened_at >= self.reset_after

    def record_success(self):
        self.failures = 0
        self.opened_at = None

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.opened_at = self.clock()