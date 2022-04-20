# Regression test to ensure that ischedule doesn't overload the CPU
import multiprocessing
import time
from functools import partial
from multiprocessing import Queue
from threading import Event

import psutil
import pytest

from src.ischedule.ischedule import reset, run_loop, schedule


def rec_fib(N: int):
    if N < 2:
        return 1
    else:
        return rec_fib(N - 1) + rec_fib(N - 2)


def abort_after(ev: Event):
    global start
    if "start" not in globals():
        start = time.monotonic()
    if time.monotonic() - start > 5:
        ev.set()


def check_cpuusage(q: Queue):
    while True:
        cpu_usage:list = psutil.cpu_percent(percpu=True)
        print(cpu_usage)
        if max(cpu_usage) > 25:
            q.put(max(cpu_usage))
        time.sleep(0.1)


def test_load():
    schedule(partial(rec_fib, 5), interval=1)
    schedule(partial(rec_fib, 10), interval=2)
    ev = Event()
    schedule(partial(abort_after, ev), interval=0.5)

    q = Queue()
    cpu_mon_proc = multiprocessing.Process(
        target=check_cpuusage, args=(q,), daemon=True
    )
    cpu_mon_proc.start()
    run_loop(stop_event=ev)
    cpu_mon_proc.kill()
    cpu_usage_overruns = []
    while not q.empty():
        cpu_usage_overruns.append(q.get(block=False))
    assert (
        len(cpu_usage_overruns) < 3
    ), f"CPU overuse detected {len(cpu_usage_overruns)} times: {cpu_usage_overruns}. Ischedule should run without consuming significant amounts of CPU, but this could also be caused by other applications in the system. Close other applications and re-run the test"


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    reset()


if __name__ == "__main__":
    test_load()
