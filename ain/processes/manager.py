"""Creates and manages processes required.

The class checks max number of CPUs a machine has and
determines how many parallel processes can be run.

It would reject the request to create more processes if the
queue is full. Hence it is important to close processes once
they are done.
"""

import multiprocessing
from multiprocessing import Pool
from multiprocessing.pool import IMapIterator
from typing import Iterable, Callable, List
from watchdog.observers.api import BaseObserver

from ain import search_engine


def pool_init():
    """Called while initialising Process Pool"""
    search_engine.init_engine()
    print("Process Pool initialised")


class ProcessManager:
    """Managed a pool of processes.

    The class should not be instantiated in order to ensure
    only a single process pool is created.

    Also, ProcessManager should only be initiated once per
    application lifetime.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(f"Can't create {cls.__name__!r} objects directly")

    @classmethod
    def create_manager(cls):
        """Creates an instance of the process manager."""
        # Don't use __new__ *on this class*, but on the next one in the
        # MRO. We'll have to manually apply __init__ now.
        instance = super().__new__(cls)
        instance.__init__()
        return instance

    def __init__(self) -> None:
        self._cpu_num = multiprocessing.cpu_count()
        # pool contains one less process since one process shall be dedicated
        # to indexing.
        self._process_pool = Pool(processes=self._cpu_num - 1)
        pool_init()
        self._results: List[IMapIterator] = []

    def start_engine(self) -> BaseObserver:
        """Creates a process to run the search engine."""
        # index_proc = multiprocessing.Process(target=search_engine.start_engine)
        # index_proc.start()
        # return index_proc
        return search_engine.start_engine()

    def start_async(self, func: Callable, *args: Iterable) -> None:
        """Starts a new async process"""
        self._results.append(self._process_pool.imap(func, args))

    def close_all(self) -> None:
        """Closes all processes.

        Before closing processes it waits for the processes to complete.
        """
        # Wait for the job to complete.
        self._process_pool.close()
        self._process_pool.join()
