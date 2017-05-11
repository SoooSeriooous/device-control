__author__ = 'pronin_v'

import re
import math
import time
import curses
import serial
import socket
import itertools
import threading
import ControlSumModule
from ConfigParser import SafeConfigParser
from distutils.util import strtobool

end_flag = True


class Device():
    data_dict = dict()

    def __init__(self, devtype=None):
        if devtype is not None:
            self.__data = dict()
            self.__data["data"] = 0.0
            self.__data["auto"] = True
            self.__data["type"] = str(devtype)
            self.__data["active"] = True
            self.__data["number"] = 1
            self.__data["k"] = 1
            self.__data["C"] = 0
            self.data_dict = self.__data
        else:
            print "\nDevice wasn't registred."

    def __comand_0(self):
        response_str = '!' + self.data_dict['type'] + ';'
        return response_str + ControlSumModule.generate_cs(response_str) + '\r'

    def __comand_1(self):
        response_str = '!' + str(self.data_dict['number']) + ';' + str(self.data_dict['data']) + ';'
        control_sum = ControlSumModule.generate_cs(response_str) + '\r'
        response_str += control_sum
        return response_str

    def __comand_3(self):
        response_str = '!' + '0;'
        return response_str + ControlSumModule.generate_cs(response_str) + '\r'

    def __comand_4(self):
        response_str = '!' + '0;'
        return response_str + ControlSumModule.generate_cs(response_str) + '\r'

    def __comand_5(self):
        response_str = '!' + '0;'
        return response_str + ControlSumModule.generate_cs(response_str) + '\r'

    def print_data(self):
        output_list = list()
        if len(str(self.data_dict.get("number"))) == 1:
            dev_number = " " + str(self.data_dict.get("number"))
        else:
            dev_number = str(self.data_dict.get("number"))
        output_list.append(dev_number)
        output_list.append(str(self.data_dict.get("auto")))
        output_list.append(str(self.data_dict.get("active")))
        output_list.append(str(self.data_dict.get("data")))
        return output_list

    def set_data(self, *args):
        """ Set new data to device.
        It can be dict: dict[number_of_parameter_or_its_name]: required_data
        or serial listing of required data - if user asks about 2nd or 4th parameter,
        procedure should get list of required data for 2nd or 4th param. Any other param should be with "None" value"""

        if not args:
            print "No input arguments.\n"

        else:
            # dict for values
            buff_dict = dict()
            buff_dict["type"] = "type"
            buff_dict["number"] = "number"
            buff_dict["auto"] = "auto"
            buff_dict["data"] = "data"
            buff_dict["active"] = "active"
            buff_dict["k"] = "k"
            buff_dict["C"] = "C"

            for arg in args:
                if isinstance(arg, dict):
                    for key in arg.keys():
                        if key in buff_dict.keys():
                            try:
                                self.data_dict[buff_dict[key]] = arg.get(key)
                            except KeyError:
                                print "\nNo such argument.\n"

    def evaluate_command(self, command_num=None):
        if command_num == 0:
            a = self.__comand_0()
        elif command_num == 1:
            a = self.__comand_1()
        elif command_num == 3:
            a = self.__comand_3()
        elif command_num == 4:
            a = self.__comand_4()
        elif command_num == 5:
            a = self.__comand_5()
        else:
            a = "\nNo such command.\n"
        return a


