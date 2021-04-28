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
import Adafruit_BBIO.GPIO as GPIO

# Data Frames for Saving
pressure_list = ["Pressure"]
pressure_time_list = ["time"]
temperature_fill_list = ["Temperature Fill"]
temperature_fill_time_list = ["time"]
temperature_empty_list = ["Temperature Empty"]
temperature_empty_time_list = ["time"]
official_time_list = ["Official Time"]

# # Valve Definition and Classes
actuator_prop = Valve('Actuator Propellant Valve', 'P8_4', 'P8_4', 'prop', 4, 20)
actuator_solenoid = Valve('Actuator Solenoid Valve', 'P8_4', 0, 'solenoid', 0, 0)
fill_valve = Valve('Fill Valve', 'P8_8', 0, 'solenoid', 0, 0)
vent_valve = Valve('Vent Valve', 'P8_45', 0, 'solenoid', 0, 0)

# Pressure Sensor Definition and Classes
pressure_cold_flow = Sensor('pressure_cold_flow', 'pressure', 'P9_16', 'P9_16',
                            'P9_16', '000', '010', '100')

# Temperature Sensor Definition and Classes
temperature_fill_line = Sensor('temperature_fill_line', 'temperature', 'P9_12',
                               'P9_12', 'P9_12', '000', '000', '000')
temperature_empty_line = Sensor('temperature_empty_line', 'temperature',
                                'P9_14', 'P9_14', 'P9_16', '000', '000', '000')

# Relief Valve Counter: Will always start at zero
counter = 0

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
        ], className="pretty_container"),
        html.Div([
            html.H3('Cold Flow'),
            html.Button('Check', id='coldflowcheckbutton', n_clicks=0),
            html.Div('idle', id='coldflowcheckresponse'),
            html.Button('Liquid Nitrogen Fill', id='liquidfillbutton', n_clicks=0),
            html.Button('Liquid Nitrogen Fill End', id='liquidfillbuttonend', n_clicks=0),
            html.Div('idle', id='liquidfillresponse'),
            html.Div('idle', id='liquidfillresult'),
            html.Button('Helium Fill', id='heliumfillbutton', n_clicks=0),
            html.Button('Helium Fill End', id='heliumfillbuttonend', n_clicks=0),
            html.Div('idle', id='heliumfillresponse'),
            html.Div('idle', id='heliumfillresult'),
            html.Div('idle', id='coldflowready'),
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
    html.Div([
        html.H3('Override Buttons'),
        dcc.Input(id="inputpercentage", type="number", placeholder="Percent Open", debounce=True),
        html.Div([
            html.Button('Actuator Prop Open', id='actuatorpropopen', n_clicks=0),
            html.Button('Actuator Prop Percent Open', id='actuatorproppercentopen', n_clicks=0),
            html.Button('Actuator Sol Open', id='actuatorsolopen', n_clicks=0),
            html.Button('Pressurant Valve Open', id='pressurantvalveopen', n_clicks=0),
            html.Button('Vent Valve Open', id='ventvalveopen', n_clicks=0),
            html.Button('Actuator Prop Close', id='actuatorpropclose', n_clicks=0),
            html.Button('Actuator Sol Close', id='actuatorsolclose', n_clicks=0),
            html.Button('Pressurant Valve Close', id='pressurantvalvclose', n_clicks=0),
            html.Button('Vent Valve Close', id='ventvalveclose', n_clicks=0),
            html.Button('All Valves Close', id='allvalveclose', n_clicks=0),
            html.Button('All Valves Open', id='allvalveopen', n_clicks=0)]),
        html.Div('idle', id='emergencyholder'),
    ],
        className='pretty_container four columns'),

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
    html.Div(id='time_official', style={'display': 'none'}),
], className='row flex-display')


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
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if n_clicks > 0 and m_clicks == 0:

        if 'openbutton' in changed_id:
            actuator_solenoid.open()
            actuator_prop.partial_open()

        pres, time_pres = pressure_cold_flow.read_sensor()
        temp_fill, time_fill = temperature_fill_line.read_sensor()
        temp_empty, time_empty = temperature_empty_line.read_sensor()
        time_official = time.process_time()
        return pres, time_pres, temp_fill, time_fill, temp_empty, time_empty, time_official
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
     Input(component_id='time_official', component_property='children'),
     Input('startbutton', 'n_clicks'),
     Input('recordbutton', 'n_clicks'),
     Input('stopbutton', 'n_clicks')])
