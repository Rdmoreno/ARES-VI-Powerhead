# Ryan Moreno new Sensor Module (work in progress)
import csv
import time
from csv import reader
import pandas as pd
import numpy as np
from random import randint
# import Adafruit_BBIO.ADC as ADC


class Sensor:
    def __init__(self, given_name, given_type,
                 given_pin0, given_pin1, given_pin2):
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
        self.data = []
        self.avg_data = []

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
        temps = [t, randint(1, 20), randint(1, 20), randint(1, 20)]

        # temps = [ADC.read(self.pin0), ADC.read(self.pin1),
        #         ADC.read(self.pin2)]

        # Converts all pressure sensor readings from volts to psi
        # if self.type == 'pressure':
        #    psi_dat = self.volt_to_psi(temps)

        # Appending numpy array to data list
        self.data.append(temps)
        print(self.data)

        # fetching voted average
        avg = self.vote(temps[1::])

        # Appends temporary data to sensor data array
        self.data.append(np.array(temps))
        self.avg_data.append(avg)

        # Returns average sensor reading to the main function
        return avg

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
        average = sum(temps) / len(temps)
        return average

    def vote(self, temps):
        """
        Voting of the three sensor readings

        description: Votes and removes the sensor most deviating from the
        average of the three sensor readings.

        :param temps: Array of the operation time and the three sensor readings

        :return: average(temps): the final average after voting

        """

        # Averages the given temporary three sensor data array and
        # votes/removes the sensor deviating furthest from the average.
        list_avg = self.average(temps)
        difference = [abs(list_avg - temps[0]), abs(list_avg - temps[1]),
                      abs(list_avg - temps[2])]
        del temps[difference.index(max(difference))]

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
        return 1715.465955 * (temps * 1.8) - 312.506433

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
