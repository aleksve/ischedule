from math import isclose
from time import monotonic

from src.ischedule import reset, run_loop, schedule


def test_cancel_notasks():
    reset()
    run_loop(return_after=1)


def test_cancel_longtast():
    reset()

    @schedule(interval=2)
    def task():
        print("Doing task")

    start = monotonic()
    run_loop(return_after=1.5)
    end = monotonic()
    print(end - start)
    assert isclose(end - start, 1.5, abs_tol=0.001)
