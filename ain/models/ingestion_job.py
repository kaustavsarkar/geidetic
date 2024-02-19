"""Contains models pertaining to ingestion job."""
from enum import Enum
from datetime import datetime


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

    @property
    def to_dict(self) -> str:
        """Converts the class into dictionary."""
        return self.__dict__

    def processed_file(self, file_path: str, page_number: str, total_pages: int) -> bool:
        """Determines whether a file has been completely processed or not."""
        if self._total_files[file_path] is None:
            self._total_files[file_path] = total_pages
        if self._in_process_files[file_path] is None:
            self._in_process_files[file_path] = []
        self._in_process_files[file_path].append(page_number)

        if len(self._in_process_files[file_path]) == self._total_files[file_path]:
            self.completed_files.append(file_path)
            return True
        return False
