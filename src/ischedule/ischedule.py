import time
from datetime import timedelta
from threading import Event
from time import monotonic
from typing import Callable, List, Union


class _Task:
    def __init__(self, func: Callable, interval: timedelta):
        self.func = func
        self.interval = interval
        self.previous_call = monotonic()
        self.missed_executions = 0


_tasks: List[_Task] = []


def schedule(func: Callable, *, interval: Union[timedelta, float]):
    """
    Args:
        func: scheduled functions
        interval: how often the function is called. Either a `datetime.timedelta` or a number of seconds

    Raises:
        TypeError: The supplied interval cannot be interpreted as timedelta seconds
    """
    if not isinstance(interval, timedelta):
        # Raises TypeError
        interval = timedelta(seconds=interval)
    _tasks.append(_Task(func, interval))


def run_pending():
    t = monotonic()
    for task in _tasks:
        intervals_since_last_call: float = (
            t - task.previous_call
        ) / task.interval.total_seconds()
        if intervals_since_last_call >= 1:
            i_intervals_since_last_call = int(intervals_since_last_call)
            task.previous_call += (
                task.interval.total_seconds() * i_intervals_since_last_call
            )
            task.missed_executions += i_intervals_since_last_call - 1
            task.func()


def reset():
    _tasks.clear()


def run_loop(sleep_interval: Union[timedelta, float] = 0.01, stop_event: Event = None):
    """
    Runs the pending tasks until the event is set.

    Args:
        sleep_interval: how long to sleep between the pending task exections.
            Checking if any tasks are pending doesn't take much processing time, but doing so without
            any pause would still take 100% CPU time
        stop_event: run until this event is set. If `None`, run until the program is terminated

    Raises:
        TypeError: the supplied sleep_interval cannot be interpreted as a number of seconds
    """
    if not isinstance(sleep_interval, timedelta):
        sleep_interval = timedelta(seconds=sleep_interval)
    sleep_interval = sleep_interval.total_seconds()

    if stop_event is None:
        stop_event = Event()

    while not stop_event.is_set():
        run_pending()
        time.sleep(sleep_interval)
