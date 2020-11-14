# Ryan Moreno new Sensor Module (work in progress)
import csv
import time
from csv import reader
import pandas as pd
import numpy as np
from random import randint


class Sensor:
    def __init__(self, given_name, given_type,
                 given_pin0, given_pin1, given_pin2):
        self.name = given_name
        self.type = given_type
        self.pin0 = given_pin0
        self.pin1 = given_pin1
        self.pin2 = given_pin2
        self.data = []
        self.avg_data = []

    def read_pressure(self):
        """"
        Read data from pressure sensor
        
        description blah vail
        
        :returns
        avg: Float, 
            the average of the sensor data, after running through the 
            vote function.        
        """

        # Streaming data from CSV to simulate sensor reading
        # with open("pressuretestdata.csv", 'rU') as f:
        #     tempdata = [list(map(int, rec)) for rec in
        #                 reader(f, delimiter=',')]

        # Recording sensor time
        t = time.process_time()
        # print(t)
        # Placing sensor data into numpy array
        temps = [t, randint(1, 20), randint(1, 20), randint(1, 20)]

        # Appending numpy array to data list
        self.data.append(temps)
        # print(self.data)

        # fetching voted average
        avg = self.vote(temps[1::])

        self.data.append(np.array(temps))
        self.avg_data.append(avg)

        return avg

    # noinspection PyMethodMayBeStatic
    def average(self, temps):
        average = sum(temps) / len(temps)
        return average

    def vote(self, temps):
        list_avg = self.average(temps)
        difference = [abs(list_avg - temps[0]), abs(list_avg - temps[1]),
                      abs(list_avg - temps[2])]

        del temps[difference.index(max(difference))]
        return self.average(temps)

    # noinspection PyMethodMayBeStatic
    def volt_to_psi(self, val):
        return 1715.465955 * (val * 1.8) - 312.506433

    def save_data(self):
        data_df = pd.DataFrame(self.data, columns=['time', 'p0', 'p1', 'p2'])
        data_df.to_excel('raw_data.xlsx')
        avg_df = pd.DataFrame(self.avg_data, columns=['avg'])
        avg_df.to_excel('avg_data.xlsx')
