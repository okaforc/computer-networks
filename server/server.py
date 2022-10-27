# based on https://pythontic.com/modules/socket/udp-client-server-example


# TODO: code sometimes (~70%?) hangs due to no received input to server


# https://stackoverflow.com/questions/46174121/recvfrom-is-stuck-and-i-dont-know-why
# https://stackoverflow.com/questions/20289981/python-sockets-stop-recv-from-hanging


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
c_relayed = 0x1c
c_end = 0x1F

# Workers
w_greet = 0xc0
w_returned = 0xc4
w_ready = 0xc8
w_end = 0xcf

# Outwards
ack = 0xf0
fetch = 0xf4
relayed = 0xf8
ready = 0xfa
end = 0xff
# server_sig = b"S - "  # server signature

# Create a datagram socket
s_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
s_UDP.bind((localIP, localPort))

print("UDP server up and listening")
client_shutdowns = 0
worker_shutdowns = 0

workerIPs = []
usedWorkerIPs = []

# list of dictionaries each with one containing an address as a key and a queue of requests as the value
clients = []

# list of dictionaries each with one containing an address as a key and a queue of requests as the value
worker_bl = {}  # worker backlog

requests = []


def send_client_content(client_index: int, file_index: int):
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
        s_UDP.sendto(bytesToSend, workerIPs[worker_chosen])

        # mark the chosen worker as used
        usedWorkerIPs.append(workerIPs[worker_chosen])
        workerIPs.remove(workerIPs[worker_chosen])


def is_client_backlog_empty():
    for i in range(len(clients)):
        if len(value_in_dict_list(clients, i, 0)) > 0:
            return False
    return True


def is_worker_backlog_empty():
    for _, vals in worker_bl.items():
        if len(vals) > 0:
            return False
    return True