def update_pressure_data(pressure, time_pres, temp_fill, time_fill, temp_empty,
                         time_empty, time_official, n_clicks, m_clicks, j_clicks):
    if n_clicks > 0 and j_clicks == 0:

        pres_update = 'Current Pressure: {}'.format(pressure)
        fill_update = 'Temperature Fill: {}'.format(temp_fill)
        empty_update = 'Temperature Empty: {}'.format(temp_empty)
        # return data_pres, data_fill, data_empty, pres_update, fill_update, empty_update
        return pres_update, fill_update, empty_update
    else:
        raise PreventUpdate


@app.callback(
    [Output(component_id='pres_graph', component_property='extendData'),
     Output(component_id='fill_graph', component_property='extendData'),
     Output(component_id='empty_graph', component_property='extendData')],
    [Input(component_id='pressure', component_property='children'),
     Input(component_id='time_pres', component_property='children'),
     Input(component_id='temp_fill', component_property='children'),
     Input(component_id='time_fill', component_property='children'),
     Input(component_id='temp_empty', component_property='children'),
     Input(component_id='time_empty', component_property='children'),
     Input(component_id='time_official', component_property='children'),
     Input('recordbutton', 'n_clicks'),
     Input('stopbutton', 'n_clicks')])
def record_data(pressure, time_pres, temp_fill, time_fill, temp_empty, time_empty, time_official, n_clicks, j_clicks):
    if n_clicks > 0 and j_clicks == 0:

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

        return data_pres, data_fill, data_empty
    else:
        raise PreventUpdate


@app.callback(
    Output('coldflowcheckresponse', 'children'),
    [Input('coldflowcheckbutton', 'n_clicks'),
     ])
