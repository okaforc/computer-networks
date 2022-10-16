# based on https://pythontic.com/modules/socket/udp-client-server-example
import socket
import time
import random
from helper import *

# Headers

# Inwards
# server_sig = b'S - '  # server signature
ack = 0xf0
returned = 0xf8
s_ready = 0xfa

# Outwards
# client_sig = b'C - '  # client signature
greet = 0x10
fetch = 0x14
received = 0x18
end = 0x1F


new_files_dir = "../rec_files/" # received files


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


items_to_request = get_available_files()
# items_to_request = ["1.txt", "2.txt", "3.txt", "4.txt",
#                     "5.txt", "6.txt", "7.txt", "8.txt", "9.txt", "10.txt",
#                     "selfie.jpg", "high_quality.png", "ringtone.mp3", "cat.png",
#                     "cat_2.png", "cat_3.png", "groceries.txt", "dog.jpg"]


# add a random amount of random file indexes
rand_n = random.randrange(1, 5)
for i in range(rand_n):
    add_item_to_request(random.randrange(0, len(items_to_request)-1))

# create a list for each part of the file received using the filename as the key
for i in item_indexes_to_request:
    item_parts[items_to_request[i].rstrip()] = []


len_of_items_requested = len(item_indexes_to_request)

# msg1 = greet
# bytesToSend = msg1
# Send to server using created UDP socket
UDPClientSocket.sendto(combine_bytes(greet, f="cs"), serverAddressPort)

a = time.time()

while True:
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    message = msgFromServer[0]
    
    temp = hex(int.from_bytes(message, "big"))[2:] # header + data
    n = len(temp)
    action = get_bytes(message, n-2, 2)
    client_ind = get_bytes(message, n-4, 2)
    file_ind = get_bytes(message, n-8, 4)
    packet_number = get_bytes(message, n-12, 4)
    total_packets = get_bytes(message, n-16, 4)
    # only respond once a response from the server has been achieved
    if msgFromServer:
        display_msg(message, .5)
        if action == ack or action == s_ready:
            # send all the files in the queue
            # bytesToSend = client_sig + start_req
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            while len(item_indexes_to_request) > 0:
                current_file_to_request = item_indexes_to_request[0]
                # print("Requesting " + get_available_files()[item_indexes_to_request[0]])
                # print()
                # server is awake, so ask to awaken workers
                bytesToSend = combine_bytes(
                    fetch, current_file_to_request, f="cs")
                # print(msg)
                # Send to server using created UDP socket
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                # ic = message[4:].split(b' ')[-1]  # incoming content
                # pop received item from queue
                remove_item_from_request(current_file_to_request)
                del items_to_request[0]
            # bytesToSend = client_sig + end_req
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        elif action == returned:
            bytesToSend = combine_bytes(received, client_ind, file_ind, f="full")
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            
            data = get_bytes(message, 0, n-16) # data from incoming file
            if packet_number == total_packets:
                print("Received " + get_available_files()[file_ind] + ": " + str(packet_number) + "/" + str(total_packets))
                received_items.append(file_ind)
            else:
                print("Partial File: " + get_available_files()[file_ind])
            
            
            with open(new_files_dir+get_available_files()[file_ind], 'ab') as f:
                f.write(message[16:]) # data without header
            
            # ic = message[4:].split(b' ')[1]  # incoming content
            # remove_item_from_request(ic)  # pop received item from queue
            # bytesToSend = combine_bytes(received, file, f="cs")
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        else:
            # print(received_items)
            pass
        if len(item_indexes_to_request) == 0 and len(received_items) == len_of_items_requested:
            bytesToSend = combine_bytes(end, f="cs")
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            break

b = time.time()
print("############################\n" +
      str(b - a) + " " + str(received_items) + "\n############################")
