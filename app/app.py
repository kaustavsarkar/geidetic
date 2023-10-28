import customtkinter
from frames.explorer.explorer import Explorer
import subprocess
from db.db_operation import create_table
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("2100x1800")
        self.title("Ain - Legal AI")

        self.grid_rowconfigure(1, weight=2)  # configure grid system
        self.grid_columnconfigure(1, weight=2)
        subprocess.run(['python', './app/search_engine.py'])
        create_table()
    

    def launch_explorer(self):
        self.explorer_frame = Explorer(master=self)
        self.explorer_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.explorer_frame.pack(pady=20)
