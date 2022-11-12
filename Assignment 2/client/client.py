import socket

msg = "hi im a client"
clientPort = 55555

fwdAddressPort = ("192.168.17.10", 54321)

# Create a UDP socket at client side
c_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
c_UDP.bind(("", clientPort))

print("client ready")

bufferSize = 65507
c_UDP.sendto(str.encode(msg), fwdAddressPort)
msgFromServer = c_UDP.recvfrom(bufferSize)
header = msgFromServer[0]
print("Client - {}".format(header))
        
