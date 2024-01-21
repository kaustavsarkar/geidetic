"""Main class to launch the application."""
import os
import threading
from PIL import Image
import webview
import flask
from ain.fileio import reader
from ain.processes.manager import ProcessManager

# from ain.pages import search

FAV_ICON = 'favicon.ico'
path = os.path.join(os.getcwd(), 'ain', 'assets', FAV_ICON)
app = flask.Flask(__name__)

window = None


@app.route('/list', methods=['GET'])
def list_directories():
    files = window.create_file_dialog(
        webview.OPEN_DIALOG, allow_multiple=True, file_types={'PDF Files(*.pdf)'})
    reader.parse_pdfs(files)
    return {'files': list(files)}, 200


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
    return response


def get_entrypoint():
    def exists(path):
        print('checking index.html in ', os.path.join(
            os.path.dirname(__file__), path))
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists('frontend/dist/index.html'):  # unfrozen development
        return 'frontend/dist/index.html'

    if exists('Resources/frontend/dist/index.html'):  # frozen py2app
        return 'Resources/frontend/dist/index.html'

    if exists('frontend/dist/index.html'):
        return 'frontend/dist/index.html'

    raise Exception('No index.html found')


ENTRY = get_entrypoint()


def start_server():
    pm = ProcessManager.create_manager()
    pm.start_engine()
    app.run()


if __name__ == '__main__':
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    window = webview.create_window('ain', url=ENTRY, server=app)
    webview.start(debug=True)
