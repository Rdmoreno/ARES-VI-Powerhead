import time
import pandas as pd
import csv
from sensors_test import Sensor
from valve import Valve
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_daq as daq
import plotly.express as px
import plotly.graph_objects as go

# Valve Definition and Classes
lox_main = Valve('LOX Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, 10)
lox_vent = Valve('LOX Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)
met_vent = Valve('Methane Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)
p_valve = Valve('Pressurant Valve', 'P8_12', 0, 'Solenoid', 0, 0)

# Pressure Sensor Definition and Classes
pressure_cold_flow = Sensor('pressure_cold_flow', 'pressure', 'P9_12', 'P9_14', 'P9_16', '000', '000', '000')

# Temperature Sensor Definition and Classes
temperature_fill_line = Sensor('temperature_fill_line', 'temperature', 'P9_12', 'P9_14', 'P9_16', '000', '000', '000')
temperature_empty_line = Sensor('temperature_empty_line', 'temperature', 'P9_12', 'P9_14', 'P9_16', '000', '000', '000')

data = [dict(x=[0], y=[0], type='scattergl', mode='lines+markers')]
layout_pressure = dict(title=dict(text='Live Pressure'),
                       xaxis=dict(autorange=False, range=[0, 60]),
                       yaxis=dict(autorange=False, range=[0, 110]))
layout_temperature = dict(title=dict(text='Live Temperature'),
                          xaxis=dict(autorange=False, range=[0, 60]),
                          yaxis=dict(autorange=False, range=[-220, 80]))

pressure_fig = dict(data=data, layout=layout_pressure)
temperature_fig_fill = dict(data=data, layout=layout_temperature)
temperature_fig_empty = dict(data=data, layout=layout_temperature)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__)
app.layout = html.Div([
    html.Dialog(id='box2', children=[html.P('Test'), html.H1('Big')],
                hidden=True, contextMenu='Help', style=dict(backgroundColor='Black')),
    html.H6('Cold Flow Pressure Test'),
    html.Button('Check System', id='checkbutton', n_clicks=0),
    html.Div('idle', id='checkoutput'),
    html.Div('idle', id='coldflowoutput'),
    html.Button('Save', id='savebutton', n_clicks=0),
    html.Button('Cold Flow', id='coldflow', n_clicks=0),
    html.Div(id='save_data'),
    daq.Gauge(
        showCurrentValue=True,
        id='pressure_gauge',
        units='PSI',
        label='Pressure Sensors at Location',
        min=0,
        max=300,
        value=0),
    daq.Gauge(
        showCurrentValue=True,
        id='fill_gauge',
        units='C',
        label='Temperature at Fill Line',
        min=-220,
        max=80,
        value=0),
    daq.Gauge(
        showCurrentValue=True,
        id='empty_gauge',
        units='C',
        label='Temperature at Empty Line',
        min=-220,
        max=80,
        value=0),
    dcc.Graph(id='pres_graph', figure=pressure_fig, animate=True),
    dcc.Graph(id='fill_graph', figure=temperature_fig_fill, animate=True),
    dcc.Graph(id='empty_graph', figure=temperature_fig_empty, animate=True),
    # SET INTERVAL = 0 FOR ACTUAL TEST
    dcc.Interval(id='interval-component',
                 interval=00.1 * 1000,
                 n_intervals=0),

    # Hidden DIV
    html.Div(id='pressure', style={'display': 'none'}),
    html.Div(id='time_pres', style={'display': 'none'}),
    html.Div(id='temp_fill', style={'display': 'none'}),
    html.Div(id='time_fill', style={'display': 'none'}),
    html.Div(id='temp_empty', style={'display': 'none'}),
    html.Div(id='time_empty', style={'display': 'none'}),
])


@app.callback(
    [Output('pressure', 'children'),
     Output('time_pres', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def read_press(n_intervals):
    return pressure_cold_flow.read_sensor()


@app.callback(
    [Output('temp_fill', 'children'),
     Output('time_fill', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def read_temp_fill(n_intervals):
    return temperature_fill_line.read_sensor()


@app.callback(
    [Output('temp_empty', 'children'),
     Output('time_empty', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def read_temp_fill(n_intervals):
    return temperature_empty_line.read_sensor()


@app.callback(
    [Output(component_id='pressure_gauge', component_property='value'),
     Output(component_id='pres_graph', component_property='extendData'),
     Output(component_id='fill_gauge', component_property='value'),
     Output(component_id='fill_graph', component_property='extendData'),
     Output(component_id='empty_gauge', component_property='value'),
     Output(component_id='empty_graph', component_property='extendData')],
    [Input(component_id='pressure', component_property='children'),
     Input(component_id='time_pres', component_property='children'),
     Input(component_id='temp_fill', component_property='children'),
     Input(component_id='time_fill', component_property='children'),
     Input(component_id='temp_empty', component_property='children'),
     Input(component_id='time_empty', component_property='children')])
def update_pressure_data(pressure, time_pres, temp_fill, time_fill, temp_empty, time_empty):
    data_pres = (dict(x=[[time_pres]], y=[[pressure]]))
    data_fill = (dict(x=[[time_fill]], y=[[temp_fill]]))
    data_empty = (dict(x=[[time_empty]], y=[[temp_empty]]))
    return pressure, data_pres, temp_fill, data_fill, temp_empty, data_empty


@app.callback(
    Output('checkoutput', 'children'),
    [Input('checkbutton', 'n_clicks')]
)
def check_system(n_clicks):
    if n_clicks > 0:
        print("Before Test Start: Verify Electronic Connections and Follow Safety Procedures\n")
        print("------------------------------------------")
        print("\nProject Daedalus: Powerhead Hardware/Software Test\n")
        print("""\
    
                           ._ o o
                           \_`-)|_
                        ,""       \ 
                      ,"  ## |   ಠ ಠ. 
                    ," ##   ,-\__    `.
                  ,"       /     `--._;)
                ,"     ## /
              ,"   ##    /
    
    
                """)
        print("------------------------------------------\n")
        input("Press Enter to Start the Cold Flow Test:")

        print("\nVerifying Sensor and Valve Connections\n")
        while not pressure_cold_flow.verify_connection() and temperature_fill_line.verify_connection() \
                and temperature_empty_line.verify_connection():
            input("\nPress Enter to Start Verification Again:")
        print("\nAll Sensors are Functional\n")

        while not lox_main.verify_connection_valve and lox_vent.verify_connection_valve and \
                met_vent.verify_connection_valve and p_valve.verify_connection_valve:
            input("\nPress Enter to Start Verification Again:")
        print("\nAll Valves are Functional\n")
        print("\nVerification Complete, Press Enter to Continue:\n")

        print("\nBeginning Opening of Solenoid Valves\n")
        while True:
            try:
                lox_vent.open()
                met_vent.open()
                p_valve.open()
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input('\nHave all Solenoids opened? (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")

        print("\nBeginning Closing of Solenoid Valves\n")
        while True:
            try:
                lox_vent.close()
                met_vent.close()
                p_valve.close()
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input('\nHave all Solenoids Closed? (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")

        print("\nBeginning Opening of Actuator Valve\n")
        while True:
            try:
                percentage = 100
                lox_main.open()
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input('\nHas the Actuator Opened (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        while True:
            try:
                percentage = 5
                lox_main.open()
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input('\nHas the Actuator Opened 5% (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        while True:
            try:
                percentage = 50
                lox_main.open()
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input('\nHas the Actuator Opened Selected percentage(yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")

        print("\nBeginning Opening of Actuator Valve\n")
        while True:
            try:
                lox_main.close()
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input('\nHas the Actuator Closed (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        return 'System Check Successful'

@app.callback(
    Output('coldflowoutput', 'children'),
    [Input('coldflow', 'n_clicks')]
)
def cold_flow_initiate(n_clicks):
    if n_clicks > 0:
        return 'Successful Cold Flow'


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


if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
    # 192.168.7.2
