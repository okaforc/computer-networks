# import math
# import time
# import random
import socket

print("server ready")

srvrPort = 54321
srvrIP = "172.30.1.2"


# Create a UDP socket at server side
s_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
s_UDP.bind((srvrIP, srvrPort))
bufferSize = 65507

recvd = s_UDP.recvfrom(bufferSize)
header = recvd[0]
print("Server - {}".format(header))
