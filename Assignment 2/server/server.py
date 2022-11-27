# import math
# import time
# import random
import socket
from sys import argv

name = int(argv[1], 16)
s_ip = argv[2]
s_fwd_ip = argv[3]
ctrl_ip = argv[4]


# Create a UDP socket at server side
s_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
srvrPort = 54321
s_UDP.bind((s_ip, srvrPort))


bufferSize = 65507

print("server ready")
recvd = s_UDP.recvfrom(bufferSize)
header = recvd[0]
print("Server - {}".format(header))
