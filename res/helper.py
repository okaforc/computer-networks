""" 
    A general-purpose helper module to avoid clutter and repetition in actual work files.
"""


import time
import os
from binascii import hexlify

#################################################### HEADER INFORMATION ####################################################
c_greet = 0x10
c_fetch = 0x14
c_received = 0x18
c_relayed = 0x1c
c_end = 0x1F

s_ack = 0xf0
s_fetch = 0xf4
s_relayed = 0xf8
s_ready = 0xfa
# s_np = 0xfc
s_end = 0xff

w_greet = 0xc0
w_returned = 0xc4
w_ready = 0xc8
w_end = 0xcf


code = {
    c_greet: "Client GREET",
    c_fetch: "Client FETCH",
    c_received: "Client RECEIVED",
    c_relayed: "Client RELAYED",
    c_end: "Client END",

    s_ack: "Server ACK",
    s_fetch: "Server FETCH",
    s_relayed: "Server RELAY",
    s_ready: "Server READY",
    # s_np: "Server NEXT",
    s_end: "Server END",

    w_greet: "Worker GREET",
    w_returned: "Worker RETURN",
    w_ready: "Worker READY",
    w_end: "Worker END"
}


#################################################### HEADER INFORMATION ####################################################

def prettify(msg: bytes):
    """Prettify `msg`, seperating it every 2 bytes"""

    return hexlify(msg, "-", 2)


def display_msg(msg: bytes, d=0.0):
    """Decode and print the encoded message `msg` and wait `d` seconds"""

    temp = hex(int.from_bytes(msg, "big"))[2:]  # header + data
    n = len(temp)

    action = code[get_bytes(msg, n-2, 2)]
    new_msg = action
    if action == code[c_fetch]:
        new_msg += " " + get_available_files()[get_bytes(msg, n-6, 4)]
    elif action in (code[c_received], code[c_relayed]):
        new_msg += " " + str(get_bytes(msg, n-4, 2))
        new_msg += " " + get_available_files()[get_bytes(msg, n-8, 4)]
        new_msg += " " + str(get_bytes(msg, n-12, 4))
        new_msg += " " + str(get_bytes(msg, n-16, 4))
    elif action == code[s_fetch]:
        new_msg += " " + str(get_bytes(msg, n-4, 2))
        new_msg += " " + get_available_files()[get_bytes(msg, n-8, 4)]
    elif action == code[s_relayed]:
        new_msg += " " + str(get_bytes(msg, n-4, 2))
        new_msg += " " + get_available_files()[get_bytes(msg, n-8, 4)]
        new_msg += " " + str(get_bytes(msg, n-12, 4))
        new_msg += " " + str(get_bytes(msg, n-16, 4))
    elif action == code[w_returned]:
        new_msg += " " + str(get_bytes(msg, n-4, 2))
        new_msg += " " + get_available_files()[get_bytes(msg, n-8, 4)]
        new_msg += " " + str(get_bytes(msg, n-12, 4))
        new_msg += " " + str(get_bytes(msg, n-16, 4))

    print("{}".format(new_msg))
    time.sleep(d)


def get_available_files():
    """Return the list of available files as a list of strings"""

    fl = open("files.txt")
    l = fl.readlines()
    fl.close()
    for i in range(len(l)):
        l[i] = l[i].rstrip()  # remove newline
    return l


