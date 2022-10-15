# based on https://pythontic.com/modules/socket/udp-client-server-example
import socket
import time

# Headers

# Inwards
fetch = b'FETCH '
server_sig = b"S - "  # server signature

# Outwards
returned = b'RETURN '
greet = b'GREET '
end = b'END'
worker_sig = b"W - "  # worker signature

serverAddressPort = ("", 20001)
bufferSize = 1024


def display_msg(message, delay):
    """display the encoded message `msg` after `delay` seconds"""
    print("{}".format(message))
    time.sleep(delay)


# time.sleep(.5)
bytesToSend = worker_sig + greet + b"Initial Ping"
# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

while True:
    resp = UDPClientSocket.recvfrom(bufferSize)
    msg = resp[0]
    content = msg[4:].split(b' ')
    action = content[0]

    if msg:
        display_msg(msg, 0)
        match action:
            case b'FETCH':
                # Send to server using created UDP socket
                del content[0]
                bytesToSend = worker_sig + returned + b' '.join(content)
                # print(bytesToSend)
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            case b'END':
                # display_msg(msg, 0)
                bytesToSend = worker_sig + end
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                break
            case _:
                # display_msg(msg, 0)
                pass
