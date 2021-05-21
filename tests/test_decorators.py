import time
from threading import Event, Thread

import pytest

from src.ischedule import reset, run_loop, schedule


def set_stop_event_on_separate_thread(event):
    def th():
        time.sleep(2)
        event.set()

    Thread(target=th, daemon=False).start()


def test_thread():
    @schedule(interval=0.1)
    def task_1():
        print("Task 1")

    @schedule(interval=0.2)
    def task_2():
        print("Task 2")

    stop = Event()
    set_stop_event_on_separate_thread(stop)
    run_loop(stop_event=stop)


if __name__ == "__main__":
    pytest.main()


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    reset()