class ListOfDevices():
    instance_dict = dict()

    def __init__(self, input_data=None):
        """ checking arguments, they must be full.
        input data as dict: dict[type_of_device] = number_of_device
        or
        input_data as int: number_of_devices (integer), type_of_devices will be set by default as 18 ("IRT 1730U/A") """

        if isinstance(input_data, dict):
            if input_data == dict():
                print "\nNo input arguments.\n"
            else:
                i = 1
                for inp_key in input_data.keys():
                    for j in range(input_data[inp_key]):
                        inst = Device(inp_key)
                        inst.set_data({"number": i})
                        self.instance_dict[i] = inst
                        i += 1
        elif isinstance(input_data, int):
            if input_data == 0:
                print "No input arguments.\n"
            else:
                for i in range(input_data):
                    inst = Device("18")
                    inst.set_data({"number": i + 1})
                    self.instance_dict[i + 1] = inst
        else:
            print "\nInvalid argument " + str(input_data) + ".\n"

    def print_data(self, *arqs):
        instance_dict = self.instance_dict
        lod_output_list = []  # list for lists, which contain information about devices
        if arqs is None:
            lod_output_list.append('Error.')
            lod_output_list.append("\nNo input arguments.")
        else:
            if len(arqs) != 0:
                for i in arqs:
                    if isinstance(i, int):
                        if i in instance_dict:
                            # get list of data from object, then insert some data about device number and devider
                            device_output_list = instance_dict[i].print_data()
                            lod_output_list.append(device_output_list)
                        else:
                            lod_output_list.append('Error.')
                            lod_output_list.append("\nInvalid argument: " + str(i))
                            lod_output_list.append(
                                "There is no device with number " + str(i) + " in the list of devices.")
                    else:
                        lod_output_list.append('Error.')
                        lod_output_list.append("\nInvalid argument: " + str(i))
                        lod_output_list.append(
                            "The number of device should be specified to show data about required devices.")
            else:
                for i in instance_dict.keys():
                    device_output_list = instance_dict[i].print_data()
                    device_output_list.insert(0, "\nDevice number " + str(instance_dict[i].data_dict["number"]))
                    device_output_list.insert(1, "========")
                    lod_output_list.append(device_output_list)
        return lod_output_list

    def set_data(self, setting_dict=None):
        """
         Getting a dictionary with data, which should be set.
         setting_dict[number_of_device_in_the_list]:
         dictionary_or_tuple_with_changing_data_like_parameter_in_set_data_of_device
        """
        inst_dict = self.instance_dict
        if setting_dict is None:
            print "\nNo input arguments.\n"
        else:
            if isinstance(setting_dict, dict):
                for i in setting_dict.keys():
                        inst_dict[i].set_data(setting_dict[i])
                        if inst_dict[i].data_dict["number"] != i:
                            inst_dict[inst_dict[i].data_dict["number"]] = inst_dict[i]
                            del (inst_dict[i])
            else:
                print "\nInvalid argument type.\n"

    def evaluate_command(self, input_dict=None):
        """
        Getting dict, which contains number of device as key and number of command as value.
        """
        if input_dict is not None:
            for key in input_dict.keys():
                if key in self.instance_dict.keys():
                    a = self.instance_dict[key].evaluate_command(input_dict[key])
                else:
                    print "\nInvalid argument: " + str(key)
                    print "There is no device with number " + str(key) + " in the list of devices.\n"
                    a = None
        else:
            print "\nNo input arguments.\n"
            a = None
        return a


