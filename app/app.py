import customtkinter
from frames.explorer.explorer import Explorer


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500")
        self.title("Ain - Legal AI")

        self.grid_rowconfigure(1, weight=2)  # configure grid system
        self.grid_columnconfigure(1, weight=2)


    def launch_explorer(self):
        self.explorer_frame = Explorer(master=self)
        self.explorer_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.explorer_frame.pack(pady=20)
