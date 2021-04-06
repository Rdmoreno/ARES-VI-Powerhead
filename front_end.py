import time
import csv
from itertools import zip_longest
from sensors import Sensor
from valve import Valve
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# Data Frames for Saving
pressure_list = ["Pressure"]
pressure_time_list = ["time"]
temperature_fill_list = ["Temperature Fill"]
temperature_fill_time_list = ["time"]
temperature_empty_list = ["Temperature Empty"]
temperature_empty_time_list = ["time"]
official_time_list = ["Official Time"]

# # Valve Definition and Classes
actuator_prop = Valve('Actuator Propellant Valve', 'P8_12', 'P8_12', 'Prop', 4, 100)
actuator_solenoid = Valve('Actuator Solenoid Valve', 'P8_16', 0, 'solenoid', 0, 0)
fill_valve = Valve('Fill Valve', 'P8_4', 0, 'solenoid', 0, 0)
vent_valve = Valve('Vent Valve', 'P8_8', 0, 'solenoid', 0, 0)

# Pressure Sensor Definition and Classes
pressure_cold_flow = Sensor('pressure_cold_flow', 'pressure', 'P9_12', 'P9_12',
                            'P9_12', '011', '101', '111')

# Temperature Sensor Definition and Classes
temperature_fill_line = Sensor('temperature_fill_line', 'temperature', 'P9_12',
                               'P9_12', 'P9_12', '000', '000', '000')
temperature_empty_line = Sensor('temperature_empty_line', 'temperature',
                                'P9_14', 'P9_14', 'P9_16', '000', '000', '000')

