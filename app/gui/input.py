# make html includes automatically
from flask import render_template
import requests as rqs
from config import base

############ fields ############
# https://codepen.io/stevenkuipers/pen/OrRroX
def dropdown(name, items, **kwargs):
    default = {
        'c': "dropdown",
    } | kwargs
    
    hitems = "\n".join([rf"<li>{i}</li>" for i in items])
    return rf"""
<nav class="{default['c']}">
     <input id="toggle" type="checkbox" checked>
     <h2>{name}</h2>
   <ul>
     {hitems}
   </ul>
</nav>
"""

# https://uiverse.io/Satwinder04/ancient-sloth-30
def input(name, **kwargs):
    default = {
        'c': "input",
    } | kwargs
    return rf"""
<div class="input-container">
  <input placeholder="{name}" class="input-field {default['c']}" type="text">
  <label for="input-field" class="input-label">{name}</label>
  <span class="input-highlight"></span>
</div>
"""

def textarea(name, title="JSON Input", **kwargs):
    default = {
        'c': "textarea",
        'placeholder': 'Enter JSON here',
    } | kwargs
    return rf"""
<textarea type="text" id="{name}" name="{name}" class title="{title}"
minlength="10" maxlength="999999" style="width:98.2%; height: 250px;  padding: 1px; resize: vertical;" 
placeholder="{default['placeholder']}" style="width: 98%; ">
</textarea>
"""

# https://uiverse.io/WhiteNervosa/green-donkey-82
def toggle(name, **kwargs):
    default = {
        'c': "toggle",
    } | kwargs
    return rf"""
<div class="container {default['c']}">
    <input type="checkbox" id="{name}" style="display: none;">
    <label for="{name}" class="check">
        <svg width="18px" height="18px" viewBox="0 0 18 18">
            <path d="M 1 9 L 1 9 c 0 -5 3 -8 8 -8 L 9 1 C 14 1 17 5 17 9 L 17 9 c 0 4 -4 8 -8 8 L 9 17 C 5 17 1 14 1 9 L 1 9 Z"></path>
            <polyline points="1 9 7 14 15 4"></polyline>
        </svg>
        {name}
    </label>
</div>
"""


class Form():
    fields = []
    default_kwargs = {
        'template':"main",
        'proxy':'',
        'base':"layout.jinja2",
        'title':"Naive Method Input",
        'action':'',
        'method':'POST',
        'target':'_self',
        'submit':'Enter',
        }
    
    def __init__(self, fields, **kwargs):
        self.default_kwargs.update(kwargs)
        self.fields = fields
    
    def render(self, **kwargs):
        self.default_kwargs.update(kwargs)
        return render_template("form.jinja2", raster = self.fields, **self.default_kwargs)
    
def redirect_to(url):
    return rqs.post(f'{base}/redirect/{url}')
