import os
from typing import Any
import streamlit as st
from PIL import Image
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

from ain.db.db_operation import get_file_path

FAV_ICON = 'favicon.ico'
path = os.path.join(os.getcwd(), 'ain', 'assets', FAV_ICON)
image = Image.open(path)
st.set_page_config(
    page_title='AIN',
    page_icon=image
)

query_text = st.text_input(label='Search Docs')


def find_results(saerch_text: str) -> 'list[dict[str, Any]]':
    """Finds results from the index."""
    ix = open_dir("my_search_index")
    search_result: ' list[dict[str, Any]]' = []
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(saerch_text)
        results = searcher.search(query, limit=None)
        for hit in results:
            # path is the path along with page number.
            path = hit['path']
            path_without_extension = os.path.splitext(
                os.path.basename(path))[0]
            page_no_file_name = path_without_extension.split('#')
            page_number = page_no_file_name[0]
            file_name = page_no_file_name[1]
            file_path = get_file_path(file_name)
            # print(file_path)
            if file_path is None:
                return
            flag = False
            for pdfs in search_result:
                if pdfs['file_path'] == file_path:
                    pdfs['pages'].append(page_number)
                    flag = True
            if flag is False:
                search_result.append(
                    {'file_path': file_path, 'pages': [page_number]})
    return search_result


if query_text:
    print('searching for', query_text)
    search_results = find_results(query_text)
    print(len(search_results))
    if search_results:
        st.write('---')
        cols = st.columns(4, gap='large')
        result = search_results[0]
        file_name = result['file_path']
        page_numbers = result['pages']
        st.caption(f'{file_name}')
        st.markdown(f'{page_numbers}')
        for idx in range(len(search_results)-1):
            i = idx % 4
            if i == 0:
                st.write('---')
                cols = st.columns(4, gap='large')
            with cols[i]:
                result = search_results[idx]
                file_name = result['file_path']
                page_numbers = result['pages']
                st.caption(f'{file_name}')
                st.markdown(f'{page_numbers}')
