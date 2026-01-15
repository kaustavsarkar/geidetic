from pypdf import PdfReader

def check_part_ix(pdf_path):
    reader = PdfReader(pdf_path)
    for i in range(110, 145):  # Check pages around the expected gap
        if i >= len(reader.pages): break
        text = reader.pages[i].extract_text()
        if "PART IX" in text:
            print(f"Found PART IX candidate on page {i}")
            print(text[:200]) # print first 200 chars

if __name__ == "__main__":
    check_part_ix("/Users/kaustavsarkar/Desktop/Work/ain/code/geidetic/pdf_util/parts_articles.pdf")
