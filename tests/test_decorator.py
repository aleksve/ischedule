from src.ischedule import run_loop, every


@every(interval=0.1)
def task():
    print("Performing a task")


def test():
    run_loop(return_after=1)
