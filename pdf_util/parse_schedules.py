
import re
import json
import os

def parse_schedules(text_file_path, output_path):
    with open(text_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into pages
    raw_pages = re.split(r'--- PAGE \d+ ---', content)
    print(f"DEBUG: Found {len(raw_pages)} pages")
    
    pages_data = [] # List of { 'body': str, 'footnotes': {id: text} }

    # Regex for footnote separator
    footnote_sep = re.compile(r'_{10,}')
    
    # Process each page to separate body and footnotes
    for i, raw_page in enumerate(raw_pages):
        raw_page = raw_page.strip()
        if not raw_page:
            continue
            
        parts = footnote_sep.split(raw_page)
        body = parts[0]
        footnotes = {}
        
        if len(parts) > 1:
            fn_section = parts[1].strip()
            # Parse footnotes: "1. Text...", "2. Text..."
            # Sometimes footnotes span multiple lines.
            
            # Simple heuristic: Split by lookahead for number + dot or number + bracket
            # But footnotes here look like "1. Subs..." or "1. The words..."
            # markers in text are often "1[", "2[". The footnote list usually matches.
            
            fn_lines = fn_section.split('\n')
            current_fn_id = None
            current_fn_text = []
            
            for line in fn_lines:
                line = line.strip()
                if not line: continue
                
                # Match start of footnote "1. ", "2. ", "*", "**"
                match = re.match(r'^(\d+|[*]+)\s?[\.\)](.*)', line)
                if match:
                    if current_fn_id:
                        footnotes[current_fn_id] = " ".join(current_fn_text)
                    current_fn_id = match.group(1).strip('*') # Handle * as well if mapped
                    if not current_fn_id and '*' in match.group(0): current_fn_id = '*' # literal *
                    
                    if not current_fn_id: # fallback
                         current_fn_id = line.split('.')[0]
                         
                    text = match.group(2).strip()
                    current_fn_text = [text]
                else:
                    if current_fn_id:
                        current_fn_text.append(line)
            
            if current_fn_id:
                footnotes[current_fn_id] = " ".join(current_fn_text)

        # Cleanup Body: Remove headers
        # "THE CONSTITUTION OF INDIA (First Schedule) Name Territories 254"
        body_lines = body.split('\n')
        clean_lines = []
        for line in body_lines:
            line = line.strip()
            if "THE CONSTITUTION OF INDIA" in line: continue
            if re.match(r'^\d+$', line): continue # Page numbers like 253
            clean_lines.append(line)
        
        pages_data.append({
            'page_idx': i, # 0-indexed
            'body_lines': clean_lines,
            'footnotes': footnotes
        })

    # Now parsed stream
    output_entries = []
    
    current_schedule = None
    current_part = None
    current_entry = None
    
    # We need a continuous stream that still knows which page it came from
    # Stream items: {'text': line, 'page': i}
    stream = []
    for p in pages_data:
        if p['page_idx'] == 0:
            print(f"DEBUG: Page 0 lines: {len(p['body_lines'])}")
            for l in p['body_lines'][:5]:
                print(f"DEBUG: P0 Line: '{l}'")
        for line in p['body_lines']:
            stream.append({'text': line, 'page': p['page_idx']})

    # Regexes
    # Schedule: "FIRST SCHEDULE", "SECOND SCHEDULE", etc. 
    # Often enclosed in 1[...], e.g. "1[FIRST SCHEDULE"
    re_schedule = re.compile(r'(?:^|\s)(\d*\[)?(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)\s+SCHEDULE')
    
    re_part = re.compile(r'^(?:1\[)?(PART\s+[A-Z]+|Part\s+[A-Z]+|I\.|II\.|IIIA\.|IV\.|V\.)\s+(.+)$', re.IGNORECASE)
    
    # Entry: numbered list "1. Name", "2. Name"
    re_entry = re.compile(r'^(?:1\[|2\[)?(\d+)(\.|\])\s+(.+)$')

    processed_data = []

    def commit_entry():
        nonlocal current_entry
        if current_entry:
            # Post-process the text for amendments
            # Find [marker][...text...] or just marker[...text...]
            # This is complex because extraction might have broken brackets.
            # For now, just save as is.
            # Refine lookup of footnotes: Scan full text for markers like `2[...]` or `1.`
            
            # The structure for user:
            # "text": The full text
            # "amendments": list of footnotes found in this text.
            
            raw_text = " ".join([t['text'] for t in current_entry['lines']])
            
            # Find amendment markers
            # Pattern 1: `N[...]` i.e. 2[The territories...]
            # Pattern 2: `N.` or `N` just superscripts (hard to detect in plain text without brackets)
            # The text file has `1[...]`, `2[...]`.
            
            amendments = []
            
            # Find all M[...] pattern
            # Group 1: Marker, Group 2: Content (greedy? no, balanced?)
            # Nested brackets are hard with regex. 
            # Simple approach: find Marker[ and assume it ends at next ]? Or balanced?
            # Given the text structure `2[The territories specified ... Act, 1959]`
            
            # Let's iterate over the segments from the lines to find footnotes from respective pages
            
            # Naive scan for footnotes used in this entry
            used_footnotes = set()
            
            # We iterate the collected lines to map them back to their pages
            # and verify if any markers exist.
            
            full_text_str = ""
            
            for line_obj in current_entry['lines']:
                line_text = line_obj['text']
                page_idx = line_obj['page']
                page_fns = pages_data[page_idx]['footnotes']
                
                # Check for markers in this line
                # Look for `(\d+)\[`
                matches = re.finditer(r'(\d+)(\[)', line_text)
                for m in matches:
                    marker = m.group(1)
                    if marker in page_fns:
                        # Construct amendment object
                        # Try to find span text? 
                        # For now, just link the footnote
                        amendments.append({
                            "marker": marker,
                            "scope": "ENTRY", # Default
                            "span_text": None, # Parsing exact span is hard without robust bracket matching
                            "footnote": page_fns[marker]
                        })
                
                full_text_str += line_text + " "
            
            final_entry = {
                "number": current_entry['number'],
                "name": current_entry['name'],
                "text": full_text_str.strip(),
                "amendments": amendments
            }
            
            # Add to parent
            # If part exists, add to part? User example has "part": "I. THE STATES".
            # It seems the JSONL row represents an ENTRY context.
            # The user example:
            # { "schedule": ..., "part": ..., "entries": [ {entry} ] }
            # Wait, the user example has "entries": [ ... ]. 
            # Does this mean one JSON object per Schedule or per Part?
            # "create a jsonl file which shall structure the data... so that one can identify all the schedules... entries..."
            # The example shows ONE object with "schedule", "part", "entries".
            # So I should emit one JSON object per Part (or Schedule if no Part).
            
            current_entry['final'] = final_entry

    # We need to structure output as hierarchy:
    # Schedule -> Part -> Entries
    
    root = []
    
    def get_or_create_schedule(title):
        if not root or root[-1]['schedule'] != title:
            root.append({'schedule': title, 'parts': []})
        return root[-1]
    
    def get_or_create_part(sched_obj, part_title):
        if not sched_obj['parts'] or sched_obj['parts'][-1]['name'] != part_title:
            sched_obj['parts'].append({'name': part_title, 'entries': []})
        return sched_obj['parts'][-1]
    
    # Loop lines
    current_sched_title = None
    current_part_title = None
    
    # Store lines buffer to detect multiline headers?
    # Simple line-by-line
    
    idx = 0
    while idx < len(stream):
        line_obj = stream[idx]
        text = line_obj['text']
        page = line_obj['page']
        
        # SCHEDULE
        s_match = re_schedule.search(text)
        if s_match:
            commit_entry()
            current_entry = None
            current_sched_title = text.strip() # Or cleaner title
            # Clean title: Remove 1[...] wrapper if present
            current_sched_title = re.sub(r'^\d+\[', '', current_sched_title).strip(']')
            current_part_title = None # Reset part
            idx += 1
            # Add implicit part if needed? Or wait for part line.
            continue
        
        # PART
        p_match = re_part.search(text)
        if p_match and current_sched_title:
            commit_entry()
            current_entry = None
            current_part_title = text.strip()
            # Clean if needed
            idx += 1
            continue
            
        # ENTRY
        # Entries usually start with "1. " or "2. "
        # Or have leading amendment marker "1[2.]"
        e_match = re_entry.search(text)
        if e_match and current_sched_title:
            commit_entry()
            
            num = e_match.group(1)
            # Name: The rest of the line?
            # In "1. Andhra Pradesh", Name is "Andhra Pradesh".
            # In "1. Delhi", Name is "Delhi".
            # Sometimes name and text are on same line?
            # "1. Andhra Pradesh The territories..." -> Name: Andhra Pradesh, Text: The territories...
            # We need to split name and text. usually separated by variable whitespace or just logic.
            # Heuristic: Name is usually short.
            
            rest = e_match.group(3).strip()
            
            # If rest is short (< 30 chars) assume it's Name.
            # If long, maybe Name + Text.
            # In the PDF layout, Name is col 1, Text is col 2.
            # pdftotext (python pypdf) might merge them with simple spaces.
            
            # Attempt to split name/text
            # "Andhra Pradesh   The territories..."
            # look for double space?
            
            name = rest
            content_start = ""
            
            # Common pattern in this file: Name is title case, Text starts with "The territories..."
            split_match = re.search(r'\s{2,}', rest)
            if split_match:
                name = rest[:split_match.start()]
                content_start = rest[split_match.end():]
            elif "The territories" in rest:
                # Split before "The territories"
                parts = rest.split("The territories", 1)
                name = parts[0].strip()
                content_start = "The territories" + parts[1]
            
            current_entry = {
                'number': int(num),
                'name': name,
                'lines': [{'text': content_start, 'page': page}] if content_start else []
            }
            idx += 1
            continue
        
        # If in entry, append line
        if current_entry:
            current_entry['lines'].append(line_obj)
        
        idx += 1
        
    commit_entry() # Last one

    # Convert to JSONL
    # Output format: one object per Part?
    # { "schedule": "FIRST SCHEDULE", "part": "I. THE STATES", "entries": [...] }
    
    with open(output_path, 'w', encoding='utf-8') as out:
        for sched in root:
            # If schedule has no parts, maybe create a default one?
            # Or formatted as requested.
            
            if not sched['parts']:
                # Maybe the whole schedule is one part or no part
                # Check user requirement: "part inside the schedules"
                # If no part, output null?
                
                # However, all entries are stored in parts in my logic.
                # If entries were found without a Part header, I need to handle that.
                # In current logic, if current_part_title is None, entries aren't added to root properly?
                # Wait, I didn't add the add-logic in the loop.
                pass
            
            # Actually, I haven't linked entries to root in the loop.
            # I must reconstruct the tree from the processed entries.
            # Wait, `commit_entry` updated `current_entry` but didn't push to `root`.
            pass

    # FIXED LOGIC:
    # Use a linear list of (Schedule, Part, Entry).
    # Then group by Schedule+Part.
    
    final_records = {} # Key: (Schedule, Part), Value: entries list
    
    # Re-run the commit logic but simpler
    # ... (omitted re-writing logic above, fixing below)

    # LET'S RE-IMPLEMENT THE LOOP TO POPULATE `root` DIRECTLY
    pass

# Redefined Loop Logic
    
    output_data = [] # List of {schedule, part, entries}
    
    curr_sched = None
    curr_part = None
    curr_entry_obj = None # API format
    
    entry_lines = []
    
    def finalize_entry():
        nonlocal entry_lines, curr_entry_obj
        if curr_entry_obj:
            # Build text and amendments
            full_text = ""
            
            for l in entry_lines:
                txt = l['text']
                full_text += txt + " "
            
            curr_entry_obj['text'] = full_text.strip()
            
            # Extract amendments line-by-line to ensure correct page footnote resolution
            amendments = []
            
            for l in entry_lines:
                txt = l['text']
                pid = l['page']
                page_fns = pages_data[pid]['footnotes']
                
                # 1. Strong markers: N[
                ms_strong = re.finditer(r'(\d+)\s*\[', txt)
                for m in ms_strong:
                    mk = m.group(1)
                    if mk in page_fns:
                        amendments.append({
                            "marker": mk,
                            "scope": "ENTRY",
                            "span_text": None,
                            "footnote": page_fns[mk]
                        })

                # 2. Heuristic markers: detached numbers
                all_nums = re.finditer(r'\b(\d+)\b', txt)
                for m in all_nums:
                    num_str = m.group(1)
                    if num_str not in page_fns:
                        continue
                        
                    # Avoid duplicates if captured by strong marker
                    # Check if this match position is start of a strong match?
                    # Simplify: deduplicate by marker ID later.
                    
                    # Context checks
                    start, end = m.span()
                    pre_text = txt[:start]
                    post_text = txt[end:]
                    
                    if len(num_str) == 4 and (num_str.startswith("19") or num_str.startswith("20")):
                        continue
                        
                    context_window = pre_text[-15:].lower() if len(pre_text) > 15 else pre_text.lower()
                    if re.search(r'(section|sect\.|s\.|act|no\.|article|art\.|clause|cl\.|entry)\s*$', context_window):
                        continue
                        
                    if re.match(r'\s*of\s+\d{4}', post_text):
                        continue
                    
                    # Also skip if followed immediately by [ (handled by strong)
                    if re.match(r'\s*\[', post_text):
                        continue
                        
                    amendments.append({
                        "marker": num_str,
                        "scope": "ENTRY",
                        "span_text": None,
                        "footnote": page_fns[num_str]
                    })
            
            # De-duplicate preserving order?
            # Or prioritize strong matches?
            # Just unique by marker ID.
            unique_amendments = []
            seen_mk = set()
            for a in amendments:
                if a['marker'] not in seen_mk:
                    unique_amendments.append(a)
                    seen_mk.add(a['marker'])
            curr_entry_obj['amendments'] = unique_amendments
            
            # Add to current container
            target = None
            for item in output_data:
                if item['schedule'] == curr_sched and item['part'] == curr_part:
                    target = item
                    break
            if not target:
                target = {'schedule': curr_sched, 'part': curr_part, 'entries': [], 'schedule_amendments': []}
                # Check for pending schedule amendments
                if pending_sched_amendments:
                     target['schedule_amendments'] = pending_sched_amendments
                output_data.append(target)
            
            target['entries'].append(curr_entry_obj)
            
        curr_entry_obj = None
        entry_lines = []

    print(f"DEBUG: Processing {len(stream)} lines")
    idx = 0
    pending_sched_amendments = [] # Store sched amendments to attach to first Part object
    
    while idx < len(stream):
        line_obj = stream[idx]
        text = line_obj['text'].strip()
        page = line_obj['page']
        
        # SCHEDULE
        s_match = re_schedule.search(text)
        if s_match:
            # print(f"DEBUG: Found Schedule: {text}")
            finalize_entry()
            curr_sched = text
            
            # Validates schedule amendments like "1[FIRST SCHEDULE"
            # Capture marker
            m_chk = re.match(r'^(\d+)\s*\[', curr_sched)
            pending_sched_amendments = []
            
            if m_chk:
                mk = m_chk.group(1)
                page_fns = pages_data[page]['footnotes']
                if mk in page_fns:
                    pending_sched_amendments.append({
                         "marker": mk,
                         "scope": "SCHEDULE",
                         "span_text": None,
                         "footnote": page_fns[mk]
                    })
            
            curr_sched = re.sub(r'^\d+\[', '', curr_sched).strip(']')
            curr_part = "NO PART" 
            idx += 1
            continue
            
        # PART
        p_match = re_part.search(text)
        if p_match: # and current_sched_title?
            print(f"DEBUG: Found Part: {text}")
            finalize_entry()
            curr_part = text
            # If we were in NO PART, we switch.
            idx += 1
            continue
            
        # ENTRY
        e_match = re_entry.search(text)
        # Avoid matching footnote references in text as entries (usually they are inside text)
        # Entry starts line.
        is_entry = False
        if e_match:
            # Check context: If we are deep in text, this might be a list inside an entry?
            # But "1." at start of line is strong signal.
            # Exception: "1." inside a table of content or something?
            # Assuming strictly formatted.
            
            num = e_match.group(1)
            # Check validity?
            is_entry = True
        
        if is_entry:
            # print(f"DEBUG: Found Entry: {num} in {curr_sched}")

            finalize_entry()
            
            rest = e_match.group(3).strip()
            
            # Split Name/Text
            # Priority: Look for large whitespace gap
            # "Andhra              2[The..."
            
            name = rest
            content = ""
            
            # Regex for Name followed by optional marker and Text
            # Name usually ends before a large space.
            # Marker might be "2[" or just "The..."
            
            split_match = re.search(r'\s{2,}', rest)
            
            if split_match:
                name = rest[:split_match.start()]
                content = rest[split_match.end():]
            elif "The territories" in rest:
                # If no large space, try specific keyword but be careful of markers
                # Check for "N[The territories" vs "Name The territories"
                # If "The territories" is present, split, but if preceding char is brackets, include them.
                
                # Find start of "The territories"
                idx_t = rest.find("The territories")
                # Look back for "2["
                # "Name 2[The territories"
                
                # Scan backwards from idx_t to find whitespace
                last_space = rest.rfind(' ', 0, idx_t)
                if last_space != -1:
                    potential_marker = rest[last_space+1:idx_t] # "2["
                    if re.match(r'\d+\[', potential_marker):
                        name = rest[:last_space].strip()
                        content = rest[last_space+1:]
                    else:
                         name = rest[:idx_t].strip()
                         content = rest[idx_t:]
                else:
                    name = rest[:idx_t].strip()
                    content = rest[idx_t:]

            curr_entry_obj = {
                "number": int(num),
                "name": name,
                "text": "", # Fill later
                "amendments": []
            }
            if content:
                entry_lines.append({'text': content, 'page': page})
            
            idx += 1
            continue
            
        # Text line
        if curr_entry_obj:
            entry_lines.append(line_obj)
        
        idx += 1
        
    finalize_entry()
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in output_data:
            f.write(json.dumps(item) + "\n")

if __name__ == "__main__":
    txt_path = "/Users/kaustavsarkar/Desktop/Work/ain/code/geidetic/constitution_data/temp_schedules.txt"
    jsonl_path = "/Users/kaustavsarkar/Desktop/Work/ain/code/geidetic/constitution_data/schedules.jsonl"
    parse_schedules(txt_path, jsonl_path)
