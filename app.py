import dash
import dash_core_components as dcc
from dash_core_components.RadioItems import RadioItems
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_audio_components as dac
import dash_player
import plotly.express as px
import flask

import pandas as pd

df = pd.read_csv('starless.csv')
df['algo'] = df['algo'].astype('str')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

fig = px.scatter(df, x='x', y='y', color='algo')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(id='title', children='Starless'),
    dcc.Graph(id='scatter', figure=fig),
    # dac.DashAudioComponents(
    #     id='audio-player',
    #     src='static/starless.mp3',
    #     autoPlay=False,
    #     controls=True,
    #     height='100px',
    #     currentTime=0
    # ),
    # html.Button('Jump to 1:00', id='jump-button', n_clicks=0)
    dcc.Graph(id='timebars', )
])

@app.callback(
    Output('audio-player', 'currentTime'),
    Input('jump-button', 'n_clicks'))
def update_output(n_clicks):
    return 60

@app.callback(
    Output('title', 'children'),
    Input('audio-player', 'currentTime'),
)
def update_title(currentTime):
    return 'Current time is: {}'.format(currentTime)

if __name__ == '__main__':
    app.run_server(debug=True)