def cold_flow_check(n_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'coldflowcheckbutton' in changed_id:

        check_1 = pressure_cold_flow.verify_connection()
        check_2 = temperature_fill_line.verify_connection()
        check_3 = temperature_empty_line.verify_connection()

        if not check_1 and check_2 and check_3:
            return 'Check Unsuccessful: Check Sensor Connections'

        check_1 = actuator_prop.verify_connection_valve
        check_2 = actuator_solenoid.verify_connection_valve
        check_3 = fill_valve.verify_connection_valve
        check_4 = vent_valve.verify_connection_valve

        if not check_1 and check_2 and check_3 and check_4:
            return 'Check Unsuccessful: Check Valve Connections'

        actuator_solenoid.close()
        actuator_prop.close()
        fill_valve.close()
        vent_valve.close()

        return 'Check Successful: Ready to Fill'
    else:
        raise PreventUpdate


@app.callback(
    Output('liquidfillresponse', 'children'),
    [Input('liquidfillbutton', 'n_clicks'),
     Input('liquidfillbuttonend', 'n_clicks')])
def cold_flow_nitrogen_fill(n_clicks, m_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'liquidfillbutton' in changed_id:
        vent_valve.open()
        return 'Vent Valve Opened'
    else:
        raise PreventUpdate


@app.callback(
    Output('liquidfillresult', 'children'),
    [Input('liquidfillbutton', 'n_clicks'),
     Input('liquidfillbuttonend', 'n_clicks'),
     Input(component_id='pressure', component_property='children')])
def cold_flow_nitrogen_fill_end(n_clicks, m_clicks, pressure):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'liquidfillbuttonend' in changed_id:
        vent_valve.close()
        result = pressure
        return 'Vent Valve Closed: Pressure is {} psi'.format(result)
    else:
        raise PreventUpdate


@app.callback(
    Output('heliumfillresponse', 'children'),
    [Input('heliumfillbutton', 'n_clicks'),
     Input('heliumfillbuttonend', 'n_clicks')])
def cold_flow_helium_fill(n_clicks, m_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'heliumfillbutton' in changed_id:
        fill_valve.open()
        return 'Vent Valve and Pressurant Line Opened'
    else:
        raise PreventUpdate


@app.callback(
    [Output('heliumfillresult', 'children'),
     Output('coldflowready', 'children')],
    [Input('heliumfillbutton', 'n_clicks'),
     Input('heliumfillbuttonend', 'n_clicks'),
     Input(component_id='pressure', component_property='children')])
def cold_flow_helium_fill_end(n_clicks, m_clicks, pressure):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'heliumfillbuttonend' in changed_id:
        vent_valve.close()
        result = pressure
        return 'All Valves Closed: Pressure is {} psi'.format(result), 'Ready for Cold FLow'
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
        # global act_prop_state, act_sol_state, fill_state, vent_state
        print('Opening All Valves')
        actuator_solenoid.open()
        actuator_prop.open()
        fill_valve.close()
        vent_valve.open()
        call = ['True']
        return call
    else:
        raise PreventUpdate


@app.callback(
    Output('emergencyholder', 'children'),
    [Input('inputpercentage', 'value'),
     Input('actuatorproppercentopen', 'n_clicks'),
     Input('actuatorpropopen', 'n_clicks'),
     Input('actuatorsolopen', 'n_clicks'),
     Input('pressurantvalveopen', 'n_clicks'),
     Input('ventvalveopen', 'n_clicks'),
     Input('actuatorpropclose', 'n_clicks'),
     Input('actuatorsolclose', 'n_clicks'),
     Input('pressurantvalvclose', 'n_clicks'),
     Input('ventvalveclose', 'n_clicks'),
     Input('allvalveclose', 'n_clicks'),
     Input('allvalveopen', 'n_clicks')
     ]
)
def override_commands(input1, n1_clicks, n2_clicks, n3_clicks, n4_clicks, n5_clicks, n6_clicks, n7_clicks, n8_clicks,
                      n9_clicks, n10_clicks, n11_clicks):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'actuatorpropopen' in changed_id:
        actuator_solenoid.open()
        actuator_prop.open()
        call = 'Actuator Prop Opened'
        return call
    elif 'actuatorproppercentopen' in changed_id:
        actuator_solenoid.open()
        actuator_prop_partial = Valve('Actuator Propellant Valve', 'P8_4', 'P8_4', 'Prop', 4, input1)
        actuator_prop_partial.partial_open()
        call = u'Actuator Prop Opened {} percent'.format(input1)
        return call
    elif 'actuatorsolopen' in changed_id:
        actuator_solenoid.open()
        call = 'Actuator Solenoid Opened'
        return call
    elif 'pressurantvalveopen' in changed_id:
        fill_valve.open()
        call = 'Pressurant Valve Opened'
        return call
    elif 'ventvalveopen' in changed_id:
        vent_valve.open()
        call = 'Vent Valve Opened'
        return call
    elif 'actuatorpropclose' in changed_id:
        actuator_prop.close()
        actuator_solenoid.close()
        call = 'Actuator Prop Closed'
        return call
    elif 'actuatorsolclose' in changed_id:
        actuator_solenoid.close()
        call = 'Actuator Solenoid Closed'
        return call
    elif 'pressurantvalvclose' in changed_id:
        fill_valve.close()
        call = 'Pressurant Valve Closed'
        return call
    elif 'ventvalveclose' in changed_id:
        vent_valve.close()
        call = 'Vent Valve Closed'
        return call
    elif 'allvalveclose' in changed_id:
        vent_valve.close()
        fill_valve.close()
        actuator_solenoid.close()
        actuator_prop.close()
        call = 'All Valves Closed'
        return call
    elif 'allvalveopen' in changed_id:
        vent_valve.open()
        fill_valve.open()
        actuator_solenoid.open()
        actuator_prop.open()
        call = 'All Valves Opened'
        return call
    else:
        raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=False, host='192.168.7.2')
    # host='192.168.7.2'
