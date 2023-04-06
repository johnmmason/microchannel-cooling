from dash import Dash
from flask import render_template

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


def new_app(server, prefix, cache=None, **kwargs):
    template_kwargs.update(kwargs)
    with server.app_context(), server.test_request_context():
        app = Dash(__name__, server=server,
                   routes_pathname_prefix=prefix,
                   long_callback_manager=cache, meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                   )
        app.index_string = render_template("blank.jinja2", **template_kwargs)
    return app