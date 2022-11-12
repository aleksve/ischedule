import time
from threading import Event

import pytest

from src.ischedule.ischedule import reset, run_loop, every, schedule


def test_example():
    start_time = time.time()
    stop_event = Event()

    def task_1():
        dt = time.time() - start_time
        print(f"Started a _fast_ task at t={dt:.3f}")
        if dt > 3:
            stop_event.set()

    def task_2():
        dt = time.time() - start_time
        print(f"Started a *slow* task at t={dt:.3f}")

        if dt < 2:
            time.sleep(0.91)
        else:
            time.sleep(0.09)

    schedule(interval=0.1, task=task_1)
    every(interval=0.5, run=task_2)

    run_loop(stop_event=stop_event)
    print("Finished")


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    reset()
