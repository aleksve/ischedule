from datetime import timedelta
from threading import Event
from time import monotonic
from typing import Callable, List, Optional, Union


class _Task:
    def __init__(self, func: Callable, interval: timedelta):
        self.func = func
        self.interval = interval
        self.previous_call = monotonic()
        self.missed_executions = 0

    def next_call(self) -> float:
        return self.previous_call + self.interval.total_seconds()


_tasks: List[_Task] = []


def reset():
    _tasks.clear()


def schedule(func: Callable, *, interval: Union[timedelta, float]):
    """
    Args:
        func: scheduled functions
        interval: how often the function will be called. Either a `datetime.timedelta` or a number of seconds

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


def run_loop(stop_event: Optional[Event] = None):
    """
    Runs the pending tasks until the stop_event is set, or until an exception is raised by a task.

    Args:
        stop_event: optionally provide an event that will trigger a clean return from the loop when set

    Raises:
        Exception: All exceptions raised by the tasks will propagate through here
    """
    if stop_event is None:
        stop_event = Event()
    assert isinstance(stop_event, Event)

    while not stop_event.is_set():
        run_pending()
        next_call_time = min([t.next_call() for t in _tasks]) - monotonic()
        if next_call_time > 0:
            stop_event.wait(next_call_time)
