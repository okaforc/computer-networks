import socket
from sys import argv
# import time

print("Controller ready")

# forwarding table, in the form of a dictionary
MAP_ID = {
    0xFF0000: '103.17.0.20',
    0xFF0001: '140.120.10.20',
    0xFF0002: '140.120.10.20',
    0xFF0003: '103.17.0.20',
    0xFF0004: '172.30.1.3',
}

# ip_local1 = argv[1]
# ip_local2 = argv[2]
# ip_local3 = argv[3]
# ip_relay = argv[4]
# ip_internet = argv[5]
# ip_cloud = argv[6]

ctrlPort = 54321

# fwdAddressPort = ("172.30.1.2", 54321)
bufferSize = 65507

# Create a UDP socket at client side
ctrl_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
ctrl_UDP.bind(("", ctrlPort))

while True:
    # time.sleep(.1)
    msg = ctrl_UDP.recvfrom(bufferSize)
    header = int(msg[0], 16) # message received
    address = msg[1] # client address
    print("Controller - Message from {}".format('0x' + hex(header)[2:].upper()))

    # if MAP_ID[header] == '':
        # MAP_ID[header] = address[1]

    # send node's next destination back
    ctrl_UDP.sendto(str.encode(MAP_ID[header]), address) # relay message from client to server

# ctrl_UDP.sendto(str.encode("message forwarded"), address) # inform client of successful relay

