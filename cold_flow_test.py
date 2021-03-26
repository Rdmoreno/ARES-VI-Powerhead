import csv
import time
from sensors import Sensor
from valve import Valve
from csv import reader
import pandas as pd
import numpy as np

# allValves will be an array of all of the valves currently configured as defined in the previous file
def coldFlowTest(allValves):
    n2Valve = null
    heValve = null

    for cValve in allValves:
        cValve.close()
        if cValve.name == "LN2":
            n2Valve = cValve
        if cValve.name = "H2":
            heValve = cValve

    n2Valve.open()
    # Wait for temp spike
    n2Valve.close()

    heValve.open()
    # wait for pressure to reach requirement
    heValve.close()