class TCPDataReceiver(threading.Thread):
    def __init__(self, screen, devices, tcp_port, com_port, bytes_only):
        super(TCPDataReceiver, self).__init__()

        if tcp_port is None:
            screen.addstr(3, 1, "Connection address wasn't set.")
        else:
            self._screen = screen
            self._host = '127.0.0.1'
            self._port = tcp_port
            self.socket_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ser_com_input = serial.Serial()
            self.ser_com_input.port = com_port
            self.ser_com_input.timeout = 0.001
            self.ser_com_input.write_timeout = 0
            self.devices = devices
            self.connections = []
            self.stop_flag = False
            self._starting = True

            self.bytes_only = bytes_only
            ser_thread = threading.Thread(target=self.receive_com_data)
            if self._starting:
                ser_thread.start()

    def run(self):
        """input_value_processing"""
        try:
            self.socket_inst.bind((self._host, self._port))
            self._starting = True
        except socket.error, err:
            self._starting = False
            if err.errno == 11:
                self._screen.addstr(3, 1, 'Resource temporarily unavailable.')
                self._screen.refresh()
            else:
                error_print(err, self._screen)

        if self._starting:
            while 1:
                if self.stop_flag:
                    break
                self.socket_inst.listen(0)
                conn, addr = self.socket_inst.accept()
                conn.settimeout(1)
                thr = threading.Thread(target=self.receive_tcp_data, args=[conn])
                self.connections.append(conn)
                thr.start()

        self.socket_inst.close()

    def stop(self):
        self.stop_flag = True
        for conn in self.connections:
            conn.close()
        stop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stop_socket.connect((self._host, self._port))

    def _evaluate(self, buff_str, buff_chr):
        buff_str += buff_chr
        if buff_chr == '\r':
            correct_input, command = check_input(buff_str)
            if correct_input:
                dev_num = get_num_from_command(command)
                if dev_num:
                    if self.devices.instance_dict[dev_num].data_dict['active']:
                        res_str = self.devices.evaluate_command({dev_num: 1})
                        print self.bytes_only
                        if self.bytes_only:
                            for i in range(len(res_str)):
                                for conn in self.connections:
                                    conn.send(res_str[i])
                                self.ser_com_input.write(res_str[i])
                        else:
                            for conn in self.connections:
                                conn.send(res_str)
                            self.ser_com_input.write(res_str)
            buff_str = ''
        return buff_str

    def receive_tcp_data(self, conn):
        buff_str = ''
        while 1:
            try:
                buff_chr = conn.recv(1)
            except socket.timeout:
                pass
            except socket.error, err:
                if err.errno == 10054 or err.errno == 10035 or err.errno == 9:
                    self.connections.remove(conn)
                    break
            else:
                if buff_chr == '':
                    self.connections.remove(conn)
                    break
                buff_str = self._evaluate(buff_str, buff_chr)

    def receive_com_data(self):
        """
        Function receives data from COM-port,
        and evaluate one of the device's commands.
        """
        buff_str = ''
        try:
            self.ser_com_input.open()
            starting = True
        except serial.SerialException, err:
            starting = False
            error_print(err, self._screen)

        if starting:
            while 1:
                if not self.stop_flag:
                    buff_chr = self.ser_com_input.read()
                    buff_str = self._evaluate(buff_str, buff_chr)
                else:
                    break


def error_print(error, left_screen):
    ind = 1
    left_screen.clear()
    left_screen.box()
    left_screen.addstr(1, 1, "Command console: ", curses.A_BOLD)
    left_screen.hline(2, 1, curses.ACS_HLINE, 28)
    left_screen.addstr(3, 1, "Couldn't start port reading.")
    err_str = str(error).decode('1251')
    for i in range(1, len(err_str) / 30):
        if len(str(error).decode('1251')) > 29:
            left_screen.addstr(4 + i, 1, err_str[:25] + ' - ')
            err_str = err_str[25:]
            ind = i
        else:
            left_screen.addstr(4 + ind, 1, err_str)
    left_screen.addstr(4 + ind + 1, 1, err_str[25:])
    left_screen.refresh()


def get_num_from_command(command=None):
    if command is None:
        result = None
    else:
        pattern = ":\d{1,3};"
        match_str = re.match(pattern, command)
        buff = match_str.group(0)[1:-1]  # delete ':' from found string
        if buff.isdigit():
            result = int(buff)
        else:
            result = None
    return result


def check_input(input_string):
    """
    Checking input string from COM-port for conformity of input format
    and control sum.
    """
    # Here we translating input from ascii to string
    if input_string:
        pattern = ':\d{1,3};1;\d{1};\d{1,}\r'
        match = re.search(pattern, input_string)

        if match is not None:
            command = match.group(0)
        else:
            command = ''

        if command:
            gen_checksum = ControlSumModule.generate_cs(';'.join(command.split(';')[:-1]) + ';')
            input_checksum = command.split(';')[-1].strip()
        else:
            gen_checksum = 1
            input_checksum = 0

        correct_input, command = True if gen_checksum == input_checksum else False, command
    else:
        correct_input, command = False, ''

    return correct_input, command


def sin_generator(sin_iter, iter_amount):
    x = 2 * math.pi * (sin_iter / iter_amount)
    sin_value = round(math.sin(x), 4)
    return sin_value


def device_sin_data_changing(dev_list, a, period):

    iter_amount = float(len(a)-1)
    for i in itertools.cycle(a):
        if end_flag:
            sin = sin_generator(i, iter_amount)
            keys = dev_list.instance_dict.keys()
            setting_dict = {}
            for key in keys:
                if dev_list.instance_dict[key].data_dict['auto']:
                    setting_dict[key] = {'data': round(sin * dev_list.instance_dict[key].data_dict['k'] +
                                                       dev_list.instance_dict[key].data_dict['C'], 4)}
            dev_list.set_data(setting_dict)
            time.sleep(period)
        else:
            break


