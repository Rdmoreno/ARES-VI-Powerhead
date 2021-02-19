# Ryan Moreno new Sensor Module (work in progress)
# ARES VI (2020-2021)
import csv
import time
from csv import reader
import pandas as pd
import numpy as np
from random import randint
import Adafruit_BBIO.GPIO as GPIO
from Adafruit_BBIO.SPI import SPI
import spidev


class Sensor:
    def __init__(self, given_name, given_type,
                 given_pin0, given_pin1, given_pin2, given_channel1, given_channel2, given_channel3):
        """
        Read data from sensor

        description:
            Takes sensor information including name, type, and pin locations to read the sensor and return the
            average of the sensors after voting.

        :param given_name: Name of the group of sensors
        :param given_type: Type of Sensor
        :param given_pin0: The first pin in the group
        :param given_pin1: The second pin in the group
        :param given_pin2: The third pin in the group

        :return: avg: Float, the average of the sensor data, after running through the vote function.
        """

        # Given sensor information added to class self type for function use
        self.name = given_name
        self.type = given_type
        self.pin0 = given_pin0
        self.pin1 = given_pin1
        self.pin2 = given_pin2
        self.pins = [given_pin0, given_pin1, given_pin2]
        self.data = []
        self.avg_data = []
        self.channel1 = given_channel1
        self.channel2 = given_channel2
        self.channel3 = given_channel3
        self.channel = [given_channel1, given_channel2, given_channel3]

    def read_pressure(self):
        """
       Read data from pressure sensor

        description:
            Reads the pressure sensors and returns them to the main function after converting from volts to psi and
            averaging.

        :return: avg: Float, the average of the sensor data, after running through the vote function.
        """

        # Streaming data from CSV to simulate sensor reading
        # with open("pressuretestdata.csv", 'rU') as f:
        #     tempdata = [list(map(int, rec)) for rec in
        #                 reader(f, delimiter=',')]

        # Recording sensor time
        t = time.process_time()

        # Placing sensor data into numpy array
        # volts = np.array([randint(1, 20), randint(1, 20), randint(1, 20)])

        processed_data = self.adc_reading()
        volts = np.array([processed_data[0], processed_data[1], processed_data[2]])
        print(volts)
        volts_ref = self.reference_volt_conversion(volts)

        # Converts all pressure sensor readings from volts to psi
        # if self.type == 'pressure':
        pressure = self.volt_to_psi(volts_ref)

        # fetching voted average
        avg = self.vote(pressure)
        # Testing
        # Appends temporary data to sensor data array
        raw_data = np.append([t], [pressure])
        self.data.append(raw_data)
        self.avg_data.append(avg)
        # self.save_data()

        # Returns average sensor reading to the main function
        return avg, t

    def adc_reading(self):
        processed_data = [0]*3
        for x in range(3):
            GPIO.output(self.pins[x], GPIO.LOW)

            spi = spidev.SpiDev()
            spi.open(0, 0)

            spi.mode = 0
            spi.bits_per_word = 8
            spi.max_speed_hz = 1000000

            if self.type == 'pressure':
                bit_mode = '0'
            else:
                bit_mode = '1'

            # bit_channel = bit_mode + format(self.channel[x], '03b')
            bit_channel = bit_mode + self.channel[x]
            byte_1 = int(('000001' + bit_channel[0:1]), base=2)
            byte_2 = int((bit_channel[2:3] + '000000'), base=2)
            byte_3 = 0b00000000
            # print(bin(byte_1))
            # print(bin(byte_2))
            # print(bin(byte_3))
            # print()

            adc = spi.xfer2([byte_1, byte_2, byte_3])
            raw_data = format(adc[1], '08b') + format(adc[2], '08b')
            data_conversion = int(raw_data[4:], 2)/4095*3350
            processed_data[x] = data_conversion
            print(raw_data)
            print(data_conversion)
            print(processed_data[x])
            print()

            spi.close()
            GPIO.output(self.pins[x], GPIO.HIGH)
        return processed_data

    # noinspection PyMethodMayBeStatic
    def average(self, temps):
        """
        Averages the data from sensors

        description: Averages the readings from the three sensors before and
        after voting occurs

        :param temps: Array of the operation time and the three sensor readings

        :return: avg: Float, the average of the sensor data, after running
        through the vote function.
        """

        # Averages the current temporary sensor data array and returns it to
        # the vote function
        average = np.sum(temps) / len(temps)
        return average

    def vote(self, temps):
        """
        Voting of the three sensor readings

        description: Votes and removes the sensor most deviating from the
        average +of the three sensor readings.

        :param temps: Array of the operation time and the three sensor readings

        :return: average(temps): the final average after voting

        """

        # Averages the given temporary three sensor data array and
        # votes/removes the sensor deviating furthest from the average.
        list_avg = self.average(temps)
        difference = [abs(list_avg - temps[0]), abs(list_avg - temps[1]),
                      abs(list_avg - temps[2])]
        temps = np.delete(temps, difference.index(max(difference)))

        # Returns the average of the remaining two sensor readings as the
        # final sensor reading
        return self.average(temps)

    # noinspection PyMethodMayBeStatic
    def volt_to_psi(self, temps):
        """
        Convert pressure sensor reading

        description:
            Converts given pressure sensor reading from volts to psi

        :param temps: the array of all three pressure sensor readings in volts
        :param val: The reading from the three pressure sensors in volts

        :return:
            The given pressure sensor reading in psi
        """

        # Returns the pressure sensor reading in psi using the equation
        # listed below
        temps = 1715.465955 * (1.8 * temps) - np.array([312.506433, 312.506433, 312.506433])

        return temps

    def reference_volt_conversion(self, temps):
        """
        Correct voltage reading to the correct voltage reference

        description:
            Corrects the voltage reading to the reading based on the reference
            voltage of 3.3 Volts

        :param temps: the array of all three pressure sensor readings in volts
        :param val: The reading from the three pressure sensors in volts

        :return:
            The given voltage in the correct reference frame
        """

        reference_voltage = 3.3
        temps = temps / reference_voltage * 4095

        return temps

    def save_data(self):
        """
        Record sensor data

        description: Records the data from the current iteration of the
        sensor reading into a excel file.
        """

        # Takes raw sensor data readings and appends them into the excel
        # document
        data_df = pd.DataFrame(self.data, columns=['time', 'p0', 'p1', 'p2'])
        data_df.to_excel('raw_data.xlsx')

        # Takes the average sensor reading after voting and appends them
        # into an excel document
        avg_df = pd.DataFrame(self.avg_data, columns=['avg'])
        avg_df.to_excel('avg_data.xlsx')
