# Valve Module
import Adafruit_BBIO.GPIO as GPIO
from smbus2 import SMBus, i2c_msg
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
        self.state = 'Error, no state given'
        self.df = pd.DataFrame(columns=['time', 'position'])
        self.device = givenDevice
        self.partial = givenPartial
        if self.type == 'solenoid':
            GPIO.setup(self.pin0, GPIO.OUT)
        if self.type == 'Prop':
            GPIO.setup(self.pin0, GPIO.OUT)
            GPIO.setup(self.pin1, GPIO.OUT)

    def close(self):
        """
        Close the Valve

        description:
            Fully close the selected valve and append its status to the save file at the
            specified operation time.
        """

        t = time.process_time()
        if self.type == 'Solenoid':
            GPIO.output(self.pin0, GPIO.LOW)
        else:
            dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=2)
            percentage_calc = 4095 * .1509434
            rounded_percentage = round(percentage_calc)
            dac.set_voltage(rounded_percentage)
            #with SMBus(2) as bus:
                #msg = i2c_msg.write(self.device, [64, 0, 0])
                #bus.i2c_rdwr(msg)
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
            dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=2)
            percentage_calc = 4095 * (.60377358 * (self.partial / 100) + .1509434)
            rounded_percentage = round(percentage_calc)
            dac.set_voltage(rounded_percentage)
            # with SMBus(2) as bus:
                # percentage_calc = 4095 * (self.partial/100)
                # rounded_percentage = round(percentage_calc)
                # byte_1 = (rounded_percentage >> 4)
                #  = (rounded_percentage & 15) << 4
                # msg = i2c_msg.write(self.device, [byte_1, byte_2])
                # bus.i2c_rdwr(msg)
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
            GPIO.output(self.pin0, GPIO.HIGH)
        else:
            dac = Adafruit_MCP4725.MCP4725(address=0x60, busnum=2)
            percentage_calc = 4095 * 0.75471698
            rounded_percentage = round(percentage_calc)
            dac.set_voltage(rounded_percentage)
            #with SMBus(2) as bus:
                #msg = i2c_msg.write(self.device, [64, 255, 240])
                #bus.i2c_rdwr(msg)
        self.state = 'Open'
        self.df = pd.DataFrame([[t, 1]], columns=['time', 'position'])

    def get_state(self):
        """
        Get the valve state

        description:
            Retrieve the current status of a specified pin and return it to the user.
        """

        print(self.name, ' is ', self.state)

    def verify_connection_valve(self):
        """
        Verify functionality

        description: verifies that all sensors can be read before testing can
        continue
        """
        while True:
            try:
                if self.type == 'Solenoid':
                    GPIO.output(self.pin0, GPIO.HIGH)
                    time.sleep(2)
                    GPIO.output(self.pin0, GPIO.LOW)
                else:
                    with SMBus(2) as bus:
                        msg = i2c_msg.write(self.device, [15, 255])
                        bus.i2c_rdwr(msg)
                        time.sleep(2)
                        msg = i2c_msg.write(self.device, [0, 0])
                        bus.i2c_rdwr(msg)
                return True
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS FOR...")
                print(self.name)
                return False
