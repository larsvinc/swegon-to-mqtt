import minimalmodbus 
import datetime
from time import sleep


#--------------------------------------------------
# Modbus Settings
#--------------------------------------------------

MODBUS_ADDRESS = 128
USB_ID = "0403:6001"

REGISTER_INDEX         = 0
FUNCTIONCODE_INDEX     = 1
NAME_INDEX             = 2
DECIMALS_INDEX         = 3
TARGET_VALUE_INDEX     = 4
CURRENT_VALUE_INDEX    = 4
LAST_READING_INDEX     = 5

DEFAULT_UNIT_STATUS = [[304, 4, "Unit running",                   0, -1000, -1000],
                    [305, 4, "Unit state",                      0, -1000, -1000],
                    [306, 4, "Heating",                         0, -1000, -1000],
                    [307, 4, "Cooling",                         0, -1000, -1000],
                    [308, 4, "Summer cooling",                  0, -1000, -1000],
                    [309, 4, "Freeze protection",               0, -1000, -1000],
                    [310, 4, "Preheating",                      0, -1000, -1000],
                    [311, 4, "Chilling",                        0, -1000, -1000],
                    [313, 4, "Fireplace function",              0, -1000, -1000],
                    [319, 4, "Defrost starter",                 0, -1000, -1000],
                    [324, 4, "Afterheater set point",           0, -1000, -1000],
                    [325, 4, "Afterheater regulating mode",     0, -1000, -1000],
                    [326, 4, "Afterheater controller output",   0, -1000, -1000],
                    [327, 4, "Afterheater room output",         0, -1000, -1000]]

DEFAULT_SENSORS =  [[333, 4, "Outside Temperature (T1)",        1, -1000, -1000],
                    [334, 4, "Supply Air before afterheater (T2) ", 1, -1000, -1000],
                    [335, 4, "Exhaust Temperature (T3)",        1, -1000, -1000],
                    [336, 4, "Supply Air after afterheater (T4)", 1, -1000, -1000],
                    [337, 4, "Exhaust Air Temperature (T5)",    1, -1000, -1000],
                    [338, 4, "Afterheater Overtemperature (T6)",1, -1000, -1000],
                    [339, 4, "Preheater Overtemperature (T7)",  1, -1000, -1000],
                    [340, 4, "Room Temperature (T8)",           1, -1000, -1000],
                    [341, 4, "HX efficiency",                   0, -1000, -1000],
                    [346, 4, "24V diagnostic",                  1, -1000, -1000],
                    [347, 4, "5V diagnostic",                   1, -1000, -1000],
                    [358, 4, "Supply fan",                      0, -1000, -1000],
                    [359, 4, "Exhaust fan",                     0, -1000, -1000],
                    [361, 4, "HX bypass",                       0, -1000, -1000],
                    [362, 4, "Bypass air status",               0, -1000, -1000]]

DEFAULT_ALARMS =   [[367, 4, "Alarm temperature deviation",     0, -1000, -1000],
                    [368, 4, "Alarm freezing danger",           0, -1000, -1000],
                    [369, 4, "Alarm filter guard",              0, -1000, -1000],
                    [370, 4, "Alarm overheat afterheater",      0, -1000, -1000],
                    [371, 4, "Alarm efficiency",                0, -1000, -1000],
                    [372, 4, "Alarm supply fan failure",        0, -1000, -1000],
                    [373, 4, "Alarm exhaust fan failure",       0, -1000, -1000],
                    [374, 4, "Alarm service reminder",          0, -1000, -1000],
                    [375, 4, "Alarm temperature sensor",        0, -1000, -1000]]

