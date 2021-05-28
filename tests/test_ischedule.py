import time
from datetime import timedelta
from functools import partial
from threading import Event

import pytest

from src.ischedule import ischedule

GRANULARITY = 1e-4

_i = 0
N_seconds = 5


def execute_N_times_and_throw_exception(N: int):
    global _i
    print(f"Execution {_i}")
    if _i == N:
        raise InterruptedError(N)
    _i += 1


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
    """
    Test what happens when a task uses so much time that the next execution have to skip
    """
    ischedule.schedule(
        partial(execute_N_times_and_throw_exception, N=N_seconds), interval=1
    )
    ischedule.schedule(skip_execution, interval=skip_sched_time)

    with pytest.raises(InterruptedError):
        while True:
            ischedule.run_pending()
            time.sleep(GRANULARITY)


def test_timedelta():
    ischedule.schedule(
        partial(execute_N_times_and_throw_exception, N=10),
        interval=timedelta(milliseconds=100),
    )
    with pytest.raises(InterruptedError):
        ischedule.run_loop()


stop_event = Event()
N_task_with_event_reset = 0


def task_with_event_reset():
    global N_task_with_event_reset
    if N_task_with_event_reset == 5:
        stop_event.set()

    if N_task_with_event_reset == 6:
        raise AssertionError()

    N_task_with_event_reset += 1


def test_run_loop():
    ischedule.schedule(task_with_event_reset, interval=timedelta(milliseconds=200))
    ischedule.run_loop(stop_event=stop_event)


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    global _i
    _i = 0
    ischedule.reset()


if __name__ == "__main__":
    pytest.main()
