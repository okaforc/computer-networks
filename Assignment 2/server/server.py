# import math
# import time
# import random
import socket
from sys import argv
from helper import FORMAT_2

name = argv[1]
s_ip = argv[2]
s_fwd_ip = argv[3]
ctrl_ip = argv[4]


# Create a UDP socket at server side
s_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
srvrPort = 54321
s_UDP.bind((s_ip, srvrPort))

greet = "GREET"

bufferSize = 65507

print("server ready")
msg_1 = FORMAT_2.format(name, greet)
s_UDP.sendto(str.encode(msg_1), (ctrl_ip, srvrPort))
while True:
    recvd = s_UDP.recvfrom(bufferSize)
    header = recvd[0]
    print("Server - {}".format(header))