DEFAULT_SETTINGS = [[8000, 3, "Unit running",                    0,   1, 0], # Default 1
                    [8001, 3, "Afterheater/Summercooling",       0,   2, 0], # Default 2
                    [8002, 3, "Fan speed",                       0,   3, 0], # Default 3
                    [8003, 3, "Temperature setpoint",            1,  20, 0], # Default 170
                    [8004, 3, "Fireplace impulse",               0,   0, 0], # Default 0
                    [8005, 3, "SA speed 1",                      0,  40, 0], # Default 40
                    [8006, 3, "SA speed 2",                      0, 100, 0], # Default 65
                    [8007, 3, "SA speed 3",                      0,  70, 0], # Default 75
                    [8008, 3, "SA speed 4",                      0,  85, 0], # Default 85
                    [8009, 3, "SA speed 5",                      0, 100, 0], # Default 100
                    [8010, 3, "EA speed 1",                      0,  45, 0], # Default 60
                    [8011, 3, "EA speed 2",                      0,  28, 0], # Default 72
                    [8012, 3, "EA speed 3",                      0,  70, 0], # Default 75
                    [8013, 3, "EA speed 4",                      0,  85, 0], # Default 85
                    [8014, 3, "EA speed 5",                      0, 100, 0], # Default 100
                    [8015, 3, "Profile speed Away",              0,   1, 0], # Default 1
                    [8016, 3, "Profile speed Home",              0,   3, 0], # Default 3
                    [8017, 3, "Profile speed Boost",             0,   5, 0], # Default 5
                    [8018, 3, "Profile speed Heating",           0,   3, 0], # Default 3
                    [8019, 3, "Profile speed Cooling",           0,   4, 0], # Default 4
                    [8020, 3, "Profile speed Chilling",          0,   4, 0], # Default 4
                    [8021, 3, "Afterheater outside temp limit",  0,  12, 0], # Default 0
                    [8022, 3, "Preheater outside start temp",    0, -20, 0], # Default -20
                    [8023, 3, "Preheat outside temp limit",      0,   0, 0], # Default 0
                    [8024, 3, "Summer cooling room temp limit",  0,  20, 0], # Default 20
                    [8025, 3, "Summer cooling outside temp limit",0, 18, 0], # Default 18
                    [8026, 3, "Summer cooling room/outside diff", 0,  1, 0], # Default 1
                    [8027, 3, "Summer cooling fan speed",         0,  0, 0]] # Default 0

# Misc registers
PASSWORD_REGISTER               = [4000, 3, "Password",       0, 1234, 0]
SECURITY_LEVEL                  = [4023, 3, "Security level", 0,    2, 0]
UPTIME_REGISTER_BASE            = 200
OPERATING_MODE_REGISTER         = 4100
FAN_MODE_REGISTER               = 8002
TEMPERATURE_SETPOINT_REGISTER   = 8003
FIREPLACE_IMPULSE_REGISTER      = 8004
SUMMER_COOLING_INSIDE_REGISTER  = 8024
SUMMER_COOLING_OUTSIDE_REGISTER = 8025
CLEAR_ALARMS_REGISTER           = 8028
CLOCK_BASE                      = 8029

# Ranges
SYSTEM_MODE_RANGE        = range(306, 319 + 1)
TEMPERATURE_SENSOR_RANGE = range(333, 340 + 1)
VOLTAGE_RANGE            = range(346, 347 + 1)
FAN_SPEED_RANGE          = range(358, 359 + 1)


AFTERHEATER_REGISTER  = 326
AFTERHEATER_MAXVAL    = 255
AFTERHEATER_MAXPOWER  = 800

# Misc settings
MIN_SUMMER_HEATING_TEMPERATURE  = 16
ALPHA = 0.5 # Filter is filtered_value = ALPHA*value + (1-ALPHA)*old_filtered_value
FAN_FILTER_ROUNDING = 100
FAN_MODES = {"Away":       1,
             "Compensate": 2,
             "Home":       3,
             "Boost":      5}



#--------------------------------------------------
# Public API
#--------------------------------------------------


