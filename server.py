# based on https://pythontic.com/modules/socket/udp-client-server-example
import socket
import time
import random

localIP = ""
localPort = 20001
bufferSize = 1024

# Headers
# (headers such as 'RETURN' or 'FETCH' aren't included as they're simply passed on through the server.)

# Inwards
client_sig = b"C - "  # client signature
worker_sig = b"W - "  # worker signature

# Outwards
ready = b'READY'
end = b'END' 
server_sig = b"S - "  # server signature


def display_msg(message, delay):
    """display the encoded message `msg` after `delay` seconds"""
    print("{}".format(message))
    time.sleep(delay)


# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")
shutdowns = 0

workerIPs = []
usedWorkerIPs = []
clientIP = []

# Listen for incoming datagrams
while True:
    time.sleep(.5)
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]

    # signature of received message.
    # the address is saved for each message
    rec_sig = message[:4]

    # Determine the next action based on who said what.
    # Each message is prefixed with the signature of the origin, including the messages the server sends out.
    content = message[4:].split(b' ')
    action = content[0]
    if rec_sig == client_sig:
        # what is the client asking to do?
        match action:
            case b'GREET':
                display_msg(message, .5)
                clientIP.append(address)
                msgFromServer = "Client Acknowledged"
                bytesToSend = server_sig + str.encode(msgFromServer)
                # Sending a reply to client
                UDPServerSocket.sendto(bytesToSend, address)
            case b'FETCH':
                display_msg(message, .5)
                # if there are any free workers available,
                if len(workerIPs) > 0:
                    # workers are available
                    bytesToSend = server_sig + b" ".join(content)

                    # Sending a reply to chosen worker
                    worker_chosen = random.randrange(0, len(workerIPs))
                    UDPServerSocket.sendto(bytesToSend, workerIPs[worker_chosen])

                    # mark the chosen worker as used
                    usedWorkerIPs.append(workerIPs[worker_chosen])
                    workerIPs.remove(workerIPs[worker_chosen])
                else:
                    msgFromServer = "Workers not ready"
                    bytesToSend = server_sig + str.encode(msgFromServer)

                    # Sending a reply to client
                    UDPServerSocket.sendto(bytesToSend, address)
            case b'RECEIVED':
                display_msg(message, .5)
                bytesToSend = server_sig + ready
                UDPServerSocket.sendto(bytesToSend, address)
            case b'END':
                display_msg(message, .5)
                bytesToSend = server_sig + end
                [UDPServerSocket.sendto(bytesToSend, x) for x in workerIPs] # shut down all workers
            case _:
                bytesToSend = server_sig + str.encode("ERROR Unknown Requested Action: ") + message
                UDPServerSocket.sendto(bytesToSend, address)
    elif rec_sig == worker_sig:
        match action:
            case b'GREET':
                # There shouldn't be any duplicate addresses, but the check is just in case
                if address not in workerIPs:
                    # add all new worker IP addresses.
                    workerIPs.append(address)
                    display_msg(message, .5)
                    msg = "Worker Acknowledged"
                    bytesToSend = server_sig + str.encode(msg)
                    UDPServerSocket.sendto(bytesToSend, address)
            case b'RETURN':
                display_msg(message, .5)
                # free the current worker IP address
                usedWorkerIPs.remove(address)
                workerIPs.append(address)
                bytesToSend = server_sig + b" ".join(content)
                UDPServerSocket.sendto(bytesToSend, clientIP[0])
            case b'END':
                display_msg(message, .1)
                shutdowns += 1
                if shutdowns == len(workerIPs):
                    print(server_sig + b'Goodbye')
                    break
    else:
        print("ERROR Unexpected signal from \"" + rec_sig + "\"")
