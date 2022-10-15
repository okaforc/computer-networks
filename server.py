# based on https://pythontic.com/modules/socket/udp-client-server-example
import socket
import time
import random

localIP = ""
localPort = 20001
bufferSize = 1024

# Headers
# (headers such as 'RETURN' or 'FETCH' aren't included as they're simply passed on through the server.)

# Inwards
client_sig = b"C - "  # client signature
worker_sig = b"W - "  # worker signature
greet = b'GREET'
fetch = b'FETCH'
start_req = b'START REQUEST'
end_req = b'END REQUEST'
received = b'RECEIVED'
end = b'END'

# Outwards
ready = b'READY'
end = b'END'
server_sig = b"S - "  # server signature

bytecode = 0 # server header


def display_msg(message, delay):
    """display the encoded message `msg` after `delay` seconds"""
    print("{}".format(message))
    time.sleep(delay)


def key_from_value(d, val):
    print(d)
    print(val)
    if val in d:
        print(list(d.keys())[list(d.values()).index(val)])
        return list(d.keys())[list(d.values()).index(val)]
    return None


def str_to_tuple(s: str):
    """"Given a well-formed tuple string `s`, return it as a tuple.
    `s` must be in the form \"(a.b.c.d, x)\", where `s[0]` is a string and
    `s[1]` is an int, and a, b, c, d, x are ints"""
    p = s.replace("(", "").replace(")", "").strip().split(",")
    a = p[0][1:-1]
    b = int(p[1])
    return (a, b)


# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))

print("UDP server up and listening")
client_shutdowns = 0
worker_shutdowns = 0

workerIPs = []
usedWorkerIPs = []
clients = {}

requests = []
is_receiving = False
curr_add = 0


def is_backlog_empty():
    for i in clients:
        if len(clients[i]) > 0:
            return False
    return True


def send_client_content(address, content):
    """Sends the `address`' message (`content`) to any available workers

    Args:
        address (tuple): address that is requesting the item
        content (byte): the content of the address' message
    """

    if len(workerIPs) > 0:
        cont = None
        if type(content) == list:
            cont = b' '.join(content)
        else:
            cont = content
        # if there are any free workers available,
        # workers are available
        bytesToSend = server_sig + cont + b' | ' + str.encode(str(address))

        # Sending a reply to chosen worker
        print(len(workerIPs))
        worker_chosen = random.randrange(0, len(workerIPs))
        UDPServerSocket.sendto(bytesToSend, workerIPs[worker_chosen])

        # mark the chosen worker as used
        usedWorkerIPs.append(workerIPs[worker_chosen])
        workerIPs.remove(workerIPs[worker_chosen])


# Listen for incoming datagrams
while True:
    time.sleep(.5)

    # if there are still items left to send, send them to the workers
    if not is_backlog_empty():
        for i in clients:
            for j in clients[i]:
                # print(j)
                if len(workerIPs) > 0:
                    send_client_content(i, j)
                    clients[i].remove(j)

    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    # signature of received message.
    # the address is saved for each message
    rec_sig = message[:4]

    # Determine the next action based on who said what.
    # Each message is prefixed with the signature of the origin, including the messages the server sends out.
    content = message[4:].split(b' ')
    action = content[0]

    if rec_sig == client_sig:
        display_msg(message, .5)
        # what is the client asking to do?
        # match action:
        if action == greet:
            clients[address] = []
            msgFromServer = "Client Acknowledged"
            bytesToSend = server_sig + str.encode(msgFromServer)
            # Sending a reply to client
            UDPServerSocket.sendto(bytesToSend, address)
        elif action == start_req:
            is_receiving = True
            curr_add = address
        elif action == fetch:
            is_receiving = False
            if len(workerIPs) > 0:
                send_client_content(address, content)
            else:
                # send to client backlog
                # print(clients[address])
                clients[address].append(b" ".join(content))
        elif action == received:
            bytesToSend = server_sig + ready
            UDPServerSocket.sendto(bytesToSend, address)
        elif action == end:
            client_shutdowns += 1
            if client_shutdowns == len(clients):
                bytesToSend = server_sig + end
                [UDPServerSocket.sendto(bytesToSend, x) for x in workerIPs]  # shut down all workers
        else:
            if is_receiving:
                clients[curr_add].append(b" ".join(content[1:]))
            bytesToSend = server_sig + \
                str.encode("ERROR Unknown Requested Action: ") + message
            UDPServerSocket.sendto(bytesToSend, address)
    elif rec_sig == worker_sig:
        display_msg(message, .5)
        match action:
            case b'GREET':
                # There shouldn't be any duplicate addresses, but the check is just in case
                if address not in workerIPs:
                    # add all new worker IP addresses.
                    workerIPs.append(address)
                    # display_msg(message, .5)
                    msg = "Worker Acknowledged"
                    bytesToSend = server_sig + str.encode(msg)
                    UDPServerSocket.sendto(bytesToSend, address)
            case b'RETURN':
                # display_msg(message, .5)
                # free the current worker IP address
                usedWorkerIPs.remove(address)
                workerIPs.append(address)
                bytesToSend = server_sig + b" ".join(content)
                #  + b' ' + str.encode(str(address[1]))
                # get backlog client's address
                ad = str_to_tuple(bytesToSend.split(b" | ")[-1].decode())
                UDPServerSocket.sendto(
                    bytesToSend + b' ' + str.encode(str(address[1])), ad)
                # remove item from client backlog
                mes = fetch + b' ' + content[1]
                if mes in clients[ad]:
                    clients[ad].remove(fetch + b' ' + content[1])
            case b'END':
                # display_msg(message, .1)
                worker_shutdowns += 1
                if worker_shutdowns == len(workerIPs):
                    print(server_sig + b'Goodbye')
                    break
    else:
        print("ERROR Unexpected signal from \"" + rec_sig + "\"")
