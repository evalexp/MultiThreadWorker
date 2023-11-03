import time
from typing import List, Dict, Tuple

from MultiThreadWorker import MultiThreadWorker


class MyHandler(MultiThreadWorker.TaskHandler):
    def __init__(self):
        super().__init__()
        self.data = []

    def down(self):
        print("Result is :")
        for args in self.data:
            print(args)

    def handle(self, *args, **kwargs):
        if args[0] >= 30:
            self.data.append(args)
        time.sleep(0.5)


class MyLoader(MultiThreadWorker.DataLoader):
    def __init__(self):
        self.data = [(i, i + 1) for i in range(200)]
        self.index = 0

    def next(self) -> List | Dict | Tuple:
        rdata = self.data[self.index]
        self.index += 1
        return rdata

    def size(self) -> int:
        return len(self.data)

    def has_next(self) -> bool:
        return self.index < self.size()


if __name__ == "__main__":
    worker = MultiThreadWorker()
    worker.handler = MyHandler()
    worker.data_loader = MyLoader()
    worker.register_progress_report("[*] {time} Progress : {done}/{total}, {percent:.2%}", 1)
    worker.work()
