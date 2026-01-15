from markitdown import MarkItDown


def parse_pdf():
    mid = MarkItDown()
    mid.convert("schedules/First_Schedule.pdf")

    

if __name__ == "__main__":
    parse_pdf()