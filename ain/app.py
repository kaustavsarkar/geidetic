"""Implements the Tkinter App.

Usage:
```
    app = App()
    app.launch_explorer()
    app.mainloop()
```
"""
import traceback
from tkinter import messagebox
import customtkinter
from watchdog.observers.api import BaseObserver
from ain.frames.explorer.explorer import Explorer
from ain.frames.search.search import Search
from ain.db.db_operation import create_table
from ain.processes.manager import ProcessManager


class App(customtkinter.CTk):
    """Main app which runs the Tkinter."""

    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.geometry("2100x1800")
        self.title("Ain - Legal AI")

        self._search_frame: Search
        self._explorer_frame: Explorer

        self.grid_rowconfigure(1, weight=2)  # configure grid system
        self.grid_columnconfigure(1, weight=2)
        self._pm = ProcessManager.create_manager()
        self._indexer: BaseObserver = self._pm.start_engine()
        create_table()

    def launch_explorer(self):
        """Launch explorer frame."""
        self._explorer_frame = Explorer(master=self)
        self._explorer_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew")
        self._explorer_frame.pack(pady=20)

    def launch_search(self):
        """Launch search frame."""
        self._search_frame = Search(master=self)
        self._search_frame.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew")
        self._search_frame.pack(pady=20)

    def on_closing(self) -> None:
        """Triggered when the window is closed.

        The function ensures we clear up the resources being used by
        the application.
        """
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            # TODO kaustavsarkar: Add a logic to close all the background processes.
            # Stop indexer.
            try:
                if self._indexer.is_alive():
                    self._indexer.stop()
                # Stop ProcessManager.
                self._pm.close_all()
                # Stop Tkinter.
                self.destroy()
            except Exception:
                traceback.print_exc()
            finally:
                pass
