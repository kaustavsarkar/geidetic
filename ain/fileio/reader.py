"""Handles interactions with the file system."""
from typing import List, Sequence
import os
import re
from multiprocessing import Process
import fitz
from ain.db.db_operation import insert_file_mapping


def find_pdfs_in(folder_path: str) -> List[str]:
    """Looks for pdf files inside the path."""
    pdf_files: List[str] = []

    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)) and filename.endswith('.pdf'):
            pdf_files.append(os.path.join(folder_path, filename))

    return pdf_files


def save_to_text_file(pdf_text, text_file_name):
    """Writes the text in the provided file name."""
    output_directory = "pdf_extracted_data"  # Replace with your desired directory
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    unique_filename = os.path.join(output_directory, text_file_name)

    with open(unique_filename, 'w', encoding="UTF-8") as file:
        file.write(pdf_text)


def parse_pdfs(pdf_paths: Sequence[str]):
    """Saves pdfs as text files.

    Iterates the list paths provided and saves each page of a
    pdf as a text file.
    """
    p = Process(target=_save, args=(pdf_paths, ), name="python_ain_pdf_parser")
    p.start()


def _save(pdf_paths: Sequence[str]):
    for file_path in pdf_paths:
        if file_path:
            pdf_document = fitz.Document(file_path)
            pdf_name = pdf_document.name
            pdf_name = os.path.splitext(os.path.basename(file_path))[0]
            pdf_name = re.sub(r'[^a-zA-Z0-9\s]', '', pdf_name)
            pdf_name = pdf_name.replace(' ', '_')
            insert_file_mapping(file_name=pdf_name,
                                file_path=pdf_document.name)
            for i in range(len(pdf_document)):
                page = pdf_document.load_page(i)
                pdf_text = page.get_text("text")
                text_file_name = str(i) + '#' + pdf_name + '.txt'
                save_to_text_file(pdf_text, text_file_name)
