# Valve Module
# Legacy module from Greg Liesen (ARES V 2019-2020)
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
from Adafruit_I2C import Adafruit_I2C
from smbus2 import SMBus, i2c_msg
import pandas as pd
import time


class Valve:
    def __init__(self, givenName, givenPin, givenPin2, givenType, givenDevice):
        """
        Change or read Valve Status

        description:
            Change the status of a selected valve through the manipulation of the actuator
            and return the status to the user.

        :param givenName: Name of the Valve
        :param givenPin: Pin number of the Valve
        :param givenType: Type of Valve being manipulated
        """
        self.name = givenName
        self.pin = givenPin
        self.pin2 = givenPin2
        self.type = givenType
        self.state = 'Error, no state given'
        self.df = pd.DataFrame(columns=['time', 'position'])
        self.device = givenDevice
        if self.type == 'solenoid':
            GPIO.setup(self.pin, GPIO.OUT)
        if self.type == 'arduino':
            GPIO.setup(self.pin, GPIO.OUT)
            GPIO.setup(self.pin2, GPIO.OUT)

    def close(self):
        """
        Close the Valve

        description:
            Fully close the selected valve and append its status to the save file at the
            specified operation time.
        """

        t = time.process_time()
        if self.type == 'Solenoid':
            GPIO.output(self.pin, GPIO.LOW)
        else:
            # PWM.stop(self.pin)
            bus = SMBus(self.device)
            bus.read_i2c_block_data(self.device, )
        self.state = 'Closed'
        self.df = pd.DataFrame([[t, 0]], columns=['time', 'position'])

    def partial_open(self):
        """
        Partially Open the valve

        description:
            Open the valve to a hard-coded value percentage the selected valve and
            append its status to the save file at the specified operation time.
        """

        t = time.process_time()
        if self.type != 'Solenoid':
            with SMBus(2) as bus:
                percentage_calc = 4095 * .1
                rounded_percentage = round(percentage_calc)
                byte_1 = (rounded_percentage >> 8) & 0xff
                byte_2 = rounded_percentage & 0xff
                msg = i2c_msg.write(self.device, [byte_1, byte_2])
                bus.i2c_rdwr(msg)
            self.state = 'Partially Opened'
        self.df = pd.DataFrame([[t, 0.1]], columns=['time', 'position'])

    def open(self):
        """
        Open the Valve

        description:
            Fully open the selected valve and append its status to the save file at the
            specified operation time.
        """

        t = time.process_time()
        if self.type == 'Solenoid':
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            with SMBus(2) as bus:
                # PWM.set_duty_cycle(self.pin, 255)
                msg = i2c_msg.write(self.device, [15, 255])
                bus.i2c_rdwr(msg)
        self.state = 'Open'
        self.df = pd.DataFrame([[t, 1]], columns=['time', 'position'])

    def get_state(self):
        """
        Get the valve state

        description:
            Retrieve the current status of a specified pin and return it to the user.
        """

        print(self.name, ' is ', self.state)
