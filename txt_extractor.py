import os
import concurrent.futures
import threading
import langdetect
import pymupdf

root_dir = 'raw_data/output'  # PDF source dir
txt_output_dir = 'txt_data'  # where extracted text files should be saved

all_pdf_paths: set = set([])
non_en_files = []
err_files = []
empty_files = []
lock = threading.Lock()


def walk_dir_for_pdfs(dir_name):
    for dir_path, dir_names, file_names in os.walk(dir_name):
        pdfs = filter(lambda f: f.endswith('.pdf'), file_names)
        all_pdf_paths.update([os.path.join(dir_path, f) for f in pdfs])
        for dir_name in dir_names:
            walk_dir_for_pdfs(os.path.join(dir_path, dir_name))


def extract_txt(pdf_path, out_dir):
    try:
        stat_res = os.stat(pdf_path)
        if stat_res.st_size == 0:
            with lock:
                empty_files.append(pdf_path)
            return
        doc: pymupdf.Document = pymupdf.open(pdf_path)
        name: str = os.path.splitext(os.path.basename(pdf_path))[0]
        name = name.replace(' ', '_')
        out_path = os.path.join(out_dir, f'{name}.txt')
        # print(f'Extracting {pdf_path} to {out_path}')
        is_non_en = False
        with open(out_path, 'wt') as f:
            for page in doc.pages():
                text: str = page.get_textpage().extractText()
                lang = langdetect.detect(str(text))
                if page.number > 0 and lang != 'en' and not is_non_en:
                    with lock:
                        non_en_files.append(f'{pdf_path},{lang}')
                    is_non_en = True
                f.write(text)
                # f.write(bytes((12,)))  # page delim, form feed 0x0c
                f.write('##EOP##\n')

        if is_non_en:
            os.remove(out_path)
    except Exception as e:
        with lock:
            err_files.append(f'{pdf_path}, ERROR:{e}')


def extract_txt_all():
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        print(f'Extracting text from {len(all_pdf_paths)} files...')
        for i, pdf_path in enumerate(all_pdf_paths):
            futures.append(executor.submit(extract_txt, pdf_path, txt_output_dir))

    concurrent.futures.wait(futures)

    print('Extraction completed.')

    non_en_files.sort()
    if non_en_files:
        with open('non_en_files.txt', 'w') as f:
            f.writelines('\n'.join(non_en_files))
    print(f'Non-English file count: {len(non_en_files)}')

    empty_files.sort()
    if empty_files:
        with open('empty_files.txt', 'w') as f:
            f.writelines('\n'.join(empty_files))
    print(f'Empty file count: {len(empty_files)}')

    err_files.sort()
    if err_files:
        with open('err_files.txt', 'w') as f:
            f.writelines('\n'.join(err_files))
    print(f'Error file count: {len(err_files)}')


def sample_detect(pdf_path):
    doc: pymupdf.Document = pymupdf.open(pdf_path)
    page: pymupdf.Page = doc.load_page(0)
    for page in doc.pages():
        text = page.get_textpage().extractText()
        lang = langdetect.detect(str(text))
        print(page.number, lang)


def main():
    global all_pdf_paths, root_dir
    walk_dir_for_pdfs(root_dir)
    all_pdf_paths: list = sorted(all_pdf_paths)
    extract_txt_all()

    # sample debug
    # test_path = 'raw_data/output/01-01-2023/14-03-2023 (English)_2127_2022_12_1502_42682_Judgement_14-Mar-2023.pdf'
    # sample_detect(test_path)