# Valve States and Tracking Global Variables
filling_trigger = False

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
        html.H1('ARES: Team Daedalus'),
        html.Div([
            html.Button('Start', id='startbutton', n_clicks=0),
            html.Button('Record', id='recordbutton', n_clicks=0),
            html.Button('Open', id='openbutton', n_clicks=0),
            html.Button('Stop', id='stopbutton', n_clicks=0),
            html.Button('Save', id='savebutton', n_clicks=0),
            html.Button('Clean Up', id='finishexperiment', n_clicks=0),
        ], className="pretty_container"),
        html.Div(id='save_data'),
        html.Div([
            html.H3('Test Buttons'),
            html.Button('Check System', id='generalcheckbutton', n_clicks=0),
            html.Button('Hardware/Software Check', id='checkbutton', n_clicks=0),
            html.Button('Cold Flow', id='coldflowbutton', n_clicks=0),
            html.Button('Fill Check Button', id='coldflowfillbutton', n_clicks=0),
        ], className="pretty_container"),
        html.Div([
            html.H3('Valve State'),
            html.Div('Actuator Propellant Valve: NOT SET', id='actuatorpropstate'),
            html.Div('Actuator Solenoid Valve: NOT SET', id='actuatorsolstate'),
            html.Div('Fill Solenoid Valve: NOT SET', id='fillstate'),
            html.Div('Vent Solenoid Valve: NOT SET', id='ventstate'),
        ], className="pretty_container"),
        html.Div([
            html.H3('System State'),
            html.Div('Hardware/Software Update', id='checkoutput'),
            html.Div('Cold Flow Update', id='coldflowoutput'),
            html.Div('Relief Valve Update', id='pressurerelief'),
            html.Div('Relief Valve Update', id='fillcheck'),
        ], className="pretty_container"),
        html.Div([
            html.H3('Preliminary Check'),
            html.Div('idle', id='valvecheck'),
            html.Div('idle', id='pressurecheck'),
            html.Div('idle', id='temperaturecheck'),
        ], className="pretty_container"),
        html.Div('idle', id='placeholder0', style={'display': 'none'}),
        html.Div('idle', id='placeholder1', style={'display': 'none'}),
        html.Div('idle', id='placeholder2', style={'display': 'none'})
        ], className='pretty_container four columns'),
    html.Div([
        html.Div([
            html.H3('idle', id='pressoutput'),
            html.H3('idle', id='filloutput'),
            html.H3('idle', id='emptyoutput'),
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
    html.Div(id='time_official', style={'display': 'none'}),
], className='row flex-display')


#@app.callback(
#    [Output('placeholder0', 'children')],
#    [Input('startbutton', 'n_clicks')]
#)
#def program_start(n_clicks):
#    global program_start_flag
#    if program_start_flag:
#        global act_prop_state, act_sol_state, fill_state, vent_state
#        actuator_prop.close()
#        actuator_solenoid.close()
#        fill_valve.close()
#        vent_valve.close()
#        call = ['True']
#        act_prop_state = 'Actuator Propellant Valve: Close'
#        act_sol_state = 'Actuator Solenoid Valve: Close'
#        fill_state = 'Fill Solenoid Valve: Close'
#        vent_state = 'Vent Solenoid Valve: Close'
#        program_start_flag = False
#        return call
#    else:
#        raise PreventUpdate


#@app.callback(
#    [Output('placeholder1', 'children')],
#    [Input('startbutton', 'n_clicks')]
#)
#def open_valve_cold_flow_start(n_clicks):
#    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
#    if 'startbutton' in changed_id:
#        global act_prop_state, act_sol_state
#        actuator_prop.open()
#        actuator_solenoid.open()
#        act_prop_state = 'Actuator Propellant Valve: Open'
#        act_sol_state = 'Actuator Solenoid Valve: Open'
#        call = ['True']
#        return call
#    else:
#        raise PreventUpdate


@app.callback(
    [Output('pressure', 'children'),
     Output('time_pres', 'children'),
     Output('temp_fill', 'children'),
     Output('time_fill', 'children'),
     Output('temp_empty', 'children'),
     Output('time_empty', 'children'),
     Output('time_official', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('startbutton', 'n_clicks'),
     Input('stopbutton', 'n_clicks'),
     Input('openbutton', 'n_clicks')]
    )
def read(n_intervals, n_clicks, m_clicks, j_clicks):
    #changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if n_clicks > 0 and m_clicks == 0:

        #if 'openbutton' in changed_id:
        #    actuator_prop.open()
        #    print('Act prop opened')
        #    actuator_solenoid.open()
        #    print('Act Sol opened')

        pres, time_pres = pressure_cold_flow.read_sensor()
        temp_fill, time_fill = temperature_fill_line.read_sensor()
        temp_empty, time_empty = temperature_empty_line.read_sensor()
        time_official = time.process_time()
        return pres, time_pres, temp_fill, time_fill, temp_empty, time_empty, time_official
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
     Input(component_id='time_official', component_property='children'),
     Input('startbutton', 'n_clicks'),
     Input('stopbutton', 'n_clicks')])
def update_pressure_data(pressure, time_pres, temp_fill, time_fill, temp_empty,
                         time_empty, time_official, n_clicks, m_clicks):
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
        official_time_list.append(time_official)

        pres_update = 'Current Pressure: {}'.format(pressure)
        fill_update = 'Current Pressure: {}'.format(temp_fill)
        empty_update = 'Current Pressure: {}'.format(temp_empty)

        return data_pres, data_fill, data_empty, pres_update, fill_update, empty_update
    else:
        raise PreventUpdate


#@app.callback(
#    Output(component_id='pressurerelief', component_property='children'),
#    [Input(component_id='pressure', component_property='children'),
#     Input('startbutton', 'n_clicks'),
#     Input('stopbutton', 'n_clicks')
#     ])
#def relief_pressure_check(pressure, n_clicks, m_clicks):
#    if n_clicks > 0 and m_clicks == 0:
#        # global act_prop_state, act_sol_state, fill_state, vent_state
#        maximum_pressure = 645
#        nominal_pressure = 500
#        if pressure >= maximum_pressure:
#            time_relief = time.process_time()
#            vent_valve.open()
#            # fill_state = 'Fill Solenoid Valve: Close'
#            # vent_state = 'Vent Solenoid Valve: Open'
#            print('Pressure Exceeded Maximum: Opening Relief Valve')
#            print(time_relief)
#            while True:
#                pres_relief = pressure_cold_flow.read_sensor()
#                if pres_relief[0] < nominal_pressure:
#                    time_relief_end = time.process_time()
#                    print('Closing Relief Valve')
#                    vent_valve.close()
#                    # fill_state = 'Fill Solenoid Valve: Open'
#                    # vent_state = 'Vent Solenoid Valve: Close'
#                    print(time_relief_end)
#                    break
#            return 'Ouput: {}'.format('Pressure has returned to nominal value')
#        else:
#            raise PreventUpdate
#    else:
#        raise PreventUpdate


@app.callback(
    [Output('actuatorpropstate', 'children'),
     Output('actuatorsolstate', 'children'),
     Output('fillstate', 'children'),
     Output('ventstate', 'children')],
    [Input('startbutton', 'n_clicks')
     ])
def valve_state(n_clicks):
    if n_clicks > 0:
        act_prop_update = actuator_prop.get_state()
        act_sol_update = actuator_solenoid.get_state()
        fill_valve_update = fill_valve.get_state()
        vent_valve_update = vent_valve.get_state()

        return act_prop_update, act_sol_update, fill_valve_update, vent_valve_update
    else:
        raise PreventUpdate


@app.callback(
    Output('checkoutput', 'children'),
    [Input('checkbutton', 'n_clicks')]
)
def hardware_software_test(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'checkbutton' in changed_id:
        global act_prop_state, act_sol_state, fill_state, vent_state
        check_flag = False
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
        while not check_flag:
            try:
                vent_valve.open()
                actuator_solenoid.open()
                fill_valve.open()
                act_sol_state = 'Actuator Solenoid Valve: Open'
                fill_state = 'Fill Solenoid Valve: Open'
                vent_state = 'Vent Solenoid Valve: Open'
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
                        check_flag = True
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")
        check_flag = False
        print("\nBeginning Closing of Solenoid Valves\n")
        while not check_flag:
            try:
                vent_valve.close()
                actuator_solenoid.close()
                fill_valve.close()
                act_sol_state = 'Actuator Solenoid Valve: Close'
                fill_state = 'Fill Solenoid Valve: Close'
                vent_state = 'Vent Solenoid Valve: Close'
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
                        check_flag = True
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")
        check_flag = False
        print("\nBeginning Opening of Actuator Valve\n")
        while not check_flag:
            try:
                actuator_prop.open()
                act_prop_state = 'Actuator Propellant Valve: Open'
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
                        check_flag = True
                        break
        check_flag = False
        while not check_flag:
            try:
                actuator_prop_check = Valve('Actuator Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, 5)
                actuator_prop_check.partial_open()
                act_prop_state = 'Actuator Propellant Valve: Opened 5%'
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
                        check_flag = True
                        break
        check_flag = False
        while not check_flag:
            try:
                actuator_prop_check = Valve('Actuator Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, 50)
                actuator_prop_check.partial_open()
                act_prop_state = 'Actuator Propellant Valve: Opened 50%'
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
                        check_flag = True
                        break
        print("\nVerification Complete, Press Enter to Continue:\n")
        check_flag = False
        print("\nBeginning Closing of Actuator Valve\n")
        while not check_flag:
            try:
                actuator_prop.close()
                act_prop_state = 'Actuator Propellant Valve: Closed'
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
                        check_flag = True
                        break
        return 'System Check Successful'
    else:
        raise PreventUpdate


@app.callback(
    [Output('fillcheck', 'children')],
    [Input('coldflowfillbutton', 'n_clicks')])
def filling_stop(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'coldflowfillbutton' in changed_id:
        global filling_trigger
        filling_trigger = True
        return ['Filling Procedure Stopped']
    else:
        raise PreventUpdate

@app.callback(
    [Output('coldflowoutput', 'children')],
    [Input('coldflowbutton', 'n_clicks'),
     Input('coldflowfillbutton', 'n_clicks')])
def cold_flow_fill(n_clicks, m_clicks):
    #global act_prop_state, act_sol_state, fill_state, vent_state
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'coldflowbutton' in changed_id:
        global filling_trigger
        print('Welcome to the Team Daedalus Cold Flow Test')
        input('Please Press Enter to Confirm Start')
        print('Starting System Check')
        print()
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

        print()
        print('Closing All Valves')

        actuator_prop.close()
        actuator_solenoid.close()
        fill_valve.close()
        vent_valve.close()
        #act_prop_state = 'Actuator Propellant Valve: Closed'
        #act_sol_state = 'Actuator Solenoid Valve: Closed'
        #fill_state = 'Fill Solenoid Valve: Closed'
        #vent_state = 'Vent Solenoid Valve: Closed'

        input('Press Enter to Open filling valve')
        print('Opening Fill Valve: Begin Liquid Nitrogen Filling Procedure')
        input('Press Enter to Begin Filling and Enter again to end filling')
        vent_valve.open()
        #fill_state = 'Fill Solenoid Valve: Open'

        maximum_pressure = 645
        nominal_pressure = 500

        time.sleep(10)

        while not filling_trigger:
            pressure = pressure_cold_flow.read_sensor()
            temp_empty = temperature_empty_line.read_sensor()
            temp_fill = temperature_fill_line.read_sensor()
            print([pressure[0], temp_empty[0], temp_fill[0]])
            # if pressure[0] >= maximum_pressure:
            #     time_relief = time.process_time()
            #     print('Pressure Exceeded Maximum: Opening Relief Valve')
            #     print(time_relief)
            #     flag = 0
            #     while pressure[0] >= maximum_pressure:
            #         pressure = pressure_cold_flow.read_sensor()
            #         print(pressure[0])
            #         if flag == 0:
            #             fill_valve.close()
            #             #fill_state = 'Fill Solenoid Valve: Closed'
            #             vent_valve.open()
            #             #vent_state = 'Vent Solenoid Valve: Open'
            #             flag = 1
            #         if pressure[0] <= nominal_pressure:
            #             time_relief_end = time.process_time()
            #             fill_valve.open()
            #             #fill_state = 'Fill Solenoid Valve: Open'
            #             vent_valve.close()
            #             #vent_state = 'Vent Solenoid Valve: Closed'
            #             print(time_relief_end)
            time.sleep(.3)
        filling_trigger = False
        fill_valve.close()
        print('Closing Vent Valve')
        #fill_state = 'Fill Solenoid Valve: Closed'
        final_pressure = pressure_cold_flow.read_sensor()
        pressure_message = 'Final Liquid Nitrogen Fill Pressure: {}'.format(final_pressure[0])
        print(pressure_message)

        input('Press Enter to Open Filling and Vent valve')
        fill_valve.open()
        vent_valve.open()
        #fill_state = 'Fill Solenoid Valve: Open'
        print('Opening Fill Valve: Begin Helium Filling Procedure')
        input('Press Enter to Begin Filling, Press Enter again to End')
        time.sleep(10)

        while not filling_trigger:
            pressure = pressure_cold_flow.read_sensor()
            temp_empty = temperature_empty_line.read_sensor()
            temp_fill = temperature_fill_line.read_sensor()
            print([pressure[0], temp_empty[0], temp_fill[0]])
            # if pressure[0] >= maximum_pressure:
            #     time_relief = time.process_time()
            #     print('Pressure Exceeded Maximum: Opening Relief Valve')
            #     print(time_relief)
            #     flag = 0
            #     while pressure[0] >= maximum_pressure:
            #         pressure = pressure_cold_flow.read_sensor()
            #         print(pressure[0])
            #         if flag == 0:
            #             fill_valve.close()
            #             #fill_state = 'Fill Solenoid Valve: Closed'
            #             vent_valve.open()
            #             #vent_state = 'Vent Solenoid Valve: Open'
            #             flag = 1
            #         if pressure[0] <= nominal_pressure:
            #             time_relief_end = time.process_time()
            #             fill_valve.open()
            #             #fill_state = 'Fill Solenoid Valve: Open'
            #             vent_valve.close()
            #             #vent_state = 'Vent Solenoid Valve: Closed'
            #             print(time_relief_end)
            time.sleep(.3)
        fill_valve.close()
        vent_valve.close()
        print('Closing Fill and Vent Valve')
        #fill_state = 'Fill Solenoid Valve: Closed'
        final_pressure = pressure_cold_flow.read_sensor()
        pressure_message = 'Final Helium Fill Pressure: {}'.format(final_pressure[0])
        print(pressure_message)
        input('Cold Flow Filling Procedure Completed: Press Enter to Confirm')
        print('done')
        return 'Cold Flow Filling Finished: Press Open to Begin Cold Flow'
    else:
        raise PreventUpdate


@app.callback(
    Output(component_id='save_data', component_property='children'),
    [Input(component_id='savebutton', component_property='n_clicks')])
def update_saved_data(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'savebutton' in changed_id:
        saved_data_combined = [pressure_list, pressure_time_list, temperature_fill_list, temperature_fill_time_list,
                               temperature_empty_list, temperature_empty_time_list, official_time_list]
        export_data = zip_longest(*saved_data_combined, fillvalue='')
        with open('data.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
            wr = csv.writer(myfile)
            wr.writerows(export_data)
        myfile.close()
        return 'Ouput: {}'.format('Saved')
    else:
        raise PreventUpdate


@app.callback(
        [Output('valvecheck', 'children'),
         Output('pressurecheck', 'children'),
         Output('temperaturecheck', 'children')],
        [Input('generalcheckbutton', 'n_clicks')]
)
def check_system(n_clicks):
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
        [Output('placeholder2', 'children')],
        [Input('finishexperiment', 'n_clicks')]
)
def cleanup_procedure(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'finishexperiment' in changed_id:
        #global act_prop_state, act_sol_state, fill_state, vent_state
        print('Opening All Valves')
        actuator_prop.open()
        actuator_solenoid.open()
        fill_valve.open()
        vent_valve.open()
        #act_prop_state = 'Actuator Propellant Valve: Open'
        #act_sol_state = 'Actuator Solenoid Valve: Open'
        #fill_state = 'Fill Solenoid Valve: Open'
        #vent_state = 'Vent Solenoid Valve: Open'
        call = ['True']
        return call
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=False, host='192.168.7.2')
    # 192.168.7.2
