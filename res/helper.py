""" 
    A general-purpose helper module to avoid clutter and repetition in actual work files.
"""


import time


def get_available_files():
    """Return the list of available files as a list of strings"""
    
    return open("files.txt").readlines()


def combine_bytes(*byte_parts: bytes):
    """
        Takes in an arbitrary amount of byte strings and combines them into a 8-byte bytecode.\n
        Note that the bytes must be in reverse order beginning from MSB \n
        (e.g., array of W, X, Y, Z => returns 0xWXYZ)\n
        Additionally, the combined lengths of said bytes must sum to no more than 8. Anything further
        will be ignored. If they sum to less than 8, all remaining bytes will be set to 0 and 
        should be ignored by any functions using returned byte.
    """

    full_byte = ""
    for byt in byte_parts:
        full_byte += str(hex(byt))[2:]
    if len(full_byte) < 16:
        while len(full_byte) < 16:
            full_byte += "0"
    if "0x" in full_byte: full_byte = full_byte.replace("0x", "")
    return bytes.fromhex(full_byte[:16])


def get_bytes(bytestring: bytes, pos: int, length: int):
    """
        Return the bytes in `bytestring` at `pos` up the string for length `length.`\n
        This will return the bytes ascending up the string from LSB to MSB (right to left) 
        indexed at 0.\n\n

        e.g., `get_bits(0x12345678, 4, 3)` will return 0x234
    """

    return int.from_bytes(bytestring, "big") >> 4*(pos) & int("0x" + "F"*length, 16)


def display_msg(msg: bytes, delay):
    """Print the encoded message `msg` after `delay` seconds"""
    print("{}".format(msg))
    time.sleep(delay)


def index_key_in_list(l:list, k):
    """"Given a list `l` of dictionaries and a key `k`, return the index of the dictionary
        that has k as a value, or -1 if it isn't in it."""
    
    for i in range(len(l)):
        d = l[i]
        if k in list(d.keys()):
            return i
    return -1


def key_in_dict_list(l:list, i:int, n:int):
    """"Given a list `l` of dictionaries and an int `i`, return the `n`th value in the 
        dictionary at the index `i`."""
    return list(l[i].keys())[n]


def key_from_value(d: dict, val):
    """"Given a dictionary `d`, return the key with the value `val`."""

    print(d)
    print(val)
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
