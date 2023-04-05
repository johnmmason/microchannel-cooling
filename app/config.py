title = "Microchannel Cooling"
base = 'http://localhost:5000'


layout_kwargs={'paper_bgcolor':'rgba(0,0,0,0)',
    'plot_bgcolor':'rgba(0,0,0,0)',
    'margin_l':0.25,
    'margin_r':0.0,
    'font': dict(color = '#192236'),}
gridcolor = dict(gridcolor = '#192236', zerolinecolor = '#192236')
line_kwargs={'line_color':"#BC2D29"}

def update_style(fig):
    fig.update_layout(**layout_kwargs)
    fig.update_yaxes(**gridcolor)
    fig.update_xaxes(**gridcolor)
    fig.update_traces(**line_kwargs)