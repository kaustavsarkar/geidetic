from typing import List
import os
import fnmatch


def find_pdfs_in(folder_path: str) -> List[str]:
    pdf_files: List[str] = []

    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)) and filename.endswith('.pdf'):
            pdf_files.append(os.path.join(folder_path, filename))

    return pdf_files

def save_to_text_file(pdf_text, text_file_name):
        output_directory = "pdf_extracted_data"  # Replace with your desired directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        unique_filename = os.path.join(output_directory, text_file_name)

        with open(unique_filename, 'w') as file:
            file.write(pdf_text)
