from csv import reader
import pandas as pd
import numpy as np
import time
from sensors_test import Sensor
from valve_test import Valve
from itertools import zip_longest
import threading

# Data Frames for Saving
pressure_list = ["Pressure"]
pressure_time_list = ["time"]
temperature_fill_list = ["Temperature Fill"]
temperature_fill_time_list = ["time"]
temperature_empty_list = ["Temperature Empty"]
temperature_empty_time_list = ["time"]
official_time_list = ["Official Time"]

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

# Valve States and Tracking Global Variables
act_prop_state = 'Actuator Propellant Valve: NOT SET'
act_sol_state = 'Actuator Solenoid Valve: NOT SET'
fill_state = 'Fill Solenoid Valve: NOT SET'
vent_state = 'Vent Solenoid Valve: NOT SET'






@app.callback(
    [Output('coldflowoutput', 'children')],
    [Input('coldflowbutton', 'n_clicks'),
     Input('coldflowfillbutton', 'n_clicks')])
def coldFlowTest(n_clicks, m_clicks):
    global act_prop_state, act_sol_state, fill_state, vent_state
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'coldflowbutton' in changed_id:
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
        act_prop_state = 'Actuator Propellant Valve: Closed'
        act_sol_state = 'Actuator Solenoid Valve: Closed'
        fill_state = 'Fill Solenoid Valve: Closed'
        vent_state = 'Vent Solenoid Valve: Closed'

        input('Press Enter to Open filling valve')
        print('Opening Fill Valve: Begin Filling Procedure')
        input('Press Enter to begin filling and Enter again to end filling')
        fill_valve.open()
        fill_state = 'Fill Solenoid Valve: Open'

        maximum_pressure = 645
        nominal_pressure = 500

        print('Press the Cold FLow Filling Button When Desired Pressure is Met')
        time.sleep(10)

        while 'coldflowfillbutton' not in changed_id:
            pressure = pressure_cold_flow.read_sensor()
            if pressure[0] >= maximum_pressure:
                time_relief = time.process_time()
                print('Pressure Exceeded Maximum: Opening Relief Valve')
                print(time_relief)
                flag = 0
                while pressure[0] >= maximum_pressure:
                    pressure = pressure_cold_flow.read_sensor()
                    print(pressure[0])
                    if flag == 0:
                        fill_valve.close()
                        fill_state = 'Fill Solenoid Valve: Closed'
                        vent_valve.open()
                        vent_state = 'Vent Solenoid Valve: Open'
                        flag = 1
                    if pressure[0] <= nominal_pressure:
                        time_relief_end = time.process_time()
                        fill_valve.open()
                        fill_state = 'Fill Solenoid Valve: Open'
                        vent_valve.close()
                        vent_state = 'Vent Solenoid Valve: Closed'
                        print(time_relief_end)
            time.sleep(.3)
        fill_valve.close()
        fill_state = 'Fill Solenoid Valve: Closed'
        final_pressure = pressure_cold_flow.read_sensor()
        pressure_message = 'Final Liquid Nitrogen Fill Pressure: {}'.format(final_pressure[0])
        print(pressure_message)

        input('Press Enter to Open filling valve')
        fill_valve.open()
        fill_state = 'Fill Solenoid Valve: Open'
        print('Opening Fill Valve: Begin Helium Filling Procedure')
        input('Press Enter to begin filling')
        print('Press the Cold FLow Filling Button When Desired Pressure is Met')
        time.sleep(10)

        while 'coldflowfillbutton' not in changed_id:
            pressure = pressure_cold_flow.read_sensor()
            if pressure[0] >= maximum_pressure:
                time_relief = time.process_time()
                print('Pressure Exceeded Maximum: Opening Relief Valve')
                print(time_relief)
                flag = 0
                while pressure[0] >= maximum_pressure:
                    pressure = pressure_cold_flow.read_sensor()
                    print(pressure[0])
                    if flag == 0:
                        fill_valve.close()
                        fill_state = 'Fill Solenoid Valve: Closed'
                        vent_valve.open()
                        vent_state = 'Vent Solenoid Valve: Open'
                        flag = 1
                    if pressure[0] <= nominal_pressure:
                        time_relief_end = time.process_time()
                        fill_valve.open()
                        fill_state = 'Fill Solenoid Valve: Open'
                        vent_valve.close()
                        vent_state = 'Vent Solenoid Valve: Closed'
                        print(time_relief_end)
            time.sleep(.3)
        fill_valve.close()
        fill_state = 'Fill Solenoid Valve: Closed'
        final_pressure = pressure_cold_flow.read_sensor()
        pressure_message = 'Final Helium Fill Pressure: {}'.format(final_pressure[0])
        print(pressure_message)
        input('Cold Flow Filling Procedure Completed: Press Enter to Confirm')
        print('done')
        return 'Cold Flow Filling Finished: Press Start'
    else:
        raise PreventUpdate