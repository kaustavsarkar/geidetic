"""Main class to launch the application."""
from ain.app import App


def launch():
    """Launches Tkinter App."""
    app = App()
    app.launch_explorer()
    app.mainloop()


if __name__ == '__main__':
    launch()
