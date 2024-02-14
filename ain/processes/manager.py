"""Creates and manages processes required.

The class checks max number of CPUs a machine has and
determines how many parallel processes can be run.

It would reject the request to create more processes if the
queue is full. Hence it is important to close processes once
they are done.
"""

import multiprocessing
from multiprocessing import Process
from multiprocessing.pool import IMapIterator
from typing import List
from watchdog.observers.api import BaseObserver

from ain.engine import search_engine


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
        self._processes: List[Process] = []
        self._results: List[IMapIterator] = []

    def close_all(self) -> None:
        """Closes all processes.

        Before closing processes it waits for the processes to complete.
        """
