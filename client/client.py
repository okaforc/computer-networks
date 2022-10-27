# based on https://pythontic.com/modules/socket/udp-client-server-example
import math
import socket
import time
import random
from helper import *

# Headers

# Inwards
# server_sig = b'S - '  # server signature
ack = 0xf0
s_relayed = 0xf8
s_ready = 0xfa

# Outwards
# client_sig = b'C - '  # client signature
greet = 0x10
fetch = 0x14
received = 0x18
relayed = 0x1c
end = 0x1F

new_files_dir = "../rec_files/"  # received files

item_indexes_to_request = []
received_items = []
item_parts = {}

serverAddressPort = ("", 20001)
bufferSize = 65507

# Create a UDP socket at client side
c_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

loss_threshold = 0 # max amount of packets allowed to be lost


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
    to_add = random.randrange(0, len(items_to_request))
    if to_add not in item_indexes_to_request:
        add_item_to_request(to_add)

# create a list for each part of the file received using the filename as the key
for i in item_indexes_to_request:
    print(items_to_request[i])
    item_parts[items_to_request[i].rstrip()] = []


len_of_items_requested = len(item_indexes_to_request)

# msg1 = greet
# bytesToSend = msg1
# Send to server using created UDP socket
c_UDP.sendto(combine_bytes(greet, f="cs"), serverAddressPort)

a = time.time()

while True:
    # print("client rotation 1")
    # socket.setdefaulttimeout(10)
    msgFromServer = c_UDP.recvfrom(bufferSize)
    header = msgFromServer[0]

    temp = hex(int.from_bytes(header, "big"))[2:]  # header + data
    n = len(temp)
    action = get_bytes(header, n-2, 2)
    client_ind = get_bytes(header, n-4, 2)
    file_ind = get_bytes(header, n-8, 4)
    packet_number = get_bytes(header, n-12, 4)
    total_packets = get_bytes(header, n-16, 4)
    # only respond once a response from the server has been achieved
    if msgFromServer:
        display_msg(header[:16], .5)
        # display_msg(header[:16], 0)
        if action == ack or action == s_ready:
            # send all the files in the queue
            # bytesToSend = client_sig + start_req
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            while len(item_indexes_to_request) > 0:
                # print("client rotation 2")
                current_file_to_request = item_indexes_to_request[0]
                # print("Requesting " + get_available_files()[item_indexes_to_request[0]])
                # print()
                # server is awake, so ask to awaken workers
                bytesToSend = combine_bytes(
                    fetch, current_file_to_request, f="cs")
                # print(msg)
                # Send to server using created UDP socket
                c_UDP.sendto(bytesToSend, serverAddressPort)
                # ic = message[4:].split(b' ')[-1]  # incoming content
                # pop received item from queue
                remove_item_from_request(current_file_to_request)
                # del items_to_request[0]
            # bytesToSend = client_sig + end_req
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        elif action == s_relayed:
            item_parts[items_to_request[file_ind]].append(header[16:])

            data = get_bytes(header, 0, n-16)  # data from incoming file
            # if packet_number == total_packets: # if it's received the last numbered packet
            # if packet_number >= total_packets - 10: # if it's received one of the final 10 packets
            # if len(item_parts[items_to_request[file_ind].rstrip()]) >= math.ceil(total_packets/5): # if it's received at least a fifth of the total packets
            # if it's received most packets
            if len(item_parts[items_to_request[file_ind].rstrip()]) >= total_packets - loss_threshold:
                # if len(item_parts[items_to_request[file_ind].rstrip()]) == total_packets: # if received all packets
                print("Received " + items_to_request[file_ind])
                received_items.append(file_ind)
                # tell the server that the client received the file when the file has been received fully
                bytesToSend = combine_bytes(
                    received, client_ind, file_ind, packet_number, total_packets, f="full")
                c_UDP.sendto(bytesToSend, serverAddressPort)

            else:
                # print("Partial File: " + items_to_request[file_ind] + ": " + str(
                #     packet_number) + "/" + str(total_packets))
                c_UDP.sendto(combine_bytes(relayed, client_ind, file_ind, packet_number, total_packets, f="full"), serverAddressPort)
                

            with open(new_files_dir + str(client_ind) + "_" + items_to_request[file_ind], 'ab') as f:
                f.write(header[16:])  # data without header

            # ic = message[4:].split(b' ')[1]  # incoming content
            # remove_item_from_request(ic)  # pop received item from queue
            # bytesToSend = combine_bytes(received, file, f="cs")
            # UDPClientSocket.sendto(bytesToSend, serverAddressPort)
        else:
            # print(received_items)
            pass

        if len(item_indexes_to_request) == 0 and len(received_items) == len_of_items_requested:
            bytesToSend = combine_bytes(end, f="cs")
            c_UDP.sendto(bytesToSend, serverAddressPort)
            for i in received_items:
                with open(new_files_dir + str(client_ind) + "_" + items_to_request[file_ind], 'ab') as f:
                    f.close()
            break

b = time.time()
print("############################\n" +
      str(b - a) + " " + str([items_to_request[i] for i in received_items]) + "\n############################")
