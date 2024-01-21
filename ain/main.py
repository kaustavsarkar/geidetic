"""Main class to launch the application."""
import os
from time import time
import threading
from PIL import Image
import webview
from ain.processes.manager import ProcessManager

# from ain.pages import search

FAV_ICON = 'favicon.ico'
path = os.path.join(os.getcwd(), 'ain', 'assets', FAV_ICON)


class Api:
    def fullscreen(self):
        webview.windows[0].toggle_fullscreen()

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, 'w') as f:
            f.write(content)

    def ls(self):
        return os.listdir('.')


def get_entrypoint():
    def exists(path):
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists('frontend/dist/index.html'):  # unfrozen development
        return 'frontend/dist/index.html'

    if exists('Resources/frontend/dist/index.html'):  # frozen py2app
        return 'Resources/frontend/dist/index.html'

    if exists('frontend/dist/index.html'):
        return 'frontend/dist/index.html'

    raise Exception('No index.html found')


def set_interval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():  # executed in another thread
                while not stopped.wait(interval):  # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True  # stop if the program exits
            t.start()
            return stopped
        return wrapper
    return decorator


def launch():
    print(path)
    image = Image.open(path)
    pm = ProcessManager.create_manager()
    pm.start_engine()
    # search.open()


entry = get_entrypoint()


@set_interval(1)
def update_ticker():
    if len(webview.windows) > 0:
        webview.windows[0].evaluate_js(
            'window.pywebview.state.setTicker("%d")' % time())


if __name__ == '__main__':
    window = webview.create_window('ain', entry, js_api=Api())
    webview.start(update_ticker, debug=True)
