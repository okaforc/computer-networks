# based on https://pythontic.com/modules/socket/udp-client-server-example
import math
import os
import socket
from helper import *


serverAddressPort = ("", 20001)
incomingBuffer = 65507  # max possible UDP buffer size
dataBuffer = 65507 - 8 # max possible UDP buffer size - size of header (in bytes)

file_indexes = "files.txt"
files_location = "files/"

is_packetised = False  # has the current requested file already been packetized?
poll_ack = False  # poll server ACK
output = 0x0
packet_number = 0x1
total_packets = 0x1
has_packets_to_send = False


bytesToSend = combine_bytes(w_greet, f="full")
w_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
w_UDP.sendto(bytesToSend, serverAddressPort)


while True:
    w_UDP.settimeout(2)
    try:
        resp = w_UDP.recvfrom(incomingBuffer)
        msg = resp[0]
        action = get_bytes(msg, 14, 2)
        client_index = get_bytes(msg, 12, 2)
        file_requested = get_bytes(msg, 8, 4)
        if msg:
            display_msg(msg)
            # print(prettify(msg), client_index)
            if action == s_ack:
                poll_ack = False
            elif action == s_fetch:
                current_file_to_return = []  # list of file to return split into bytes
                
                # Access the file requested by its index and split it into parts to send in a loop
                fs = files_location + get_available_files()[file_requested]
                # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^", file_requested)
                total_size = os.stat(fs).st_size

                # round the division upwards for partial packets
                total_packets = math.ceil(total_size / dataBuffer)
                if total_packets < 1:
                    total_packets = 0x1
                packet_number = 0x1
                # print("total packets", total_packets)
                # print("client num", client_index)

                # packetize file
                file_to_send = open(fs, "rb")
                packet_part = file_to_send.read(dataBuffer)
                while packet_part:
                    head = combine_bytes(
                        w_returned, client_index, file_requested, packet_number, total_packets, f="full")
                    current_file_to_return.append(
                        combine_bytes_any(
                            int.from_bytes(head),
                            int.from_bytes(packet_part),
                            f="any",
                            length=min(total_size, dataBuffer)
                        )
                    )
                    # print(prettify(head))
                    # print(packet_part)
                    packet_part = file_to_send.read(dataBuffer)
                    packet_number += 0x1
                file_to_send.close()
                # send the packet regardless of if an ACK was received
                w_UDP.sendto(current_file_to_return[0], serverAddressPort)
                i = 1
                while True:
                    try:
                        # print(prettify(current_file_to_return[0][:16]))
                        # send packets to server after receiving a response
                        packet_resp = w_UDP.recvfrom(incomingBuffer)
                        p_msg = packet_resp[0]
                        # display_msg(p_msg)
                        temp = hex(int.from_bytes(p_msg, "big"))[2:]  # header + data
                        p_n = len(temp)
                        p_action = get_bytes(p_msg, p_n-2, 2)
                        p_pckt = get_bytes(p_msg, p_n-12, 4)
                        # if p_action == s_ack and p_pckt == i - 1:
                        if p_action == s_ack:
                            if i >= total_packets:
                                break
                            w_UDP.sendto(current_file_to_return[i], serverAddressPort)
                        else: 
                            print ("Wrong packet returned")
                            i -= 1
                    except TimeoutError:
                        w_UDP.settimeout(2)
                        i -= 1
                        print("Packet timed out:", client_index, get_available_files()[file_requested], i+1, total_packets)
                        w_UDP.sendto(current_file_to_return[i], serverAddressPort)
                    i += 1  # increment only if the packet has been received
    
                print("file sent")
            elif action == s_end:
                # display_msg(msg, 0)
                bytesToSend = combine_bytes(w_end, f="sw")
                # Send to server using created UDP socket
                w_UDP.sendto(bytesToSend, serverAddressPort)
                break
            else:
                # display_msg(msg, 0)
                pass
    except TimeoutError:
        # print("worker timed out :(")
        pass

    if poll_ack:
        w_UDP.sendto(combine_bytes(w_ready, f="any"), serverAddressPort)
        print("polling ready")