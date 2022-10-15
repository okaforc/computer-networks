# based on https://pythontic.com/modules/socket/udp-client-server-example
import socket
import time
import random

# Headers

# Inwards
server_sig = b'S - '  # server signature
returned = b'RETURN '

# Outwards
client_sig = b'C - '  # client signature
greet = b'GREET '
fetch = b'FETCH '
start_req = b'START REQUEST'
end_req = b'END REQUEST'
received = b'RECEIVED '
end = b'END'

messages_to_request = []
received_items = []


def display_msg(msg, delay):
    """display the encoded message `msg` after `delay` seconds"""
    print("{}".format(msg))
    time.sleep(delay)


def add_item_to_request(item: str):
    """push an item onto the server request queue"""
    messages_to_request.append(str.encode(item))


def remove_item_from_request(item: bytes):
    """pop the item from the server requests queue"""
    messages_to_request.remove(item)
    # try:
    # except:
    #     print("ERROR: NOT VALID ITEM")


items_to_request = ["1.txt", "2.txt", "3.txt", "4.txt",
                    "5.txt", "6.txt", "7.txt", "8.txt", "9.txt", "10.txt",
                    "selfie.jpg", "high_quality.png", "ringtone.mp3", "cat.png",
                    "cat_2.png", "cat_3.png", "groceries.txt", "dog.jpg"]


# add a random amount of random files (5 files max)
rand_n = random.randrange(1, 6)
for i in range(rand_n):
    add_item_to_request(
        items_to_request[random.randrange(0, len(items_to_request))])


len_of_items_requested = len(messages_to_request)

serverAddressPort = ("", 20001)
bufferSize = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# bytesToSend = str.encode(msg1)
msg1 = client_sig + greet + b"Initial Ping"
bytesToSend = msg1
# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

a = time.time()

while True:
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    message = msgFromServer[0]
    # only respond once a response from the server has been achieved
    if msgFromServer:
        display_msg(message, .5)
        if message == b'S - Client Acknowledged' or message == b'S - READY':
            # send all the files in the queue
            # bytesToSend = client_sig + start_req
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            while len(messages_to_request) > 0:
                msg = messages_to_request[0]
                # server is awake, so ask to awaken workers
                bytesToSend = client_sig + fetch + msg
                # print(msg)
                # Send to server using created UDP socket
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                # ic = message[4:].split(b' ')[-1]  # incoming content
                remove_item_from_request(msg)  # pop received item from queue
            # bytesToSend = client_sig + end_req
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        elif server_sig + returned in message:
            ic = message[4:].split(b' ')[1]  # incoming content
            # remove_item_from_request(ic)  # pop received item from queue
            bytesToSend = client_sig + received + ic
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            received_items.append(ic)
        if len(messages_to_request) == 0 and len(received_items) == len_of_items_requested:
            bytesToSend = client_sig + end
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            break

b = time.time()
print("############################\n" +
      str(b - a) + " " + str(received_items) + "\n############################")