def printing_dev_info(list_of_devices, dev_num=None):
    if dev_num is None:
        information = list_of_devices.print_data()
    else:
        information = list_of_devices.print_data(*dev_num)
    if 'Error.' in information[0]:
        for info in information[1:]:
            print info
    else:
        for info in information:
            for i in info:
                print str(i)
    print '\n'


def input_value_processing(input_string):
    param = None
    if ',' in input_string:
        param = ','
    elif ' ' in input_string:
        param = None
    elif '' in input_string:
        param = None
    else:
        print 'Unnable to execute comand. List of devices must be seperated by spaces or comas.\n'
    buff_list = input_string.split(param)
    devices = []
    for i in buff_list:
        if i.strip().isdigit():
            devices.append(int(i))
        else:
            print "Param " + i + " isn't a device's number. Param will be ignored.\n"
    return devices


def check_input_values(keys_from_device_list, chosen_numbers, message_array):
    buff_arr = []
    for i in chosen_numbers:
        if i not in keys_from_device_list:
            buff_arr.append(i)

    for i in buff_arr:
        if i in chosen_numbers:
            chosen_numbers.remove(i)
            message_array.append("Invalid argument: " + str(i))
            message_array.append("There is no device with number " + str(i) + ".")

    return chosen_numbers, message_array


def check_match_list(list_of_devices, match_list, mode, left_screen):
    setting_dict = {}
    message_array = []
    if match_list:
        for i in match_list:
            if '(' and ')' in i:
                buff_i = i.split('=')
                buff_keys = buff_i[0].strip('(').strip(')')
                val = buff_i[1]
                if '-' in buff_keys:
                    buff_i = buff_keys.split('-')
                    err_array = []
                    for j in buff_i:
                        if j is None or not j.isdigit():
                            message_array.append('Incorrect input: ' + str(buff_keys) + '.')
                            err_array.append(j)
                    for ii in err_array:
                        if ii in buff_i:
                            buff_i.remove(ii)
                    keys_for_set_dict = range(int(buff_i[0]), int(buff_i[1]) + 1)
                elif ',' in buff_keys:
                    buff_keys = buff_keys.split(',')
                    for j in buff_keys:
                        if j is None or not j.isdigit():
                            message_array.append('Incorrect input: ' + str(buff_keys) + '.')
                            buff_keys.remove(j)
                    keys_for_set_dict = [int(x) for x in buff_keys]
                else:
                    message_array.append('Incorrect input: ' + str(i) + '.')
                    continue

                passed_control, ret_array = check_input_values(list_of_devices.instance_dict.keys(), keys_for_set_dict,
                                                               message_array)
                message_array.extend(ret_array)
                if passed_control:
                    if mode == 'auto':
                        for j in passed_control:
                            setting_dict[j] = {'auto': bool(strtobool(val))}
                    if mode == 'active':
                        for j in passed_control:
                            setting_dict[j] = {'active': bool(strtobool(val))}
                    if mode == 'data':
                        for j in passed_control:
                            if not list_of_devices.instance_dict[j].data_dict["auto"]:
                                setting_dict[j] = {'data': float(val)}
                            else:
                                message_array.append('Device # ' + str(j) + ' should be set')
                                message_array.append('to manual mode.')
                                message_array.append('Use "change_mode" command for it.')

                else:
                    left_screen.addstr(3, 1, 'No data to set.')
            else:
                buff_i = i.split('=')
                if buff_i[0] == 'all':
                    if mode == 'auto':
                        for key in list_of_devices.instance_dict.keys():
                            setting_dict[key] = {'auto': bool(strtobool(buff_i[1]))}
                    if mode == 'active':
                        for key in list_of_devices.instance_dict.keys():
                            setting_dict[key] = {'active': bool(strtobool(buff_i[1]))}
                    if mode == 'data':
                        for key in list_of_devices.instance_dict.keys():
                            setting_dict[key] = {'data': float(buff_i[1])}
                elif int(buff_i[0]) in list_of_devices.instance_dict.keys():
                    if mode == 'auto':
                        setting_dict[int(buff_i[0])] = {'auto': bool(strtobool(buff_i[1]))}
                    if mode == 'active':
                        setting_dict[int(buff_i[0])] = {'active': bool(strtobool(buff_i[1]))}
                    if mode == 'data':
                        if not list_of_devices.instance_dict[int(buff_i[0])].data_dict["auto"]:
                            setting_dict[int(buff_i[0])] = {'data': float(buff_i[1])}
                        else:
                            message_array.append('Device # ' + buff_i[0] + ' should be set')
                            message_array.append('to manual mode.')
                            message_array.append('Use "change_mode" command for it.')

                else:
                    message_array.append('There is no device with number ' + buff_i[0] + '.')

    else:
        message_array.append('Incorrect input.')
    return setting_dict, message_array


