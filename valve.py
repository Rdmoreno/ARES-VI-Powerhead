# Valve Module
import Adafruit_BBIO.GPIO as GPIO
import pandas as pd
import time
import Adafruit_MCP4725


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
        if self.type == 'solenoid':
            GPIO.setup(self.pin0, GPIO.OUT)
        if self.type == 'prop':
            GPIO.setup(self.pin0, GPIO.OUT)

    def close(self):
        """
        Close the Valve

        description:
            Fully close the selected valve and append its status to the save file at the
            specified operation time.
        """

        t = time.process_time()
        if self.type == 'solenoid':
            GPIO.output(self.pin0, GPIO.LOW)
        else:
            dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=2)
            percentage_calc = 663
            rounded_percentage = round(percentage_calc)
            dac.set_voltage(rounded_percentage)
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
        if 0 > self.partial > 105:
            self.state = 'Partial Open Failed: Falls out of Range'
            pass
        elif self.type != 'solenoid':
            dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=2)
            percentage_calc = 2731.7 * (self.partial / 100) + 663.29
            rounded_percentage = round(percentage_calc)
            dac.set_voltage(rounded_percentage)
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
        if self.type == 'solenoid':
            GPIO.output(self.pin0, GPIO.HIGH)
        else:
            dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=2)
            percentage_calc = 2731.7 * (105 / 100) + 663.29
            rounded_percentage = round(percentage_calc)
            dac.set_voltage(rounded_percentage)
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
        while True:
            try:
                if self.type == 'solenoid':
                    GPIO.output(self.pin0, GPIO.HIGH)
                    time.sleep(1)
                    GPIO.output(self.pin0, GPIO.LOW)
                else:
                    dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=2)
                    percentage_calc = 4095 * 0.75471698
                    rounded_percentage = round(percentage_calc)
                    dac.set_voltage(rounded_percentage)
                    time.sleep(1)
                    percentage_calc = 4095 * .1509434
                    rounded_percentage = round(percentage_calc)
                    dac.set_voltage(rounded_percentage)
                return True
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS FOR...")
                print(self.name)
                return False
