"""Main class to launch the application."""
import multiprocessing
import os
import re
import threading
import webbrowser
import webview
from flask import Flask, request
from ain.engine.search_engine import start_engine, init_engine, Engine
from ain.db.db_operation import create_tables
from ain.fileio import reader
from ain.models import ingestion_job
from ain.db import db_operation as db
from ain.logs.ain_logs import logger

FAV_ICON = 'favicon.ico'
path = os.path.join(os.getcwd(), 'ain', 'assets', FAV_ICON)
app = Flask(__name__)

window = None
search_engine: Engine


@app.route('/fetchPdfs', methods=['GET'])
def list_directories():
    """Lists the directories selected by the researcher."""
    files = window.create_file_dialog(
        webview.OPEN_DIALOG, allow_multiple=True, file_types={'PDF Files(*.pdf)'})
    files = [f for f in files if os.path.getsize(f) > 0]
    return {'files': list(files)}, 200


@app.route('/indexpdfs', methods=['POST'])
def index_pdfs():
    """Runs index job on the requested files."""
    files = request.get_json()['selectedFiles']
    reader.parse_pdfs(files)
    return '', 200


@app.route('/search', methods=['POST'])
def search_text():
    """Searches text in the database."""
    text = request.get_json()['searchString']
    logger.info('search string', text)
    results = search_engine.find_results(text)
    logger.info('Results for search', results)
    return results.to_json(), 200


@app.route('/openpdf', methods=['POST'])
def open_pdf():
    """Opens the pdf in the default browser."""
    file_path = request.get_json()['filePath']
    page_number = request.get_json()['pageNumber']
    file_url = 'file://'+file_path+'#page='+page_number
    is_successful = webbrowser.open(file_url)
    if is_successful:
        return '', 200

    return '', 500


@app.route('/jobs', methods=['POST'])
def list_jobs():
    """Lists ingestion jobs."""
    status = request.get_json()['status']
    jobs = None
    if status == ingestion_job.JobStatus.IN_PROGRESS.name:
        jobs = db.list_in_progress_jobs()
    response: 'list[str]' = []
    if not jobs:
        return '', 404

    for job in jobs:
        response.append(job.to_dict)
    logger.info('list job response length', len(response))
    return {'jobs': response}, 200


@app.route('/job', methods=['POST'])
def get_job():
    "Gets the job details"
    job_id = request.get_json()['id']
    job = db.get_job_details(job_id=job_id)

    if not job:
        return '', 404
    return job.to_dict, 200


@app.route('/pdfpath', methods=['POST'])
def get_pdf_path():
    "Gets the path of the PDF."
    pdf_name = request.get_json()['pdfName']
    pdf_name = re.sub(r'[^a-zA-Z0-9\s]', '', pdf_name)
    pdf_name = pdf_name.replace(' ', '_')
    file_path = db.get_file_path(file_name=pdf_name)

    if not file_path:
        return '', 404
    return {'path': file_path}, 200


@app.after_request
def after_request(response):
    """Allows CORS."""
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
    return response


def get_entrypoint():
    """Returns path of the generated html."""
    def exists(html_path):
        logger.info('checking index.html in ', os.path.join(
            os.path.dirname(__file__), html_path))
        return os.path.exists(os.path.join(os.path.dirname(__file__), html_path))

    if exists('frontend/dist/index.html'):  # unfrozen development
        return 'frontend/dist/index.html'

    if exists('Resources/frontend/dist/index.html'):  # frozen py2app
        return 'Resources/frontend/dist/index.html'

    if exists('frontend/dist/index.html'):
        return 'frontend/dist/index.html'

    raise FileNotFoundError('No index.html found')


ENTRY = get_entrypoint()


def start_server():
    """Starts the application server."""
    app.run()

def on_closing():
    logger.info('closing ain.')
    try:
        logger.info('closing observer.')
        if observer.is_alive():
            observer.stop()
            observer.join()
    except Exception as e:
        logger.error('Exception while closing file Observer', e)
    finally:
        logger.info('Oberserver closed.')

    try:
        logger.info('Closing indexer.')
        search_engine.close()
    except Exception as e:
        logger.error('Exception while closing the search engine', e)
    finally:
        logger.info('Indexer closed.')

    try:    
        logger.info('closing daemon.')
        if daemon.is_alive():
            daemon.join(timeout=1)
    except Exception as e:
        logger.error('Exception while closing daemon', e)
    finally:
        logger.info('closed daemon.')


if __name__ == '__main__':
    logger.info('inside init')
    multiprocessing.freeze_support()
    daemon = threading.Thread(target=start_server)
    daemon.daemon = True
    daemon.start()
    logger.info('started daemon thread.')

    logger.info('init engine')
    init_engine()
    create_tables()
    search_engine, observer = start_engine()
    window = webview.create_window('ain', url=ENTRY, server=app)
    window.events.closing += on_closing
    logger.info('start webview.')
    webview.start(debug=True)
