import csv
import time
from sensors import Sensor
from valve import Valve
from itertools import zip_longest
import threading

input_flag = 1
counter = 0


def leak_test():
    global input_flag
    time_duration = 86400

    # Data Frames for Saving
    pressure_list = ["Pressure"]
    pressure_time_list = ["time"]
    temperature_fill_list = ["Temperature Fill"]
    temperature_fill_time_list = ["time"]
    temperature_empty_list = ["Temperature Empty"]
    temperature_empty_time_list = ["time"]

    # Valve Definition and Classes
    actuator_prop = Valve('Actuator Propellant Valve', 'P8_4', 'P8_4', 'Prop', 4, 100)
    actuator_solenoid = Valve('Actuator Solenoid Valve', 'P8_8', 0, 'solenoid', 0, 0)
    fill_valve = Valve('Fill Valve', 'P8_12', 0, 'solenoid', 0, 0)
    vent_valve = Valve('Vent Valve', 'P8_16', 0, 'solenoid', 0, 0)

    actuator_prop.open()
    actuator_solenoid.open()
    fill_valve.open()
    vent_valve.open()

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
    input("\nVerification Complete, Press Enter to Continue:\n")

    print()
    print('Closing All Valves')
    actuator_prop.close()
    actuator_solenoid.close()
    fill_valve.close()
    vent_valve.close()

    print(actuator_prop.get_state())
    print(actuator_solenoid.get_state())
    print(fill_valve.get_state())
    print(vent_valve.get_state())

    input('Press Enter to Open filling valve')
    print('Opening Fill Valve: Begin Filling Procedure')
    input('Press Enter to begin filling and Enter again to end filling')
    fill_valve.open()
    vent_valve.open()

    print(fill_valve.get_state())
    print(vent_valve.get_state())

    print('Press Enter When Desired Pressure is Met')
    time.sleep(3)
    i = threading.Thread(target=get_input)
    i.start()

    while input_flag == 1:
        pressure = pressure_cold_flow.read_sensor()
        print(pressure[0])
        time.sleep(.1)
    fill_valve.close()
    vent_valve.close()
    print(fill_valve.get_state())
    print(vent_valve.get_state())
    final_pressure = pressure_cold_flow.read_sensor()

    print("Filling Completed: Current Pressure is...")
    print(final_pressure[0])
    input("Press Enter to Begin Leak Test")
    print('Beginning Leak Test')

    input_flag = 1
    time_start = time.time()
    wait_time = 600
    n = 0

    while time.time() - time_start < time_duration:
        read_sensors(n, time_start, wait_time)
        time.sleep(wait_time)
        n = n + 1

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


def read_sensors(n, time_start, wait_time):

    # Valve Definition and Classes
    vent_valve = Valve('Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)

    # Pressure Sensor Definition and Classes
    pressure_cold_flow = Sensor('pressure_cold_flow', 'pressure', 'P9_12', 'P9_14',
                                'P9_16', '000', '000', '000')

    # Temperature Sensor Definition and Classes
    temperature_fill_line = Sensor('temperature_fill_line', 'temperature', 'P9_12',
                                   'P9_14', 'P9_16', '000', '000', '000')
    temperature_empty_line = Sensor('temperature_empty_line', 'temperature',
                                    'P9_12', 'P9_14', 'P9_16', '000', '000', '000')
    maximum_pressure = 6000
    nominal_pressure = 500

    pressure_list = []
    pressure_time_list = []
    temperature_fill_list = []
    temperature_fill_time_list = []
    temperature_empty_list = []
    temperature_empty_time_list = []

    for i in range(1000):
        global counter
        pressure, time_pres = pressure_cold_flow.read_sensor()
        temp_fill, time_fill = temperature_fill_line.read_sensor()
        temp_empty, time_empty = temperature_empty_line.read_sensor()

        pressure_list.append(pressure)
        pressure_time_list.append(time_pres + wait_time * n)
        temperature_fill_list.append(temp_fill)
        temperature_fill_time_list.append(time_fill + wait_time * n)
        temperature_empty_list.append(temp_empty)
        temperature_empty_time_list.append(time_empty + wait_time * n)

        if pressure >= maximum_pressure:
            counter = counter + 1
        else:
            counter = 0

        if counter >= 3:
            time_relief = time.process_time()
            vent_valve.open()
            print('Pressure Exceeded Maximum: Opening Relief Valve')
            print(time_relief)
            while True:
                pres_relief = pressure_cold_flow.read_sensor()
                if pres_relief[0] < nominal_pressure:
                    time_relief_end = time.process_time()
                    print('Closing Relief Valve')
                    vent_valve.close()
                    print(time_relief_end)
                    break

    current_time = 'Time Update: {} seconds'.format(time.time() - time_start)
    print(current_time)
    saved_data_combined = [pressure_list, pressure_time_list, temperature_fill_list, temperature_fill_time_list,
                           temperature_empty_list, temperature_empty_time_list]
    export_data = zip_longest(*saved_data_combined, fillvalue='')

    with open('leak_data.csv', 'a', encoding="ISO-8859-1", newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerows(export_data)
    myfile.close()


j = threading.Thread(target=leak_test)
j.start()
