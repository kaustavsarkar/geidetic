import customtkinter
from tkinter import filedialog
from fileio.reader import find_pdfs_in


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


    def browse(self):
        folder_path = filedialog.askdirectory(title='Select a directory to index')
        if folder_path:
            self.selected_dir = folder_path
        return
    

    def list_pdfs(self):
        pdf_paths = find_pdfs_in(self.selected_dir)
        for path in pdf_paths:
            self.textbox.insert("end", path + "\n")