def refresh(list_devices, left_screen, right_screen):

    right_screen.clear()
    right_screen.box()
    left_screen.box()

    right_screen.addstr(1, 1, "Devices: ", curses.A_BOLD)
    right_screen.hline(2, 1, curses.ACS_HLINE, 32)
    right_screen.addstr(3, 5, "ID | AUTO | ACTIVE | DATA")
    right_screen.hline(4, 1, curses.ACS_HLINE, 32)
    for key in sorted(list_devices.instance_dict.keys()):
        val = '   '.join(list_devices.instance_dict[key].print_data())
        right_screen.addstr(key + 5, 5, val)
    right_screen.noutrefresh()
    curses.doupdate()


def win_refresher(list_devices, left_screen, right_screen):
    while 1:
        if end_flag:
            refresh(list_devices, left_screen, right_screen)
            time.sleep(0.1)
        else:
            break


def change_device_params(left_screen, list_of_devices, input_string, pattern, mode):

    message_array = []
    match_list = re.findall(pattern, input_string)
    setting_dict, message_array = check_match_list(list_of_devices, match_list, mode, left_screen)
    if setting_dict:
        list_of_devices.set_data(setting_dict)
    else:
        message_array.append(" ")
        message_array.append("Incorrect input.")
        message_array.append("There's no data for changing.")

    left_screen.clear()
    left_screen.box()
    left_screen.addstr(1, 1, "Command console: ", curses.A_BOLD)
    left_screen.hline(2, 1, curses.ACS_HLINE, 28)
    if message_array:
        for i in range(len(message_array)):
            left_screen.addstr(3+i, 1, str(message_array[i]))
    left_screen.refresh()


def init_devices(parser):
    """
    initialize list of devices object with config data
    """
    id_list_18 = parser.get('Type 18', 'id').split(',')
    id_list_19 = parser.get('Type 19', 'id').split(',')

    pre_devices = dict()
    pre_devices[18] = get_id_from_list(id_list_18)
    pre_devices[19] = get_id_from_list(id_list_19)

    check = list(set(pre_devices[18]) & set(pre_devices[19]))
    if check:
        dev_list = []
        for i in check:
            dev_list.append("Number " + str(i) + " is used")
            dev_list.append("for both type of devices.")
            dev_list.append("Correct the config file.")

    else:

        min_amp_18 = int(parser.get('Type 18', 'min_amp'))
        max_amp_18 = int(parser.get('Type 18', 'max_amp'))
        min_amp_19 = int(parser.get('Type 19', 'min_amp'))
        max_amp_19 = int(parser.get('Type 19', 'max_amp'))
        k_18 = abs((max_amp_18 - min_amp_18) / 2)
        c_18 = (max_amp_18 + min_amp_18) / 2
        k_19 = abs((max_amp_19 - min_amp_19) / 2)
        c_19 = (max_amp_19 + min_amp_19) / 2

        dev_list = ListOfDevices(len(pre_devices[18]) + len(pre_devices[19]))
        for i in range(1, len(pre_devices[18]) + len(pre_devices[19]) + 1):
            dev_list.set_data({i: {'k': k_18, 'C': c_18}})

        for i in pre_devices[19]:
            dev_list.set_data({i: {'type': 19, 'k': k_19, 'C': c_19}})

    return dev_list


