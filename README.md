# MultiThreadWorker

> This is a library that can help you implement multithreading faster, which can be useful when you are writing scripts for certain gadgets that require multithreading.

## How to use

### Define handler

You should define your handler by extending `MultiThreadWorker.TaskHandler` and implement all abstract function and constructor.

By the way, the constructor must call `super.__init__()`.

#### TaskHandler.handle

This function actually processing the data.

And you mustn't specify any parameter names, please use `*args` and `**kwargs`.

`*args` would be passed if your data loader return a `List` or a `Tuple`, `**kwargs` would be passed if your data loader return a `Dict`.

For example, if your data loader return a single data like `[1,2,3]` or `(1,2,3)`, it would pass like `handle(*(1,2,3))`;

if your data loader return a single data like `{"a": "b"}`, it would pass like `handle(**{"a":"b"})`.

Here is an example:

```python
def handle(self, *args, **kwargs):
    if args[0] == args[1]:
        print(args[3])
    print(kwargs['a'])
```

#### TaskHandler.down

This function would be called when the program shutdown.

#### TaskHandler.__init__

Please call `super.__init__()`, and add your constructor code

### Define data loader

We all know that multithreading is used to process large amounts of data, so you need to define a data loader to serve the data.

You should define your data loader by extending `MultiThreadWorker.DataLoader` or `MultiThreadWorker.ProgressLoader`.

> Actually, `MultiThreadWorker.ProgressLoader` extend `MultiThreadWorker.DataLoader`, it defines the interface for saving progress, and you can save progress by extend this loader

#### DataLoader.next

You should return a single data from your data source, the data must be typeof `List`, `Tuple`, `Dict`, this function would be called in a loop until `has_next` return `False`.

You can load your data from file, or from some variables, it depends on you.

#### DataLoader.size

This function should return the data source's size.

One simple way is to load all data into memory at once, and use `len` function to calculate its length.

If your data is too large, try to count it at first.

#### DataLoader.has_next

If data loader can continue to fetch data, return `True`, otherwise return `False`

#### ProgressLoader.save

The arg `done_list` is a list which contains all processed data.

This function is used to save progress in real time when you need to interrupt, and can only be interrupted by `Ctrl + C`.

> Notice: if you define save function, please notice that you have to load your progress in the constructor, one simple way is to detect if the file you save is existed.

For example, use pickle to save progress:

```python
from MultiThreadWorker import MultiThreadWorker
import pickle
import os
from typing import List, Any
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
```

> Transform `done_list` to set, and get its complementary set. And this is the progress need to save.

### Start to process

After defining your handler and data loader, it's time to start your program to process data multithreading.

Basically, use `.work()` to start processing:

```python
if __name__ == "__main__":
    worker = MultiThreadWorker()
    worker.handler = MyHandler()
    worker.data_loader = MyLoader()
    worker.work()
```

Thread num would be default set to 8, you can use `MultiThreadWorker` class's constructor to specify it like `worker = MultiThreadWorker(10)`.

If you want to view the process progress, you could register a progress report:

```python
if __name__ == "__main__":
    worker = MultiThreadWorker(10)
    worker.handler = MyHandler()
    worker.data_loader = MyLoader()
    worker.register_progress_report("[*] {time} Current Progress is {done}/{total}, {percent:.2%}", 1)
    worker.work()
```

And yes, there's some magic variables:

| Name    | Content                       | Example  |
|---------|-------------------------------|----------|
| time    | Current Time                  | 12:00:00 |
| total   | Data source's size            | 3000000  |
| done    | The account of processed data | 1000     |
| percent | The progress percentage       | 0.921    |

### Example

You can find the examples in `.example` folder.