import json
import logging
import random

from flask import Flask, url_for, jsonify, Response,  render_template, redirect

from donapp.session import start_session, get_session


logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-7s] %(message)s')

app = Flask("donapp")
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/start/')
def start():
    id = str(hash(random.random()))
    return redirect(url_for("get_qr", id=id))

@app.route('/extract/<id>')
def get_qr(id):
    s = start_session(id)
    qr = s.get_qr()
    return render_template("qr.html", **locals())

@app.route('/qr_status/<id>')
def qr_status(id):
    s = get_session(id)
    status = s.get_qr_status()
    return jsonify(status)

@app.route('/prepare/<id>')
def prepare_download(id):
    get_session(id).start_scraping()
    return render_template("prepare.html", **locals())

@app.route('/scrape_status/<id>')
def scrape_status(id):
    s = get_session(id)
    status = s.get_progress()
    return jsonify(status)

@app.route('/download/<id>')
def download(id):
    return render_template("download.html", **locals())

@app.route('/downloadfile/<id>')
def download_file(id):
    s = get_session(id)
    with s.lock:
        assert s.status == "DONE"
        result = json.dumps(s.links)
        print(s.links)
    return Response(result, mimetype='application/json',
                    headers={'Content-Disposition':'attachment;filename=whatsapp.json'})

@app.route('/error/<id>')
def error(id):
    s = get_session(id)
    status = s.get_progress()
    return render_template("error.html", **status)