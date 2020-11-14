import time
import pandas as pd
import csv
from sensors import Sensor
from valve import Valve
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go


y = [100, 30, 40, 50]

x = [time.process_time(),
     time.process_time(),
     time.process_time(),
     time.process_time()]

pressure_test = Sensor('sensor_test_class', 'pressure', 'pin0', 'pin1', 'pin2')
data = [dict(x=x, y=y, type='scatter', mode='lines+markers')]
layout = dict(title=dict(text='Live Pressure'))

fig = dict(data=data, layout=layout)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H6('Cold Flow Pressure Test'),
    html.Button('Read', id='readbutton', n_clicks=0),
    html.Button('Save', id='savebutton', n_clicks=0),
    html.Div(id='pressure_data'),
    html.Div(id='save_data'),
    dcc.Graph(id='graph', figure=fig, animate=True),
    dcc.Interval(id='interval-component',
                 interval=0.5*1000,
                 n_intervals=0)
])


@app.callback(
    [Output(component_id='pressure_data', component_property='children'),
     Output(component_id='graph', component_property='extendData')],
    [Input(component_id='interval-component', component_property='n_intervals')])
def update_pressure_data(n_clicks):
    t = time.process_time()
    vals = pressure_test.read_pressure()
    x.append(t)
    y.append(vals)
    data = (dict(x=[[t]], y=[[vals]]))
    return 'Output: {}'.format(vals), data


@app.callback(
    Output(component_id='save_data', component_property='children'),
    [Input(component_id='savebutton', component_property='n_clicks')])
def update_saved_data(n_clicks):
    if n_clicks > 0:
        pressure_test.save_data()
        return 'Ouput: {}'.format('Saved')
    return 'Ouput: {}'.format('Not Saved')


if __name__ == '__main__':
    app.run_server(debug=True)
