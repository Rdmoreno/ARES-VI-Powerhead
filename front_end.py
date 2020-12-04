import time
import pandas as pd
import csv
from sensors import Sensor
from valve import Valve
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go

y = [100, 30, 40, 50]

x = [time.process_time(),
     time.process_time(),
     time.process_time(),
     time.process_time()]

pressure_test = Sensor('sensor_test_class', 'pressure', 'pin0', 'pin1', 'pin2')
data = [dict(x=x, y=y, type='scattergl', mode='lines+markers')]
layout = dict(title=dict(text='Live Pressure'),
              xaxis=dict(autorange=False, range=[0, 100]),
              yaxis=dict(autorange=False, range=[0, 110]))

fig = dict(data=data, layout=layout)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)
app.layout = html.Div([
    html.Dialog(id='box2', children=[html.P('Test'), html.H1('Big')],
                hidden=True, contextMenu='Help', style=dict(backgroundColor='Black')),
    html.H6('Cold Flow Pressure Test'),
    html.Button('Read', id='readbutton', n_clicks=0),
    html.Button('Save', id='savebutton', n_clicks=0),
    html.Button('Dialog', id='dialog', n_clicks=0),
    html.Div(id='save_data'),
    daq.Gauge(
        showCurrentValue=True,
        id='my-daq-gauge',
        units='PSI',
        label='Pressure Sensors at Location',
        min=0,
        max=300,
        value=0),
    dcc.Graph(id='graph', figure=fig, animate=True),
    dcc.Interval(id='interval-component',
                 interval=00.1 * 1000,
                 n_intervals=0),


    # Hidden DIV
    html.Div(id='pressure', style={'display': 'none'}),
    html.Div(id='time', style={'display': 'none'})
])


@app.callback(
    [Output('pressure', 'children'),
     Output('time', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def read_press(n_intervals):
    return pressure_test.read_pressure()


@app.callback(
    [Output(component_id='my-daq-gauge', component_property='value'),
     Output(component_id='graph', component_property='extendData')],
    [Input(component_id='pressure', component_property='children'),
     Input(component_id='time', component_property='children')])
def update_pressure_data(pressure, time):
    data = (dict(x=[[time]], y=[[pressure]]))
    return pressure, data


# @app.callback(
#     Output(component_id='my-daq-gauge', component_property='value'),
#     [Input(component_id='interval-component', component_property='n_intervals')])
# def update_pressure_data(n_clicks):
#     vals = pressure_test.read_pressure()
#     return vals

@app.callback(
    Output(component_id='save_data', component_property='children'),
    [Input(component_id='savebutton', component_property='n_clicks')])
def update_saved_data(n_clicks):
    if n_clicks > 0:
        pressure_test.save_data()
        return 'Ouput: {}'.format('Saved')
    return 'Ouput: {}'.format('Not Saved')


@app.callback(
    Output('box2', 'hidden'),
    [Input('dialog', 'n_clicks')]
)
def test(n_clicks):
    if n_clicks > 0:
        return False
    return False


if __name__ == '__main__':
    app.run_server(debug=True)
