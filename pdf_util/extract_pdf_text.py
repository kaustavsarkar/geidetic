
from pypdf import PdfReader
import sys
import os

def extract_text(pdf_path, output_path):
    print(f"Reading {pdf_path}...")
    reader = PdfReader(pdf_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, page in enumerate(reader.pages):
            text = page.extract_text(extraction_mode="layout")
            f.write(text)
            f.write('\n')
            f.write(f"\n--- PAGE {i+1} ---\n\n")

if __name__ == "__main__":
    pdf_path = "/Users/kaustavsarkar/Desktop/Work/ain/code/geidetic/constitution_data/data/schedules.pdf"
    output_path = "/Users/kaustavsarkar/Desktop/Work/ain/code/geidetic/constitution_data/temp_schedules.txt"
    extract_text(pdf_path, output_path)
    print(f"Extracted text to {output_path}")