def get_id_from_list(id_list):
    res_list = []
    for i in id_list:
        if i.isdigit():
            res_list.append(int(i))
        elif '-' in i:
            buff_i = i.strip().split('-')
            err_array = []
            for j in buff_i:
                if j is None or not j.isdigit():
                    err_array.append(j)
            for ii in err_array:
                if ii in buff_i:
                    buff_i.remove(ii)
            res_list.extend(range(int(buff_i[0]), int(buff_i[1]) + 1))

    return res_list


def info_array_generator():
    info_arr = []
    info_arr.append("There are 3 main commands:")
    info_arr.append("")
    info_arr.append("1 - 'mode' - for mode changing.")
    info_arr.append("Only boolean value;")
    info_arr.append("2 - 'active' - to disable device.")
    info_arr.append("Only boolean value;")
    info_arr.append("3 - 'set' - for set data value.")
    info_arr.append("Only numbers for value;")
    info_arr.append("===========================================")
    info_arr.append("You can choose devices in 'active', 'mode'")
    info_arr.append("or 'set' commands.")
    info_arr.append("Type name of command, then type id of ")  # 111
    info_arr.append("device and set its value:")
    info_arr.append("'active (1,3,5,7)=True'")
    info_arr.append("or 'set (1-5)=4.123'")
    info_arr.append("or 'mode 6=False'.")
    info_arr.append("To make changes in every device type 'all'")
    info_arr.append("and set value, e.g. 'mode all=True'.")
    return info_arr


