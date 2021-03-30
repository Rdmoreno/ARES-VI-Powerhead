# Valve Module
import pandas as pd
import time


class Valve:
    def __init__(self, givenName, givenPin, givenPin2, givenType, givenDevice, givenPartial):
        """
        Change or read Valve Status

        description:
            Change the status of a selected valve through the manipulation of the actuator
            and return the status to the user.

        :param givenName: Name of the Valve
        :param givenPin: Pin number of the Valve
        :param givenType: Type of Valve being manipulated
        :param givenDevice: Select the device to connect to via. I2C
        :param givenPartial: The percentage open the actuators should open
        """
        self.name = givenName
        self.pin0 = givenPin
        self.pin1 = givenPin2
        self.type = givenType
        self.state = 'NULL'
        self.df = pd.DataFrame(columns=['time', 'position'])
        self.device = givenDevice
        self.partial = givenPartial

    def close(self):
        """
        Close the Valve

        description:
            Fully close the selected valve and append its status to the save file at the
            specified operation time.
        """

        t = time.process_time()
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
        self.state = 'Open'
        self.df = pd.DataFrame([[t, 1]], columns=['time', 'position'])

    def get_state(self):
        """
        Get the valve state

        description:
            Retrieve the current status of a specified pin and return it to the user.
        """

        return '{}: {}'.format(self.name, self.state)

    def verify_connection_valve(self):
        """
        Verify functionality

        description: verifies that all sensors can be read before testing can
        continue
        """

