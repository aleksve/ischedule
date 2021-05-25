import time

from src.ischedule import run_pending
from src.ischedule import schedule_decorator as schedule


@schedule(interval=0.1)
def task():
    print("x")


def test():
    time.sleep(0.1)
    run_pending()
