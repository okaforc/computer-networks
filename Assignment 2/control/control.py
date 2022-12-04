import socket
from sys import argv
from helper import *


print("Controller ready")

# Forwarding table
table = {
    # structured like
    # 123.456.78.9: ["123.456.78.212", "123.446.78.10"],
    # 21.164.1.53: ["21.164.1.30", "et cetera"]
}

# Table of IDs
ids = {
    # structured like
    # 0xFF0000: '103.17.0.20',
    # 0xFF0001: '140.120.10.20',
    # etc.
}

greet = "GREET"
fwd = "FWD"
ack = "ACK"
ret = "PATH"
edge = "EDGE"
invalid_path = "INVALID"

name = argv[1]
# ip_local1 = argv[1]
# ip_local2 = argv[2]
# ip_local3 = argv[3]
# ip_relay = argv[4]
# ip_internet = argv[5]
# ip_cloud = argv[6] 

# ips = [argv[1], argv[2], argv[3], argv[4], argv[5], argv[6]]
# registered_ips = []

ctrlPort = 54321

bufferSize = 65507

# Create a UDP socket at client side
ctrl_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
ctrl_UDP.bind(("", ctrlPort))

while True:
    # time.sleep(.1)
    msg = ctrl_UDP.recvfrom(bufferSize)
    header = msg[0] # message received
    address = msg[1] # address
    ip = address[0] # ip address
    params = header.decode().split(" ")
    print("Controller - Message from {}".format(params[0]))
    
    if params[1] == greet:
        ids[params[0]] = ip # ID table
        addVertex(table, ip) # add IP to graph
        updateGraph(table) # update graph
        ctrl_UDP.sendto(str.encode(FORMAT_3.format(name, ack, "")), address) # return ACK greeting
    elif params[1] == edge:
        ids[params[0]] = ip # ID table
        addEdge(table, params[2], params[3]) # add edge from ip1 to ip2
        updateGraph(table) # update graph
        ctrl_UDP.sendto(str.encode(FORMAT_3.format(name, ack, "")), address) # return ACK greeting
    elif params[1] == fwd:
        dest = params[2] # destination
        if "0x" in dest: 
            dest = ids[dest] # get destination if only given an ID instead of an IP
        path = strPathTo(table, ids[params[0]], dest) # path from ID1 to ID2 as a string
        
        if path:
            ctrl_UDP.sendto(str.encode(FORMAT_3.format(name, ret, path)), address) # return path
        else:
            ctrl_UDP.sendto(str.encode(FORMAT_3.format(name, ret, invalid_path)), address) # invalid path, so return "INVALID"

