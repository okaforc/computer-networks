import socket
from sys import argv

print("Controller ready")

# forwarding table, in the form of a dictionary
MAP_ID = {
    0x110010: '',
    0xAA0000: '113.105.55.20',
    0xAA0001: '140.120.100.20',
    0xAA0002: '172.30.1.3',
    0xCCCC00: '',
}

ip_local = argv[1]
ip_re1 = argv[2]
ip_re2 = argv[3]
ip_cloud = argv[4]

ctrlPort = 54321

# fwdAddressPort = ("172.30.1.2", 54321)
bufferSize = 65507

# Create a UDP socket at client side
ctrl_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
ctrl_UDP.bind(("", ctrlPort))

while True:
    msg = ctrl_UDP.recvfrom(bufferSize)
    header = int(msg[0], 16) # message received
    address = msg[1] # client address
    print("Controller - Message from {}".format(hex(header).upper()))

    # if MAP_ID[header] == '':
        # MAP_ID[header] = address[1]

    # send node's next destination back
    ctrl_UDP.sendto(str.encode(MAP_ID[header]), address) # relay message from client to server

# ctrl_UDP.sendto(str.encode("message forwarded"), address) # inform client of successful relay

