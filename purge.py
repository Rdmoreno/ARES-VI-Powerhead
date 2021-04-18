from sensors import Sensor
from valve import Valve


# Valve Definition and Classes
actuator_prop = Valve('Actuator Propellant Valve', 'P8_4', 'P8_4', 'Prop', 4, 20)
actuator_solenoid = Valve('Actuator Solenoid Valve', 'P8_8', 0, 'solenoid', 0, 0)
fill_valve = Valve('Fill Valve', 'P8_12', 0, 'solenoid', 0, 0)
vent_valve = Valve('Vent Valve', 'P8_16', 0, 'solenoid', 0, 0)

actuator_prop.close()
actuator_solenoid.close()
fill_valve.close()
vent_valve.close()

input('Press Enter to Begin Purging')

fill_valve.open()
actuator_prop.partial_open()
actuator_solenoid.open()

input('Press Enter to End Purge')

actuator_prop.open()
fill_valve.close()

input('Press Enter when Pressurant line has been closed')

fill_valve.open()

input('Press Enter to continue clean up')

fill_valve.open()
actuator_prop.open()
actuator_solenoid.open()
vent_valve.open()

print('End of Purging: Continue to Cold Flow')
