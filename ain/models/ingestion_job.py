"""Contains models pertaining to ingestion job."""
from enum import Enum
from datetime import datetime
from ain.logs.ain_logs import logger


class JobStatus(Enum):
    """Represents the status of an ingestion job."""
    STARTED = 1
    IN_PROGRESS = 2
    FAILED = 3
    SUCCESS = 4

    @staticmethod
    def from_string(status: str):
        """Convers string to enum"""
        if status == JobStatus.STARTED.name:
            return JobStatus.STARTED
        if status == JobStatus.IN_PROGRESS.name:
            return JobStatus.IN_PROGRESS
        if status == JobStatus.FAILED.name:
            return JobStatus.FAILED

        return JobStatus.SUCCESS


class IngestionJob():
    """Represents data about an ingestion job."""

    def __init__(self, job_id: str, status: JobStatus,
                 reason: str, files: 'list[str]',
                 completed_files: 'list[str]', progress: float,
                 created_at: datetime = None, updated_at: datetime = None) -> None:
        self.id = job_id
        self.status = status
        self.reason = reason
        self.files = files
        self.completed_files = completed_files
        self.progress = progress
        self.created_at = created_at
        self.updated_at = updated_at
        # Total pages against each file.
        self._total_files: 'dict[str, int]' = {}
        self._in_process_files: 'dict[str, list[str]]' = {}
        self._doc_count = 0

    @property
    def to_dict(self) -> str:
        """Converts the class into dictionary."""
        return {
            'id': self.id,
            'status': self.status.name,
            'reason': self.reason,
            'files': self.files,
            'completedFiles': self.completed_files,
            'progress': self.progress,
            'createdAt': self.created_at,
            'updatedAt': self.updated_at,
        }

    def processed_file(self, file_path: str, page_number: str) -> bool:
        """Determines whether a file has been completely processed or not."""
        if file_path not in self._in_process_files:
            self._in_process_files[file_path] = []
        self._in_process_files[file_path].append(page_number)

        # print("is file complete ", self._in_process_files, self._total_files)

        if len(self._in_process_files[file_path]) == self._total_files[file_path]:
            self.completed_files.append(file_path)
            return True
        return False

    def add_file_page_count(self, file_path: str, page_count: str):
        """Assigns number of pages to a file."""
        if file_path not in self.files:
            self.files.append(file_path)
        if file_path not in self._total_files:
            self._total_files[file_path] = int(page_count)

    def has_file(self, file_name: str) -> bool:
        """Check if a file exists in a job."""
        logger.debug(self.files, file_name)
        return file_name in self.files

    def is_done(self) -> bool:
        """Returns if the job is done."""
        # print("is job done", self.files, self.completed_files)
        return len(self.files) == len(self.completed_files)

    @property
    def get_progress(self) -> float:
        progress = (len(self.completed_files) / len(self.files)) * 100
        print("progress", progress)
        return progress
