import time
from threading import Event

import pytest

from src.ischedule.ischedule import reset, run_loop, schedule


def test_example():
    start_time = time.time()
    stop_event = Event()

    def job_1():
        dt = time.time() - start_time
        print(f"Started a _fast_ job at t={dt:.2f}")
        if dt > 3:
            stop_event.set()

    def job_2():
        dt = time.time() - start_time
        if dt > 2:
            return
        print(f"Started a *slow* job at t={dt:.2f}")
        time.sleep(1)

    schedule(job_1, interval=0.1)
    schedule(job_2, interval=0.5)

    run_loop(stop_event=stop_event)


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    global _i
    _i = 0
    reset()
