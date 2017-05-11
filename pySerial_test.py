__author__ = 'pronin_v'

import serial
import time

ser_com5 = serial.Serial()
ser_com5.port = "COM5"
ser_com5.write_timeout = 0
ser_com5.timeout = 0.001
ser_com5.open()

print ser_com5.isOpen()
arr = list(':1;1;2;32202\r')
arr_of_bytes = []
for i in arr:
    arr_of_bytes.append(ord(i))
str_inp = ','.join(arr_of_bytes)
print arr
print arr_of_bytes
ser_com5.write(arr)

time.sleep(0.1)

input_string = ''
while 1:
    inp_char = ser_com5.read()
    input_string += inp_char
    if len(input_string) == 73:
        break

print input_string

ser_com5.close()
