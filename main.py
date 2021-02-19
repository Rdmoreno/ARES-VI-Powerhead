import time
import pandas as pd
import csv
from Adafruit_BBIO import GPIO
from sensors import Sensor
from valve import Valve

Iter = 0

# config-pin p9_17 spi_cs
# config-pin p9_18 spi
# config-pin p9_21 spi
# config-pin p9_22 spi_sclk
# config-pin p9_17 spi_cs;  config-pin p9_18 spi; config-pin p9_21 spi; config-pin p9_22 spi_sclk

# Pressure Sensor Definitions and Classes
GPIO.setup("P9_11", GPIO.OUT)
GPIO.output("P9_11", GPIO.HIGH)
GPIO.setup("P9_13", GPIO.OUT)
GPIO.output("P9_13", GPIO.HIGH)
GPIO.setup("P9_15", GPIO.OUT)
GPIO.output("P9_15", GPIO.HIGH)
pressure_test = Sensor('sensor_test_class', 'temperature', 'P9_11', 'P9_13', 'P9_15', '000', '000', '000')

avg = pressure_test.read_pressure()

print(avg)

# Valve Definition and Classes
# lox_main = Valve('LOX Propellant Valve', 'P8_13', 'Prop')
# met_main = Valve('Methane Propellant Valve', 'P8_19', 'Prop')
# lox_vent = Valve('LOX Vent Valve', 'P8_12', 'Solenoid')
# met_vent = Valve('Methane Vent Valve', 'P8_14', 'Solenoid')
# p_valve = Valve('Pressurant Valve', 'P8_16', 'Solenoid')
