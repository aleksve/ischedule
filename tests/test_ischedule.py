import time
from functools import partial

import pytest

from src import ischedule

GRANULARITY = 1e-4

_i = 0
N_seconds = 5


def execute_N_times_and_throw_exception(N: int):
    global _i
    print(f"Execution {_i}")
    if _i == N:
        raise InterruptedError(N)
    _i += 1


t = 0
_PERIOD = 0.01


def check_time_slip():
    global t
    if not t:
        t = time.time()
    else:
        t += _PERIOD

    dt = abs(time.time() - t)
    print(dt)
    assert dt < _PERIOD / 10 + GRANULARITY * 10 + 0.01
    time.sleep(_PERIOD / 2)


def test():
    ischedule.schedule(
        partial(execute_N_times_and_throw_exception, N=N_seconds), interval=1
    )
    ischedule.schedule(check_time_slip, interval=_PERIOD)
    with pytest.raises(InterruptedError):
        while True:
            ischedule.run_pending()
            time.sleep(GRANULARITY)


skip_time = 0
skip_N = 0

skip_sched_time = 0.5


def skip_execution():
    global skip_N
    assert ischedule._tasks[1].missed_executions == int((skip_N) / 3)
    skip_N += 1
    if not skip_N % 3:
        # Deliberatly spend too much time so that we miss the next execution
        time.sleep(skip_sched_time * 2 + 0.1)


def test_skip():
    ischedule.schedule(
        partial(execute_N_times_and_throw_exception, N=N_seconds), interval=1
    )
    ischedule.schedule(skip_execution, interval=skip_sched_time)

    with pytest.raises(InterruptedError):
        while True:
            ischedule.run_pending()
            time.sleep(GRANULARITY)


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    global _i
    _i = 0
    ischedule.reset()


if __name__ == "__main__":
    reset_scheduler()
    test()
