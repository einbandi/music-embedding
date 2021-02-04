import dash
import dash_core_components as dcc
from dash_core_components.RadioItems import RadioItems
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_audio_components as dac
import plotly.express as px
import plotly.graph_objects as go
import flask

import pandas as pd
import numpy as np
import interval

df = pd.read_csv('starless_mfcc.csv')
df['Channel'] = ['Left' if a else 'Right' for a in df['algo']]

n_frames = len(df)
sr = 22050
frame_len = 2**15
hop_len = 2**13


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

scatter = px.scatter(df,
    x='x',
    y='y',
    color='Channel',
    color_discrete_sequence=px.colors.qualitative.D3,
    custom_data=['frame_id'],
    width=900,
    height=900,
    labels={
        'x': '',
        'y': ''
    }
)
scatter.update_layout(
    plot_bgcolor='rgb(250,250,250)',
    legend={
        'x': 0.85,
        'y': 0.95,
        'bgcolor': 'rgb(250,250,250)'
    }
)

def make_range_plot(indices):
    bars = np.zeros(len(df)//2)
    bars[indices] = 1
    rangeplot = px.imshow([bars],
        color_continuous_scale=['white', 'gray'],
        # width=400,
        # height=50,
        aspect='auto',
        zmin=0,
        zmax=1
    )
    rangeplot.update_traces(showscale=False)
    return rangeplot

app.layout = html.Div([
    html.H1(id='title', children='Music Embedding'),
    dcc.Graph(id='scatter',
        figure=scatter,
        selectedData={'points': []},
        style={'backgroundColor': None}
    ),
    html.Div(id='audio'),
    dcc.Graph(id='timerange',
        figure=make_range_plot([])
    )
    # dac.DashAudioComponents(
    #     id='audio-player',
    #     src='static/starless.mp3',
    #     autoPlay=False,
    #     controls=True,
    #     height='100px',
    #     currentTime=0
    # ),
    # html.Button('Jump to 1:00', id='jump-button', n_clicks=0)
    #dcc.Graph(id='timebars', )
])

@app.callback(
    Output('timerange', 'figure'),
    Input('scatter', 'selectedData'))
def update_timerange_and_audio(selection):
    if selection is None:
        return make_range_plot([])
    else:
        new_indices = [p['customdata'][0] for p in selection['points']]
        return make_range_plot(new_indices)

@app.callback(
    Output('audio', 'children'),
    Input('scatter', 'clickData'))
def update_audio(clicked):
    if clicked is None:
        return []
    else:
        source = 'static/frames/frame-{:04d}.wav'.format(
            clicked['points'][0]['customdata'][0])
        return html.Audio(src=source, controls=True)
        

if __name__ == '__main__':
    app.run_server(debug=True)