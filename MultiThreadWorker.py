import time
import warnings
from concurrent.futures import ThreadPoolExecutor, wait
from typing import List, Any, Dict, Tuple
import signal
from abc import abstractmethod, ABCMeta


class MultiThreadWorker:
    class DataLoader(metaclass=ABCMeta):
        @abstractmethod
        def next(self) -> List | Dict | Tuple:
            """
            get the next element
            :return: the next element
            """
            pass

        @abstractmethod
        def size(self) -> int:
            """
            get the total data size
            :return: the total data size
            """
            pass

        @abstractmethod
        def has_next(self) -> bool:
            """
            check whether you could get next arg
            :return: true if you could get next one
            """
            pass

    class ProgressLoader(DataLoader, metaclass=ABCMeta):
        @abstractmethod
        def save(self, done_list: List[Any]):
            """
            would call after Ctrl + C gracefully shutdown program
            :param done_list: the arg list which is handled
            :return: bool
            """
            pass

    class TaskHandler(metaclass=ABCMeta):
        def __init__(self):
            self.signal = None

        @abstractmethod
        def handle(self, *args, **kwargs):
            """
            the handle function
            :param args:
            :param kwargs:
            :return:
            """
            pass

        @abstractmethod
        def down(self):
            """
            would call when the program shutdown
            :return:
            """
            pass

        def shutdown(self):
            self.signal = True

    def __init__(self, thread_num: int = 8):
        self.__report_delta: float | None = None
        self.__done_list = []
        self.__task_list = []
        self.__handler: MultiThreadWorker.TaskHandler | None = None
        self.__data_loader: MultiThreadWorker.DataLoader | None = None
        self.__format_str: str | None = None
        self.__thread_num = thread_num
        self.__register_gracefully_exit()

    @property
    def handler(self):
        return self.__handler

    @handler.setter
    def handler(self, handler: TaskHandler):
        self.__handler = handler

    @property
    def data_loader(self):
        return self.__data_loader

    @data_loader.setter
    def data_loader(self, loader: DataLoader):
        self.__data_loader = loader

    def __gracefully_exit(self, signum, frame):
        for task in self.__task_list:
            task.cancel()
        if not self.__handler.signal and isinstance(self.__data_loader, MultiThreadWorker.ProgressLoader):
            self.__data_loader.save(self.__done_list)
        self.__handler.down()
        exit(0)

    def __handler_wrapper(self, work_args: List[Any] | Dict[str, Any] | Tuple[Any]):
        if self.__handler.signal:
            self.__gracefully_exit(None, None)
        if isinstance(work_args, dict):
            self.__handler.handle(**work_args)
        else:
            self.__handler.handle(*work_args)
        self.__done_list.append(work_args)

    def __register_gracefully_exit(self):
        signal.signal(signal.SIGINT, self.__gracefully_exit)
        signal.signal(signal.SIGTERM, self.__gracefully_exit)

    def register_progress_report(self, format_str: str, seconds_delta: float):
        self.__format_str = format_str
        self.__report_delta = seconds_delta

    def work(self):
        if self.__data_loader.size() == 0:
            print(f"[!] Error: Input list or data loader not set")
            return
        if self.__handler is None:
            raise Exception("Worker [TaskHandler] must not be None")

        thread_pool = ThreadPoolExecutor(max_workers=self.__thread_num)
        while self.__data_loader.has_next():
            work_arg = self.__data_loader.next()
            if isinstance(work_arg, dict) or isinstance(work_arg, list) or isinstance(work_arg, tuple):
                self.__task_list.append(thread_pool.submit(self.__handler_wrapper, work_arg))
            else:
                warnings.warn(f"There's an error when parsing args \"{work_arg}\", is it a dict or a list?")

        if self.__format_str is not None:
            while not list(reversed(self.__task_list))[0].done():
                t = time.localtime()
                print(self.__format_str.format(
                    total=self.__data_loader.size(),
                    done=len(self.__done_list),
                    time=f"{t.tm_hour}:{t.tm_min}:{t.tm_sec}",
                    percent=len(self.__done_list) / self.__data_loader.size()
                ))
                time.sleep(self.__report_delta)
        else:
            wait(self.__task_list)
        self.__handler.down()
