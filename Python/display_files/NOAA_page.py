"""
Working file currently for RPI Zero.

Functions:
Pulls last 24 hours of data from NOAA and trims to 12 hour dataframes
Accomplishing a five minute refresh on data from NOAA
Generates a 3 graph pack of temp / baro pressure / tide on left side
Single polar graph on right with 12 hour wind history


Improvements TODO:
Add 7 day hi/low from Beaufort station
Include tide predictions for Bogue inlet
Generate 'predictions graph' for 12 hr window with 'now' centered
Determine how to incorporate 'local' tide data with sensor

"""


import pandas as pd
import time
import requests
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import logging

# Configuring logger
logger = logging.getLogger('NOAA_data_web_page')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('./NOAA.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

logger.info('Logger configured')


# Defining app and callbacks
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
logger.info('Defining instance of Dash app')
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('Temperature / Pressure / Tides'),
            dcc.Graph(id='g1'),
            dcc.Interval(
                id='int_g1',
                interval=300 * 1000,  # in milliseconds
                n_intervals=0
            )
        ], className="six columns"),

        html.Div([
            html.H3('Wind Data'),
            dcc.Graph(id='g2'),
            dcc.Interval(
                id='int_g2',
                interval=300 * 1000,  # in milliseconds
                n_intervals=0
            )
        ], className="six columns"),
    ], className="row")
])

def get_data(product):
    """uses current time to pull last 24 hours of wind / temp / pressure / tide data from beaufort marine lab"""
# times not needed, can just pull last __ hours based on request time
#    yr, mo, dy, _, _, _, _, _, _ = time.localtime()
#    yr_str = str(yr)
#    mo_str = _pad_date(mo)
#    dy_str = _pad_date(dy)

    url_dict = {
        'wind': f'https://tidesandcurrents.noaa.gov/api/datagetter?product=wind&application=NOS.COOPS.TAC.WL&range=24&station=8656483&time_zone=lst_ldt&units=english&interval=6&format=json',
        'temp': f'https://tidesandcurrents.noaa.gov/api/datagetter?product=air_temperature&application=NOS.COOPS.TAC.WL&range=24&station=8656483&time_zone=lst_ldt&units=english&interval=6&format=json',
        'press': f'https://tidesandcurrents.noaa.gov/api/datagetter?product=air_pressure&application=NOS.COOPS.TAC.WL&range=24&station=8656483&time_zone=lst_ldt&units=english&interval=6&format=json',
        'tide': f'https://tidesandcurrents.noaa.gov/api/datagetter?product=water_level&application=NOS.COOPS.TAC.WL&range=24&datum=MSL&station=8656483&time_zone=lst_ldt&units=english&format=json',
    }

    connection = False

    while not connection:
        logger.info('Testing of network connectivity')
        if requests.get('http://www.google.com').status_code == 200:
            connection = True
            logger.info('Status code=200 on www.google.com')

    logger.info(f'Updated data for {product}')
    return requests.get(url_dict[product]).content


def _pad_date(val):
    """adds a zero to date if single digit"""
    if val < 10:
        return '0' + str(val)
    else:
        return str(val)

def resp_to_df(content):
    """Accepts the response object and returns a df trimmed to last 12 hours data"""
    logger.info('Processing content to dataframe')
    json_data = json.loads(content)
    new_df = pd.DataFrame(json_data['data'])
    new_df['t'] = pd.to_datetime(new_df['t'])

    hrs_ago = datetime.datetime.now() - datetime.timedelta(hours=12)

    mask = new_df['t'] > hrs_ago
    return new_df.loc[mask]

@app.callback(Output('g2', 'figure'),
              [Input('int_g2', 'n_intervals')])
def create_wind_plot(n):
    """Creates the figure/plot of wind data"""
    wind_df = resp_to_df(get_data('wind'))

    pol_fig = go.Figure(data=
    go.Scatterpolar(
        r=wind_df['s'],
        theta=wind_df['d'],
        mode='markers',
        marker=dict(size=8,
                    color=wind_df.index,
                    colorscale="GnBu")
    ))

    pol_fig.update_layout(
        showlegend=False,
        polar=dict(
            radialaxis_tickfont_size=12,
            angularaxis=dict(
                tickfont_size=12,
                rotation=90,  # start position of angular axis
                direction="clockwise"
                )
        ),
        height=800
    )

    return pol_fig


@app.callback(Output('g1', 'figure'),
              [Input('int_g1', 'n_intervals')])
def create_wx_tide_plot(n):
    """Creates the 3 element plot for temp/pressure/tide"""
    temp_df = resp_to_df(get_data('temp'))
    tide_df = resp_to_df(get_data('tide'))
    press_df = resp_to_df(get_data('press'))

    press_df['v'] = press_df['v'].astype(float) / 33.864

    fig = make_subplots(rows=3, cols=1, subplot_titles=('Temp', 'Barometric Pressure', 'Tide level'))

    fig.add_trace(go.Scatter(x=temp_df['t'], y=temp_df['v'], name='Temp', line_color='orange'),
                  row=1, col=1)

    fig.update_yaxes(#range=[40, 100],
                     row=1, col=1,
                     title="Degrees F")

    fig.add_trace(go.Scatter(x=press_df['t'], y=press_df['v'], name='Pressure', line_color='green'),
                  row=2, col=1)

    fig.update_yaxes(#range=[28, 31],
                     row=2, col=1,
                     tickformat='.2f',
                     title="inches Hg")

    fig.add_trace(go.Scatter(x=tide_df['t'], y=tide_df['v'], name='Tide Level', line_color='blue'),
                  row=3, col=1)

    fig.update_yaxes(#range=[-10, 10],
                     row=3, col=1,
                     title="ft MSL")

    fig.update_layout(height=800, width=800)

    return fig

if __name__ == '__main__':
    logger.info('Starting app server.')
    app.run_server(debug=False, port=8050, host='127.0.0.1')
