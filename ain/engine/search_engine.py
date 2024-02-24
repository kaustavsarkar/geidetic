"""A whoosh wrapper for AIN.
"""

from multiprocessing import Queue
import os
import time
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, FileIndex, exists_in, open_dir
from whoosh.writing import IndexWriter
from whoosh.qparser import QueryParser
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileCreatedEvent
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver
from ain.db.db_operation import get_file_path, update_job_progress, update_job_status
from ain.engine.search_results import SearchItem, SearchResult
from ain.models import ingestion_job as ij


_INDEX_DIR = "my_search_index"
_EXTRACTED_PDF = "pdf_extracted_data"


def _check_and_create_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def init_engine() -> None:
    """Initialises search engine"""
    init_dir()


def start_engine(job_task_q: 'Queue[tuple[str, str, str]]') -> 'tuple[Engine,BaseObserver]':
    """Starts indexing"""
    curr_dir = os.getcwd()
    path = os.path.join(curr_dir, _EXTRACTED_PDF)
    search_engine = Engine(index_dir=_INDEX_DIR,
                           src_dir=_EXTRACTED_PDF,
                           job_task_q=job_task_q)
    observer = Observer()
    observer.schedule(event_handler=search_engine,
                      path=path, recursive=False)
    observer.start()
    print("observer started")
    return search_engine, observer


def init_dir() -> None:
    """Creates directory for saving indexed data."""
    curr_dir = os.getcwd()
    _check_and_create_path(os.path.join(curr_dir, _INDEX_DIR))
    path = os.path.join(curr_dir, _EXTRACTED_PDF)
    _check_and_create_path(path)


class Engine(FileSystemEventHandler):
    """Wraps implementation of indexing the texts"""

    def __init__(self, index_dir: str, src_dir: str,
                 job_task_q: 'Queue[tuple[str, str, str]]') -> None:
        self._schema = Schema(file_path=ID(stored=True),
                              page_number=ID(stored=True), content=TEXT)
        if not exists_in(index_dir):
            self._ix = create_in(index_dir, self._schema)
        else:
            self._ix = open_dir("my_search_index", schema=self._schema)
        self._src_dir = src_dir
        # A dictionary with job_id as key and dict. The other dict is
        # file path as key for total pages and page.
        self._job_cache: 'dict[str, ij.IngestionJob]' = {}

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
                file_path, file_name, page_number, total_pages, job_id, pdf_count = self._extract_details_from_path(
                    path=src_path)
                writer.add_document(file_path=file_path,
                                    page_number=page_number, content=content)
                print("---> indexed in", time.time() - start, "seconds")
                if job_id not in self._job_cache:
                    self._job_cache[job_id] = ij.IngestionJob(
                        job_id=job_id,
                        status=ij.JobStatus.IN_PROGRESS,
                        files=[],
                        completed_files=[],
                        reason="",
                        progress=0)
                    self._job_cache[job_id].set_doc_count(int(pdf_count))
                    print("Marking job as in progress", job_id)
                    update_job_status(
                        job_id, ij.JobStatus.IN_PROGRESS, reason="")

                self._job_cache[job_id].add_file_page_count(
                    file_path=file_path, page_count=total_pages)
                print("from src path", file_path, file_name,
                      page_number, total_pages, job_id)
                is_done = self._job_cache[job_id].processed_file(
                    file_path=file_path, page_number=page_number)

                if int(page_number) % 10 == 0:
                    update_job_progress(
                        job_id=job_id,
                        completed_files=self._job_cache[job_id].completed_files,
                        progress=self._job_cache[job_id].get_progress)
                if is_done:
                    update_job_progress(
                        job_id=job_id,
                        completed_files=self._job_cache[job_id].completed_files,
                        progress=100)
                job = self._job_cache[job_id]
                if job.is_done():
                    update_job_status(job_id, ij.JobStatus.SUCCESS, "")
                    del self._job_cache[job_id]

            os.remove(src_path)
            print("---> total process in", time.time() - start_a,
                  "seconds and doc count", self._ix.doc_count())

    def _job_id_for_file(self, file_name: str) -> str:
        if len(self._job_cache) == 0:
            return ""
        for job_id, job in self._job_cache.items():
            print("check if job has file")
            if job.has_file(file_name=file_name):
                print("found job id", job_id)
                return job_id
        return ""

    def find_results(self, search_text: str) -> SearchResult:
        """Finds results from the index."""
        search_result: SearchResult = SearchResult()
        with self._ix.searcher() as searcher:
            query = QueryParser("content", self._ix.schema).parse(search_text)
            results = searcher.search(query, limit=None)
            for hit in results:
                # path is the path along with page number.
                file_path = hit['file_path']
                page_number = hit['page_number']
                # print(file_path)
                if file_path is None:
                    return []
                flag = False
                for item in search_result.search_items:
                    if item.file_path == file_path:
                        item.append_page(page_number)
                        flag = True
                if flag is False:
                    search_result.add_search_item(
                        SearchItem(file_path=file_path, pages=[page_number])
                    )
        return search_result

    def _extract_details_from_path(self, path: str) -> 'tuple[str, str, str, str, str, str]':
        # <pdf_name>#<page_number>#<total_pages>#<job_id>#<pdf_count>.txt
        path_without_extension = os.path.splitext(
            os.path.basename(path))[0]
        page_no_file_name = path_without_extension.split('#')
        file_name = page_no_file_name[0]
        page_number = page_no_file_name[1]
        total_pages = page_no_file_name[2]
        job_id = page_no_file_name[3]
        pdf_count = page_no_file_name[4]
        file_path = get_file_path(file_name)
        return file_path, file_name, page_number, total_pages, job_id, pdf_count


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
