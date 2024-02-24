import math
from typing import Optional
import sqlite3
import uuid
from datetime import datetime
from sqlite3 import Connection
from ain.models import directory, ingestion_job

# Create a new SQLite database (or connect to an existing one)

CONN: Connection = sqlite3.connect('file_mapping.db', check_same_thread=False)


def create_tables():
    """Creates required tables."""
    cursor = CONN.cursor()

    # Create a table to store the file mappings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_mapping (
            id        INTEGER PRIMARY KEY,
            file_name TEXT    NOT NULL,
            file_path TEXT    NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS IngestionJobs (
            id       TEXT PRIMARY KEY,
            status   TEXT NOT NULL,
            reason   TEXT,
            files    TEXT,
            completedFiles TEXT,
            progress REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Commit the changes and close the database connection
    CONN.commit()


def close_database():
    """Closes the datavase."""
    if CONN:
        CONN.close()


def insert_file_mapping(file_name, file_path):
    """Inserts file name and path which has been processed.

    Args:
        file_name: Name of the file.
        file_path: path of the file.
    """
    cursor = CONN.cursor()

    cursor.execute(
        'INSERT INTO file_mapping (file_name, file_path) VALUES (?, ?)', (file_name, file_path))

    CONN.commit()


def get_file_path(file_name: str) -> Optional[str]:
    """Queries the database to fetch complete path for the file name.

    Args:
        file_name: Name of the file to be searched.
    """
    cursor = CONN.cursor()

    cursor.execute(
        'SELECT file_path FROM file_mapping WHERE file_name = ?', (file_name,))
    result = cursor.fetchone()

    if result:
        return result[0]

    return None


def list_all_files() -> 'list[directory.PdfMetadata]':
    """Queries database for all parsed pdfs."""
    cursor = CONN.cursor()

    cursor.execute('SELECT * FROM file_mapping')
    result = cursor.fetchall()
    pdfs: 'list[directory.PdfMetadata]' = []
    for row in result:
        pdf = directory.PdfMetadata.from_tuple(row)
        pdfs.append(pdf)
    return pdfs


def insert_new_job(files: 'list[str]') -> str:
    """Creates a new row for an ingestion job."""
    cursor = CONN.cursor()
    job_id = str(uuid.uuid1())
    cursor.execute(
        '''INSERT INTO 
            IngestionJobs (id, status, files, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?)''',
        (job_id, ingestion_job.JobStatus.STARTED.name, ','.join(files),
         datetime.now(), datetime.now()))

    CONN.commit()
    return job_id


def update_job_status(job_id: str, status: ingestion_job.JobStatus, reason: 'Optional[str]'):
    """Updates the provided job_id status to IN_PROGRESS."""
    cursor = CONN.cursor()
    if reason:
        cursor.execute('''
        UPDATE IngestionJobs
        SET status = ?, reason = ?, updated_at = ?
        WHERE id = ?
        ''', (status.name, reason, datetime.now(), job_id))
    else:
        cursor.execute('''
        UPDATE IngestionJobs
        SET status = ?, updated_at = ?
        WHERE id = ?
        ''', (status.name, datetime.now(), job_id))

    CONN.commit()


def update_job_progress(job_id: str, completed_files: 'list[str]', progress: float):
    """Updates job progress."""
    print("updating job progress", job_id, progress)
    cursor = CONN.cursor()
    files = ','.join(completed_files)
    cursor.execute('''
    UPDATE IngestionJobs
    SET completedFiles = ?, progress = ?, updated_at = ?
    WHERE id = ?
    ''', (files, progress, datetime.now(), job_id))

    CONN.commit()


def list_in_progress_jobs() -> 'Optional[list[ingestion_job.IngestionJob]]':
    """Lists all jobs in progress."""
    cursor = CONN.cursor()
    cursor.execute('''
    SELECT 
        id, status, reason, files, completedFiles, created_at, updated_at, progress 
        FROM IngestionJobs
    WHERE status = "IN_PROGRESS"
    ''')
    jobs = []
    for row in cursor:
        jobs.append(_map_row_to_job(row))

    return jobs


def get_job_details(job_id: str) -> Optional[ingestion_job.IngestionJob]:
    """Returns details about a job."""
    cursor = CONN.cursor()
    cursor.execute('''
    SELECT 
        id, status, reason, files, completedFiles, created_at, updated_at, progress
        FROM IngestionJobs
        WHERE id = ?
    ''', (job_id,))
    row = cursor.fetchone()
    if row:
        return _map_row_to_job(row)
    return None


def _map_row_to_job(row: any) -> ingestion_job.IngestionJob:
    job_id = row[0]
    status = ingestion_job.JobStatus.from_string(status=row[1])
    reason = row[2]
    files = str(row[3]).split(',')
    completed_files = str(row[4]).split(',')
    created_at = row[5]
    updated_at = row[6]
    progress = row[7]
    job = ingestion_job.IngestionJob(
        job_id=job_id, status=status, reason=reason,
        files=files, completed_files=completed_files,
        created_at=created_at, updated_at=updated_at,
        progress=progress)
    return job
