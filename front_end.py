import time
import pandas as pd
import csv
from itertools import zip_longest
from sensors_test import Sensor
from valve_test import Valve
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_daq as daq
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go

# Data Frames for Saving
pressure_list = ["Pressure"]
pressure_time_list = ["time"]
temperature_fill_list = ["Temperature Fill"]
temperature_fill_time_list = ["time"]
temperature_empty_list = ["Temperature Empty"]
temperature_empty_time_list = ["time"]

# # Valve Definition and Classes
actuator_prop = Valve('Actuator Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, 100)
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

data = [dict(x=[0], y=[0], type='scattergl', mode='lines+markers')]
layout_pressure = dict(title=dict(text='Live Pressure'),
                       xaxis=dict(autorange=True, range=[0, 60]),
                       yaxis=dict(autorange=True, range=[0, 200]))
layout_temperature = dict(title=dict(text='Live Temperature'),
                          xaxis=dict(autorange=True, range=[0, 60]),
                          yaxis=dict(autorange=True, range=[-220, 80]))

pressure_fig = dict(data=data, layout=layout_pressure)
temperature_fig_fill = dict(data=data, layout=layout_temperature)
temperature_fig_empty = dict(data=data, layout=layout_temperature)

external_stylesheets = ['s1.css', 'style2.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.Dialog(id='box2', children=[html.P('Test'), html.H1('Big')],
                hidden=True, contextMenu='Help',
                style=dict(backgroundColor='Black')),
    html.Div([
        html.H3('Cold Flow Pressure Test'),
        html.Button('Start', id='startbutton', n_clicks=0),
        html.Button('Stop', id= 'stopbutton', n_clicks=0),
        html.Button('Save', id='savebutton', n_clicks=0),
        html.Button('Check System', id='checkbutton', n_clicks=0),
        html.Button('Cold Flow', id='coldflowbutton', n_clicks=0),
        html.Div('idle', id='checkoutput'),
        html.Div('idle', id='coldflowoutput'),
        html.Div('idle', id='pressurerelief'),
        html.Div(id='save_data')], className='pretty_container four columns'),
    html.Div([
        html.Div([
            html.Div('idle', id='pressoutput'),
            html.Div('idle', id='filloutput'),
            html.Div('idle', id='emptyoutput'),
        ], className="pretty_container"),
        html.Div(dcc.Graph(id='pres_graph', figure=pressure_fig, animate=True),
                 className="pretty_container"),
        html.Div(dcc.Graph(id='fill_graph', figure=temperature_fig_fill, animate=True),
                 className="pretty_container"),
        html.Div(dcc.Graph(id='empty_graph', figure=temperature_fig_empty, animate=True),
                 className="pretty_container")
        ],
        className='twelve columns'),



    # SET INTERVAL = 0 FOR ACTUAL TEST interval=0.1 * 1000
    dcc.Interval(id='interval-component',
                 interval=0.1*1000,
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
    [Output(component_id='pres_graph', component_property='extendData'),
     Output(component_id='fill_graph', component_property='extendData'),
     Output(component_id='empty_graph', component_property='extendData'),
     Output('pressoutput', 'children'),
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

        data_pres = (dict(x=[[time_pres]], y=[[pressure]]))
        data_fill = (dict(x=[[time_fill]], y=[[temp_fill]]))
        data_empty = (dict(x=[[time_empty]], y=[[temp_empty]]))

        pressure_list.append(pressure)
        pressure_time_list.append(time_pres)
        temperature_fill_list.append(temp_fill)
        temperature_fill_time_list.append(time_fill)
        temperature_empty_list.append(temp_empty)
        temperature_empty_time_list.append(time_empty)

        pres_update = 'Current Pressure: {}'.format(pressure)
        fill_update = 'Current Pressure: {}'.format(temp_fill)
        empty_update = 'Current Pressure: {}'.format(temp_empty)

        return data_pres, data_fill, data_empty, pres_update, fill_update, empty_update
    else:
        raise PreventUpdate


@app.callback(
    Output('checkoutput', 'children'),
    [Input('checkbutton', 'n_clicks')]
)
def check_system(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'checkbutton' in changed_id:
        print(
            "Before Test Start: Verify Electronic Connections and Follow Safety Procedures\n")
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

        while not actuator_prop.verify_connection_valve and actuator_solenoid.verify_connection_valve and \
                fill_valve.verify_connection_valve and vent_valve.verify_connection_valve:
            input("\nPress Enter to Start Verification Again:")
        print("\nAll Valves are Functional\n")
        print("\nVerification Complete, Press Enter to Continue:\n")

        print("\nBeginning Opening of Solenoid Valves\n")
        while True:
            try:
                vent_valve.open()
                actuator_solenoid.open()
                fill_valve.open()
            except Exception:
                print(
                    "\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input(
                        '\nHave all Solenoids opened? (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")

        print("\nBeginning Closing of Solenoid Valves\n")
        while True:
            try:
                vent_valve.close()
                actuator_solenoid.close()
                fill_valve.close()
            except Exception:
                print(
                    "\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input(
                        '\nHave all Solenoids Closed? (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")

        print("\nBeginning Opening of Actuator Valve\n")
        while True:
            try:
                actuator_prop.open()
            except Exception:
                print(
                    "\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input(
                        '\nHas the Actuator Opened (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        while True:
            try:
                actuator_prop_check = Valve('Actuator Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, 5)
                actuator_prop_check.partial_open()
            except Exception:
                print(
                    "\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input(
                        '\nHas the Actuator Opened 5% (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        while True:
            try:
                actuator_prop_check = Valve('Actuator Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, 50)
                actuator_prop_check.partial_open()
            except Exception:
                print(
                    "\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input(
                        '\nHas the Actuator Opened Selected percentage(yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")

        print("\nBeginning Opening of Actuator Valve\n")
        while True:
            try:
                actuator_prop.close()
            except Exception:
                print(
                    "\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
                input("\nPress Enter to Start Verification Again:")
                continue
            else:
                while True:
                    verification = input(
                        '\nHas the Actuator Closed (yes/no)?\n')
                    if verification == 'yes' or 'Yes':
                        break
        return 'System Check Successful'
    else:
        raise PreventUpdate


@app.callback(
    Output('coldflowoutput', 'children'),
    [Input('coldflowbutton', 'n_clicks')]
)
def cold_flow_initiate(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'coldflowbutton' in changed_id:
        return 'Cold Flow Start Successful'
    else:
        raise PreventUpdate


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
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'savebutton' in changed_id:
        saved_data_combined = [pressure_list, pressure_time_list, temperature_fill_list, temperature_fill_time_list,
                               temperature_empty_list, temperature_empty_time_list]
        export_data = zip_longest(*saved_data_combined, fillvalue='')
        with open('data.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
            wr = csv.writer(myfile)
            wr.writerows(export_data)
        myfile.close()
        return 'Ouput: {}'.format('Saved')
    else:
        raise PreventUpdate


@app.callback(
    Output(component_id='pressurerelief', component_property='children'),
    [Input(component_id='pressure', component_property='children')])
def relief_pressure_check(pressure):
    maximum_pressure = 200
    if pressure >= maximum_pressure:
        time_relief = time.time()
        print('Pressure Exceeded Maximum: Opening Relief Valve')
        print(time_relief)
        while pressure >= maximum_pressure:
            vent_valve.open()
            if pressure < maximum_pressure:
                time_relief_end = time.time()
                vent_valve.close()
                print(time_relief_end)
                return 'Ouput: {}'.format('Pressure has returned to nominal value')
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
    # 192.168.7.2
