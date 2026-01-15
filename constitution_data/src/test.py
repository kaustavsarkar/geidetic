

from parsers.schedules import extract_schedule

def test_extract_schedules():
    pdf_path = "data/schedules_split/Fourth_Schedule.pdf"
    schedules = extract_schedule(pdf_path)

if __name__ == "__main__":
   test_extract_schedules()