import csv
import time
from sensors_test import Sensor
from valve_test import Valve
from itertools import zip_longest
from csv import reader
import numpy as np
import threading

input_flag = 1


def leak_test():

    time_duration = 300

    # Data Frames for Saving
    pressure_list = ["Pressure"]
    pressure_time_list = ["time"]
    temperature_fill_list = ["Temperature Fill"]
    temperature_fill_time_list = ["time"]
    temperature_empty_list = ["Temperature Empty"]
    temperature_empty_time_list = ["time"]

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

    saved_data_combined = [pressure_list, pressure_time_list, temperature_fill_list, temperature_fill_time_list,
                           temperature_empty_list, temperature_empty_time_list]
    export_data = zip_longest(*saved_data_combined, fillvalue='')
    with open('leak_data.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerows(export_data)
    myfile.close()

    print('Welcome to the Team Daedalus: Leak Test')
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

    actuator_prop.get_state()
    actuator_solenoid.get_state()
    fill_valve.get_state()
    vent_valve.get_state()

    input('Press Enter to Open filling valve')
    print('Opening Fill Valve: Begin Filling Procedure')
    print('Press Enter to begin filling and Enter again to end filling')
    fill_valve.open()
    fill_valve.get_state()

    maximum_pressure = 200000
    nominal_pressure = 100

    print('Press Enter When Desired Pressure is Met')
    time.sleep(3)
    i = threading.Thread(target=get_input)
    i.start()

    while input_flag == 1:
        pressure = pressure_cold_flow.read_sensor()
        # pressure = np.array([tempdata[i][0], tempdata[i][1], tempdata[i][2]])
        # i = i + 1
        print(pressure[0])
        if pressure[0] >= maximum_pressure:
            time_relief = time.time()
            print('Pressure Exceeded Maximum: Opening Relief Valve')
            print(time_relief)
            flag = 0
            while pressure[0] >= maximum_pressure:
                pressure = pressure_cold_flow.read_sensor()
                # pressure = np.array([tempdata[i][0], tempdata[i][1], tempdata[i][2]])
                # i = i + 1
                print(pressure[0])
                if flag == 0:
                    fill_valve.close()
                    fill_valve.get_state()
                    vent_valve.open()
                    vent_valve.get_state()
                    flag = 1
                if pressure[0] <= nominal_pressure:
                    time_relief_end = time.time()
                    fill_valve.open()
                    fill_valve.get_state()
                    vent_valve.close()
                    vent_valve.get_state()
                    print(time_relief_end)
    fill_valve.close()
    fill_valve.get_state()
    final_pressure = pressure_cold_flow.read_sensor()

    print("Filling Completed: Current Pressure is...")
    print(final_pressure[0])
    input("Press Enter to Begin Leak Test")

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
            pressure_time_list.append(time_pres + 30*n)
            temperature_fill_list.append(temp_fill)
            temperature_fill_time_list.append(time_fill + 30*n)
            temperature_empty_list.append(temp_empty)
            temperature_empty_time_list.append(time_empty + 30*n)

            saved_data_combined = [pressure_list, pressure_time_list, temperature_fill_list, temperature_fill_time_list,
                                   temperature_empty_list, temperature_empty_time_list]
            export_data = zip_longest(*saved_data_combined, fillvalue='')

        with open('leak_data.csv', 'a', encoding="ISO-8859-1", newline='') as myfile:
            wr = csv.writer(myfile)
            wr.writerows(export_data)
        myfile.close()
        n = n + 1
        time.sleep(30)
    print('done')
    print(time.time() - time_start)
    input('Press Enter to Open Valves and Depressurize Tank')
    actuator_prop.open()
    actuator_solenoid.open()
    fill_valve.open()
    vent_valve.open()

    actuator_prop.get_state()
    actuator_solenoid.get_state()
    fill_valve.get_state()
    vent_valve.get_state()


def get_input():
    global input_flag
    input('')
    input_flag = False


j = threading.Thread(target=leak_test)
j.start()
