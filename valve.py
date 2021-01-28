# Valve Module
# Legacy module from Greg Liesen (ARES V 2019-2020)
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import pandas as pd
import time


class Valve:
    def __init__(self, givenName, givenPin, givenType):
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
        self.type = givenType
        self.state = 'Error, no state given'
        self.df = pd.DataFrame(columns=['time', 'position'])
        if self.type == 'solenoid':
            GPIO.setup(self.pin, GPIO.OUT)

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
            PWM.stop(self.pin)
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
            PWM.start(self.pin, 10)
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
            PWM.set_duty_cycle(self.pin, 255)
        self.state = 'Open'
        self.df = pd.DataFrame([[t, 1]], columns=['time', 'position'])

    def get_state(self):
        """
        Get the valve state

        description:
            Retrieve the current status of a specified pin and return it to the user.
        """

        print(self.name, ' is ', self.state)
