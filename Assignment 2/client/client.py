import socket
import time
from sys import argv

"""
argv are identical to the argv values in a Java or C main function (which also has an argc parameter)
e.g., a file named helloWorld.java
    public static main(String[] args) {
        System.out.println(args[0]);
    }
    >>> java helloWorld "hello world"
    >>> "hello world"
in this case, the first value is the name of the file, and the rest are the arguments are
passed into it in the docker-compose.yml file (under the 'command' field)
"""



name = argv[1]
c_ip = argv[2]
target = argv[3]
c_fwd_ip = argv[4]
ctrl_ip = argv[5]

# Create a UDP socket at client side
c_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
clientPort = 54321
c_UDP.bind((c_ip, clientPort))

fwdAddressPort = (c_fwd_ip, 54321)

print("C - I am Client {} and I am contacting Server {}".format(name, target))
time.sleep(.1)
msg = "hello {}, i am {}".format(target, name)
bufferSize = 65507
c_UDP.sendto(str.encode(msg), fwdAddressPort)
msgFromServer = c_UDP.recvfrom(bufferSize)
header = msgFromServer[0]
# print("Client - ACK from {}".format(c_fwd_ip))

