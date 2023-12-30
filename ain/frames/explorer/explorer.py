"""Explorer frame for AIN.

The Tkinter Frame contains the logic to perform following actions.
1. Find PDFs.
2. Show selected PDFs.
3. Search PDFs.
"""
import os
from tkinter import filedialog, END
import customtkinter
from PIL import Image, ImageTk
from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from ain.fileio.reader import find_pdfs_in, parse_pdfs
from ain.db.db_operation import get_file_path
from ain.pdf_viewer.PDFMiner import PDFMiner


class Explorer(customtkinter.CTkFrame):
    """Implements Explorer Frame."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        screen_width = master.winfo_screenwidth()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.rowconfigure(1, weight=1)
        self.rowconfigure(3, weight=1)

        self.selected_dir = ''

        # add widgets to app
        self.button = customtkinter.CTkButton(
            self, command=self.browse, text='Select a folder')
        self.button.grid(row=0, column=0, padx=10, pady=10)

        self.textbox = customtkinter.CTkTextbox(
            master=self, 
            width=(screen_width * master.scale_factor), 
            corner_radius=0)
        self.textbox.grid(row=1, column=0, sticky="nsew")
        self.textbox.insert("0.0", "Pdfs\n")

        # add search input 
        self.search_input = customtkinter.CTkEntry(
            self, placeholder_text="type here to search")
        self.search_input.grid(row=2, column=0, padx=10, pady=10)
        self.search_input.bind('<Return>', (lambda event: self.perform_search()))

        self.pdf_viewer_frame = customtkinter.CTkFrame(self)
        self.pdf_viewer_frame.grid(row=3, sticky='ew', padx = 10)

    def browse(self):
        folder_path = filedialog.askdirectory(
            title='Select a directory to index')
        if folder_path:
            self.selected_dir = folder_path
        return

    def list_pdfs(self):
        pdf_paths = find_pdfs_in(self.selected_dir)

        # clear textbox contents before showing any further details
        self.textbox.delete('1.0', END)
          
        for path in pdf_paths:
            self.textbox.insert("end", path + "\n")
        parse_pdfs(pdf_paths)

    def button_click2(self):
        print("button click")
        return

    def perform_search(self):
        for widget in self.pdf_viewer_frame.winfo_children():
            widget.destroy()
        query_text = self.search_input.get()
        search_result = []
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
                if file_path is None:
                    return
                flag = False
                for pdfs in search_result:
                    if pdfs['file_path'] == file_path:
                        pdfs['pages'].append(page_no)
                        flag = True
                if flag is False:
                    search_result.append(
                        {'file_path': file_path, 'pages': [page_no]})

        self.show_results(search_result)

    def show_results(self, search_results):
        if len(search_results) > 0:
            # creating the  frame
            self.result_frame = customtkinter.CTkFrame(self.pdf_viewer_frame)
            # # placing the frame using inside main window using pack
            self.result_frame.pack(fill='both', expand=True)
            # # Create a scrollbar and link it to the canvas
            # self.scrollbar_pdf_list = customtkinter.CTkScrollbar(self.pdf_viewer_frame, orientation="vertical", command=self.result_frame.yview)
            # self.scrollbar_pdf_list.grid(row=0,column=1,sticky='ns')
            # self.result_frame.configure(yscrollcommand=self.scrollbar_pdf_list.set)
            # creating a vertical scrollbar
            self.scrolly_pdf_list = customtkinter.CTkScrollbar(
                self.result_frame, orientation="vertical")
            # adding the scrollbar
            self.scrolly_pdf_list.grid(row=0, column=1, sticky='ns')
            # # creating a horizontal scrollbar
            # self.scrollx_pdf_list = customtkinter.CTkScrollbar(self.result_frame, orientation="horizontal")
            # # adding the scrollbar
            # self.scrollx_pdf_list.grid(row=1, column=0, sticky='we')
            # creating the canvas for display the PDF pages
            self.pdf_list_frame = customtkinter.CTkCanvas(
                self.result_frame, bg='#000000', width=560, height=435)
            # self.pdf_list_frame.configure(yscrollcommand=self.scrolly_pdf_list.set, xscrollcommand=self.scrollx_pdf_list.set)
            self.pdf_list_frame.grid(row=0, column=0)
            self.scrolly_pdf_list.configure(command=self.pdf_list_frame.yview)
        for result in search_results:
            pdf_path = result['file_path']
            file_name = os.path.splitext(os.path.basename(pdf_path))[0]
            result_data = customtkinter.CTkLabel(
                self.pdf_list_frame, text=file_name)
            result_data.pack()
            for page in result['pages']:
                page_no_in_pdf = customtkinter.CTkButton(self.pdf_list_frame, text=str(
                    page+1), command=lambda pdf_path=pdf_path, page=page, file_name=file_name: self.open_pdf_viewer(pdf_location=pdf_path, page_no=page, pdf_name=file_name))
                page_no_in_pdf.pack()

        region = self.pdf_list_frame.bbox(customtkinter.ALL)
        # making the region to be scrollable
        self.pdf_list_frame.configure(scrollregion=region)

    def on_frame_configure(self, event):
        self.result_frame.configure(scrollregion=self.result_frame.bbox("all"))

    def on_mousewheel(self, event):
        self.result_frame.yview_scroll(-1 * (event.delta // 120), "units")

    def open_pdf_viewer(self, pdf_location="", page_no=0, pdf_name=''):
        self.pdf_window = customtkinter.CTkToplevel(self)
        self.pdf_window.title(pdf_name)
        self.pdf_window.geometry("2100x1800")
        self.pdf_window.grid()
        # creating the top frame
        self.top_frame = customtkinter.CTkFrame(
            self.pdf_window, width=2000, height=1700)
        # placing the frame using inside main window using pack
        self.top_frame.pack(fill='both', expand=True)
        # creating the bottom frame
        self.bottom_frame = customtkinter.CTkFrame(
            self.pdf_window, width=1998, height=1698)
        # placing the frame using inside main window using pack
        self.bottom_frame.pack(fill='both', expand=True)
        # creating a vertical scrollbar
        self.scrolly = customtkinter.CTkScrollbar(
            self.top_frame, orientation="vertical")
        # adding the scrollbar
        self.scrolly.grid(row=0, column=1, sticky='ns')
        # creating a horizontal scrollbar
        self.scrollx = customtkinter.CTkScrollbar(
            self.top_frame, orientation="horizontal")
        # adding the scrollbar
        self.scrollx.grid(row=1, column=0, sticky='we')
        # creating the canvas for display the PDF pages
        self.output = customtkinter.CTkCanvas(
            self.top_frame, bg='#ECE8F3', width=1500, height=900)
        # inserting both vertical and horizontal scrollbars to the canvas
        self.output.configure(yscrollcommand=self.scrolly.set,
                              xscrollcommand=self.scrollx.set)
        # adding the canvas
        self.output.grid(row=0, column=0)
        # configuring the horizontal scrollbar to the canvas
        self.scrolly.configure(command=self.output.yview)
        # configuring the vertical scrollbar to the canvas
        self.scrollx.configure(command=self.output.xview)

        # loading the button icons
        global leftarrow_icon
        global rightarrow_icon
        leftarrow_icon = ImageTk.PhotoImage(Image.open("left.png"))
        rightarrow_icon = ImageTk.PhotoImage(Image.open("right.png"))
        # creating an up button with an icon
        self.leftbutton = customtkinter.CTkButton(
            self.bottom_frame, image=leftarrow_icon, text='', command=self.previous_page)
        # adding the button
        self.leftbutton.grid(row=0, column=1, pady=8)
        # creating a down button with an icon
        self.rightbutton = customtkinter.CTkButton(
            self.bottom_frame, image=rightarrow_icon, text='', command=self.next_page)
        # adding the button
        self.rightbutton.grid(row=0, column=3, pady=8)
        # label for displaying page numbers
        self.page_label = customtkinter.CTkLabel(
            self.bottom_frame, text='page')
        # adding the label
        self.page_label.grid(row=0, column=4, padx=5)

        if pdf_location:
            # declaring the path
            self.path = pdf_location
            # extracting the pdf file from the path
            filename = os.path.basename(self.path)
            # passing the path to PDFMiner
            self.miner = PDFMiner(self.path, page_no=page_no)
            # getting data and numPages
            data, numPages = self.miner.get_metadata()
            # setting the current page to 0
            self.current_page = page_no
            # checking if numPages exists
            if numPages:
                # getting the title
                self.name = data.get('title', filename[:-4])
                # getting the author
                self.author = data.get('author', None)
                self.numPages = numPages
                # setting fileopen to True
                self.fileisopen = True
                # calling the display_page() function
                self.display_page()

    def display_page(self):
        # checking if numPages is less than current_page and if current_page is less than
        # or equal to 0
        if 0 <= self.current_page < self.numPages:
            # getting the page using get_page() function from miner
            self.img_file = self.miner.get_page(self.current_page)
            # inserting the page image inside the Canvas
            self.output.create_image(0, 0, anchor='nw', image=self.img_file)
            # the variable to be stringified
            self.stringified_current_page = self.current_page + 1
            # updating the page label with number of pages
            self.page_label['text'] = str(
                self.stringified_current_page) + ' of ' + str(self.numPages)
            # creating a region for inserting the page inside the Canvas
            region = self.output.bbox(customtkinter.ALL)
            # making the region to be scrollable
            self.output.configure(scrollregion=region)

    def next_page(self):
        # checking if file is open
        if self.fileisopen:
            # checking if current_page is less than or equal to numPages-1
            if self.current_page <= self.numPages - 1:
                # updating the page with value 1
                self.current_page += 1
                # displaying the new page
                self.display_page()

     # function for displaying the previous page
    def previous_page(self):
        # checking if fileisopen
        if self.fileisopen:
            # checking if current_page is greater than 0
            if self.current_page > 0:
                # decrementing the current_page by 1
                self.current_page -= 1
                # displaying the previous page
                self.display_page()
