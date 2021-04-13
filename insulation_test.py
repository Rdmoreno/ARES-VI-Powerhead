import csv
import time
from sensors import Sensor
from valve import Valve
from itertools import zip_longest
import threading

input_flag = 1
test_flag = 1


def insulation_test():

    # Data Frames for Saving
    pressure_list = ["Pressure"]
    pressure_time_list = ["time"]

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

    saved_data_combined = [pressure_list, pressure_time_list]
    export_data = zip_longest(*saved_data_combined, fillvalue='')
    with open('insulation_data.csv', 'w', encoding="ISO-8859-1", newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerows(export_data)
    myfile.close()

    print('Welcome to the Team Daedalus: Insulation Test')
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

    vent_valve.open()
    print(vent_valve.get_state())

    print('Press Enter When Desired Tank Ullage is Met')
    time.sleep(3)
    i = threading.Thread(target=get_input)
    i.start()

    while input_flag == 1:
        temp_fill = temperature_fill_line.read_sensor()
        temp_empty = temperature_empty_line.read_sensor()
        pressure = pressure_cold_flow.read_sensor()
        print(temp_fill[0], temp_empty[0], pressure[0])
        time.sleep(.1)
    vent_valve.close()
    print(vent_valve.get_state())
    final_pressure = pressure_cold_flow.read_sensor()

    print("Filling Completed: Current Pressure is...")
    print(final_pressure[0])
    input("Press Enter to Begin Leak Test")
    print('Beginning Leak Test')

    time_start = time.time()
    wait_time = 1
    n = 0

    k = threading.Thread(target=test_end_input)
    k.start()

    while test_flag == 1:
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


def test_end_input():
    global test_flag
    input('')
    test_flag = False


def read_sensors(n, time_start, wait_time):

    # Valve Definition and Classes
    vent_valve = Valve('Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)

    # Pressure Sensor Definition and Classes
    pressure_cold_flow = Sensor('pressure_cold_flow', 'pressure', 'P9_12', 'P9_14',
                                'P9_16', '000', '000', '000')

    pressure_list = []
    pressure_time_list = []

    for i in range(100):
        pressure, time_pres = pressure_cold_flow.read_sensor()
        pressure_list.append(pressure)
        pressure_time_list.append(time_pres + wait_time * n)

    current_time = 'Time Update: {} seconds'.format(time.time() - time_start)
    print(current_time)
    saved_data_combined = [pressure_list, pressure_time_list]
    export_data = zip_longest(*saved_data_combined, fillvalue='')

    with open('leak_data.csv', 'a', encoding="ISO-8859-1", newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerows(export_data)
    myfile.close()


j = threading.Thread(target=insulation_test)
j.start()
