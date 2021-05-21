An elegant way to schedule periodic tasks in a Python program. Both the scheduluer and the task run in the main thread, which avoids the issue of synchronizing the data access between tasks and simplifies exception handling.

**Basic example**

```python
from ischedule import schedule, run_loop

def task_1():
    print("task 1")

def task_2():
    print("task 2")

schedule(task_1, interval=1.0)
schedule(task_2, interval=0.2)

run_loop()
```
Output:
```text
task 2
task 2
task 2
task 2
task 1
task 2
task 2
task 2
task 2
task 2
task 1
```

**Implemnentation details**

Periodic scheduling has certain quirks that have been taken care of under the hood by ```ischedule```. For example, it accounts for the time it takes for the task function to execute. If a task is scheduled every second and takes 0.6 seconds to complete, there will be a delay of only 0.4 seconds between consecutive executions.  Delays are not propagated. If the previously-mentioned task is scheduled for execution at t=1 second, but is delayed by 0.3 seconds, the next execution of the same task will never the less be scheduled at t=2 seconds. 

**What happens during heavy loading**

* If more than one task become pending at the same time, they are executed in the order in which they were added to the schedule by `schedule()`.
* Regardless of the load, no task will be completely starved. All pending tasks will be executed as soon as possible after they become pending.
* If the execution of a task is delayed that the next execution of the same task become pending, this execution will be skipped.

**Exceptions**

Exceptions during the execution are propagated out of `run_pending()`, and can be dealt with by the caller.

**Cancellable loops**

If `run_loop()` is executed without parameters, it will continue running until the process is terminated. If the program needs to be able to cancel it, it should supply a `stop_event`, which is expected to be a `threading.Event`. When this event is set, run_loop will cleanly return to the caller after completing the currently pending tasks.

**More advanced example**

In this example, two tasks are scheduled for periodic execution. The first one is scheduled with an interval of 0.1 seconds, and the second one is scheduled with an interval of 0.5 seconds. The second task takes a lot of time to complete, stress-testing the scheduler.

```python
import time

from ischedule import schedule, run_loop
from threading import Event

start_time = time.time()
stop_event = Event()

def task_1():
    dt = time.time() - start_time
    print(f"Started a _fast_ task at t={dt:.2f}")
    if dt > 3:
        stop_event.set()

def task_2():
    dt = time.time() - start_time
    if dt > 2:
        return
    print(f"Started a *slow* task at t={dt:.2f}")
    time.sleep(1)

schedule(task_1, interval=0.1)
schedule(task_2, interval=0.5)

run_loop(stop_event=stop_event)
print("Finished")
```
Output:
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
Finished
```
The fast task runs every 0.1 seconds, and completes quickly. When the slow task starts running at t=0.5, it doesn't return control until one second later, at t=1.50s. By that time, both the fast and the slow tasks become pending, and are executed in the order they were added to the scheduler. The slow task does not run after t=2.0, so the fast task returns to running normally every 0.1 seconds.



**Known issues**

None at this time. Issues and suggestions can be submitted to https://github.com/aleksve/ischedule/issues.

[![Python package](https://github.com/aleksve/ischedule/actions/workflows/python-package.yml/badge.svg)](https://github.com/aleksve/ischedule/actions/workflows/python-package.yml)
