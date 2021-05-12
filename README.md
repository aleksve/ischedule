An elegant and simple way to schedule periodic tasks in Python. Created because [`schedule`](https://github.com/dbader/schedule) is too complicated and counterintuitively does not account for the time it takes for the job function to execute. Please note the following implementational details:

* Both the scheduler and the task run in the main thread. No new threads are created.
* Each task can run until it finishes.
* Each execution of `run_pending` checks the tasks in the same order as they were added by `schedule`. It executes the first task that is ready to be executed.* If a task was not executed during the scheduled interval, a single execution will be missed
* A task execution will be skipped if a the next execution of the same task is due by the time the control is returned to the scheduler.
* Exceptions during the execution are propagated out of `run_pending`, and can be dealth with by the caller.


