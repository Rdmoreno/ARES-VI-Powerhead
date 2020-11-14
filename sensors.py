# Ryan Moreno new Sensor Module (work in progress)
import csv
import time
from csv import reader
import pandas as pd

Iter = 0


class Sensor:
    def __init__(self, given_name, given_type, given_pin0, given_pin1, given_pin2):
        self.name = given_name
        self.type = given_type
        self.pin0 = given_pin0
        self.pin1 = given_pin1
        self.pin2 = given_pin2
        self.data = pd.DataFrame(columns=['time', 'sensor0', 'sensor1', 'sensor2'])

    def read_pressure(self):
        global Iter
        with open("pressuretestdata.csv", 'rU') as f:
            tempdata = [list(map(int, rec)) for rec in reader(f, delimiter=',')]
        t = time.process_time()
        temps = [tempdata[0][0], tempdata[0][1], tempdata[0][2]]
        self.data = self.data.append({'time': t, 'sensor0': temps[0], 'sensor1': temps[1], 'sensor2': temps[2]}, ignore_index=True)
        print(self.data)
        Sensor.save_data(self, temps, t)
        Sensor.vote(self, temps)

    # noinspection PyMethodMayBeStatic
    def average(self, temps):
        average = sum(temps) / len(temps)
        return average

    def vote(self, temps):
        list_avg = Sensor.average(self, temps)
        difference = [abs(list_avg - temps[0]), abs(list_avg - temps[1]), abs(list_avg - temps[2])]
        del temps[difference.index(max(difference))]
        return Sensor.average(self, temps)

    # noinspection PyMethodMayBeStatic
    def volt_to_psi(self, val):
        return 1715.465955 * (val * 1.8) - 312.506433

    def save_data(self, temps, t):
        with open("pressure_data.csv", 'w', newline='') as f:
            pressure_writer = csv.writer(f)
            if Iter == 0:
                pressure_writer.writerow(['time', 'sensor0', 'sensor1', 'sensor2'])
            pressure_writer.writerow([t, self.data.iloc[Iter]['sensor0'], self.data.iloc[Iter]['sensor1'],
                                      self.data.iloc[Iter]['sensor2']])
