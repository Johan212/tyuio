import serial
import crcmod
import binascii
import sqlite3
import datetime as dt

result = []


class Modules:

    def __init__(self):
        self.test = ""
        self.timestamp = str((dt.datetime.now()).strftime("%y/%m/%d %H:%M:%S"))
        self.parallel_num = []
        self.serial_number = []
        self.work_mode = []
        self.fault_code = []
        self.grid_voltage = []
        self.grid_frequency = []
        self.ac_output_voltage = []
        self.ac_output_frequency = []
        self.ac_output_apparent_power = []
        self.ac_output_active_power = []
        self.load_percentage = []
        self.battery_voltage = []
        self.battery_charging_current = []
        self.battery_capacity = []
        self.pv_input_voltage = []
        self.total_charging_current = []
        self.total_ac_output_apparent_power = []
        self.total_output_active_power = []
        self.total_ac_output_percentage = []
        self.inverter_Status = []
        self.output_mode = []
        self.charger_source_priority = []
        self.max_charger_current = []
        self.max_charger_range = []
        self.max_ac_charger_current = []
        self.pv_input_current_for_battery = []
        self.battery_discharge_current = []


    def serial_coms(self):
        global com, response
        ser = serial.Serial(port="/dev/ttyUSB0", baudrate=2400, bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1,
                            xonxoff=False, rtscts=False, dsrdtr=False, writeTimeout=2)
        crc_func = crcmod.predefined.mkCrcFun('xmodem')
        ser_open = ser.isOpen()
        # print(ser_open)
        # com = input('Enter Command : ')
        com = "QPGS0"
        command = com.encode()
        cr = '\r'.encode()
        crc = command + binascii.unhexlify(hex(crc_func(command)).replace('0x', '', 1)) + cr
        ser.write(crc)
        re = ser.readline()
        if re == b'':
            response = "None"
        else:
            response = str(re)
        ser.close()
        return response

    def retrieve_data(self):
        global timestamp, parallel_num, serial_number, work_mode, fault_code, grid_voltage, grid_frequency, \
            ac_output_voltage, ac_output_frequency, ac_output_apparent_power, ac_output_active_power, \
            load_percentage, battery_voltage, battery_charging_current, battery_capacity, pv_input_voltage, \
            total_charging_current, total_ac_output_apparent_power, total_output_active_power, total_ac_output_percentage, \
            inverter_Status, output_mode, charger_source_priority, max_charger_current, max_charger_range, \
            max_ac_charger_current, pv_input_current_for_battery, battery_discharge_current, data

        data = ''
        respons = self.serial_coms()
        # print(respons)
        for i in respons:
            if i == ' ':
                i = ','
                data += i
            elif i in ("b", "(", "'", '"'):
                pass
            elif i == '\\':
                break
            else:
                data += i
        print("This is the string for {} : {}".format(com, data))
        if data == 'NAKss' or data == 'None':
            pass
        else:
            self.timestamp = str((dt.datetime.now()).strftime("%y/%m/%d %H:%M:%S"))
            self.parallel_num = data[0]
            self.serial_number = data[2:16]
            self.work_mode = data[17:18]
            self.fault_code = data[19:21]
            self.grid_voltage = data[22:27]
            self.grid_frequency = data[28:33]
            self.ac_output_voltage = data[34:39]
            self.ac_output_frequency = data[40:45]
            self.ac_output_apparent_power = data[46:50]
            self.ac_output_active_power = data[51:55]
            self.load_percentage = data[56:59]
            self.battery_voltage = data[60:64]
            self.battery_charging_current = data[65:68]
            self.battery_capacity = data[69:72]
            self.pv_input_voltage = data[73:78]
            self.total_charging_current = data[79:82]
            self.total_ac_output_apparent_power = data[83:88]
            self.total_output_active_power = data[89:94]
            self.total_ac_output_percentage = data[95:98]
            self.inverter_Status = data[99:107]
            self.output_mode = data[108:109]
            self.charger_source_priority = data[110:111]
            self.max_charger_current = data[112:115]
            self.max_charger_range = data[116:119]
            self.max_ac_charger_current = data[120:122]
            self.pv_input_current_for_battery = data[123:125]
            self.battery_discharge_current = data[126:129]


    def create_table(self):
        connection = sqlite3.connect("axpert.db")
        connection.execute("""CREATE TABLE 'QPGS0' (
            'timestamp' TEXT, 'parallel_num' TEXT, 'serial_number' TEXT, 'work_mode' TEXT, 'fault_code' TEXT,
            'grid_voltage' REAL, 'grid_frequency' REAL, 'ac_output_voltage' REAL, 'ac_output_frequency' REAL,
            'ac_output_apparent_power' INTEGER, 'ac_output_active_power' INTEGER, 'load_percentage' INTEGER,
            'battery_voltage' REAL, 'battery_charging_current' INTEGER, 'battery_capacity' INTEGER,
            'pv_input_voltage' REAL, 'total_charging_current' INTEGER, 'total_ac_output_apparent_power' INTEGER,
            'total_output_active_power' INTEGER, 'total_ac_output_percentage' INTEGER, 'inverter_Status' TEXT,
            'output_mode' INTEGER, 'charger_source_priority' TEXT, 'max_charger_current' INTEGER,
            'max_charger_range' INTEGER, 'max_ac_charger_current' INTEGER, 'pv_input_current_for_battery' REAL,
            'battery_discharge_current' INTEGER);""")
        connection.commit()
        connection.close()


    def get_last_entrys(self):
        connection = sqlite3.connect("axpert.db")
        cursor = connection.cursor()
        cursor.execute("""select * from 
            (select * from QPGS0 order by "timestamp" DESC limit 200) order by "timestamp" ASC""")
        result = cursor.fetchall()
        connection.commit()
        connection.close()
        return result


    def insert_record(self):
        connection = sqlite3.connect("axpert.db")
        connection.execute("""INSERT INTO "QPGS0" ('timestamp', 'parallel_num', 'serial_number', 'work_mode',
        'fault_code', 'grid_voltage', 'grid_frequency', 'ac_output_voltage', 'ac_output_frequency',
        'ac_output_apparent_power', 'ac_output_active_power', 'load_percentage', 'battery_voltage',
        'battery_charging_current', 'battery_capacity', 'pv_input_voltage','total_charging_current',
        'total_ac_output_apparent_power', 'total_output_active_power','total_ac_output_percentage',
        'inverter_Status', 'output_mode', 'charger_source_priority','max_charger_current', 'max_charger_range',
        'max_ac_charger_current', 'pv_input_current_for_battery','battery_discharge_current') VALUES (?,
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) """, (
            self.timestamp, self.parallel_num, self.serial_number, self.work_mode, self.fault_code, self.grid_voltage,
            self.grid_frequency, self.ac_output_voltage, self.ac_output_frequency, self.ac_output_apparent_power,
            self.ac_output_active_power, self.load_percentage, self.battery_voltage, self.battery_charging_current,
            self.battery_capacity, self.pv_input_voltage, self.total_charging_current, self.total_ac_output_apparent_power,
            self.total_output_active_power, self.total_ac_output_percentage, self.inverter_Status, self.output_mode,
            self.charger_source_priority, self.max_charger_current, self.max_charger_range, self.max_ac_charger_current,
            self.pv_input_current_for_battery, self.battery_discharge_current))
        connection.commit()
        connection.close()
        print("Completed")

    def data_collect(self):
        test_data = self.serial_coms()
        if test_data != "None" and test_data[3] != "N":
            print("Coms Succes")
            self.retrieve_data()
            self.insert_record()
        else:
            print("Coms failed")
            test_data = self.serial_coms()
            # print("this is test : {}".format(test_data))
            if test_data != "None" and test_data[3] != "N":
                print("Coms Succes")
                self.retrieve_data()
                self.insert_record()
                print("retry OK")

    @staticmethod
    def chart_display():
        tes = Modules.get_last_entrys()
        for i in tes:
            dict1 = dict({'date': i[0], 'bat': i[12]})
            result.append(dict1)
        return result
