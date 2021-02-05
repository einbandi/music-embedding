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

n_frames = len(df)//2
sr = 22050
frame_len = 2**15
hop_len = 2**13
# minutes = np.arange(0,n_frames*hop_len/sr/60,1, dtype=np.int)
# labels = np.full(n_frames, '', dtype=object)
# for m in minutes:
#     idx = int(np.floor(60 * m / hop_len * sr))
#     labels[idx] = '{:d}:00'.format(m)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

scatter = px.scatter(
    df,
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
scatter.update_xaxes(visible=False)
scatter.update_yaxes(visible=False)
scatter.update_layout(margin={'l':60, 'r': 0, 't': 0, 'b': 80})


def make_range_plot(indices):
    bars = np.zeros(n_frames)
    bars[indices] = 1
    rangeplot = px.imshow(
        [bars],
        #x=labels,
        labels={'x': 'Time (s)'},
        color_continuous_scale=['rgb(250,250,250)', 'gray'],
        # width=400,
        # height=50,
        aspect='auto',
        zmin=0,
        zmax=1
    )
    rangeplot.update_yaxes(visible=False)
    rangeplot.layout.hovermode = False
    rangeplot.layout.coloraxis.showscale = False
    return rangeplot


app.layout = html.Div([
    html.H1(
        id='title',
        children='King Crimson –⁠ Starless',
        style={
            'paddingLeft': '60px',
            'paddingTop': '20px'
        }
    ),
    html.Div([
        html.Div(
            dcc.Graph(
                id='scatter',
                figure=scatter,
                # selectedData={'points': []},
                style={
                    'backgroundColor': None,
                    'padding': '0px 0px 0px 0px'
                },
                config={
                    'displaylogo': False,
                    'modeBarButtonsToRemove': [
                        'toImage',
                        'zoomIn2d', 'zoomOut2d', 'autoScale2d', 
                        'resetScale2d', 'toggleSpikelines',
                        'hoverClosestCartesian',
                        'hoverCompareCartesian']
                }
            ),
            style={
                'width': '49%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            }
        ),
        html.Div([
            html.Div(
                id='audio',
                style={
                    'height': 100,
                }
            ),
            dcc.Graph(
                id='timerange',
                figure=make_range_plot([]),
                style={'height': 200},
                config={'displayModeBar': False}
            )],
            style={
                'width': '49%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            }
        )]
    )
    # dac.DashAudioComponents(
    #     id='audio-player',
    #     src='static/starless.mp3',
    #     autoPlay=False,
    #     controls=True,
    #     height='100px',
    #     currentTime=0
    # )
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
        source = 'static/frames/frame-{:04d}.wav'.format(new_index)
        audio = html.Audio(
            src=source,
            controls=True,
            style={
                'paddingLeft': '100px'
            }
        )
        return make_range_plot([new_index]), audio

    elif selection is not None:

        new_indices = [p['customdata'][0] for p in selection['points']]
        subset = df.loc[new_indices, 'mfcc01':'mfcc20']
        nearest = np.sum((subset - subset.mean(axis=0))**2, axis=1).idxmin()
        source = 'static/frames/frame-{:04d}.wav'.format(nearest)
        audio = html.Audio(
            src=source,
            controls=True,
            style={
                'paddingLeft': '100px'
            }
        )
        return make_range_plot(new_indices), audio


if __name__ == '__main__':
    app.run_server(debug=True)
