import pytest

from stock_agent.circuit import CircuitBreaker
from stock_agent.ratelimit import TokenBucket


def test_bucket_blocks_when_empty(fake_time):
    b = TokenBucket(1, 2, clock=fake_time.clock, sleep=fake_time.sleep)
    b.acquire()
    b.acquire()
    assert fake_time.slept == []  # burst allowed
    b.acquire()
    assert fake_time.slept[0] == pytest.approx(1.0)  # had to wait


def test_breaker_opens_and_recovers(fake_time):
    cb = CircuitBreaker(failure_threshold=2, reset_after=60, clock=fake_time.clock)
    assert cb.allow()
    cb.record_failure()
    assert cb.allow()
    cb.record_failure()
    assert not cb.allow()  # open
    fake_time.t += 61
    assert cb.allow()  # trial call allowed
    cb.record_success()
    assert cb.allow()