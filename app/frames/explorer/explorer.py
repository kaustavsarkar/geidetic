import customtkinter
# import pdftotext
from tkinter import filedialog
from PIL import Image
from PIL import ImageTk
from fileio.reader import find_pdfs_in
from fileio.reader import save_to_text_file
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from db.db_operation import insert_file_mapping
from db.db_operation import get_file_path
import fitz
import os
import re

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



    def browse(self):
        folder_path = filedialog.askdirectory(title='Select a directory to index')
        if folder_path:
            self.selected_dir = folder_path
        return
    
    def open_pdf(self,pdf_paths):
        for file_path in pdf_paths:
            if file_path:
                pdf_document = fitz.Document(file_path)
                pdf_name = pdf_document.name
                pdf_name = os.path.splitext(os.path.basename(file_path))[0]
                pdf_name = re.sub(r'[^a-zA-Z0-9\s]', '', pdf_name)
                pdf_name = pdf_name.replace(' ','_')
                insert_file_mapping(file_name=pdf_name,file_path=pdf_document.name)
                for i in range(len(pdf_document)):
                    page = pdf_document.load_page(i)
                    pdf_text = page.get_text("text")
                    text_file_name = str(i) + '#' + pdf_name + '.txt'
                    save_to_text_file(pdf_text, text_file_name )
                    
                    

    def list_pdfs(self):
        pdf_paths = find_pdfs_in(self.selected_dir)
        for path in pdf_paths:
            self.textbox.insert("end", path + "\n")
        self.open_pdf(pdf_paths)

    def button_click2(self):
        print("button click")
        return
    
    def perform_search(self):
        query_text = self.search_input.get()
        ix = open_dir("my_search_index")
        with ix.searcher() as searcher:
            query = QueryParser("content", ix.schema).parse(query_text)
            results = searcher.search(query)
            for hit in results:
                file_name = hit['path']
                file_name = os.path.splitext(os.path.basename(file_name))[0]
                file_name = file_name.split('.')[0]
                modified_file_name = file_name.split('#')
                page_no = int(modified_file_name[0])
                file_name = modified_file_name[1]
                file_path = get_file_path(file_name)
                self.open_pdf_viewer(file_path,page_no)


    def open_pdf_viewer(self,pdf_file, page_no):
        doc = fitz.Document(pdf_file)
        

        pdf_page = doc.load_page(page_no)
        pdf_image = pdf_page.get_pixmap()

        pil_image = Image.frombytes("RGB", [pdf_image.width, pdf_image.height], pdf_image.samples)
        photo = ImageTk.PhotoImage(pil_image)
        # Create a Canvas for scrolling
        canvas = customtkinter.CTkCanvas(self)
        canvas.grid(sticky='ew')

        # Create a Frame to hold the Label
        frame = customtkinter.CTkFrame(canvas)
        canvas.create_window((0, 0), window=frame, anchor=customtkinter.NW)

        label = customtkinter.CTkLabel(frame, image=photo)
        label.grid()

        # Add a scrollbar for the Canvas
        scrollbar = customtkinter.CTkScrollbar(self, orientation=customtkinter.VERTICAL)
        scrollbar.grid(sticky='ew')
        canvas.config(yscrollcommand=scrollbar.set)