import socket

print("forwarder ready")
msg = "hi im a forwarder"
fwdPort = 54321

fwdAddressPort = ("172.30.1.2", 54321)
bufferSize = 65507

# Create a UDP socket at client side
f_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
f_UDP.bind(("", fwdPort))


f_UDP.sendto(str.encode(msg), fwdAddressPort)
msgFromServer = f_UDP.recvfrom(bufferSize)
header = msgFromServer[0]
address = msgFromServer[1]
print("FWD - {}".format(header))

f_UDP.sendto(str.encode("message forwarded"), address)
