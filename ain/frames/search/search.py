"""Search Frame for AIN.

The Tkinter frame contains the logic to perform the following actions.
1.
2.
3.
"""

import customtkinter as ctk
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.index import open_dir


class Search(ctk.CTkFrame):
    """Implements the Search Frame."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # add search input and button
        self._search_input = ctk.CTkEntry(
            self, placeholder_text="type here to search",
            width=400, height=50)
        self._search_input.grid(row=0, column=0, padx=10, pady=10)
        self._schema = Schema(path=ID(stored=True), content=TEXT)

        # Search button.
        self._search_button = ctk.CTkButton(
            self, text="Search", command=self.perform_search)
        self._search_button.grid(row=0, column=1, padx=10, pady=10)

    def perform_search(self):
        """Performs search on the database."""
        query_text = self._search_input.get()
        # search_result = []
        ix = open_dir("my_search_index", schema=self._schema)
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(query_text)
            results = searcher.search(query)
            for result in results:
                # The pattern is pageNumber#fileName
                file_info = result["path"]
                print(file_info)
