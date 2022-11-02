# based on https://pythontic.com/modules/socket/udp-client-server-example
import math
import socket
import time
import random
from helper import *

new_files_dir = "../rec_files/"  # received files

item_indexes_to_request = []
received_items = []
item_parts = {}

serverAddressPort = ("", 20001)
bufferSize = 65507

# Create a UDP socket at client side
c_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

loss_threshold = 3  # max amount of packets allowed to be lost


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
# rand_n = random.randrange(1, 5)
rand_n = random.randrange(1, len(items_to_request)+1)
for i in range(rand_n):
    to_add = random.randrange(0, len(items_to_request))
    if to_add not in item_indexes_to_request:
        add_item_to_request(to_add)

# add_item_to_request(1)
# add_item_to_request(3)
# add_item_to_request(19)
# add_item_to_request(5)
# add_item_to_request(7)


# create a list for each part of the file received using the filename as the key
for i in item_indexes_to_request:
    print(items_to_request[i])
    item_parts[items_to_request[i]] = {
        # "name": "",  # name of file the data is to be stored in
        "data": [],  # list to store data in
        "set": False  # has the list been initialised yet?
    }

len_of_items_requested = len(item_indexes_to_request)

# msg1 = greet
# bytesToSend = msg1
# Send to server using created UDP socket
c_UDP.sendto(combine_bytes(c_greet), serverAddressPort)

a = time.time()

while True:
    # print("client rotation 1")
    # c_UDP.settimeout(5)
    try:
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
            display_msg(header[:8])
            if action == s_ack:
                # send all the files in the queue
                while len(item_indexes_to_request) > 0:
                    current_file_to_request = item_indexes_to_request[0]
                    # server is awake, so ask to awaken workers
                    bytesToSend = combine_bytes(
                        c_fetch, FILLER, current_file_to_request)
                    # Send to server using created UDP socket
                    c_UDP.sendto(bytesToSend, serverAddressPort)
                    # pop sent item from queue
                    remove_item_from_request(current_file_to_request)
            elif action == s_relayed:
                # item_parts[items_to_request[file_ind]].append(header[16:])
                # write the data into the correct index within the list based on the packet number
                if not item_parts[items_to_request[file_ind]]["set"]:
                    item_parts[items_to_request[file_ind]
                               ]["data"] = [None]*total_packets
                    item_parts[items_to_request[file_ind]]["set"] = True

                item_parts[items_to_request[file_ind]
                           ]["data"][packet_number - 1] = header[8:]
                data = get_bytes(header, 0, n-16)  # data from incoming file

                if (item_parts[items_to_request[file_ind]]["data"]).count(None) <= loss_threshold:
                    print("Received " + items_to_request[file_ind])
                    if file_ind not in received_items:
                        received_items.append(file_ind)
                    # tell the server that the client received the file when the file has been received fully
                    bytesToSend = combine_bytes(
                        c_received, client_ind, file_ind, packet_number, total_packets)
                    c_UDP.sendto(bytesToSend, serverAddressPort)
                    print(
                        f'gotten {len(received_items)}/{len_of_items_requested} files')
                else:
                    c_UDP.sendto(combine_bytes(c_relayed, client_ind, file_ind,
                                 packet_number, total_packets), serverAddressPort)

            else:
                print("client: unknown action")
                pass
    except:
        # if there's a hang for whatever reason, tell the server you received something and move on
        c_UDP.sendto(combine_bytes(c_received), serverAddressPort)
        c_UDP.settimeout(3)

    # write to file
    if len(item_indexes_to_request) == 0 and len(received_items) == len_of_items_requested:
        for file in item_parts.keys():
            with open(new_files_dir + str(client_ind) + "_" + file, 'ab') as f:
                for i in range(len(item_parts[file]["data"])):
                    info = item_parts[file]["data"][i]
                    try:
                        f.write(info)  # data without header
                    except TypeError:
                        print("packet not received:", file, i)

        bytesToSend = combine_bytes(c_end)
        c_UDP.sendto(bytesToSend, serverAddressPort)
        break  # end

b = time.time()
print("############################\n" +
      str(b - a) + " " + str([items_to_request[i] for i in received_items]) + "\n############################")
