import time
import pandas as pd
import csv
from sensors import Sensor
from valve import Valve

Iter = 0

# Pressure Sensor Definitions and Classes
pressure_test = Sensor('sensor_test_class', 'pressure', 'pin0', 'pin1', 'pin2')

avg = pressure_test.read_pressure

print(avg)

# Valve Definition and Classes
# lox_main = Valve('LOX Propellant Valve', 'P8_13', 'Prop')
# met_main = Valve('Methane Propellant Valve', 'P8_19', 'Prop')
# lox_vent = Valve('LOX Vent Valve', 'P8_12', 'Solenoid')
# met_vent = Valve('Methane Vent Valve', 'P8_14', 'Solenoid')
# p_valve = Valve('Pressurant Valve', 'P8_16', 'Solenoid')
