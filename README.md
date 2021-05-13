An elegant and simple way to schedule periodic tasks in Python. Created because [`schedule`](https://github.com/dbader/schedule) is too complicated and counterintuitively does not account for the time it takes for the job function to execute. 

**Implementational details**

* Both the scheduler and the task run in the main thread. No new threads are created.
* Each task can run until it finishes.
* Each execution of `run_pending` checks the tasks in the same order as they were added by `schedule`. It executes the first task that is ready to be executed.* If a task was not executed during the scheduled interval, a single execution will be missed
* A task execution will be skipped if a the next execution of the same task is due by the time the control is returned to the scheduler.
* Exceptions during the execution are propagated out of `run_pending`, and can be dealth with by the caller.


**Example**
```python
import time

from src.ischedule import schedule, run_loop
from threading import Event

start_time = time.time()
stop_event = Event()

def job_1():
    dt = time.time() - start_time
    print(f"Started a _fast_ job at t={dt:.2f}")
    if dt > 3:
        stop_event.set()

def job_2():
    dt = time.time() - start_time
    if dt > 2:
        return
    print(f"Started a *slow* job at t={dt:.2f}")
    time.sleep(1)

schedule(job_1, interval=0.1)
schedule(job_2, interval=0.5)

run_loop(stop_event=stop_event)
```
This example produces the following output:
```
Started a _fast_ job at t=0.10
Started a _fast_ job at t=0.20
Started a _fast_ job at t=0.31
Started a _fast_ job at t=0.41
Started a _fast_ job at t=0.50
Started a *slow* job at t=0.50
Started a _fast_ job at t=1.51
Started a *slow* job at t=1.51
Started a _fast_ job at t=2.52
Started a _fast_ job at t=2.61
Started a _fast_ job at t=2.71
Started a _fast_ job at t=2.81
Started a _fast_ job at t=2.90
Started a _fast_ job at t=3.00
```
The fast job runs every 0.1 seconds, and completes quickly. When the slow job starts running at t=0.5, it doesn't return control until one second later, at t=1.50s. By that time, both the fast and the slow job become pending, and are executed in the order they were added to the scheduler. The slow job does not run after t=2.0, so the fast job returns to running normally every 0.1 seconds. 