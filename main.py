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
    global counter

    # Valve Definition and Classes
    actuator_prop = Valve('Actuator Propellant Valve', 'P8_4', 'P8_4', 'prop', 4, 20)
    actuator_solenoid = Valve('Actuator Solenoid Valve', 'P8_4', 0, 'solenoid', 0, 0)
    fill_valve = Valve('Fill Valve', 'P8_8', 0, 'solenoid', 0, 0)
    vent_valve = Valve('Vent Valve', 'P8_45', 0, 'solenoid', 0, 0)

    actuator_solenoid.open()
    actuator_prop.partial_open()
    time.sleep(2)

    # Pressure Sensor Definition and Classes
    pressureall = Sensor('pressure_cold_flow', 'pressure', 'P9_16', 'P9_16', 'P9_16', '000', '010', '100')
    pressure0 = Sensor('pressure_cold_flow', 'pressure', 'P9_16', 'P9_16', 'P9_16', '000', '000', '000')
    pressure2 = Sensor('pressure_cold_flow', 'pressure', 'P9_16', 'P9_16', 'P9_16', '010', '010', '010')
    pressure4 = Sensor('pressure_cold_flow', 'pressure', 'P9_16', 'P9_16', 'P9_16', '100', '100', '100')

    print('Welcome to the Team Daedalus: Leak Test')
    input('Please Press Enter to Confirm Start')
    print('Starting System Check')
    print()
    input("\nVerification Complete, Press Enter to Continue:\n")

    print()
    print('Closing All Valves')
    actuator_solenoid.close()
    actuator_prop.close()
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

    print(fill_valve.get_state())
    print(vent_valve.get_state())

    print('Press Enter When Desired Pressure is Met')
    time.sleep(3)
    i = threading.Thread(target=get_input)
    i.start()

    maximum_pressure = 10000
    nominal_pressure = 500

    while input_flag == 1:
        a = pressure0.read_sensor()
        b = pressure2.read_sensor()
        c = pressure4.read_sensor()
        e = pressureall.read_sensor()
        d = [e[0], a[0], b[0], c[0]]

        if e[0] >= maximum_pressure:
            counter = counter + 1
        else:
            counter = 0

        if counter >= 3:
            time_relief = time.process_time()
            vent_valve.open()
            print('Pressure Exceeded Maximum: Opening Relief Valve')
            print(time_relief)
            while True:
                pres_relief = pressureall.read_sensor()
                if pres_relief[0] < nominal_pressure:
                    time_relief_end = time.process_time()
                    print('Closing Relief Valve')
                    vent_valve.close()
                    print(time_relief_end)
                    break

        print(d)
        time.sleep(.2)
    fill_valve.close()
    vent_valve.close()
    print(fill_valve.get_state())
    print(vent_valve.get_state())

    input('Press Enter to Open Actuator at 10%')
    actuator_solenoid.open()
    actuator_prop.partial_open()

    input('Press Enter to Open Vent Valve')
    vent_valve.open()

    input('Enter all Other Valves')
    vent_valve.close()
    time.sleep(1)
    fill_valve.open()
    actuator_solenoid.open()
    actuator_prop.open()

    actuator_prop.get_state()
    actuator_solenoid.get_state()
    fill_valve.get_state()
    vent_valve.get_state()
    input('Press Enter to End and Close all valves')
    vent_valve.close()
    fill_valve.close()
    actuator_solenoid.close()
    actuator_prop.close()


def get_input():
    global input_flag
    input('')
    input_flag = False


j = threading.Thread(target=leak_test)
j.start()
