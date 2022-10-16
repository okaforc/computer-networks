# based on https://pythontic.com/modules/socket/udp-client-server-example
import os
import socket
from helper import *

# Headers

# Inwards
fetch = 0xf4
s_end = 0xff
# server_sig = b"S - "  # server signature

# Outwards
greet = 0xc0
returned = 0xc4
end = 0xcf
# worker_sig = b"W - "  # worker signature

serverAddressPort = ("", 20001)
bufferSize = 65507
file_indexes = "files.txt"
files_location = ""

# time.sleep(.5)
bytesToSend = combine_bytes(greet, f="full")
# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

while True:
    resp = UDPClientSocket.recvfrom(bufferSize)
    msg = resp[0]
    action = get_bytes(msg, 14, 2)
    client_index = get_bytes(msg, 12, 2)
    file_requested = get_bytes(msg, 8, 4)

    if msg:
        display_msg(msg, 0)
        if action == fetch:
            # Access the file requested by its index and split it into parts to send in a loop
            fs = files_location + get_available_files()[client_index].rstrip()
            file_to_send = open(fs, "rb")
            packet_part = file_to_send.read(bufferSize - 8)
            
            total_size = os.stat(fs).st_size
            total_packets = total_size // bufferSize # integer division
            if total_packets < 1:
                total_packets = 0x1
            packet_number = 0x1
            print(total_packets)
            
            while packet_part:
                bytesToSend = combine_bytes(returned, client_index, file_requested, packet_number, total_packets, f="full")
                print(file_requested)
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                print("worker has " + get_available_files()[file_requested])
                packet_part = file_to_send.read(bufferSize - 8)
                packet_number += 0x1
            
            file_to_send.close()
        elif action == end:
            # display_msg(msg, 0)
            bytesToSend = combine_bytes(end, f="sw")
            # Send to server using created UDP socket
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            break
        else:
            # display_msg(msg, 0)
            pass
