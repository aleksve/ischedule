import time
from functools import partial
from threading import Event

import pytest

from src.ischedule import ischedule

_t_0_set_event_after = None


def set_event_after(t: float, event: Event):
    global _t_0_set_event_after
    if _t_0_set_event_after is None:
        _t_0_set_event_after = time.monotonic()
    if _t_0_set_event_after + t < time.monotonic():
        event.set()


t_startup_time_dev = 0
_PERIOD = 0.01
_startup_time_deviations = []


def check_time_slip():
    global t_startup_time_dev
    if not t_startup_time_dev:
        t_startup_time_dev = time.time()
    else:
        t_startup_time_dev += _PERIOD

    start_time_deviation = time.time() - t_startup_time_dev
    _startup_time_deviations.append(abs(start_time_deviation))
    time.sleep(_PERIOD / 2)


def test():
    stop_event = Event()
    ischedule.schedule(partial(set_event_after, t=10, event=stop_event), interval=1)
    ischedule.schedule(check_time_slip, interval=_PERIOD)
    ischedule.run_loop(stop_event)
    max_startup_time_deviations = max(_startup_time_deviations)
    average_deviation = sum(_startup_time_deviations) / len(_startup_time_deviations)
    median_deviation = sorted(_startup_time_deviations)[
        len(_startup_time_deviations) // 2
    ]
    print(
        f"max deviation: {max_startup_time_deviations}; average deviation: {average_deviation}; "
        f"median deviation: {median_deviation}"
    )
    assert (
        max_startup_time_deviations <= 5e-3
    ), "The precision tolerance of max start time deviation was exceeded."

    assert (
        average_deviation <= 2e-4
    ), "The precision tolerance of average start time deviation was exceeded."


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    ischedule.reset()
