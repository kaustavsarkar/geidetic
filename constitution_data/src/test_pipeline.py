from db_manager import DatabaseManager
import os
from tqdm import tqdm
import traceback

from loader import load_parts, load_schedules
from processors import process_part, process_schedule, embed_text
from models.model import Part
from query_manager import search_query



# ---------------------------
# Ingest Constitution Data
# ---------------------------

def ingest_constitution(db_manager: DatabaseManager):
    """Ingest all constitution data (parts and schedules) from training_data folder."""
    
    # Determine the data directory path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "training_data")
    
    all_rows = []
    
    print("=" * 50)
    print("Loading Parts...")
    print("=" * 50)
    
    parts: list[Part] = load_parts(data_dir)
    print(f"Loaded {len(parts)} parts")
    
    for part in tqdm(parts, desc="Processing Parts"):
        source_file = f"{part.name.lower().replace(' ', '_')}.json"
        try:
            rows = process_part(part, source_file)
            all_rows.extend(rows)
            print(f"  {part.name}: {len(rows)} rows")
        except Exception as e:
            traceback.print_exc()
            print(f"  Error processing {part.name}: {e}")
    
    print("\n" + "=" * 50)
    print("Loading Schedules...")
    print("=" * 50)
    
    schedules = load_schedules(data_dir)
    print(f"Loaded {len(schedules)} schedules")
    
    for schedule in tqdm(schedules, desc="Processing Schedules"):
        source_file = f"{schedule.name.lower().replace(' ', '_')}.json"
        try:
            rows = process_schedule(schedule, source_file)
            all_rows.extend(rows)
            print(f"  {schedule.name}: {len(rows)} rows")
        except Exception as e:
            print(f"  Error processing {schedule.name}: {e}")
    
    print("\n" + "=" * 50)
    print(f"Total rows to ingest: {len(all_rows)}")
    print("Writing to LanceDB...")
    print("=" * 50)
    
    table = db_manager.get_table()
    table.add(all_rows)
    
    print("\n✓ Constitution ingestion complete!")
    print(f"  Parts processed: {len(parts)}")
    print(f"  Schedules processed: {len(schedules)}")
    print(f"  Total rows: {len(all_rows)}")



# ---------------------------
# MAIN
# ---------------------------


def verify_loading():
    # Adjust path to training_data relative to this script
    # Script is in constitution_data/src
    # Data is in constitution_data/training_data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "training_data")
    
    print(f"Loading data from: {data_dir}")
    
    parts = load_parts(data_dir)
    print(f"Loaded {len(parts)} Parts.")
    if parts:
        sample_part = parts[0]
        print(f"Sample Part: {sample_part.name} - {sample_part.heading}")
        print(f"  Articles: {len(sample_part.articles)}")
        print(f"  Chapters: {len(sample_part.chapters)}")
        
    schedules = load_schedules(data_dir)
    print(f"Loaded {len(schedules)} Schedules.")
    if schedules:
        for sch in schedules:
            print(f"Schedule: {sch.name}")
            if sch.parts:
                print(f"  Has {len(sch.parts)} parts")
            if sch.flat_entries:
                print(f"  Has {len(sch.flat_entries)} flat entries")
                # Check type of first entry
                print(f"  Entry Type: {type(sch.flat_entries[0])}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        db_manager = DatabaseManager()
        # Run ingestion
        ingest_constitution(db_manager)
    elif len(sys.argv) > 1:
        # Run query
        query = sys.argv[1]
        search_query(query)
    else:
        # Run verification by default
        verify_loading()