class Swegon(object):
    def __init__(self, debug_function):
                
        from serial.tools import list_ports
        port_name = list(list_ports.grep(USB_ID))[0][0]

        self.status   = DEFAULT_UNIT_STATUS
        self.sensors  = DEFAULT_SENSORS
        self.alarms   = DEFAULT_ALARMS
        self.settings = DEFAULT_SETTINGS
        self.invalid_settings       = 0
        self.invalid_clock_readings = 0
        self.startup_time           = datetime.datetime.now()
        self.debug    = debug_function
        self.modbus   = minimalmodbus.Instrument(port_name, MODBUS_ADDRESS)
        self.modbus.serial.baudrate = 38400
        self.modbus.close_port_after_each_call = True
        self.get_swegon_data()


    # Mode assumed to be {Away, Home, Boost, Compensate}
    def set_fan_mode(self, mode):
        try:
            fan_mode = FAN_MODES[mode]
            self._update_setting(FAN_MODE_REGISTER, fan_mode)
            self._write_settings() # Effectuate changes to settings
            self._read_settings()
        except:
            self.debug("Invalid fan mode command: " + mode)
        

    # Temperature assumed to have one decimal, i.e. 20.0
    def set_temperature(self, temperature):
        setpoint = round(float(temperature))
        self._update_setting(TEMPERATURE_SETPOINT_REGISTER, setpoint)
        self._update_summer_heating_parameters()
        self._write_settings()


    def trigger_fireplace(self):
        self.debug("Triggering fireplace function")
        self._write_register(FIREPLACE_IMPULSE_REGISTER, 1)

    

    def reset_alarms(self):
        self.debug("Clearing all alarms")
        for alarm in range(1,12):
            self._write_register(CLEAR_ALARMS_REGISTER, alarm)

    
    # Returns 4 dicts with different data sets {settings, status, sensors, alarms}
    def get_swegon_data(self):
        self._validate_security_level()
        success = False
        while not success:
            self._validate_clock()
            success = self._read_and_validate_settings()
            self._read(self.status)
            self._read(self.sensors)
            self._read(self.alarms)

            success = success and self._correct_clock
            if not success:
                self.debug("Re-running data reading")

        return self._process_data()



    #--------------------------------------------------
    # Internal functions: read and write
    #--------------------------------------------------

    def _write_register(self, register, value, decimals=0):
        try:
            self.modbus.write_register(register-1, value, number_of_decimals=decimals, functioncode=6, signed=True)
            ret = True
        except:
            ret = False
        return ret


    def _read_register(self, register, functioncode, decimals=0):
        try:
            ret = self.modbus.read_register(register-1, decimals, functioncode=functioncode, signed=True)
        except:
            ret = False
        return ret

    
    def _read_registers(self, base, functioncode, length):
        try:
            ret = self.modbus.read_registers(base-1, length, functioncode)
        except:
            ret = False
        return ret


    def _write_registers(self, base, data):
        try:
            self.modbus.write_registers(base-1, data)
            ret = True
        except:
            ret = False
        return ret



    #--------------------------------------------------
    # Internal functions: post-processing
    #--------------------------------------------------

    # Post-processes, returns all dicts
    def _process_data(self):
        settings_data = self._process_settings()
        status_data   = self._process_status()
        sensors_data  = self._process_sensors()
        alarms_data   = self._process_alarms()
        return [settings_data, status_data, sensors_data, alarms_data]


    def _process_settings(self):
        data = self._convert_raw_table(self.settings)
        data["Fan mode"] = self._lookup_fan_mode(self._get_setting(FAN_MODE_REGISTER))
        return data


    def _process_status(self):
        self._register_new_measurements(self.status)
        data = self._convert_raw_table(self.status)
        data["Operating mode"] = self._get_operating_mode_string()
        data["Afterheater power"] = self._get_afterheater_power()
        data["Unit uptime"] = self._get_unit_uptime()
        data["Controller uptime"] = self._get_controller_uptime()
        data["Times invalid settings since reboot"] = self.invalid_settings
        data["Times invalid clock since reboot"] = self.invalid_clock_readings
        return data


    def _process_alarms(self):
        self._register_new_measurements(self.alarms)
        data = self._convert_raw_table(self.alarms)
        data["Alarms"] = self._get_alarms_string()
        return data


    def _process_sensors(self):
        data = {}
        for sensor in self.sensors:

            if sensor[REGISTER_INDEX] in TEMPERATURE_SENSOR_RANGE or sensor[REGISTER_INDEX] in VOLTAGE_RANGE:
                if sensor[CURRENT_VALUE_INDEX] == -1000: sensor[CURRENT_VALUE_INDEX] = round(sensor[LAST_READING_INDEX],1)
                sensor[CURRENT_VALUE_INDEX] = round(sensor[CURRENT_VALUE_INDEX]*(1-ALPHA) + ALPHA*sensor[LAST_READING_INDEX],1)
            
            elif sensor[REGISTER_INDEX] in FAN_SPEED_RANGE:
                if sensor[CURRENT_VALUE_INDEX] == -1000: sensor[CURRENT_VALUE_INDEX] = round(sensor[LAST_READING_INDEX])
                sensor[CURRENT_VALUE_INDEX] = int(round(sensor[CURRENT_VALUE_INDEX]*(1-ALPHA) + ALPHA*sensor[LAST_READING_INDEX], -2))
            
            else:
                sensor[CURRENT_VALUE_INDEX] = round(sensor[LAST_READING_INDEX])
            data[sensor[NAME_INDEX]] = sensor[CURRENT_VALUE_INDEX]
        return data


    def _register_new_measurements(self,table):
        for item in table:
            item[CURRENT_VALUE_INDEX] = item[LAST_READING_INDEX]


    def _convert_raw_table(self, table):
        data = {}
        for item in table:
            data[item[NAME_INDEX]] = item[CURRENT_VALUE_INDEX]
        return data


    def _get_operating_mode_string(self):
        operating_mode = "Normal"
        for status in self.status:
            if status[REGISTER_INDEX] in SYSTEM_MODE_RANGE and status[CURRENT_VALUE_INDEX]:
                if operating_mode == "Normal":
                    operating_mode = status[NAME_INDEX] 
                else:
                    operating_mode += ", " + status[NAME_INDEX]
        return operating_mode


    def _get_afterheater_power(self):
        current_value = self._get_value(AFTERHEATER_REGISTER, self.status)
        power = round(current_value*AFTERHEATER_MAXPOWER/AFTERHEATER_MAXVAL)
        return power


    def _get_alarms_string(self):
        alarms = "None"
        for alarm in self.alarms:
            if alarm[CURRENT_VALUE_INDEX]:
                if alarms == "None":
                    alarms = alarms[NAME_INDEX]
                else:
                    alarms += ", " + alarms[NAME_INDEX]
        return alarms


    def _get_unit_uptime(self):
        [years, hours, minutes] = self._read_registers(UPTIME_REGISTER_BASE, 4, 3)
        uptime = datetime.timedelta(days=years*365, hours=hours, minutes=minutes)
        uptime_string = ':'.join(str(uptime).split(':')[:2])
        return uptime_string


    def _get_controller_uptime(self):
        uptime_delta = datetime.datetime.now() - self.startup_time
        uptime_string = ':'.join(str(uptime_delta).split(':')[:2])
        return uptime_string


    #--------------------------------------------------
    # Internal functions: Misc
    #--------------------------------------------------

    def _validate_security_level(self):
        current_level = self._read_register(SECURITY_LEVEL[REGISTER_INDEX], SECURITY_LEVEL[FUNCTIONCODE_INDEX])
        if current_level != SECURITY_LEVEL[TARGET_VALUE_INDEX]:
            self.debug("Found security level " + str(current_level) + " applying password.")
            self._write_register(PASSWORD_REGISTER[REGISTER_INDEX], PASSWORD_REGISTER[TARGET_VALUE_INDEX])


    def _update_summer_heating_parameters(self):
        set_point = round(self._get_setting(TEMPERATURE_SETPOINT_REGISTER)/10)
        value = max(set_point, MIN_SUMMER_HEATING_TEMPERATURE)
        self.debug("Updating summer cooling value to: " + str(value))
        self._update_setting(SUMMER_COOLING_INSIDE_REGISTER,  value + 1)
        self._update_setting(SUMMER_COOLING_OUTSIDE_REGISTER, value - 1)


    def _lookup_fan_mode(self, mode):
        for key, value in FAN_MODES.items():
            if value == mode:
                return key


    def _get_value(self, register, table):
        for entry in table:
            if entry[REGISTER_INDEX] == register:
                return entry[CURRENT_VALUE_INDEX]


    def _get_last_reading(self, register, table):
        for entry in table:
            if entry[REGISTER_INDEX] == register:
                return entry[LAST_READING_INDEX]


    def _read(self, table):
        base          = table[0][REGISTER_INDEX]
        end_register  = table[len(table)-1][REGISTER_INDEX]
        function_code = table[0][1]
        length = end_register - base + 1

        data = self._read_registers(base, function_code, length)

        for offset, value in enumerate(data):
            register = base + offset
            value = self._unsigned_to_signed(value)
            for entry in table:
                if entry[REGISTER_INDEX] == register:
                    if entry[DECIMALS_INDEX]:
                        value = round(value / 10**entry[DECIMALS_INDEX], entry[DECIMALS_INDEX])
                    if entry[LAST_READING_INDEX] != value:
                        entry[LAST_READING_INDEX] = value
                        self.debug("Read " + entry[NAME_INDEX] + ": " + str(value))


    def _unsigned_to_signed(self, value):
        ret = value
        if value > 32768:
            ret = value - 65536
        return ret



    #--------------------------------------------------
    # Internal functions: settings management
    #--------------------------------------------------

    def _read_and_validate_settings(self):
        # Allow for 5 attempts due to issues with misreadings before updating settings
        # Return True if settings were correct, otherwise false
        attempt = 0
        correct_settings = self._validate_settings()
        while not correct_settings and attempt < 5:
            attempt += 1
            sleep(2)
            correct_settings = self._validate_settings()
            
        if not correct_settings:
            self._write_settings()
            return False
        else:
            return True


    def _update_setting(self, register, value):
        for setting in self.settings:
            if setting[REGISTER_INDEX] == register:
                setting[TARGET_VALUE_INDEX] = value


    def _get_setting(self, register):
        return self._get_value(register, self.settings)


    def _write_settings(self):
        # Special handling of fireplace impulse. Do not write do anything if fireplace impulse has been fired
        if self._get_last_reading(FIREPLACE_IMPULSE_REGISTER, self.settings) == 1:
            return True
        
        for setting in self.settings:
            target_value = setting[TARGET_VALUE_INDEX]* (10**setting[DECIMALS_INDEX])
            if target_value != setting[LAST_READING_INDEX]:                
                # Special case for fan mode to write operating mode
                if setting[REGISTER_INDEX] == FIREPLACE_IMPULSE_REGISTER:
                    pass # Ignore fireplace impulse
                elif (setting[REGISTER_INDEX] == FAN_MODE_REGISTER and
                    target_value in [FAN_MODES["Away"], FAN_MODES["Home"], FAN_MODES["Boost"]]):

                    self.debug("Setting fan mode to: " +  self._lookup_fan_mode(target_value))
                    operating_mode_target_value = round((target_value-1)/2)
                    self._write_register(OPERATING_MODE_REGISTER, operating_mode_target_value)

                else:
                    self.debug("Writing setting " + setting[NAME_INDEX] + ": " + str(target_value))
                    self._write_register(setting[REGISTER_INDEX], target_value)
        sleep(2) # Always sleep after writing settings
        self._read(self.settings)


    def _validate_settings(self):
        self._read(self.settings)
        valid_settings = True
        
        # Special handling of fireplace impulse. Do not write do anything if fireplace impulse has been fired
        if self._get_last_reading(FIREPLACE_IMPULSE_REGISTER, self.settings) == 1:
            return True

        for setting in self.settings:
            if setting[TARGET_VALUE_INDEX] != setting[LAST_READING_INDEX]:
                self.debug("Incorrect setting for: " + setting[NAME_INDEX])
                self.debug("Found: " + str(setting[LAST_READING_INDEX]) + " expected: " + str(setting[TARGET_VALUE_INDEX]))
                valid_settings = False
        if not valid_settings:
            self.invalid_settings += 1
        return valid_settings



    #--------------------------------------------------
    # Internal functions: clock managment
    #--------------------------------------------------

    def _read_clock(self):
        return self._read_registers(CLOCK_BASE, 3, 3)


    def _correct_clock(self): # Returns true if the clock is correct
        ret = True
        now = datetime.datetime.today()
        [now_day,    now_hour,    now_min   ] = [now.weekday(), now.hour, now.minute]
        [system_day, system_hour, system_min] = self._read_clock()

        today_total_minutes = now_day*24*60 + now_hour*60 + now_min
        system_total_minutes = system_day*24*60 + system_hour*60 + system_min

        if abs(today_total_minutes - system_total_minutes) > 2: # Clock is wrong
            ret = False
            self.debug("Found invalid system clock d=" + str(system_day) 
                        + " h=" + str(system_hour) 
                        + " m=" + str(system_min))
            self.invalid_clock_readings += 1
        return ret


    def _update_system_clock(self): # Updates the clock to the system clock
        while(datetime.datetime.today().second != 0):
            sleep(.5) # Wait until seconds = 0 to set clock at the right time
        now = datetime.datetime.today()
        self.debug("Setting system clock d=" + str(now.weekday()) 
                                + " h=" + str(now.hour) 
                                + " m=" + str(now.minute))
        self._write_registers(CLOCK_BASE, [now.weekday(), now.hour, now.minute])
        sleep(5) # Wait for the system to stabilize


    def _validate_clock(self): # Corrects the cloc if it incorrect
        while not self._correct_clock():
            self._update_system_clock()