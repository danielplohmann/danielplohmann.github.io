#!/usr/bin/env python
import re
import struct
import sys


def decrypt(buf, key):
    decrypted = ""
    for char in buf:
        decrypted += chr(ord(char) ^ key)
        # rotate 3 bits
        key = ((key >> 3) | (key << (8 - 3))) & 0xFF
        key = (key + 0x53) & 0xFF
    return decrypted


def replace_bytes(buf, offset, bytes):
    return buf[:offset] + bytes + buf[offset + len(bytes):]


def decrypt_all(binary, image_base):
    # locate decryption function
    decrypt_function_offset = re.search(r"\x60\x8B.\x24\x20\x66", binary).start()
    # locate all calls to decryption function
    regex_call = r"\xe8"
    for match in re.finditer(regex_call, binary):
        call_origin = match.start()
        packed_call = binary[call_origin + 1:call_origin + 1 + 4]
        rel_call = struct.unpack("I", packed_call)[0]
        call_destination = (image_base + call_origin + rel_call + 5) & 0xFFFFFFFF
        if call_destination == image_base + decrypt_function_offset:
            # decrypt function and replace/fix
            decrypted_flag = ord(binary[call_origin - 0x2])
            if decrypted_flag == 0x0:
                key = ord(binary[call_origin - 0x3])
                size = struct.unpack("H", binary[call_origin - 0x5:call_origin - 0x3])[0] ^ 0x461F
                buf = binary[call_origin + 0x5:call_origin + 0x5 + size]
                decrypted_function = decrypt(buf, key)
                binary = replace_bytes(binary, call_origin + 0x5, decrypted_function)
                binary = replace_bytes(binary, call_origin + len(decrypted_function), "\xC3")
                binary = replace_bytes(binary, call_origin - 0x2, "\x01")
    return binary
    

def fix_call_over_crypted_string(binary, image_base):
    return


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: %s <FILEPATH> <IMAGE_BASE>" % sys.argv[0]
        sys.exit()
    binary = ""
    with open(sys.argv[1], "rb") as f_binary:
        binary = f_binary.read()
    decrypted_binary = decrypt_all(binary, int(sys.argv[2], 16))
    with open(sys.argv[1] + "_decrypted", "wb") as f_decrypted:
        f_decrypted.write(decrypted_binary)
