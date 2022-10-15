# based on https://pythontic.com/modules/socket/udp-client-server-example
import socket
import time

# Headers

# Inwards
server_sig = b'S - '  # server signature
returned = b'RETURN '

# Outwards
client_sig = b'C - '  # client signature
greet = b'GREET '
fetch = b'FETCH '
received = b'RECEIVED '
end = b'END'

messages_to_request = []


def display_msg(msg, delay):
    """display the encoded message `msg` after `delay` seconds"""
    print("{}".format(msg))
    time.sleep(delay)


def add_item_to_request(item: str):
    """push an item onto the server request queue"""
    messages_to_request.append(fetch + str.encode(item))


def remove_item_from_request(item: bytes):
    """pop the item from the server requests queue"""
    [messages_to_request.remove(s) for s in messages_to_request if item in s]


add_item_to_request("message1.txt")
add_item_to_request("legally_downloaded_popular_movie.mp4")
add_item_to_request("selfie.jpeg")
add_item_to_request("legally_downloaded_popular_song.mp3")


serverAddressPort = ("", 20001)
bufferSize = 1024

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# bytesToSend = str.encode(msg1)
msg1 = client_sig + greet + b"Initial Ping"
bytesToSend = msg1
# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)

while True:
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    message = msgFromServer[0]
    # only respond once a response from the server has been achieved
    if msgFromServer:
        display_msg(message, .5)
        match message:
            case b'S - Client Acknowledged' | b'S - Workers not ready' | b'S - READY' if len(messages_to_request) > 0:
                # server is awake, so ask to awaken workers
                bytesToSend = client_sig + messages_to_request[0]
                # Send to server using created UDP socket
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            case _ if server_sig + returned in message:
                ic = message[4:].split(b' ')[-1]  # incoming content
                remove_item_from_request(ic) # pop received item from queue
                bytesToSend = client_sig + received + ic
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            case _:
                bytesToSend = client_sig + end
                UDPClientSocket.sendto(bytesToSend, serverAddressPort)
                break
