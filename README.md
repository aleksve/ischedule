An elegant and simple way to schedule periodic tasks in Python. Created because [`schedule`](https://github.com/dbader/schedule) is too complicated and counterintuitively does not account for the time it takes for the job function to execute. 

**Implementational details**

* Both the scheduler and the task run in the main thread. No new threads are created.
* Each task can run until it finishes.
* Each execution of `run_pending` checks the tasks in the same order as they were added by `schedule`. It executes the first task that is ready to be executed.* If a task was not executed during the scheduled interval, a single execution will be missed
* A task execution will be skipped if a the next execution of the same task is due by the time the control is returned to the scheduler.
* Exceptions during the execution are propagated out of `run_pending`, and can be dealth with by the caller.


**Example**
```python
from src.ischedule import schedule, run_pending
import time

N_job_1 = 0

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
```