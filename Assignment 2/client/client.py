import socket
import time
from sys import argv
from helper import FORMAT_2, FORMAT_4

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

greet = "GREET"
fwd = "FWD"

# Create a UDP socket at client side
c_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
clientPort = 54321
c_UDP.bind((c_ip, clientPort))


msg_1 = FORMAT_2.format(name, greet)
msg_2 = FORMAT_4.format(name, fwd, target, "Hello! This is " + name)
msg_3 = FORMAT_4.format(name, fwd, target, "Hello!" + name + " is saying hello for the second time!!!")
fwdAddressPort = (c_fwd_ip, clientPort)

bufferSize = 65507

print("C - I am Client {} and I am contacting Server {}".format(name, target))
c_UDP.sendto(str.encode(msg_1), (ctrl_ip, clientPort))
time.sleep(5)
while True:
    msgFromServer = c_UDP.recvfrom(bufferSize)
    header = msgFromServer[0] # message received
    print("C: {}".format(header))
    time.sleep(5)
    # send the first message after 5 seconds to ensure all fwds have been registered
    c_UDP.sendto(str.encode(msg_2), fwdAddressPort)
    # send the second message 5 seconds later
    time.sleep(5)
    c_UDP.sendto(str.encode(msg_3), fwdAddressPort)

