from time import sleep
from flask import Blueprint, request as rq, render_template, redirect
import requests as rqs
import json as js
from config import base

gui = Blueprint('gui', __name__)

data = None # global variables to store data (a bit hacky, but this way we should have a loading screen)
job = None

form = lambda x : """<div class="row center">
  <div class="text leftAnimate">
    <h1>
      """+x+"""
    </h1>
    <div style="min-height: 5vh; min-width: 50vw;">
    <!-- https://github.com/akhilsadam/compose-dev/blob/main/app/templates/io.jinja2 for more examples -->
    <form action="" method="post">
          <div style="display: flex; justify-content: space-evenly; width: 100%; margin-right:10px;">
              <i class="fa-solid fa-plus">add</i>
              <i class="fa-solid fa-arrows-spin">modify</i>
              <i class="fa-solid fa-xmark">delete</i>
          </div>
          <br>
          <div>   
              <textarea type="text" id="inpt" name="inpt" title="JSON Input"
              minlength="10" maxlength="999999" style="width:98.2%; height: 250px;  padding: 1px; resize: vertical;" 
              placeholder="{"L":0.1, "W":100e-6, "D":10e-6, "T_in":293, "T_w":373, "Q":100}" style="width: 98%; ">
              </textarea>
	        </div>
          <input type="submit" value="Submit">
        </form>
    </div>
  </div>
</div>"""
loading = """<div class="row center">
    <h1>
      Loading...
    </h1>
    </div>
"""


# https://blog.miguelgrinberg.com/post/dynamically-update-your-flask-web-pages-using-turbo-flask
@gui.route('/naive', methods=['GET','POST'])
def naive() -> str:
    if rq.method == 'POST':
        global data
        data = js.loads(rq.form['inpt'])
    return render_template(
        "blank.jinja2",
        template="main",
        proxy='',
    )
    # notice the following line is missing:
    # blank = form("Naive Method Input"),
    # this will come from the context_processor...

@gui.context_processor
def inject_naive():
    global data, job

    if data is None and job is None:
        return dict(blank = form("Naive Method Input"))
    
    elif data != None and job is None:
        job = '/model/naive', data
        return dict(blank = loading)
    
    else: # have job
        # start job
        res = rqs.post(f'{base}{job[0]}', json=job[1])
        sleep(5) # wait for 5 seconds
        # upon end
        job = None
        data = None
        return dict(blank = res.text)
