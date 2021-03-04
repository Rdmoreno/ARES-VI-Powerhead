from sensors import Sensor
from valve import Valve
import front_end

percentage = 100

# Valve Definition and Classes
lox_main = Valve('LOX Propellant Valve', 'P8_13', 'P8_13', 'Prop', 4, percentage)
lox_vent = Valve('LOX Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)
met_vent = Valve('Methane Vent Valve', 'P8_12', 0, 'Solenoid', 0, 0)
p_valve = Valve('Pressurant Valve', 'P8_12', 0, 'Solenoid', 0, 0)

# Pressure Sensor Definition and Classes
pressure_cold_flow = Sensor('pressure_cold_flow', 'pressure', 'P9_12', 'P9_14', 'P9_16', '000', '000', '000')

# Temperature Sensor Definition and Classes
temperature_fill_line = Sensor('temperature_fill_line', 'temperature', 'P9_12', 'P9_14', 'P9_16', '000', '000', '000')
temperature_empty_line = Sensor('temperature_empty_line', 'temperature', 'P9_12', 'P9_14', 'P9_16', '000', '000', '000')

print("Before Test Start: Verify Electronic Connections and Follow Safety Procedures\n")
print("------------------------------------------")
print("\nProject Daedalus: Powerhead Hardware/Software Test\n")
print("""\

                   ._ o o
                   \_`-)|_
                ,""       \ 
              ,"  ## |   ಠ ಠ. 
            ," ##   ,-\__    `.
          ,"       /     `--._;)
        ,"     ## /
      ,"   ##    /


        """)
print("------------------------------------------\n")
input("Press Enter to Start the Cold Flow Test:")

print("\nVerifying Sensor and Valve Connections\n")
while not pressure_cold_flow.verify_connection() and temperature_fill_line.verify_connection() \
        and temperature_empty_line.verify_connection():
    input("\nPress Enter to Start Verification Again:")
print("\nAll Sensors are Functional\n")

while not lox_main.verify_connection_valve and lox_vent.verify_connection_valve and \
        met_vent.verify_connection_valve and p_valve.verify_connection_valve:
    input("\nPress Enter to Start Verification Again:")
print("\nAll Valves are Functional\n")
print("\nVerification Complete, Press Enter to Continue:\n")

print("\nBeginning Opening of Solenoid Valves\n")
while True:
    try:
        lox_vent.open()
        met_vent.open()
        p_valve.open()
    except Exception:
        print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
        input("\nPress Enter to Start Verification Again:")
        continue
    else:
        while True:
            verification = input('\nHave all Solenoids opened? (yes/no)?\n')
            if verification == 'yes' or 'Yes':
                break
print("\nVerification Complete, Press Enter to Continue:\n")

print("\nBeginning Closing of Solenoid Valves\n")
while True:
    try:
        lox_vent.close()
        met_vent.close()
        p_valve.close()
    except Exception:
        print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
        input("\nPress Enter to Start Verification Again:")
        continue
    else:
        while True:
            verification = input('\nHave all Solenoids Closed? (yes/no)?\n')
            if verification == 'yes' or 'Yes':
                break
print("\nVerification Complete, Press Enter to Continue:\n")

print("\nBeginning Opening of Actuator Valve\n")
while True:
    try:
        percentage = 100
        lox_main.open()
    except Exception:
        print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
        input("\nPress Enter to Start Verification Again:")
        continue
    else:
        while True:
            verification = input('\nHas the Actuator Opened (yes/no)?\n')
            if verification == 'yes' or 'Yes':
                break
while True:
    try:
        percentage = 5
        lox_main.open()
    except Exception:
        print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
        input("\nPress Enter to Start Verification Again:")
        continue
    else:
        while True:
            verification = input('\nHas the Actuator Opened 5% (yes/no)?\n')
            if verification == 'yes' or 'Yes':
                break
while True:
    try:
        percentage = 50
        lox_main.open()
    except Exception:
        print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
        input("\nPress Enter to Start Verification Again:")
        continue
    else:
        while True:
            verification = input('\nHas the Actuator Opened Selected percentage(yes/no)?\n')
            if verification == 'yes' or 'Yes':
                break
print("\nVerification Complete, Press Enter to Continue:\n")

print("\nBeginning Opening of Actuator Valve\n")
while True:
    try:
        lox_main.close()
    except Exception:
        print("\nERROR HAS OCCURRED: PLEASE CHECK ELECTRICAL CONNECTIONS")
        input("\nPress Enter to Start Verification Again:")
        continue
    else:
        while True:
            verification = input('\nHas the Actuator Closed (yes/no)?\n')
            if verification == 'yes' or 'Yes':
                break
print("\nVerification Complete, Press Enter to Continue:\n")

print("\nBeginning Reading of Temperature and Pressure Sensors\n")
input("\nPress Enter to Start Front End (Remember to Click Link to Page):")
