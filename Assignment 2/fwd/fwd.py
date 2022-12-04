import socket
from sys import argv
from helper import FORMAT_3, FORMAT_4


def confirmNextAddress(destination):
    """
    Query the controller for the next address to send a message to, given an IP address
    
    - -
    Returns: 
    - `bytes`: this forwarder's next IP address
    """
    
    f_UDP.sendto(str.encode(FORMAT_3.format(name, fwd, destination)), (ctrl_ip_1, 54321))
    resp = f_UDP.recvfrom(bufferSize)[0].decode().split(" ")
    if resp[1] == ret:
        # print("Path to {} is {}".format(destination, resp[0]))
        return resp[2] # path to destination
    return None


def getNextIP(fwd_path:str):
    """
    Given a path of IP addresses for the forwarder to follow, return the furthest IP address this forwarder 
    can communicate with
    
    - -
    Parameters:
    - `fwd_path`: the path of IP addresses to be considered
    - -
    Returns: 
    - `str`: the furthest IP address that can be communicated with, or
    - None: if there is no next IP address
    """
    
    if fwd_path:
        # get the next ip address to send from this path
        paths = fwd_path.split(",")
        fwd_index = 1
        if f_ip2 in paths:
            # if the second ip is in the list ahead of the first one, start from there
            fwd_index = max(paths.index(f_ip1), paths.index(f_ip2))
        return paths[fwd_index + 1]
    return None

fwds = {
    # structured like
    # 0xFF0000: '103.17.0.20,140.120.10.20',140.120.10.20',103.17.0.20',172.30.1.3'
    # 0xFF0001: 'etc.'
}

name = argv[1]
f_ip1 = argv[2]
f_ip2 = argv[3]
ctrl_ip_1 = argv[4]
ctrl_ip_2 = argv[5]
print("Forwarder", name, "ready")


# Create a UDP socket at client side
fwdPort = 54321
f_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
f_UDP.bind(("", fwdPort))
bufferSize = 65507

# target_fwd = ""
edge = "EDGE"
fwd = "FWD"
ack = "ACK"
ret = "PATH"

f_UDP.sendto(str.encode(FORMAT_4.format(name, edge, f_ip1, f_ip2)), (ctrl_ip_1, fwdPort))
while True:
    msgFromServer = f_UDP.recvfrom(bufferSize)
    header = msgFromServer[0] # message received
    address = msgFromServer[1] # client address
    params = header.decode().split(" ")
    incoming_name = params[0]
    print("FWD {} - Receiving from {}...".format(name, incoming_name))
    if params[1] == ack:
        print(name, "registered.")
    elif params[1] == fwd:
        dest = params[2]
        if dest in fwds:
            next_fwd_ip = getNextIP(fwds[dest])
            fwdAddressPort = (next_fwd_ip, fwdPort)
            f_UDP.sendto(str.encode(FORMAT_4.format(name, fwd, dest, " ".join(params[3:]))), fwdAddressPort) # send header to next forwarder
        else:
            fwd_path = confirmNextAddress(dest)
            fwds[dest] = fwd_path
            next_fwd_ip = getNextIP(fwd_path)
            if next_fwd_ip:
                fwdAddressPort = (next_fwd_ip, fwdPort)
                f_UDP.sendto(str.encode(FORMAT_4.format(name, fwd, dest, " ".join(params[3:]))), fwdAddressPort) # send header to next forwarder
            else:
                print("NO PATH TO " + dest)