def main():
    global end_flag
    # reading settings from config file
    parser = SafeConfigParser()
    parser.read('Config.ini')

    list_of_devices = init_devices(parser)
    info_arr = info_array_generator()

    stdscr = curses.initscr()
    curses.cbreak()
    screen = curses.newwin(25, 80)
    left_screen = curses.newwin(23, 45, 2, 0)
    right_screen = curses.newwin(25, 35, 0, 45)

    screen.leaveok(0)
    right_screen.leaveok(1)
    left_screen.leaveok(0)

    com_port = parser.get('Settings', 'com port')

    port = parser.get('Settings', 'PORT')
    tcp_adr = int(port)

    bytes_only = bool(strtobool(parser.get('Settings', 'bytes_only')))

    period_upd = float(parser.get('Settings', 'period_upd'))
    sin_period = float(parser.get('Settings', 'sin_period'))
    if period_upd == 0:
        left_screen.addstr(3, 1, "Update period must be ")
        left_screen.addstr(4, 1, "greater than 0.")
        left_screen.refresh()
        points = 1
    else:
        points = int(sin_period / period_upd) + 1

    if isinstance(list_of_devices, ListOfDevices):

        a = [x for x in xrange(0, points)]
        thr_sin = threading.Thread(target=device_sin_data_changing, args=(list_of_devices, a, period_upd))
        thr_refresh = threading.Thread(target=win_refresher, args=(list_of_devices, left_screen, right_screen))
        thr_tcp = TCPDataReceiver(left_screen, list_of_devices, tcp_adr, com_port, bytes_only)

        thr_sin.start()
        thr_refresh.start()
        try:
            thr_tcp.start()
        except:
            left_screen.addstr(3, 1, "Couldn't start TCP handler.")

        while 1:

            screen.clear()
            screen.box()
            right_screen.box()
            left_screen.box()
            screen.addstr(1, 1, '> ')

            left_screen.addstr(1, 1, "Command console: ", curses.A_BOLD)
            left_screen.hline(2, 1, curses.ACS_HLINE, 42)
            right_screen.addstr(1, 1, "Devices: ", curses.A_BOLD)
            right_screen.hline(2, 1, curses.ACS_HLINE, 32)
            right_screen.addstr(3, 5, "ID | AUTO | ACTIVE | DATA")
            right_screen.hline(4, 1, curses.ACS_HLINE, 32)
            stdscr.refresh()
            screen.refresh()
            left_screen.refresh()
            right_screen.refresh()

            refresh(list_of_devices, left_screen, right_screen)

            key = screen.getstr()
            # Stop command
            if key.strip().lower() == "stop":
                screen.clear()
                left_screen.addstr(3, 1, 'Leaving the program...')
                end_flag = False
                if thr_sin.isAlive():
                    thr_sin.join()
                if thr_refresh.isAlive():
                    thr_refresh.join()
                left_screen.addstr(5, 1, str(thr_tcp.isAlive()))
                left_screen.refresh()
                if thr_tcp.isAlive():
                    left_screen.addstr(6, 1, str(thr_tcp.isAlive()))
                    left_screen.refresh()
                    thr_tcp.stop()
                break
            # Change mode command
            elif 'mode' in key.strip().lower():
                pattern = '\d{1,3}=true|' \
                          '\d{1,3}=false|' \
                          '\([\d{1,3}]-[\d{1,3}]\)=false|' \
                          '\([\d{1,3}]-[\d{1,3}]\)=true|' \
                          '\([\d{1,3}\,]{1,}\)=true|' \
                          '\([\d{1,3}\,]{1,}\)=false|' \
                          'all=true|' \
                          'all=false'
                # will match X=True or X=False, (X-Y)=True or (X-Y)=False, (X,Y,Z)=True or (X,Y,Z)=False
                # where X, Y, Z - device's number
                string = key.strip().lower()[5:]
                change_device_params(left_screen, list_of_devices, string, pattern, 'auto')
            # Set data command
            elif 'set' in key.strip().lower():
                pattern = '\d{1,3}=\d{1,}[.\d]*|' \
                          '\([\d{1,}]-[\d{1,3}]\)=\d{1,}[.\d]*|' \
                          '\([\d{1,3}\,]{1,}\)=\d{1,}[.\d]*|' \
                          'all=\d{1,}[.\d]*'
                # will match X=N, (X-Y)=N or (X,Y,Z)=N, where X, Y, Z - device number, N - value (value may be float)
                string = key.strip().lower()[4:]
                change_device_params(left_screen, list_of_devices, string, pattern, 'data')
            #active command
            elif 'active' in key.strip().lower():
                pattern = '\d{1,3}=true|' \
                          '\d{1,3}=false|' \
                          '\([\d{1,3}]-[\d{1,3}]\)=false|' \
                          '\([\d{1,3}]-[\d{1,3}]\)=true|' \
                          '\([\d{1,3}\,]{1,}\)=true|' \
                          '\([\d{1,3}\,]{1,}\)=false|' \
                          'all=true|' \
                          'all=false'
                # will match X=True or X=False, (X-Y)=True or (X-Y)=False, (X,Y,Z)=True or (X,Y,Z)=False
                # where X, Y, Z - device's number
                string = key.strip().lower()[7:]
                change_device_params(left_screen, list_of_devices, string, pattern, 'active')
            # Help command
            elif key.strip().lower() == "help":
                screen.clear()
                left_screen.clear()
                for i in range(len(info_arr)):
                    left_screen.addstr(3 + i, 1, info_arr[i])
                screen.refresh()
                left_screen.refresh()
            # Clear command
            elif key.strip().lower() == "clear":
                screen.clear()
                left_screen.clear()
            # Message for unknown command
            else:
                screen.clear()
                left_screen.clear()
                left_screen.addstr(3, 1, "Unknown command '" + key + "'.")
                left_screen.addstr(4, 1, '')
                left_screen.addstr(5, 1, "Type 'help' to get information about")
                left_screen.addstr(6, 1, "available commands.")
                screen.refresh()
                left_screen.refresh()

    else:
        screen.clear()
        screen.box()
        right_screen.box()
        left_screen.box()
        screen.addstr(1, 1, '> ')

        left_screen.addstr(1, 1, "Command console: ", curses.A_BOLD)
        left_screen.hline(2, 1, curses.ACS_HLINE, 32)
        right_screen.addstr(1, 1, "Devices: ", curses.A_BOLD)
        right_screen.hline(2, 1, curses.ACS_HLINE, 32)
        stdscr.refresh()
        screen.refresh()
        left_screen.refresh()
        right_screen.refresh()

        for i in range(len(list_of_devices)):
            left_screen.addstr(3+i, 1, str(list_of_devices[i]))
        left_screen.addstr(5+len(list_of_devices), 1, 'Press any key to quit.')
        left_screen.refresh()
        screen.getstr()

    stdscr.clear()
    stdscr.refresh()
    curses.endwin()


if __name__ == '__main__':
    main()

