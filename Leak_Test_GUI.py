import csv
import time
from sensors_test import Sensor
from valve_test import Valve
from itertools import zip_longest
import numpy as np
import time
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_daq as daq
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go

# Valve Definition and Classes
actuator_prop = Valve('Actuator Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, 10)
actuator_solenoid = Valve('Actuator Solenoid Valve', 'P8_12', 0, 'Solenoid', 0, 0)
fill_valve = Valve('Fill Valve', 'P8_12', 0, 'Solenoid', 0, 0)
vent_valve = Valve('Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)

# Pressure Sensor Definition and Classes
pressure_cold_flow = Sensor('pressure_cold_flow', 'pressure', 'P9_12', 'P9_14',
                            'P9_16', '000', '000', '000')

# Temperature Sensor Definition and Classes
temperature_fill_line = Sensor('temperature_fill_line', 'temperature', 'P9_12',
                               'P9_14', 'P9_16', '000', '000', '000')
temperature_empty_line = Sensor('temperature_empty_line', 'temperature',
                                'P9_12', 'P9_14', 'P9_16', '000', '000', '000')

external_stylesheets = ['s1.css', 'style2.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Dialog(id='box2', children=[html.P('Test'), html.H1('Big')],
                hidden=True, contextMenu='Help',
                style=dict(backgroundColor='Black')),
    html.Div([
        html.H3('Leak Test'),
        html.Button('System Check', id='checkbutton', n_clicks=0),
        html.Div([
            html.Div('idle', id='valvecheck'),
            html.Div('idle', id='pressurecheck'),
            html.Div('idle', id='temperaturecheck'),
        ], className="pretty_container"),
        html.Button('Start', id='startbutton', n_clicks=0),
        html.Button('Stop', id='stopbutton', n_clicks=0),
        html.Button('Filling Procedure', id='fillingbutton', n_clicks=0),
        html.Button('Filling Stop', id='fillingstopbutton', n_clicks=0),
        html.Div('idle', id='startpressure'),
        html.Button('Leak Test Start', id='leaktestbutton', n_clicks=0),
        html.Div('idle', id='leakteststate'),
        html.Div([
            html.H3('Valve State'),
            html.Div('idle', id='actuatorpropstate'),
            html.Div('idle', id='actuatorsolstate'),
            html.Div('idle', id='fillstate'),
            html.Div('idle', id='ventstate'),
        ], className="pretty_container"),
        html.Button('Clean Up', id='finishexperiment', n_clicks=0),
        html.Div('idle', id='placeholder', style={'display': 'none'}),
        html.Div('idle', id='placeholder2', style={'display': 'none'})],
        className='pretty_container four columns'),
    html.Div([
        html.Div('idle', id='pressoutput'),
        html.Div('idle', id='filloutput'),
        html.Div('idle', id='emptyoutput')],
        className="pretty_container"),

    # SET INTERVAL = 0 FOR ACTUAL TEST interval=0.1 * 1000
    dcc.Interval(id='interval-component',
                 interval=0.1 * 1000,
                 n_intervals=0),

    # Hidden DIV
    html.Div(id='pressure', style={'display': 'none'}),
    html.Div(id='time_pres', style={'display': 'none'}),
    html.Div(id='temp_fill', style={'display': 'none'}),
    html.Div(id='time_fill', style={'display': 'none'}),
    html.Div(id='temp_empty', style={'display': 'none'}),
    html.Div(id='time_empty', style={'display': 'none'}),
], className='row flex-display')


