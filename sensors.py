# Ryan Moreno new Sensor Module (work in progress)
# ARES VI (2020-2021)
import csv
import time
from csv import reader
import pandas as pd
import numpy as np
import Adafruit_BBIO.GPIO as GPIO
import spidev


class Sensor:
    def __init__(self, given_name, given_type,
                 given_pin0, given_pin1, given_pin2, given_channel0, given_channel1, given_channel2):
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
        :param given_channel0: The first channel select for the first sensor in the group
        :param given_channel1: The second channel select for the second sensor in the group
        :param given_channel2: The third channel select for the third sensor in the group

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
        self.channel1 = given_channel0
        self.channel2 = given_channel1
        self.channel3 = given_channel2
        self.channel = [given_channel0, given_channel1, given_channel2]
        GPIO.setup(given_pin0, GPIO.OUT)
        GPIO.output(given_pin0, GPIO.HIGH)
        GPIO.setup(given_pin1, GPIO.OUT)
        GPIO.output(given_pin1, GPIO.HIGH)
        GPIO.setup(given_pin2, GPIO.OUT)
        GPIO.output(given_pin2, GPIO.HIGH)

    def read_sensor(self):
        """
       Read data from pressure sensor

        description:
            Reads the pressure sensors and returns them to the main function after converting from volts to psi and
            averaging.

        :return: avg: Float, the average of the sensor data, after running through the vote function.
        """

        # Recording sensor time
        t = time.process_time()

        processed_data = self.adc_reading()
        volts = np.array([processed_data[0], processed_data[1], processed_data[2]])
        print(np.sum(volts)/len(volts))
        # Converts all pressure sensor readings from volts to psi
        data_unit = self.volt_to_unit(volts)
        avg = self.vote(data_unit)

        # Appends temporary data to sensor data array
        raw_data = np.append([t], [data_unit])
        self.data.append(raw_data)
        self.avg_data.append(avg)
        return avg, t

    def adc_reading(self):
        """
        Reads sensors using SPI

        description: Uses SPI commands toolbox to retrieved raw binary values from
        the sensors and to convert them to an integer value

        :return: processed_data: Float, the raw converted integer values from the sensors
        """
        processed_data = [0] * 3
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

            bit_channel = bit_mode + self.channel[x]
            byte_1 = int(('000001' + bit_channel[0:2]), base=2)
            byte_2 = int((bit_channel[2:4] + '000000'), base=2)
            byte_3 = 0b00000000

            adc = spi.xfer2([byte_1, byte_2, byte_3])
            raw_data = format(adc[1], '08b') + format(adc[2], '08b')
            reference_voltage = 4870
            data_conversion = (int(raw_data[4:], 2) / 4095 * reference_voltage)
            processed_data[x] = data_conversion

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
    def volt_to_unit(self, temps):
        """
        Convert reading into its correct unit based on its type

        description:
            Converts given pressure sensor reading from volts to psi

        :param temps: the array of all three sensor readings in volts

        :return:
            The given pressure sensor reading in psi
        """

        if self.type == 'pressure':
            temps = (temps / 100) * 1000
        else:
            temps = (temps - np.array([1250, 1250, 1250])) / 5
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

    def verify_connection(self):
        """
        Verify functionality

        description: verifies that all sensors can be read before testing can
        continue
        """
        while True:
            try:
                self.adc_reading()
                return True
            except Exception:
                print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS FOR...")
                print(self.name)
                return False