# Listen for incoming datagrams
while True:
    # print("server rotation 1")
    # print("gotten here 1")
    time.sleep(.1)
    s_UDP.settimeout(10)

    # if there are still items left to send, send them to the workers
    if not is_client_backlog_empty():
        # print("server rotation 3")
        for i in range(len(clients)):
            for j in value_in_dict_list(clients, i, 0):
                if len(workerIPs) > 0:
                    # print(type(j), j)
                    # print(value_in_dict_list(clients, i, 0))
                    # print("wait a sec:", file_requested, value_in_dict_list(clients, i, 0), i)
                    send_client_content(index_key_in_list(
                        clients, key_in_dict_list(clients, i, 0)), j)
                    # print("current client index:", i, "clients:", len(clients))
                    value_in_dict_list(clients, i, 0).remove(j)
    # print("gotten here 1.5.1")

    # if there are still items left to send, send them to the clients
    if not is_worker_backlog_empty() and len(usedWorkerIPs) == 0:
        # print("server rotation 2")
        for ad, vals in worker_bl.items():
            if len(vals) > 0:
                alrprnt = False
                cl_add = None
                for bs in vals:
                    time.sleep(.5)
                    temp = hex(int.from_bytes(bs, "big"))[2:]  # header + data
                    tn = len(temp)
                    client_address = key_in_dict_list(
                        clients, get_bytes(bs, tn-4, 2), 0)
                    cl_add = client_address
                    if not alrprnt:
                        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^", get_available_files()[get_bytes(
                            bs, tn-8, 4)], "PACKET LENGTH:", len(vals), "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                        alrprnt = True
                    # print("SENDING TO CLIENT:", bs)
                    s_UDP.sendto(
                        bs,
                        client_address  # client index
                    )
                    print(prettify(bs[:32]))
                worker_bl[ad] = []

                bytesToSend = combine_bytes(ready, f="cs")
                s_UDP.sendto(bytesToSend, cl_add)

    # signature of received message.
    # the address is saved for each message
    # rec_sig = message[:4]
    # print("gotten here 1.5.3")
    bytesAddressPair = s_UDP.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    # print("gotten here 1.5.2")
    temp = hex(int.from_bytes(message, "big"))[2:]  # header + data
    n = len(temp)
    action = get_bytes(message, n-2, 2)
    file_requested = get_bytes(message, n-6, 4)

    # Determine the next action based on who said what.
    # Each message is prefixed with the signature of the origin, including the messages the server sends out.

    # client_ind = get_bytes(message, n-4, 2)

    # action = get_bytes(message, 14, 2)
    # print("////////////", get_bytes(message, len(hex(int.from_bytes(message, "big"))[2:])-2, 2))
    # print("????????????", action)
    # file_requested = get_bytes(message, 10, 4)

    display_msg(message[:16], .1)
    # print("gotten here 2")
    # display_msg(message[:16], 0)
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
        s_UDP.sendto(bytesToSend, address)
    elif action == c_fetch:
        if len(workerIPs) > 0:
            send_client_content(index_key_in_list(
                clients, address), file_requested)
        else:
            # send to client backlog
            clients[index_key_in_list(clients, address)][address].append(
                file_requested)
    elif action == c_relayed:
        pass
    elif action == received:
        # clients[index_key_in_list(clients, address)][address].append(
        #     get_bytes(message, 10, 4))
        bytesToSend = combine_bytes(ack, f="cs")
        s_UDP.sendto(bytesToSend, address)
    elif action == c_end:
        client_shutdowns += 1
        # print("client shutdowns:", client_shutdowns)
        # print("workers free:", len(workerIPs))
        if client_shutdowns == len(clients):
            bytesToSend = combine_bytes(end, f="cs")
            [s_UDP.sendto(bytesToSend, x)
                for x in workerIPs]  # shut down all workers
    elif action == w_greet:
        # There shouldn't be any duplicate addresses, but the check is just in case
        if address not in workerIPs:
            # add all new worker IP addresses.
            workerIPs.append(address)
            bytesToSend = combine_bytes(ack, f="sw")
            s_UDP.sendto(bytesToSend, address)
            worker_bl[address] = []
    elif action == w_returned:
        temp = hex(int.from_bytes(message, "big"))[2:]  # header + data
        n = len(temp)
        # print("////////////", get_bytes(message, n-2, 2))
        bytesToSend = combine_bytes(
            relayed,  # action
            get_bytes(message, n-4, 2),  # client index
            get_bytes(message, n-8, 4),  # file index
            get_bytes(message, n-12, 4),  # packet number
            get_bytes(message, n-16, 4),  # total packets
            f="full"  # format
        )  # content without fetch action

        # print("returning " + get_available_files()[get_bytes(message, 12, 2)])

        # print(prettify(message[:32]))
        # print()
        # print("#################### length: " + str(len(clients)) + " ############################")
        # print(clients)
        head = int.from_bytes(bytesToSend, "big")
        # print(message)
        data = get_bytes(message, 0, n-16)

        bytesToSend = combine_bytes_any(head, data, f="any", length=n)

        worker_bl[address].append(bytesToSend)

        # remove item from client backlog
        # mes = fetch + b' ' + file_requested[1]
        # if mes in clients[ad]:
        #     clients[ad].remove(fetch + b' ' + file_requested[1])
    elif action == w_ready:
        # free the current worker IP address
        if address in usedWorkerIPs:
            usedWorkerIPs.remove(address)
            workerIPs.append(address)
        s_UDP.sendto(combine_bytes(ack, f="full"), address)
        print("free:", len(workerIPs))

    elif action == w_end:
        # display_msg(message, .1)
        worker_shutdowns += 1
        if worker_shutdowns == len(workerIPs):
            print("Goodbye")
            break
    else:
        print("ERROR Unknown Action")

    # print("gotten here 3")
    # print("server rotation -1")

    # if action == c_greet or action == c_fetch or action == received or action == c_end:
    #     print(hex(action), "wait a sec:", file_requested, clients[index_key_in_list(clients, address)][address])