@app.callback(
    [Output('pressure', 'children'),
     Output('time_pres', 'children'),
     Output('temp_fill', 'children'),
     Output('time_fill', 'children'),
     Output('temp_empty', 'children'),
     Output('time_empty', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('startbutton', 'n_clicks'),
     Input('stopbutton', 'n_clicks')]
)
def read(n_intervals, n_clicks, m_clicks):
    if n_clicks > 0 and m_clicks == 0:
        pres, time_pres = pressure_cold_flow.read_sensor()
        temp_fill, time_fill = temperature_fill_line.read_sensor()
        temp_empty, time_empty = temperature_empty_line.read_sensor()
        return pres, time_pres, temp_fill, time_fill, temp_empty, time_empty
    else:
        raise PreventUpdate


@app.callback(
    [Output('placeholder', 'children')],
    [Input('startbutton', 'n_clicks')]
)
def close_valves(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'startbutton' in changed_id:
        actuator_prop.close()
        actuator_solenoid.close()
        fill_valve.close()
        vent_valve.close()
        call = ['True']
        return call
    else:
        raise PreventUpdate


@app.callback(
    [Output('pressoutput', 'children'),
     Output('filloutput', 'children'),
     Output('emptyoutput', 'children')],
    [Input(component_id='pressure', component_property='children'),
     Input(component_id='time_pres', component_property='children'),
     Input(component_id='temp_fill', component_property='children'),
     Input(component_id='time_fill', component_property='children'),
     Input(component_id='temp_empty', component_property='children'),
     Input(component_id='time_empty', component_property='children'),
     Input('startbutton', 'n_clicks'),
     Input('stopbutton', 'n_clicks')])
def update_pressure_data(pressure, time_pres, temp_fill, time_fill, temp_empty,
                         time_empty, n_clicks, m_clicks):
    if n_clicks > 0 and m_clicks == 0:

        pres_update = 'Current Pressure: {}'.format(pressure)
        fill_update = 'Current Temperature (FILL): {}'.format(temp_fill)
        empty_update = 'Current Temperature (EMPTY): {}'.format(temp_empty)

        return pres_update, fill_update, empty_update
    else:
        raise PreventUpdate


@app.callback(
    [Output('actuatorpropstate', 'children'),
     Output('actuatorsolstate', 'children'),
     Output('fillstate', 'children'),
     Output('ventstate', 'children')],
    [Input('startbutton', 'n_clicks'),
     Input('stopbutton', 'n_clicks')])
def valve_state(n_clicks, m_clicks):
    if n_clicks > 0 and m_clicks == 0:

        act_prop_state = actuator_prop.get_state()
        act_sol_state = actuator_solenoid.get_state()
        fill_state = fill_valve.get_state()
        vent_state = vent_valve.get_state()

        return act_prop_state, act_sol_state, fill_state, vent_state
    else:
        raise PreventUpdate


@app.callback(
        [Output('valvecheck', 'children'),
         Output('pressurecheck', 'children'),
         Output('temperaturecheck', 'children')],
        [Input('checkbutton', 'n_clicks'),
         Input('stopbutton', 'n_clicks')]
)
def check_system(n_clicks, m_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'checkbutton' in changed_id:
        if not pressure_cold_flow.verify_connection():
            pressure_check = 'Pressure Check Failed'
        else:
            pressure_check = 'Pressure Check Succeeded'

        if not temperature_fill_line.verify_connection() and temperature_empty_line.verify_connection():
            temperature_check = 'Temperature Check Failed'
        else:
            temperature_check = 'Temperature Check Succeeded'

        if not actuator_prop.verify_connection_valve and actuator_solenoid.verify_connection_valve and \
                fill_valve.verify_connection_valve and vent_valve.verify_connection_valve:
            valve_check = 'Valve Check Failed'
        else:
            valve_check = 'Valve Check Succeeded'
        return valve_check, pressure_check, temperature_check
    else:
        raise PreventUpdate


@app.callback(
        [Output('leakteststate', 'children')],
        [Input(component_id='pressure', component_property='children'),
         Input(component_id='time_pres', component_property='children'),
         Input(component_id='temp_fill', component_property='children'),
         Input(component_id='time_fill', component_property='children'),
         Input(component_id='temp_empty', component_property='children'),
         Input(component_id='time_empty', component_property='children'),
         Input('leaktestbutton', 'n_clicks')]
)
def leak_test(pressure, time_pres, temp_fill, time_fill, temp_empty,
                         time_empty, n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if 'leaktestbutton' in changed_id:

        pressure_list = ["Pressure"]
        pressure_time_list = ["time"]
        temperature_fill_list = ["Temperature Fill"]
        temperature_fill_time_list = ["time"]
        temperature_empty_list = ["Temperature Empty"]
        temperature_empty_time_list = ["time"]

        saved_data_combined = [pressure_list, pressure_time_list, temperature_fill_list, temperature_fill_time_list,
                               temperature_empty_list, temperature_empty_time_list]
        export_data = zip_longest(*saved_data_combined, fillvalue='')
        with open('leak_data.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
            wr = csv.writer(myfile)
            wr.writerows(export_data)
        myfile.close()

        time_duration = 86400
        time_start = time.time()
        n = 0

        while time.time() - time_start < time_duration:
            pressure_list = []
            pressure_time_list = []
            temperature_fill_list = []
            temperature_fill_time_list = []
            temperature_empty_list = []
            temperature_empty_time_list = []

            for i in range(1000):
                pressure, time_pres = pressure_cold_flow.read_sensor()
                temp_fill, time_fill = temperature_fill_line.read_sensor()
                temp_empty, time_empty = temperature_empty_line.read_sensor()

                pressure_list.append(pressure)
                pressure_time_list.append(time_pres + 600 * n)
                temperature_fill_list.append(temp_fill)
                temperature_fill_time_list.append(time_fill + 60 * n)
                temperature_empty_list.append(temp_empty)
                temperature_empty_time_list.append(time_empty + 60 * n)

                saved_data_combined = [pressure_list, pressure_time_list, temperature_fill_list,
                                       temperature_fill_time_list,
                                       temperature_empty_list, temperature_empty_time_list]
                export_data = zip_longest(*saved_data_combined, fillvalue='')

            with open('leak_data.csv', 'a', encoding="ISO-8859-1", newline='') as myfile:
                wr = csv.writer(myfile)
                wr.writerows(export_data)
            myfile.close()
            n = n + 1
            time.sleep(600)

        return 'Leak Test Completed'
    else:
        raise PreventUpdate


@app.callback(
        [Output('startpressure', 'children')],
        [Input(component_id='pressure', component_property='children'),
         Input('fillingbutton', 'n_clicks'),
         Input('fillingstopbutton', 'n_clicks')]
)
def filling_procedure(pressure, n_clicks, m_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'fillingbutton' in changed_id:

        fill_valve.open()
        maximum_pressure = 10000
        nominal_pressure = 100

        while True:
            if pressure >= maximum_pressure:
                time_relief = time.time()
                print('Pressure Exceeded Maximum: Opening Relief Valve')
                print(time_relief)
                flag = 0
                while pressure >= maximum_pressure:
                    if flag == 0:
                        fill_valve.close()
                        vent_valve.open()
                        flag = 1
                    if pressure <= nominal_pressure:
                        time_relief_end = time.time()
                        fill_valve.open()
                        vent_valve.close()
                        print(time_relief_end)
            if 'fillingstopbutton' in changed_id:
                fill_valve.close()
                start_pressure = pressure
                break
        return 'Starting Pressure: {}'.format(start_pressure)
    else:
        raise PreventUpdate


@app.callback(
        [Output('placeholder2', 'children')],
        [Input('finishexperiment', 'n_clicks')]
)
def cleanup_procedure(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'finishexperiment' in changed_id:
        actuator_prop.open()
        actuator_solenoid.open()
        fill_valve.open()
        vent_valve.open()
        call = ['True']
        return call
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
    # 192.168.7.2

