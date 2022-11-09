import multiprocessing

from src.ischedule import run_loop, every


def named_doer(name: str, stop_event: multiprocessing.Event):
    def do_x():
        print(f"{name} is doing x")

    def do_y():
        print(f"{name} is doing y")

    every(interval=0.1, run=do_x)
    every(interval=0.14, run=do_y)

    run_loop(stop_event)


def test_multiprocessing():
    stop_event = multiprocessing.Event()
    p1 = multiprocessing.Process(target=named_doer, args=("Albert", stop_event))
    p2 = multiprocessing.Process(target=named_doer, args=("Bertine", stop_event))
    p1.start()
    p2.start()

    stop_event.wait(0.5)
    stop_event.set()
    p1.join()
    p2.join()


if __name__ == "__main__":
    test_multiprocessing()
