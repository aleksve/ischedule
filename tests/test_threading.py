import time
from threading import Event, Thread

import pytest

from src.ischedule import reset, run_loop, every


def task_1():
    print("Task 1")


def task_2():
    print("Task 2")


def test_thread_1():
    every(interval=0.1, run_func=task_1)
    every(interval=0.2, run_func=task_2)
    stop_event = Event()
    Thread(target=lambda: [time.sleep(1), stop_event.set()]).start()
    run_loop(stop_event)


def test_thread_2():
    every(interval=0.1, run_func=task_1)
    every(interval=0.2, run_func=task_2)
    stop = Event()
    Thread(target=run_loop, kwargs={"stop_event": stop}, daemon=False).start()

    time.sleep(1)
    stop.set()


if __name__ == "__main__":
    test_thread_1()


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    reset()
