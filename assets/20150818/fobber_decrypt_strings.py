#!/usr/bin/env python
import re
import struct
import sys


def decrypt_string(crypted_string):
    decrypted = ""
    size = ord(crypted_string[0])
    key = ord(crypted_string[1])
    remaining_chars = len(crypted_string[2:])
    index = 0
    while remaining_chars > 0:
        decrypted += chr(ord(crypted_string[2 + index]) ^ remaining_chars ^ key)
        remaining_chars -= 1
        index += 1
    return decrypted + "\x00\x00"


def replace_bytes(buf, offset, bytes):
    return buf[:offset] + bytes + buf[offset + len(bytes):]


def decrypt_all_strings(binary, image_base):
    # locate decryption function
    decrypt_string_offset = re.search(r"\xE8....\x55\x89\xe5\x60.{8,16}\x30.\x30", binary).start()
    # locate calls to decryption function
    regex_call = r"\xe8"
    calls_to_decrypt_string = []
    for match in re.finditer(regex_call, binary):
        call_origin = match.start()
        packed_call = binary[call_origin + 1:call_origin + 1 + 4]
        rel_call = struct.unpack("I", packed_call)[0]
        call_destination = (image_base + call_origin + rel_call + 5) & 0xFFFFFFFF
        if call_destination == image_base + decrypt_string_offset:
            calls_to_decrypt_string.append(image_base + call_origin)
    # identify calls to these string decryption candidates
    for match in re.finditer(regex_call, binary):
        call_origin = match.start()
        packed_call = binary[call_origin + 1:call_origin + 1 + 4]
        rel_call = struct.unpack("I", packed_call)[0]
        call_destination = (image_base + call_origin + rel_call + 5) & 0xFFFFFFFF
        # decrypt string and fix in the binary
        if call_destination in calls_to_decrypt_string:
            crypted_string = binary[call_origin + 0x5:call_destination -  image_base]
            decrypted_string = decrypt_string(crypted_string)
            binary = replace_bytes(binary, call_origin, "\xE9")
            binary = replace_bytes(binary, call_origin + 0x5, decrypted_string)
            print "0x%x: %s" % (image_base + call_origin, decrypted_string)
    return binary
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: %s <FILEPATH> <IMAGE_BASE>" % sys.argv[0]
        sys.exit()
    binary = ""
    with open(sys.argv[1], "rb") as f_binary:
        binary = f_binary.read()
    decrypted_binary = decrypt_all_strings(binary, int(sys.argv[2], 16))
    with open(sys.argv[1] + "_strfixed", "wb") as f_decrypted:
        f_decrypted.write(decrypted_binary)
