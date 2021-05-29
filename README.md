An elegant way to schedule periodic tasks in a Python program. No threads or processes are created by this library, which avoids the issues of synchronizing the data access and coordinating exception handling between tasks. Both the user and the library code can therefore be made with relatively uncomplicated logic, which makes this library ideal for embedded and critical applications. 

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

Periodic scheduling has certain quirks that have been taken care of under the hood by ```ischedule```. For example, it accounts for the time it takes for the task function to execute. If a task is scheduled every second and takes 0.6 seconds to complete, there will be a delay of only 0.4 seconds between consecutive executions.  Delays are not propagated. If the previously-mentioned task is scheduled for execution at t=1 second, but is delayed by 0.3 seconds, the next execution of the same task will nevertheless be scheduled at t=2 seconds. 

**What happens during heavy loading**

Heavy loading means that there is not enough computer resources to execute all tasks as scheduled. Graceful handling of this condition is essential in a well-implemented periodic scheduler. 
* If more than one task become pending simultaneously, they will be executed in the order in which they were added to the schedule by `schedule()`.
* Regardless of the load, no task will be completely starved. All pending tasks will be executed as soon as possible after they become pending.
* There is no build-up of delayed executions. If the execution of a task is delayed so much that the next execution of the same task become pending, an execution will be skipped. 

**Exceptions**

Exceptions during the execution are propagated out of `run_loop()`/`run_pending()`, and can be dealt with by the caller.

**Cancellable loops**

If `run_loop()` is executed without parameters, it will continue running until the process is terminated. 

If the program needs to be able to cancel it, it should supply a `stop_event`, which is expected to be a `threading.Event`. When this event is set, `run_loop()` will cleanly return to the caller after completing the currently pending tasks.

The call to `run_loop()` accepts a `return_after`parameter, which allows the loop to return after a specified time, either as seconds or as a [datetime.timedelta](https://docs.python.org/3/library/datetime.html#datetime.timedelta). 

**More advanced example**

In this example, two tasks are scheduled for periodic execution. The first one is scheduled with an interval of 0.1 seconds, and the second one is scheduled with an interval of 0.5 seconds. The second task takes a lot of time to complete, stress-testing the scheduler.

```python3
import time

from ischedule import schedule, run_loop
from threading import Event

start_time = time.time()
stop_event = Event()

def task_1():
    dt = time.time() - start_time
    print(f"Started a _fast_ task at t={dt:.3f}")
    if dt > 3:
        stop_event.set()

def task_2():
    dt = time.time() - start_time
    print(f"Started a *slow* task at t={dt:.3f}")

    if dt < 2:
        time.sleep(0.91)
    else:
        time.sleep(0.09)

schedule(task_1, interval=0.1)
schedule(task_2, interval=0.5)

run_loop(stop_event=stop_event)
print("Finished")
```
Output:
```
Started a _fast_ task at t=0.100
Started a _fast_ task at t=0.200
Started a _fast_ task at t=0.300
Started a _fast_ task at t=0.400
Started a _fast_ task at t=0.500
Started a *slow* task at t=0.500
Started a _fast_ task at t=1.411
Started a *slow* task at t=1.411
Started a _fast_ task at t=2.323
Started a *slow* task at t=2.323
Started a _fast_ task at t=2.413
Started a _fast_ task at t=2.500
Started a *slow* task at t=2.500
Started a _fast_ task at t=2.600
Started a _fast_ task at t=2.700
Started a _fast_ task at t=2.800
Started a _fast_ task at t=2.900
Started a _fast_ task at t=3.000
Started a *slow* task at t=3.000
Finished
```
The fast task runs every 0.1 seconds, and completes quickly. The slow task is first scheduled for execution at t=0.5s. Initially it uses so much time that it blocks the other tasks from being executed. The scheduler becomes overloaded. It adapts by running the pending tasks as soon as it gets back the control at t=1.41s. 

After t=2.0s, the slow task changes to spend only 0.09 seconds. This is slow, but just fast enough not to create delays in the schedule. The scheduler is able to return to normal operation.

**Limitations**

If the scheduled tasks need to run concurrently on separate threads, then this package cannot be used. [Multiprocesseing parallelism](https://docs.python.org/3/library/multiprocessing.html) is however an excellent alternative in Python. An example implementation is available in the tests folder on GitHub.

**Decorator syntax**

Decorator syntax is supported for scheduling tasks: 
```python
from ischedule import run_loop, schedule


@schedule(interval=0.1)
def task():
    print("Performing a task")


run_loop(return_after=1)
```

**Timing Precision**

Deviations from the scheduled time were thoroughly tested.
In a typical 1-minute run, the median deviation is below 0.2 milliseconds, and maximum deviations is below 5 milliseconds. 
Larger deviations, on the order of tens of milliseconds, have been occasionally observed. 

**Feedback**

The project has its main [homepage on GitHub](https://github.com/aleksve/ischedule). Issues and suggestions can be submitted to [GitHub Issues](https://github.com/aleksve/ischedule/issues).  

[![Python package](https://github.com/aleksve/ischedule/actions/workflows/python-package.yml/badge.svg)](https://github.com/aleksve/ischedule/actions/workflows/python-package.yml)
