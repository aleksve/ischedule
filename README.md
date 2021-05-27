An elegant way to schedule periodic tasks in a Python program. No threads or procesees are created by this library, which avoids the issues of synchronizing the data access and coordinating exception handling between tasks. Both the user and the library code can therefore be made with much less complicated logic, which makes this library ideal for embedded and critical applications. 

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

**Implementation details**

Periodic scheduling has certain quirks that have been taken care of under the hood by ```ischedule```. For example, it accounts for the time it takes for the task function to execute. If a task is scheduled every second and takes 0.6 seconds to complete, there will be a delay of only 0.4 seconds between consecutive executions.  Delays are not propagated. If the previously-mentioned task is scheduled for execution at t=1 second, but is delayed by 0.3 seconds, the next execution of the same task will never the less be scheduled at t=2 seconds. 

**What happens during heavy loading**

* If more than one task become pending simultaneously, they will be executed in the order in which they were added to the schedule by `schedule()`.
* Regardless of the load, no task will be completely starved. All pending tasks will be executed as soon as possible after they become pending.
* There is no build-up of delayed executions. If the execution of a task is delayed so much that the next execution of the same task become pending, an execution will be skipped. 

**Exceptions**

Exceptions during the execution are propagated out of `run_loop()`/`run_pending()`, and can be dealt with by the caller.

**Cancellable loops**

If `run_loop()` is executed without parameters, it will continue running until the process is terminated. If the program needs to be able to cancel it, it should supply a `stop_event`, which is expected to be a `threading.Event`. When this event is set, `run_loop()` will cleanly return to the caller after completing the currently pending tasks.

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
Started a _fast_ task at t=0.10
Started a _fast_ task at t=0.20
Started a _fast_ task at t=0.30
Started a _fast_ task at t=0.40
Started a _fast_ task at t=0.50
Started a *slow* task at t=0.50
Started a _fast_ task at t=1.50
Started a *slow* task at t=1.50
Started a _fast_ task at t=2.50
Started a _fast_ task at t=2.60
Started a _fast_ task at t=2.70
Started a _fast_ task at t=2.80
Started a _fast_ task at t=2.90
Started a _fast_ task at t=3.00
Finished
```
The fast task runs every 0.1 seconds, and completes quickly. When the slow task starts running at t=0.5, it doesn't return control until one second later, at t=1.50s. By that time, both the fast and the slow tasks become pending, and are executed in the order they were added to the scheduler. The slow task does not run after t=2.0, so the fast task returns to running normally every 0.1 seconds.

**Limitations**

If the scheduled tasks need to be run concurrently on different threads, then this package cannot be used. [Multiprocesseing parallelism](https://docs.python.org/3/library/multiprocessing.html) is however an excellent alternative in Python. An example implementation is available in the tests folder on GitHub.

**Decorator syntax**

Decorator syntax can optionally be used to schedule tasks: 
```python
import time

from src.ischedule import run_pending, schedule_decorator as schedule


@schedule(interval=0.1)
def task():
    print("Performing a task")


def test():
    time.sleep(0.1)
    run_pending()
```

**Feedback**

Issues and suggestions can be submitted to https://github.com/aleksve/ischedule/issues. If you use and like this project, please consider [adding a star on GitHub](https://github.com/aleksve/ischedule). 

[![Python package](https://github.com/aleksve/ischedule/actions/workflows/python-package.yml/badge.svg)](https://github.com/aleksve/ischedule/actions/workflows/python-package.yml)
