import time
import pandas as pd
import csv
from Adafruit_BBIO import GPIO
from sensors import Sensor
from valve import Valve
from Adafruit_I2C import Adafruit_I2C

Iter = 1

# config-pin p9_17 spi_cs
# config-pin p9_18 spi
# config-pin p9_21 spi
# config-pin p9_22 spi_sclk
# config-pin p9_17 spi_cs; config-pin p9_18 spi; config-pin p9_21 spi; config-pin p9_22 spi_sclk

# i2cdetect -y -r 0
# i2cdetect -y -r 1

# Pressure Sensor Definitions and Classes
# GPIO.setup("P9_12", GPIO.OUT)
# GPIO.output("P9_12", GPIO.HIGH)
# GPIO.setup("P9_14", GPIO.OUT)
# GPIO.output("P9_14", GPIO.HIGH)
# GPIO.setup("P9_16", GPIO.OUT)
# GPIO.output("P9_16", GPIO.HIGH)

# pressure_test = Sensor('sensor_test_class', 'temperature', 'P9_12', 'P9_14', 'P9_16', '000', '000', '000')
# avg = pressure_test.read_pressure()
# print(avg)

# test_main = Valve('Test Valve', 'P9_19', 'P9_20', 'arduino', 4)
# test_main.partial_open()
# input("Press Enter to Continue")
# test_main.open()

# Valve Definition and Classes
# lox_main = Valve('LOX Propellant Valve', 'P8_13', 'Prop')
# met_main = Valve('Methane Propellant Valve', 'P8_19', 'Prop')
# lox_vent = Valve('LOX Vent Valve', 'P8_12', 'Solenoid')
# met_vent = Valve('Methane Vent Valve', 'P8_14', 'Solenoid')
# p_valve = Valve('Pressurant Valve', 'P8_16', 'Solenoid')

GPIO.setup("P8_46", GPIO.OUT)
GPIO.output("P8_46", GPIO.HIGH)
input("Press Enter to Continue")