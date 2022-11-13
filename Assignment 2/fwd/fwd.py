import socket

print("forwarder ready")
fwdPort = 54321

fwdAddressPort = ("172.30.1.2", 54321)
bufferSize = 65507

# Create a UDP socket at client side
f_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
f_UDP.bind(("", fwdPort))


msgFromServer = f_UDP.recvfrom(bufferSize)
header = msgFromServer[0] # message received
address = msgFromServer[1] # client address
print("FWD - {}".format(header))
f_UDP.sendto(header, fwdAddressPort) # relay message from client to server
f_UDP.sendto(str.encode("message forwarded"), address) # inform client of successful relay

