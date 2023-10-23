from typing import List
import os
import fnmatch


def find_pdfs_in(folder_path: str) -> List[str]:
    pdf_files: List[str] = []

    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)) and filename.endswith('.pdf'):
            pdf_files.append(os.path.join(folder_path, filename))

    return pdf_files
