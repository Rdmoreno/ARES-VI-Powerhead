import time
import pandas as pd
import csv
from Adafruit_BBIO import GPIO
from sensors import Sensor
from valve import Valve
from Adafruit_I2C import Adafruit_I2C
import numpy as np

# config-pin p9_17 spi_cs
# config-pin p9_18 spi
# config-pin p9_21 spi
# config-pin p9_22 spi_sclk
# config-pin p9_17 spi_cs; config-pin p9_18 spi; config-pin p9_21 spi; config-pin p9_22 spi_sclk

# i2cdetect -y -r 0
# i2cdetect -y -r 1

GPIO.setup('P8_46', GPIO.OUT)
GPIO.output('P8_46', GPIO.HIGH)

actuator_prop = Valve('Actuator Propellant Valve', 'P8_4', 'P8_4', 'solenoid', 4, 100)
actuator_solenoid = Valve('Actuator Solenoid Valve', 'P8_8', 0, 'solenoid', 0, 0)
fill_valve = Valve('Fill Valve', 'P8_12', 0, 'solenoid', 0, 0)
vent_valve = Valve('Vent Valve', 'P8_16', 0, 'solenoid', 0, 0)

input('Press Enter to Open')
actuator_prop.open()
input('Press Enter to Close')
actuator_prop.close()
input('Press Enter to Open')
actuator_solenoid.open()
input('Press Enter to Close')
actuator_solenoid.close()
input('Press Enter to Open')
fill_valve.open()
input('Press Enter to Close')
fill_valve.close()
input('Press Enter to Open')
vent_valve.open()
input('Press Enter to Close')
vent_valve.close()
input('Press Enter to End')

#for x in range(10):
#    pressure_test = Sensor('sensor_test_class', 'temperature', 'P9_16', 'P9_16', 'P9_16', '000', '000', '000')
#    stuff = pressure_test.read_sensor()
#    temp = stuff[0]
#    avg[x] = temp
#print(np.sum(avg) / len(avg))


# for y in range(3):
#    print(pin_stuff[y])
#    for x in range(8):
#        pressure_test = Sensor('sensor_test_class', 'temperature', pin_stuff[y], pin_stuff[y], pin_stuff[y],
#                               channel[x], channel[x], channel[x])
#        stuff = pressure_test.read_sensor()
#        list_val[x] = stuff[0]
#        print()
#    print()




# Valve Definition and Classes
# lox_main = Valve('LOX Propellant Valve', 'P8_13', 'Prop')
# met_main = Valve('Methane Propellant Valve', 'P8_19', 'Prop')
# lox_vent = Valve('LOX Vent Valve', 'P8_12', 'Solenoid')
# met_vent = Valve('Methane Vent Valve', 'P8_14', 'Solenoid')
# p_valve = Valve('Pressurant Valve', 'P8_16', 'Solenoid')

#test_valve = Valve('Test Valve', 'P9_19', 'P9_20', 'actuator', 60, 50)
#test_valve.close()
#input('press enter to end')
#test_valve.open()
#input('press enter to end')
#test_valve.partial_open()
#input('press enter to end')

# GPIO.setup("P8_46", GPIO.OUT)
# GPIO.output("P8_46", GPIO.HIGH)
# input("Press Enter to Continue")
