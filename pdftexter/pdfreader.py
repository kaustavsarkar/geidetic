import argparse
import os

import pdftotext

parser = argparse.ArgumentParser()
parser.add_argument("-i","--infile",help="the pdf file to read")
parser.add_argument("-o","--outfile",
	help="the text file to write output, e.g.: output.txt")
parser.add_argument("-f","--overwrite",
	help="whether program should overwrite existing out file",
	action="store_true")

pdf = None

def get_page_text(page:str) -> str:
	page_lines:[str] = []
	for line in page.split("\n"):
		l = line.strip()
		if l == "":
			continue  # skip blank lines
		try:
			int(l)
			continue  # skip page number lines
		except:
			pass
		page_lines.append(l)

	return "\n".join(page_lines)


def extract(pdf_file, out_file):
	page_texts = []

	print(f"Extracting text from {pdf_file}")
	with open(pdf_file, "rb") as f:
		pdf = pdftotext.PDF(f)
		for page in pdf:
			page_texts.append(get_page_text(page))
	print(f"Extracted {len(page_texts)} pages")

	print(f"Writing text to {out_file}")
	with open(out_file, "w") as f:
		f.writelines(page_texts)


def main(args:argparse.Namespace):
	if not args.infile or not args.outfile:
		parser.print_usage()
		exit(1)

	if not os.path.exists(args.infile):
		print(f"{args.infile} does not exist")
		exit(1)

	if os.path.exists(args.outfile) and not args.overwrite:
		print(f"{args.outfile} exists, specify -f to overwrite")
		exit(1)

	extract(args.infile, args.outfile)


if __name__ == "__main__":
	main(parser.parse_args())
