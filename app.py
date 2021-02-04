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
              #selectedData={'points': []},
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
    Output('audio', 'children'),
    [Input('scatter', 'selectedData'),
     Input('scatter', 'clickData')])
def update_timerange_and_audio(selection, clicked):
    if selection is None and clicked is None:
        return make_range_plot([]), []
    elif selection is None and clicked is not None:
        new_index = clicked['points'][0]['customdata'][0]
        source = 'static/frames/frame-{:04d}.wav'.format(
            new_index)
        return make_range_plot([new_index]), html.Audio(src=source, controls=True)
    elif selection is not None:
        new_indices = [p['customdata'][0] for p in selection['points']]
        subset = df.loc[new_indices, 'mfcc01':'mfcc20']
        nearest = np.sum((subset - subset.mean(axis=0))**2, axis=1).idxmin()
        source = 'static/frames/frame-{:04d}.wav'.format(nearest)
        return make_range_plot(new_indices), html.Audio(src=source, controls=True)

# @app.callback(
#     Output('audio', 'children'),
#     Input('scatter', 'clickData'))
# def update_audio(clicked):
#     if clicked is None:
#         return []
#     else:
#         source = 'static/frames/frame-{:04d}.wav'.format(
#             )
#         return html.Audio(src=source, controls=True)


if __name__ == '__main__':
    app.run_server(debug=True)
