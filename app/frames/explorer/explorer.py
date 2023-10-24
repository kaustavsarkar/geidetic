import customtkinter
from tkinter import filedialog
from fileio.reader import find_pdfs_in

from whoosh.qparser import QueryParser
from whoosh.index import open_dir

class Explorer(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.selected_dir = ''

        # add widgets to app
        self.button = customtkinter.CTkButton(self, command=self.browse, text='Select a folder')
        self.button.grid(row=0, column=0, padx=10, pady=10)

        self.button = customtkinter.CTkButton(self, command=self.list_pdfs, text='Find Pdfs')
        self.button.grid(row=0, column=1, padx=10, pady=10)

        self.textbox = customtkinter.CTkTextbox(master=self, width=400, corner_radius=0)
        self.textbox.grid(row=1, column=0, sticky="nsew")
        self.textbox.insert("0.0", "Pdfs\n")

         # add search input and button
        self.search_input = customtkinter.CTkEntry(self, placeholder_text="type here to search")
        self.search_input.grid(row=2, column=0, padx=10, pady=10)

        self.search_button = customtkinter.CTkButton(self, text="Search",command=self.perform_search)
        self.search_button.grid(row=2, column=1, padx=10, pady=10)

        # Create a text box to display search results
        self.result_text = customtkinter.CTkTextbox(self, wrap=customtkinter.WORD, width=100, height=100)
        self.result_text.grid(row=3, column=0, padx=10, pady=10,columnspan=2,sticky='ew')


    def browse(self):
        folder_path = filedialog.askdirectory(title='Select a directory to index')
        if folder_path:
            self.selected_dir = folder_path
        return
    

    def list_pdfs(self):
        pdf_paths = find_pdfs_in(self.selected_dir)
        for path in pdf_paths:
            self.textbox.insert("end", path + "\n")
    def button_click2(self):
        print("button click")
        return
    
    def perform_search(self):
        query_text = self.search_input.get()
        ix = open_dir("my_search_index")
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(query_text)
            results = searcher.search(query)
            self.result_text.delete(1.0, customtkinter.END)  # Clear previous results
            for hit in results:
                self.result_text.insert(customtkinter.END, hit['path'] + "\n")
                # Check if results is empty and display a message if it is
            if len(results) == 0:
                self.result_text.insert(customtkinter.END, "No results found\n")
