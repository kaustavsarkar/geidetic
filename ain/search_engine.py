"""A whoosh wrapper for AIN.
"""

import os
import time
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, FileIndex, exists_in, open_dir
from whoosh.writing import IndexWriter
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileCreatedEvent
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver


_INDEX_DIR = "my_search_index"
_EXTRACTED_PDF = "pdf_extracted_data"


def _check_and_create_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def init_engine() -> None:
    """Initialises search engine"""
    init_dir()


def start_engine() -> BaseObserver:
    """Starts indexing"""
    curr_dir = os.getcwd()
    path = os.path.join(curr_dir, _EXTRACTED_PDF)
    event_handler = Engine(index_dir=_INDEX_DIR,
                           src_dir=_EXTRACTED_PDF)
    observer = Observer()
    observer.schedule(event_handler=event_handler,
                      path=path, recursive=False)
    observer.start()
    print("observer started")
    return observer


def init_dir() -> None:
    """Creates directory for saving indexed data."""
    curr_dir = os.getcwd()
    _check_and_create_path(os.path.join(curr_dir, _INDEX_DIR))
    path = os.path.join(curr_dir, _EXTRACTED_PDF)
    _check_and_create_path(path)


class Engine(FileSystemEventHandler):
    """Wraps implementation of indexing the texts"""

    def __init__(self, index_dir: str, src_dir: str) -> None:
        self._schema = Schema(path=ID(stored=True), content=TEXT)
        if not exists_in(index_dir):
            self._ix = create_in(index_dir, self._schema)
        else:
            self._ix = open_dir("my_search_index", schema=self._schema)
        self._src_dir = src_dir

    def file_index(self) -> FileIndex:
        """Returns instance of File Index."""
        return self._ix

    def on_created(self, event: FileSystemEvent) -> None:
        """Overrides FileSystemEventHandler on_created.

        Triggers an index event in case a file is added to the
        target directory.
        """
        print("on_created triggered", event)
        if event.is_directory:
            # There should be directory changes involved here.
            print("event is a directory")
            return

        if not isinstance(event, FileCreatedEvent):
            # The event should be a file creation event
            print("not a file creation event")
            return
        txt_path: str = event.src_path
        print(txt_path)
        if txt_path.endswith(".txt"):
            self._index(txt_path)

    def _index(self, src_path: str) -> None:
        """Indexes the content of extracted PDF."""
        print("Indexing data...")
        with _Writer(self._ix) as writer:
            start_a = time.time()
            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()
                start = time.time()
                writer.add_document(path=src_path, content=content)
                print("---> indexed in", time.time() - start, "seconds")
            os.remove(src_path)
            print("---> total process in", time.time() - start_a,
                  "seconds and doc count", self._ix.doc_count())


class _Writer():
    """Writes indexed data."""

    def __init__(self, file_index: FileIndex) -> None:
        self._ix = file_index
        self._writer: IndexWriter

    def __enter__(self) -> IndexWriter:
        """Create a writer for creating indices."""
        self._writer = self._ix.writer()
        return self._writer

    def __exit__(self, exec_type, exec_val, traceback):
        if self._writer is None:
            return
        self._writer.commit()


# Define the schema for the index
# schema = Schema(path=ID(stored=True), content=TEXT)

# Create or open the search index
# if not os.path.exists(_INDEX_DIR):
#     os.mkdir(_INDEX_DIR)
# ix = create_in(_INDEX_DIR, schema)

# Create an index writer
# writer = ix.writer()

# Index text files
# for root, dirs, files in os.walk(_EXTRACTED_PDF):
#     for file in files:
#         if file.endswith(".txt"):
#             with open(os.path.join(root, file), "r") as f:
#                 content = f.read()
#             writer.add_document(path=os.path.join(root, file), content=content)

# Commit the changes
# writer.commit()
