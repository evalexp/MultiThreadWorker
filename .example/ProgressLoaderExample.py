import os.path
import time
from typing import List, Any, Dict, Tuple
import pickle
from MultiThreadWorker import MultiThreadWorker


class MyLoader(MultiThreadWorker.ProgressLoader):
    def __init__(self):
        if os.path.exists("./data.psf"):
            with open("./data.psf", 'rb') as f:
                self.data = pickle.load(f)
            os.remove("./data.psf")
        else:
            self.data = [(i, i+1) for i in range(200)]
        self.index = 0

    def save(self, done_list: List[Any]):
        with open("./data.psf", 'wb') as f:
            pickle.dump(list(set(self.data) - set(done_list)), f)

    def next(self) -> List | Dict | Tuple:
        rdata = self.data[self.index]
        self.index += 1
        return rdata

    def size(self) -> int:
        return len(self.data)

    def has_next(self) -> bool:
        return self.index < self.size()


class MyHandler(MultiThreadWorker.TaskHandler):
    def __init__(self):
        super().__init__()
        self.data = []

    def handle(self, *args, **kwargs):
        if args[0] >= 100:
            self.shutdown()
        if args[0] % 3 == 0:
            self.data.append(args)
        time.sleep(0.3)

    def down(self):
        print("Result is :")
        for args in self.data:
            print(args)


if __name__ == "__main__":
    worker = MultiThreadWorker(10)
    worker.handler = MyHandler()
    worker.data_loader = MyLoader()
    worker.register_progress_report("[*] {time} Current Progress is {done}/{total}, {percent:.2%}", 1)
    worker.work()
