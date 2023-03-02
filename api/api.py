#!/bin/python3

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<center><h1>Hello, World!</h1></center>"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
