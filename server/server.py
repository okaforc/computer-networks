import socket
import time
import random
from helper import *

localIP = ""
localPort = 20001
bufferSize = 65507


# Create a datagram socket
s_UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
s_UDP.bind((localIP, localPort))

print("UDP server up and listening")
client_shutdowns = 0
worker_shutdowns = 0
all_files_sent = False
files_sent = 0

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
        bytesToSend = combine_bytes(
            s_fetch, client_index, file_index, f="full")
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
    for vals in worker_bl.values():
        if len(vals) > 0:
            return False
    return True


# Listen for incoming datagrams
while True:
    # print("server rotation 1")
    # print("gotten here 1")
    # time.sleep(.1)

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
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ TRANSFERRING FILES ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # print(clients)
        for vals in worker_bl.values():
            print(len(vals))
            if len(vals) > 0:
                s_UDP.settimeout(1)
                send_to_next = False
                cl_add = None
                temp = hex(int.from_bytes(vals[0], "big"))[2:]  # header + data
                tn = len(temp)
                ta = get_bytes(vals[0], tn-2, 2)  # temp action
                client_address = key_in_dict_list(
                    clients, get_bytes(vals[0], tn-4, 2), 0)
                s_UDP.sendto(vals[0], client_address)
                i = 1
                while i < len(vals):
                    # for bs in vals[1:]:
                    # time.sleep(.5)
                    bs = vals[i]
                    temp = hex(int.from_bytes(bs, "big"))[2:]  # header + data
                    tn = len(temp)
                    client_address = key_in_dict_list(
                        clients, get_bytes(bs, tn-4, 2), 0)
                    # print(get_bytes(bs, tn-4, 2))
                    temp_fr = get_bytes(bs, tn-8, 4)  # temp file requested
                    temp_pn = get_bytes(bs, tn-12, 4)  # temp packet number
                    temp_tp = get_bytes(bs, tn-16, 4)  # temp total packets
                    if send_to_next:
                        # print("nadd:", get_bytes(bs, tn-4, 2))
                        s_UDP.sendto(bs, client_address)
                        # send_to_next = False
                    try:
                        c_ack = s_UDP.recvfrom(bufferSize)
                        # display_msg(c_ack[0])
                        ta = get_bytes(c_ack[0], len(
                            hex(int.from_bytes(c_ack[0], "big"))[2:])-2, 2)  # temp action
                        # if ta == c_relayed and client_address == cl_add: # ensure correct address is sending ack
                        if ta == c_relayed:
                            # cl_add = c_ack[1]
                            if not send_to_next:
                                s_UDP.sendto(bs, client_address)
                            else:
                                send_to_next = False
                                send_attempts = 0
                        elif ta == c_end or ta == c_received:
                            # the current client has received all its files, so don't send it anything
                            # instead, send the next header immediately
                            if ta == c_end:
                                client_shutdowns += 1
                                print("client", get_bytes(bs, tn-4, 2),
                                      "ended (", client_shutdowns, ")")
                            send_to_next = True
                            files_sent += 1
                        else:
                            print("???", code[ta])
                    except TimeoutError:
                        s_UDP.settimeout(1)
                        i -= 1
                        print("Packet timed out:", get_available_files()[
                              temp_fr], get_bytes(bs, tn-4, 2), temp_pn, temp_tp, i)
                        s_UDP.sendto(bs, client_address)
                        send_attempts += 1
                        if send_attempts >= 3:
                            send_to_next = True
                            i += 1
                    i += 1

                # bytesToSend = combine_bytes(ready, f="cs")
                # s_UDP.sendto(bytesToSend, cl_add)
        all_files_sent = True

    if all_files_sent and files_sent > 0:
        print("all files sent.")
        for ad in worker_bl.keys():
            worker_bl[ad] = []

        if client_shutdowns == len(clients):
            bytesToSend = combine_bytes(s_end, f="cs")
            [s_UDP.sendto(bytesToSend, x)
                for x in workerIPs]  # shut down all workers

    # signature of received message.
    # the address is saved for each message
    # rec_sig = message[:4]
    # print("gotten here 1.5.3")
    s_UDP.settimeout(10)
    bytesAddressPair = s_UDP.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    # print("gotten here 1.5.2")
    temp = hex(int.from_bytes(message, "big"))[2:]  # header + data
    n = len(temp)
    action = get_bytes(message, n-2, 2)
    file_requested = get_bytes(message, n-6, 4)

    display_msg(message[:16])

    # Determine the next action based on who said what.
    if action == c_greet:
        # add the client to the list of lists
        # clients are indexed by their client index formed upon acknowledgement
        # e.g., clients[client_a] = [2, 5, 6]
        # where [2, 5, 6] are the indexes client_a requested
        clients.append({address: []})
        bytesToSend = combine_bytes(s_ack, f="cs")
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
    elif action == c_received:
        bytesToSend = combine_bytes(s_ack, f="cs")
        s_UDP.sendto(bytesToSend, address)
    elif action == c_end:
        client_shutdowns += 1
        # print("client shutdowns:", client_shutdowns)
        # print("workers free:", len(workerIPs))
        if client_shutdowns == len(clients):
            bytesToSend = combine_bytes(s_end, f="cs")
            [s_UDP.sendto(bytesToSend, x)
                for x in workerIPs]  # shut down all workers
    elif action == w_greet:
        # There shouldn't be any duplicate addresses, but the check is just in case
        if address not in workerIPs:
            # add all new worker IP addresses.
            workerIPs.append(address)
            bytesToSend = combine_bytes(s_ack, f="sw")
            s_UDP.sendto(bytesToSend, address)
            worker_bl[address] = []
    elif action == w_returned:
        temp = hex(int.from_bytes(message, "big"))[2:]  # header + data
        n = len(temp)
        # print("////////////", get_bytes(message, n-2, 2))
        nmsg = combine_bytes(
            s_relayed,  # action
            get_bytes(message, n-4, 2),  # client index
            get_bytes(message, n-8, 4),  # file index
            get_bytes(message, n-12, 4),  # packet number
            get_bytes(message, n-16, 4),  # total packets
            f="full"  # format
        )
        # print(prettify(nmsg))
        head = int.from_bytes(nmsg, "big")
        data = get_bytes(message, 0, n-16)
        nmsg = combine_bytes_any(head, data, f="any", length=n)
        worker_bl[address].append(nmsg)
        s_UDP.sendto(
            combine_bytes(
                s_ack,
                get_bytes(message, n-4, 2),
                get_bytes(message, n-8, 4),
                get_bytes(message, n-12, 4),
                get_bytes(message, n-16, 4),
                f="full"
            ),
            address
        )
    elif action == w_ready:
        # free the current worker IP address
        if address in usedWorkerIPs:
            usedWorkerIPs.remove(address)
            workerIPs.append(address)
            print("free:", len(workerIPs))
        s_UDP.sendto(combine_bytes(s_ack, f="full"), address)

    elif action == w_end:
        # display_msg(message, .1)
        worker_shutdowns += 1
        if worker_shutdowns == len(workerIPs):
            print("Goodbye")
            break
    else:
        print("ERROR Unknown Action")
