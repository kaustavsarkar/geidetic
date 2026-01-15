from pypdf import PdfReader, PdfWriter
from pathlib import Path

INPUT_FILE_PATH = "example.pdf"
START_PAGE = 0
END_PAGE = 2
OUTPUT_DIR_PATH = "."
OUTPUT_FILE_PATH = "introduction.pdf"

def split_pdf_into_pages(input_pdf: str, output_dir: str):
    input_pdf_path = Path(input_pdf)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    reader = PdfReader(input_pdf_path)

    writer = PdfWriter()
    for i, page in enumerate(reader.pages, start=0):
        if i < START_PAGE or i > END_PAGE:
            continue
        writer.add_page(page)

    output_path = output_dir_path / OUTPUT_FILE_PATH
    with open(output_path, "wb") as f:
        writer.write(f)

    print(f"Split {len(reader.pages)} pages into {output_dir_path}")

# Example usage
split_pdf_into_pages(
    input_pdf=INPUT_FILE_PATH,
    output_dir=OUTPUT_DIR_PATH
)
