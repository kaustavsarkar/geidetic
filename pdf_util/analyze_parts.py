from pypdf import PdfReader
import re

def analyze_parts(pdf_path, output_txt_path):
    reader = PdfReader(pdf_path)
    print(f"Total pages: {len(reader.pages)}")
    
    # Pattern to match "PART" followed by Roman numerals, possibly followed by other text immediately
    part_pattern = re.compile(r"PART\s+(?P<roman>[IVXLCDM]+)", re.IGNORECASE)
    
    results = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        lines = text.split('\n')
        # Check first 5 lines
        for line in lines[:5]:
            match = part_pattern.search(line)
            if match:
                # We found a potential part header
                part_num = match.group('roman')
                # heuristic: 'PART' should be at the start of the line or very close
                if line.strip().upper().startswith("PART"):
                    print(f"Found {part_num} on page {i}: {line.strip()}")
                    results.append((i, part_num, line.strip()))
                    break 

    with open(output_txt_path, 'w') as f:
        for page_num, part_num, line_content in results:
            f.write(f"{page_num}|{part_num}|{line_content}\n")

if __name__ == "__main__":
    analyze_parts(
        "/Users/kaustavsarkar/Desktop/Work/ain/code/geidetic/pdf_util/parts_articles.pdf",
        "/Users/kaustavsarkar/Desktop/Work/ain/code/geidetic/pdf_util/parts_list.txt"
    )
