from typing import Optional
import sqlite3
from ain.models import directory

# Create a new SQLite database (or connect to an existing one)


def create_table():
    conn = sqlite3.connect('file_mapping.db')
    cursor = conn.cursor()

    # Create a table to store the file mappings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS file_mapping (
            id INTEGER PRIMARY KEY,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL
        )
    ''')

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()


def insert_file_mapping(file_name, file_path):
    conn = sqlite3.connect('file_mapping.db')
    cursor = conn.cursor()

    cursor.execute(
        'INSERT INTO file_mapping (file_name, file_path) VALUES (?, ?)', (file_name, file_path))

    conn.commit()
    conn.close()


def get_file_path(file_name: str) -> Optional[str]:
    """Queries the database to fetch complete path for the file name.

    Args:
        file_name: Name of the file to be searched.
    """
    conn = sqlite3.connect('file_mapping.db')
    cursor = conn.cursor()

    cursor.execute(
        'SELECT file_path FROM file_mapping WHERE file_name = ?', (file_name,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None


def list_all_files() -> 'list[directory.PdfMetadata]':
    """Queries database for all parsed pdfs."""
    conn = sqlite3.connect('file_mapping.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM file_mapping')
    result = cursor.fetchall()
    pdfs: 'list[directory.PdfMetadata]' = []
    for row in result:
        pdf = directory.PdfMetadata.from_tuple(row)
        pdfs.append(pdf)
    return pdfs
