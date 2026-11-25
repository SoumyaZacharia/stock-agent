from datetime import date, timedelta

import pandas as pd
import pytest

from stock_agent.prices import COLUMNS


class FakeTime:
    def __init__(self):
        self.t = 0.0
        self.slept = []

    def clock(self):
        return self.t

    def sleep(self, s):
        self.slept.append(s)
        self.t += s


@pytest.fixture
def fake_time():
    return FakeTime()


@pytest.fixture
def sample_df():
    d1 = (date.today() - timedelta(days=2)).isoformat()
    d2 = (date.today() - timedelta(days=1)).isoformat()
    return pd.DataFrame(
        [
            ["AAPL", d1, 1.0, 1.5, 0.9, 1.2, 1.2, 100],
            ["AAPL", d2, 2.0, 2.5, 1.9, 2.2, 2.2, 200],
        ],
        columns=COLUMNS,
    )