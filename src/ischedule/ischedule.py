from datetime import timedelta
from functools import partial
from multiprocessing.synchronize import Event as Event_mp
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


def schedule(
    func: Optional[Callable] = None, *, interval: Union[timedelta, float]
) -> Callable:
    """
    Schedule a function for periodic execution. Can be used as a function call or as a decorator.


    As a function call:

    def task():
        print("task")
    schedule(task, interval=1)

    Equivalently, as a decorator:

    @schedule(interval=1)
    def task():
        print("task")

    Args:
        func: The function to be scheduled. If a function not supplied, the scheduler will act as a decorator.
        interval: How often the function will be called. Either a `datetime.timedelta` or a number of seconds.

    Raises:
        TypeError: The supplied interval cannot be interpreted as timedelta seconds

    Returns:
        Passes the input `func` unmodified
    """
    if not isinstance(interval, timedelta):
        # Raises TypeError
        interval = timedelta(seconds=interval)

    if func is None:
        return partial(schedule, interval=interval)

    _tasks.append(_Task(func, interval))

    return func


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


def run_loop(
    stop_event: Optional[Event] = None,
    return_after: Optional[Union[float, timedelta]] = float("inf"),
):
    """
    Runs the pending tasks until the stop_event is set, or until an exception is raised by a task.

    Args:
        stop_event: optionally provide an event that will trigger a clean return from the loop when set
        return_after: loop exits after a certain amount of time; especially useful for testing

    Raises:
        Exception: All exceptions raised by the tasks will propagate through here
    """
    if stop_event is None:
        stop_event = Event()
    assert isinstance(stop_event, Event) or isinstance(stop_event, Event_mp)

    start_time = monotonic()
    if isinstance(return_after, timedelta):
        # timedelta doesn't support float('inf')
        return_after = return_after.total_seconds()

    while not stop_event.is_set() and not monotonic() - start_time > return_after:
        run_pending()
        next_call_time = min([t.next_call() for t in _tasks]) - monotonic()
        next_call_time = min(next_call_time, start_time + return_after)
        if next_call_time > 0:
            stop_event.wait(next_call_time)
