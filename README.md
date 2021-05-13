An elegant and simple way to schedule periodic tasks in Python. Both the scheduluer and the task run in the main thread, which avoids the issue of synchronizing the data access between tasks. However, if a task takes a lot of time to complete, the other tasks must wait until it finishes. 

```ischedule``` accounts for the time it takes for the task function to execute. For example, if a task is scheduled every second and takes 0.6 seconds to complete, there will be a delay of only 0.4 seconds between consecutive executions.  Delays are not propagated. If the previously-mentioned task is scheduled for execution at t=1 second, but is delayed by 0.3 seconds, the next execution of the same task will never the less be scheduled at t=2 seconds. 

**What happens during heavy loading**
* If more than one task become pending at the same time, they are executed in the order in which they were scheduled by `schedule`.
* Regardless of the load, all pending tasks will be executed if they become pending (unless another task hangs).
* If the execution of a task is delayed that the next execution of the same task become pending, this execution will be skipped.

**Exceptions**

Exceptions during the execution are propagated out of `run_pending`, and can be dealth with by the caller.

**Example**
In this example, two jobs are scheduled for periodic execution. The first one is scheduled with an interval of 0.1 seconds, and the second one is scheduled with an interval of 0.5 seconds. The second job takes a lot of time to complete, stress-testing the scheduler. 
```python
import time

from ischedule import schedule, run_loop

start_time = time.time()

def job_1():
    dt = time.time() - start_time
    print(f"Started a _fast_ job at t={dt:.2f}")

def job_2():
    dt = time.time() - start_time
    if dt > 2:
        return
    print(f"Started a *slow* job at t={dt:.2f}")
    time.sleep(1)


schedule(job_1, interval=0.1)
schedule(job_2, interval=0.5)

run_loop()
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
The fast job runs every 0.1 seconds, and completes quickly. When the slow job starts running at t=0.5, it doesn't return control until one second later, at t=1.50s. By that time, both the fast and the slow job become pending, and are executed in the order they were added to the scheduler. The slow job does not run after t=2.0, so the fast job returns to running normally every 0.1 seconds. The task had to be stopped with a keyboard interrupt.

**Cancellable loops**

If `run_loop()` is executed without parameters, it will continue running until the process is terminated. If the program needs to be able to cancel it, it should supply a `stop_event`, which is expected to be a `threading.Event`. When this event is set, run_loop will cleanly return to the caller after completing the currently pending tasks.


**Known issues**

None at this time. Issues and suggestions can be submitted to https://github.com/aleksve/ischedule/issues.