import re
from pathlib import Path
from pypdf import PdfReader, PdfWriter

VALID_PARTS = {
    "I", "II", "III", "IV", "IVA", "V", "VI", "VII", "VIII", 
    "IX", "IXA", "IXB", "X", "XI", "XII", "XIII", "XIV", "XIVA", 
    "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII"
}

def clean_roman(candidate: str):
    """
    Tries to find a valid part number at the start of the candidate string.
    e.g. "IICI" -> "II"
    "XIXMISCELLANEOUS" -> "XIX"
    """
    candidate = candidate.upper()
    # Try usually longest match first? 
    # Or just iterate decreasing length.
    for i in range(len(candidate), 0, -1):
        sub = candidate[:i]
        if sub in VALID_PARTS:
            return sub
    return None

def split_pdf_by_parts(input_pdf_path: str, output_dir: str):
    input_path = Path(input_pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    print(f"Processing {input_path} with {total_pages} pages...")

    # Regex: Look for "PART" 
    part_pattern = re.compile(r"PART\s+(?P<roman>[A-Za-z]+)", re.IGNORECASE)

    parts_found = [] 

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        lines = text.split('\n')
        # Check first 10 lines
        for line in lines[:10]:
            # Simplify line for merged text check
            # e.g. "1[PART IX...]" -> remove "1[" prefix if rare, 
            # or just look for PART inside the line.
            match = part_pattern.search(line)
            if match:
                raw_roman = match.group('roman')
                
                # Try to clean/validate
                valid_roman = clean_roman(raw_roman)
                
                if valid_roman:
                    parts_found.append((i, valid_roman))
                    print(f"  Page {i}: Found PART {valid_roman} (raw: {raw_roman}) in line: '{line.strip()[:60]}...'")
                    break 

    # Filter and Sort
    # We want unique parts. We assume they appear in order, but running headers might cause repeats.
    # We only care about the *first* appearance of a Part (Start Page).
    
    parts_found.sort(key=lambda x: x[0])
    
    final_parts = []
    seen_parts = set()
    
    for page_idx, part_name in parts_found:
        if part_name not in seen_parts:
            # Verify order? 
            # Sometimes headers might appear out of nowhere?
            # Assuming the document is in order.
            final_parts.append((page_idx, part_name))
            seen_parts.add(part_name)

    print(f"Identified {len(final_parts)} unique parts start points.")

    for i in range(len(final_parts)):
        start_page, part_name = final_parts[i]
        
        # End page determination
        if i < len(final_parts) - 1:
            end_page = final_parts[i+1][0]
        else:
            end_page = total_pages
            
        writer = PdfWriter()
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
            
        out_filename = f"Part_{part_name}.pdf"
        out_file = output_path / out_filename
        
        with open(out_file, "wb") as f:
            writer.write(f)
            
        print(f"  Saved {out_filename}: Pages {start_page} to {end_page-1} ({end_page - start_page} pages)")

if __name__ == "__main__":
    split_pdf_by_parts(
        input_pdf_path="parts_articles.pdf",
        output_dir="parts_split"
    )
