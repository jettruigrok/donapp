import random

from flask import Flask, url_for, jsonify
from flask import render_template, redirect

from donapp.getapps import start_selenium, get_qr_status

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
    app = start_selenium(id)
    qr = app.get_qr()
    app._last_qr = qr
    return render_template("qr.html", **locals())

@app.route('/qr_status/<id>')
def qr_status(id):
    status = get_qr_status(id)
    return jsonify(status)
