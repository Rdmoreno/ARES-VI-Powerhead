# Valve Module
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import pandas as pd
import time


class Valve:
    def __init__(self, givenName, givenPin, givenType):
        self.name = givenName
        self.pin = givenPin
        self.type = givenType
        self.state = 'Error, no state given'
        self.df = pd.DataFrame(columns=['time', 'position'])
        if self.type == 'solenoid':
            GPIO.setup(self.pin, GPIO.OUT)

    def close(self):
        t = time.process_time()
        if self.type == 'Solenoid':
            GPIO.output(self.pin, GPIO.LOW)
        else:
            PWM.stop(self.pin)
        self.state = 'Closed'
        self.df = pd.DataFrame([[t, 0]], columns=['time', 'position'])

    def partial_open(self):
        t = time.process_time()
        if self.type != 'Solenoid':
            PWM.start(self.pin, 10)
            self.state = 'Partially Opened'
        self.df = pd.DataFrame([[t, 0.1]], columns=['time', 'position'])

    def open(self):
        t = time.process_time()
        if self.type == 'Solenoid':
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            PWM.set_duty_cycle(self.pin, 255)
        self.state = 'Open'
        self.df = pd.DataFrame([[t, 1]], columns=['time', 'position'])

    def get_state(self):
        print(self.name, ' is ', self.state)