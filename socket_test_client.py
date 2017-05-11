__author__ = 'pronin_v'

import socket
import time

HOST = '127.0.0.1'
PORT = 7777

socket_inst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    socket_inst.connect((HOST, PORT))
except socket.error, e:
    print str(e).decode('1251')
    
arr = list(':1;1;2;32202\r')
arr_of_bytes = []
for i in arr:
    arr_of_bytes.append(ord(i))
outp_str = str(arr_of_bytes).strip('[').strip(']')

socket_inst.sendall(outp_str)

time.sleep(1)
while True:
    data = socket_inst.recv(200)
    print data
socket_inst.close()
