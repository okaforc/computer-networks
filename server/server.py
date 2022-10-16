# based on https://pythontic.com/modules/socket/udp-client-server-example
import socket
import time
import random
from helper import *

localIP = ""
localPort = 20001
bufferSize = 65507

# Headers
# (headers such as 'RETURN' or 'FETCH' aren't included as they're simply passed on through the server.)

# Inwards
# Client
c_greet = 0x10
c_fetch = 0x14
received = 0x18
c_end = 0x1F

# Workers
w_greet = 0xc0
w_returned = 0xc4
w_ready = 0xc8
w_end = 0xcf

# Outwards
ack = 0xf0
fetch = 0xf4
returned = 0xf8
ready = 0xfa
end = 0xff
# server_sig = b"S - "  # server signature

bytecode = 0  # server header


# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")
client_shutdowns = 0
worker_shutdowns = 0

workerIPs = []
usedWorkerIPs = []
clients = []  # list of dictionaries each with one

requests = []


def send_client_content(client_index:int, file_index:int):
    """Sends the client address at `index` the message (`content`) to any available workers

    Args:
        client_index (int): index of the address that is requesting the item
        file_index (int): index of the file the client is requesting
    """

    # if there are any free workers available, send the request to them
    if len(workerIPs) > 0:
        # tell the worker to fetch the file at file_index for the client at index
        bytesToSend = combine_bytes(fetch, client_index, file_index, f="full")
        # print(type(file_index), file_index)

        # Sending a reply to chosen worker
        # print(len(workerIPs))
        worker_chosen = random.randrange(0, len(workerIPs))
        UDPServerSocket.sendto(bytesToSend, workerIPs[worker_chosen])

        # mark the chosen worker as used
        usedWorkerIPs.append(workerIPs[worker_chosen])
        workerIPs.remove(workerIPs[worker_chosen])


def is_backlog_empty():
    for i in range(len(clients)):
        if len(value_in_dict_list(clients, i, 0)) > 0:
            return False
    return True


# Listen for incoming datagrams
while True:
    time.sleep(.5)

    # if there are still items left to send, send them to the workers
    if not is_backlog_empty():
        for i in range(len(clients)):
            for j in value_in_dict_list(clients, i, 0):
                if len(workerIPs) > 0:
                    # print(type(j), j)
                    # print(value_in_dict_list(clients, i, 0))
                    # print("wait a sec:", file_requested, value_in_dict_list(clients, i, 0), i)
                    send_client_content(index_key_in_list(clients, key_in_dict_list(clients, i, 0)), j)
                    print("current client index:", i, "clients:", len(clients))
                    value_in_dict_list(clients, i, 0).remove(j)

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    # signature of received message.
    # the address is saved for each message
    # rec_sig = message[:4]
    
    # Determine the next action based on who said what.
    # Each message is prefixed with the signature of the origin, including the messages the server sends out.
    action = get_bytes(message, 14, 2)
    file_requested = get_bytes(message, 10, 4)

    display_msg(message, .5)
    # print(hex(action))
    # what is the client asking to do?
    # match action:
    if action == c_greet:
        # add the client to the list of lists
        # clients are indexed by their client index formed upon acknowledgement
        # e.g., clients[1] = [2, 5, 6]
        # where [2, 5, 6] are the indexes the client requested
        # print(address)
        clients.append({address: []})
        bytesToSend = combine_bytes(ack, f="cs")
        # Sending a reply to client
        UDPServerSocket.sendto(bytesToSend, address)
    elif action == c_fetch:
        if len(workerIPs) > 0:
            send_client_content(index_key_in_list(clients, address), file_requested)
        else:
            # send to client backlog
            clients[index_key_in_list(clients, address)][address].append(file_requested)
    elif action == received:
        # clients[index_key_in_list(clients, address)][address].append(
        #     get_bytes(message, 10, 4))
        bytesToSend = combine_bytes(ready, f="cs")
        UDPServerSocket.sendto(bytesToSend, address)
    elif action == c_end:
        client_shutdowns += 1
        if client_shutdowns == len(clients):
            bytesToSend = combine_bytes(end, f="cs")
            [UDPServerSocket.sendto(bytesToSend, x)
                for x in workerIPs]  # shut down all workers
    elif action == w_greet:
        # There shouldn't be any duplicate addresses, but the check is just in case
        if address not in workerIPs:
            # add all new worker IP addresses.
            workerIPs.append(address)
            bytesToSend = combine_bytes(ack, f="sw")
            UDPServerSocket.sendto(bytesToSend, address)
    elif action == w_returned:
        bytesToSend = combine_bytes(
            returned, 
            get_bytes(message, 12, 2),
            get_bytes(message, 8, 4),
            get_bytes(message, 4, 4),
            get_bytes(message, 0, 4),
            f="full"
            )  # content without fetch action
        #  + b' ' + str.encode(str(address[1]))
        # get backlog client's address
        # ad = str_to_tuple(bytesToSend.split(b" | ")[-1].decode())
        print("returning " + get_available_files()[get_bytes(message, 12, 2)])
        
        print(pretty_print(message))
        # print()
        print("#################### length: " + str(len(clients)) + " ############################")
        print(clients)
        UDPServerSocket.sendto(
            bytesToSend,
            key_in_dict_list(clients, get_bytes(message, 12, 2), 0)  # client index
        )
        # remove item from client backlog
        # mes = fetch + b' ' + file_requested[1]
        # if mes in clients[ad]:
        #     clients[ad].remove(fetch + b' ' + file_requested[1])
    elif action == w_ready:
        # free the current worker IP address
        usedWorkerIPs.remove(address)
        workerIPs.append(address)
    elif action == w_end:
        # display_msg(message, .1)
        worker_shutdowns += 1
        if worker_shutdowns == len(workerIPs):
            print("Goodbye")
            break
    else:
        print("ERROR Unknown Action")
        
    
    # if action == c_greet or action == c_fetch or action == received or action == c_end:
    #     print(hex(action), "wait a sec:", file_requested, clients[index_key_in_list(clients, address)][address])
