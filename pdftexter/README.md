## PDF Reader (text extraction)

#### Dependencies

- Script uses [pdftotext](https://pypi.org/project/pdftotext/) py library. Follow the instructions to install pdftotext
  in your environment before proceeding

#### Usage

```shell
python pdfreader.py -h
usage: pdfreader.py [-h] [-i INFILE] [-o OUTFILE] [-f]

options:
  -h, --help            show this help message and exit
  -i INFILE, --infile INFILE
                        the pdf file to read
  -o OUTFILE, --outfile OUTFILE
                        the text file to write output, e.g.: output.txt
  -f, --overwrite       whether program should overwrite existing out file
```

To process multiple files (assuming files are in data/ dir):
```shell
for i in `ls -1 data/*.pdf`; do python pdfreader.py -i $i -o data/`basename -s .pdf $i`.txt;done
```