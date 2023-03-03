#!/bin/python3
from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route('/static/<path:path>')
def send_report(path):
    return send_from_directory('gui/static/', path)

# routes follow
from model.api import model
# from gui.api import gui
app.register_blueprint(model, url_prefix='/model')
# app.register_blueprint(gui, url_prefix='/')

@app.route("/")
def hello_world():
    return "<center><h1>Hello, World!</h1></center>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
