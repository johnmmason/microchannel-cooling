#!/bin/python3
from flask import Flask, render_template
from config import title
app = Flask(title)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template(
        "404.jinja2",
        title=title,
        template="base",
        proxy='',
    ), 404

# routes follow
from model.api import model
from gui.api import gui
gui.appcontext = app.app_context()
app.register_blueprint(model, url_prefix='/model')
app.register_blueprint(gui, url_prefix='/')

# dashapp example
from gui.naive_app import make_naive_app
from gui.opt import make_naive_app_opt
with app.app_context():
    app = make_naive_app(app, '/naive/')
    app = make_naive_app_opt(app, '/opt/')


@app.route("/")
def hello_world():
    return render_template(
        "main.jinja2",
        title=title,
        template="main",
        proxy='',
        filler="",
    ), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
