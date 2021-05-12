import time

import pytest

from src.ischedule import reset, run_pending, schedule

N_job_1 = 0


def test_example():
    def job_1():
        global N_job_1
        N_job_1 += 1
        print(f"Doing a fast job {N_job_1}")

    def job_2():
        print("Simulating a job that takes much time to complete.")
        time.sleep(1)

    schedule(job_1, interval=0.1)
    schedule(job_2, interval=1)

    start_time = time.time()
    while start_time + 2 > time.time():
        run_pending()
        time.sleep(0.01)


@pytest.fixture(autouse=True)
def reset_scheduler():
    print("reset")
    global _i
    _i = 0
    reset()
