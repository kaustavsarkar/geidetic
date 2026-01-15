
import os
import re
from pathlib import Path
import pdfplumber
from pypdf import PdfWriter, PdfReader

def split_schedules_pdf(input_pdf_path, output_dir_path):
    """
    Splits a PDF containing schedules into individual PDF files for each schedule.
    Uses pdfplumber to detect headers based on font attributes (robust against text references).
    """
    input_path = Path(input_pdf_path)
    output_dir = Path(output_dir_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Identify Start Pages using pdfplumber
    print(f"Scanning {input_path} with pdfplumber...")
    
    schedule_starts = []
    ordinals = {"FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH", "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH"}
    
    with pdfplumber.open(input_path) as pdf:
        num_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            # Extract words with font info
            words = page.extract_words(extra_attrs=['fontname', 'size'])
            
            # Look for sequence [Ordinal, "SCHEDULE"] with specific font
            for j in range(len(words) - 1):
                w1 = words[j]
                w2 = words[j+1]
                
                t1 = w1['text'].upper()
                t2 = w2['text'].upper()
                
                # Clean t1: remove leading digits and brackets (e.g., "1[FIRST" -> "FIRST")
                t1_clean = re.sub(r'^[\d\[]+', '', t1)
                
                # Check text match
                if t2 == "SCHEDULE" and t1_clean in ordinals:
                    # Check font match
                    # Valid headers (from exploration) use 'CIDFont+F1'
                    # References use 'CIDFont+F3'
                    f1 = w1.get('fontname', '')
                    f2 = w2.get('fontname', '')
                    
                    if 'F1' in f1 and 'F1' in f2:
                        schedule_name = f"{t1} {t2}"
                        print(f"  Found Header '{schedule_name}' on page {i+1} (Font: {f1})")
                        
                        # Add if new (avoid duplicates on same page or finding same schedule again? 
                        # Usually schedules appear once. But some might span multiple files if we were combining?
                        # Here we assume one continuous block per schedule.)
                        
                        if not schedule_starts or schedule_starts[-1]['name'] != schedule_name:
                            schedule_starts.append({'name': schedule_name, 'page': i})
                        
                        # Found a header on this page, stop scanning this page to be efficient
                        # (Assume max one schedule start per page)
                        break

    # Add end sentinel
    schedule_starts.append({'name': 'END', 'page': num_pages})
    
    # 2. Split using pypdf (more efficient writer)
    print(f"Found {len(schedule_starts) - 1} schedules. Splitting...")
    
    reader = PdfReader(input_path)
    
    for i in range(len(schedule_starts) - 1):
        start_info = schedule_starts[i]
        end_info = schedule_starts[i+1]
        
        start_page = start_info['page']
        end_page = end_info['page'] 
        
        s_name = start_info['name']
        s_clean_name = s_name.replace(" ", "_").title()
        output_filename = f"{s_clean_name}.pdf"
        output_file_path = output_dir / output_filename
        
        print(f"Writing {output_filename} (Pages {start_page+1} to {end_page})...")
        
        writer = PdfWriter()
        for p_idx in range(start_page, end_page):
            writer.add_page(reader.pages[p_idx])
            
        with open(output_file_path, "wb") as f_out:
            writer.write(f_out)
            
    print("Done.")

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent 
    input_path = base_dir / "constitution_data/data/schedules.pdf"
    output_dir = base_dir / "constitution_data/data/schedules_split"
    
    split_schedules_pdf(str(input_path), str(output_dir))
