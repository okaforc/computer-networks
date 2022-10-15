# based on https://pythontic.com/modules/socket/udp-client-server-example
import socket
import time
import random
import sys
sys.path.append("../helper")
from helper import *

# Headers

# Inwards
# server_sig = b'S - '  # server signature
ack = 0x10
s_ready = 0x20
returned = 0x1c

# Outwards
# client_sig = b'C - '  # client signature
greet = 0x10
fetch = 0x14
received = 0x18
end = 0x1F

item_indexes_to_request = []
received_items = []
item_parts = {}

serverAddressPort = ("", 20001)
bufferSize = 65507

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)



def add_item_to_request(index: int):
    """push an item onto the server request queue"""
    item_indexes_to_request.append(index)


def remove_item_from_request(index: int):
    """pop the item from the server requests queue"""
    item_indexes_to_request.remove(index)
    # try:
    # except:
    #     print("ERROR: NOT VALID ITEM")


items_to_request = ["1.txt", "2.txt", "3.txt", "4.txt", "Bee_1024.png"]
# items_to_request = ["1.txt", "2.txt", "3.txt", "4.txt",
#                     "5.txt", "6.txt", "7.txt", "8.txt", "9.txt", "10.txt",
#                     "selfie.jpg", "high_quality.png", "ringtone.mp3", "cat.png",
#                     "cat_2.png", "cat_3.png", "groceries.txt", "dog.jpg"]


# add a random amount of random file indexes (5 files max)
rand_n = random.randrange(1, 6)
for i in range(rand_n):
    add_item_to_request(random.randrange(0, len(items_to_request)))

# create a list for each part of the file received using the filename as the key
for i in item_indexes_to_request:
    item_parts[items_to_request[i]] = []


len_of_items_requested = len(item_indexes_to_request)

# msg1 = greet
# bytesToSend = msg1
# Send to server using created UDP socket
UDPClientSocket.sendto(combine_bytes(greet), serverAddressPort)

a = time.time()

while True:
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    message = msgFromServer[0]
    action = get_bytes(message, 14, 2)
    file = get_bytes(message, 8, 4)
    packet_number = get_bytes(message, 4, 4)
    total_packets = get_bytes(message, 0, 4)
    # only respond once a response from the server has been achieved
    if msgFromServer:
        display_msg(message, .5)
        if action == ack or action == s_ready:
            # send all the files in the queue
            # bytesToSend = client_sig + start_req
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            while len(item_indexes_to_request) > 0:
                current_file_to_request = item_indexes_to_request[0]
                # server is awake, so ask to awaken workers
                bytesToSend = combine_bytes(fetch, current_file_to_request)
                # print(msg)
                # Send to server using created UDP socket
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                # ic = message[4:].split(b' ')[-1]  # incoming content
                remove_item_from_request(current_file_to_request)  # pop received item from queue
            # bytesToSend = client_sig + end_req
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        elif action == returned:
            if packet_number == total_packets:
                bytesToSend = combine_bytes(received, file)
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            ic = message[4:].split(b' ')[1]  # incoming content
            # remove_item_from_request(ic)  # pop received item from queue
            bytesToSend = combine_bytes(received, ic)
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            received_items.append(ic)
        if len(item_indexes_to_request) == 0 and len(received_items) == len_of_items_requested:
            bytesToSend = combine_bytes(end)
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            break

b = time.time()
print("############################\n" +
      str(b - a) + " " + str(received_items) + "\n############################")
