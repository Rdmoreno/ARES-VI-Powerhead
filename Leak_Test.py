import csv
import time
from sensors_test import Sensor
from valve import Valve
from itertools import zip_longest

time_duration = 86400

# Data Frames for Saving
pressure_list = ["Pressure"]
pressure_time_list = ["time"]
temperature_fill_list = ["Temperature Fill"]
temperature_fill_time_list = ["time"]
temperature_empty_list = ["Temperature Empty"]
temperature_empty_time_list = ["time"]

# Valve Definition and Classes
lox_main = Valve('LOX Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, 10)
lox_vent = Valve('LOX Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)
met_vent = Valve('Methane Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)
p_valve = Valve('Pressurant Valve', 'P8_12', 0, 'Solenoid', 0, 0)

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

time_start = time.time()

while time.time() < time_start + time_duration:
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
        pressure_time_list.append(time_pres)
        temperature_fill_list.append(temp_fill)
        temperature_fill_time_list.append(time_fill)
        temperature_empty_list.append(temp_empty)
        temperature_empty_time_list.append(time_empty)

        saved_data_combined = [pressure_list, pressure_time_list, temperature_fill_list, temperature_fill_time_list,
                               temperature_empty_list, temperature_empty_time_list]
        export_data = zip_longest(*saved_data_combined, fillvalue='')

    with open('leak_data.csv', 'a', encoding="ISO-8859-1", newline='') as myfile:
        wr = csv.writer(myfile)
        wr.writerows(export_data)
    myfile.close()
    time.sleep(600)
print('done')
