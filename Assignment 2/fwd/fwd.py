import socket
from sys import argv


def confirmNextAddress():
    """Query the controller for the next address to send a message to, given an IP address"""
    f_UDP.sendto(str.encode(name), (ctrl_ip_1, 54321))
    resp = f_UDP.recvfrom(bufferSize)
    # print(resp)
    return resp[0] # return address' ip address
    

print("forwarder ready")
name = argv[1]
f_ip1 = argv[2]
f_ip2 = argv[3]
ctrl_ip_1 = argv[4]
ctrl_ip_2 = argv[5]


# Create a UDP socket at client side
fwdPort = 54321
f_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
f_UDP.bind((f_ip1, fwdPort))
bufferSize = 65507

target_fwd = ""


while True:
    msgFromServer = f_UDP.recvfrom(bufferSize)
    header = msgFromServer[0] # message received
    address = msgFromServer[1] # client address
    # print("FWD - {}".format(header))
    print("FWD {} - Relaying...".format(name))
    target_fwd = confirmNextAddress()
    fwdAddressPort = (target_fwd, fwdPort)
    f_UDP.sendto(header, fwdAddressPort) # relay message from client to server
    # f_UDP.sendto(str.encode("message forwarded"), address) # inform client of successful relay

