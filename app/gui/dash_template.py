from dash import Dash
import dash_bootstrap_components as dbc
from flask import render_template
from dash.long_callback import DiskcacheLongCallbackManager
import diskcache

template_kwargs = {
    'template':"main",
    'proxy':'',
    'display': r"""
{%app_entry%}
<footer>
    {%config%}
    {%scripts%}
    {%renderer%}
</footer>       """,
    'base': "dash_template.jinja2",
    'headcontent': r"""
{%metas%}
{%favicon%}
{%css%}             """,
    'title': '{%title%}',
    }



def new_app(server, prefix, **kwargs):
    template_kwargs.update(kwargs)
    with server.app_context(), server.test_request_context():
        app = Dash(__name__, server=server,
                   routes_pathname_prefix=prefix,
                   meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                #    external_stylesheets=[dbc.themes.BOOTSTRAP],
                   )
        app.index_string = render_template("blank.jinja2", **template_kwargs)
    return app

def new_app_opt(server, prefix, cache, **kwargs):
    template_kwargs.update(kwargs)
    with server.app_context(), server.test_request_context():
        app = Dash(__name__, server=server,
                   routes_pathname_prefix=prefix,
                   long_callback_manager=cache, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                #    external_stylesheets=[dbc.themes.BOOTSTRAP],
                   )
        app.index_string = render_template("blank.jinja2", **template_kwargs)
    return app