def combine_bytes_any(*byte_parts: bytes, f: str, length: int):
    """
        Takes in an arbitrary amount of byte strings and combines them into a `length/2`-byte bytecode.\n
        Note that the bytes must be in reverse order beginning from MSB \n
        (e.g., array of W, X, Y, Z => returns 0xWXYZ)\n
        Additionally, the combined lengths of said bytes must sum to no more than `length/2`. Anything further
        will be ignored. If they sum to less than `length/2`, all remaining bytes will be set to 0 and 
        should be ignored by any functions using returned byte.\n\n
        The `format` specified will determine how the bytecode will be filled out.\n
        \t - "any": 
        fill it out in the order given, no buffer required\n
        \t - "cs": 
        client to server. returns it buffered with the action and file requested only.\n
        \t - "full": 
        server to worker, worker to server, and server to client. returns it buffered in the order of 
        `action, client header, file, packet num, total packets`\n

    """

    full_byte = ""
    if f == "any":
        for byt in byte_parts:
            full_byte += str(hex(byt))[2:]
    elif f == "cs":
        # client to server (action(1), file(2))
        i = 0  # order
        for byt in byte_parts:
            if i == 0:
                full_byte += str(hex(byt))[2:].zfill(2)
            if i == 1:
                full_byte += str(hex(byt))[2:].zfill(4)
            i += 1
    elif f == "sw":
        # server to worker (action(1), client index(1), file(2))
        i = 0  # order
        for byt in byte_parts:
            if i <= 1:
                full_byte += str(hex(byt))[2:].zfill(2)
            if i == 2:
                full_byte += str(hex(byt))[2:].zfill(4)
            i += 1
    elif f == "full":
        # full length (action(1), client index(1), file(2), packet num(2), total packets(2))
        i = 0  # order
        for byt in byte_parts:
            if i == 0:
                full_byte += str(hex(byt))[2:].zfill(2)
            if i == 1:
                full_byte += str(hex(byt))[2:].zfill(2)
            if i >= 2:
                full_byte += str(hex(byt))[2:].zfill(4)
            i += 1

    full_byte = full_byte.replace("0x", "").replace("x", "")
    if len(full_byte) % 2 == 1:
        full_byte = full_byte + "0"  # make it evenly long if it becomes odd
    if len(full_byte) < length:
        while len(full_byte) < length:
            full_byte += "0"
    return bytes.fromhex(full_byte)


def combine_bytes(*byte_parts: bytes, f: str):
    """
        Takes in an arbitrary amount of byte strings and combines them into a 8-byte bytecode.\n
        Note that the bytes must be in reverse order beginning from MSB \n
        (e.g., array of W, X, Y, Z => returns 0xWXYZ)\n
        Additionally, the combined lengths of said bytes must sum to no more than 8. Anything further
        will be ignored. If they sum to less than 8, all remaining bytes will be set to 0 and 
        should be ignored by any functions using returned byte.\n\n
        The `format` specified will determine how the bytecode will be filled out.\n
        \t - "any": 
        fill it out in the order given, no buffer required\n
        \t - "cs": 
        client to server. returns it buffered with the action and file requested only.\n
        \t - "full": 
        server to worker, worker to server, and server to client. returns it buffered in the order of 
        `action, client header, file, packet num, total packets`\n

    """

    return combine_bytes_any(*byte_parts, f=f, length=16)


def get_bytes(bytestring: bytes, pos: int, length: int):
    """
        Return the bytes in `bytestring` at `pos` up the string for length `length.`\n
        This will return the bytes ascending up the string from LSB to MSB (right to left) 
        indexed at 0.\n\n

        e.g., `get_bytes(0x12345678, 4, 3)` will return 0x234
    """

    return int.from_bytes(bytestring, "big") >> 4*(pos) & int("0x" + "F"*length, 16)


def index_key_in_list(l: list, k):
    """Given a list `l` of dictionaries and a key `k`, return the index of the dictionary
        that has `k` as a value, or -1 if it isn't in it."""

    for i in range(len(l)):
        d = l[i]
        if k in list(d.keys()):
            return i
    return -1


def key_in_dict_list(l: list, i: int, n: int):
    """"Given a list `l` of dictionaries and an int `i`, return the `n`th key in the 
        dictionary at the index `i`."""
    return list(l[i].keys())[n]


def value_in_dict_list(l: list, i: int, n: int):
    """"Given a list `l` of dictionaries and an int `i`, return the `n`th value in the 
        dictionary at the index `i`."""
    return list(l[i].values())[n]


def key_from_value(d: dict, val):
    """"Given a dictionary `d`, return the key with the value `val`."""

    if val in d:
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
