from datetime import datetime, timedelta
from typing import Callable, List, Union


class _Task:
    def __init__(self, func: Callable, interval: timedelta):
        self.func = func
        self.interval = interval
        self.previous_call = datetime.utcnow()
        self.missed_executions = 0


_tasks: List[_Task] = []


def schedule(func: Callable, interval: Union[timedelta, float]):
    """

    Raises: TypeError if the interval cannot be converted to timedelta seconds
    """
    if not isinstance(interval, timedelta):
        # Raises TypeError
        interval = timedelta(seconds=interval)
    _tasks.append(_Task(func, interval))


def run_pending():
    t = datetime.utcnow()
    for task in _tasks:
        intervals_since_last_call: float = (t - task.previous_call) / task.interval
        if intervals_since_last_call >= 1:
            i_intervals_since_last_call = int(intervals_since_last_call)
            task.previous_call += task.interval * i_intervals_since_last_call
            task.missed_executions += i_intervals_since_last_call - 1
            task.func()
