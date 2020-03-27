import re
import struct
import sys

"""
example output:

$ python andromeda_config.py a17247808c176c81c3ea66860374d705_defanged.bin

bot_id: 0xdeadbeef, botnet_id: 0x30714
config buffer offset: 0x354
0000  14 07 03 00 d4 e2 04 63 53 03 86 e4 82 5d 97 1c   .......cS....]..
0010  c6 f8 58 9c f0 8f 2c da 79 0b 6d 1c ce cb 9d ba   ..X...,.y.m.....
0020  81 c5 c9 42 60 f1 63 48 87 45 00 c1 fe 34 8b bf   ...B`.cH.E...4..
0030  bb 84 93 0d b7 ca 47 dc 2f 8a 35 8a 2d 48 87 31   ......G./.5.-H.1
0040  33 b5 b1 3d 4f a8 2f 49 17 4d e4 58 93 11 a4 81   3..=O./I.M.X....
0050  3b 4e 1e 8a 28 79 f7 8f 16 5a 85 2f 0a 11 3e 4a   ;N..(y...Z./..>J
0060  df 5b 70 06 57 9d 33 f0 80 ae ad 6a 13 d2 ed 95   .[p.W.3....j....
0070  50 ce e7 24 0d 4c d8 db 84 4d 56 13 40 83 06 2d   P..$.L...MV.@..-
0080  3c 13 f5 52 59 f3 34 1f 84 ac 5c 46 13 ec e8 12   <..RY.4....F....
0090  c8 50 8d 87 8b 59 a8 d6 17 0d 4c d8 db 84 4d 56   .P...Y....L...MV
00a0  4e 52 c6 5c 3a 3b 54 f3 51 58 f1 39 58 90 a1 02   NR..:;T.QX.9X...
00b0  1f 0d 4c d8 db 84 4d 56 13 40 83 06 2d 3c 19 fb   ..L...MV.@..-<..
00c0  4b 55 ba 2f 13 94 e6 1b 4b 18 e4 bf 55 d6 5c 98   KU./....K...U...
00d0  1d 0d 4c d8 db 84 4d 56 0d 54 9e 15 24 21 19 ff   ..L...MV.T..$!..
00e0  11 53 e6 26 59 89 a7 16 40 04 af b7 13 d6 00 f0   .S.&Y...@.......
00f0  1b cb c7 a3 c5 68 48 ca b7 6a 91 bb 83 e9 07 ee   .....hH..j......
0100  d2 78 8b 88 85 78 28 6b 3f 39 72 36 6f 88 ff db   .x...x(k?9r6o...
0110  63 6d b4 f5 f3 89 99 c5 68 8d 68 6b 7b 62 9d 05   cm......h.hk{b..

length of identified config buffer: 288
number of C&C URL candidates: 50

traffic rc4 key:
  b7ca47dc2f8a358a2d48873133b5b13d

decrypted C&C URLs:
  hxxp://sunglobe.org/index.php
  hxxp://masterbati.net/index.php
  hxxp://0s6.ru/index.php
  hxxp://masterhomeguide.com/index.php
"""


def hexdump(src, length=16, indent=0):
    # source : http://pastebin.com/C3XszsCv
    trans_table = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
    lines = []
    for c in xrange(0, len(src), length):
        chars = src[c:c + length]
        hexed = ' '.join(["%02x" % ord(x) for x in chars])
        printable = ''.join(["%s" % ((ord(x) <= 127 and trans_table[ord(x)]) or '.') for x in chars])
        lines.append("%s%04x  %-*s  %s\n" % (indent * " ", c, length * 3, hexed, printable))
    return ''.join(lines)


def rc4crypt(data, key):
    x = 0
    box = range(256)
    for i in range(256):
        x = (x + box[i] + ord(key[i % len(key)])) % 256
        box[i], box[x] = box[x], box[i]
    x = 0
    y = 0
    out = []
    for char in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))

    return ''.join(out)


def _getUrlSequenceCandidates(crypted_block):
    possible_crypted_urls = []
    possible_crypted_url = ""
    # from back to start, since it's easier to handle this way
    for index, byte in enumerate(crypted_block[::-1]):
        if ord(byte) > 0x8 and ord(byte) < 0x30:
            possible_crypted_urls.append(possible_crypted_url[-ord(byte):][::-1])
        possible_crypted_url += byte
    return possible_crypted_urls


def _decryptUrls(crypted_urls, rc4_key):
    decrypted_urls = []
    for index, crypted_url in enumerate(crypted_urls):
        decrypted_urls.append(rc4crypt(crypted_url, rc4_key))
    return decrypted_urls


def main():
    config_buf = ""

    with open(sys.argv[1], "rb") as fin:
        config_buf = fin.read()

    crypt_block = ""
    regex = (r"\xFF\x35(?P<cnc_os>[\s\S]{4})"
             r"\xFF\x35(?P<cnc_bid>[\s\S]{4})"
             r"\xFF\x35(?P<cnc_id>[\s\S]{4})"
             r"\x68[\s\S]{4}"
             r"[\s\S]"
             r"\xFF\x15")
    match = re.search(regex, config_buf)
    config_offset = 0
    if match:
        cnc_bid = match.group("cnc_bid")
        cnc_bid = struct.unpack("I", cnc_bid)[0]
        config_offset = cnc_bid & 0xFFFF
        cnc_bid = struct.unpack("I", config_buf[cnc_bid & 0xFFFF:4 + cnc_bid & 0xFFFF])[0]
        cnc_id = match.group("cnc_id")
        cnc_id = struct.unpack("I", cnc_id)[0]
        cnc_id = struct.unpack("I", config_buf[cnc_id & 0xFFFF:4 + cnc_id & 0xFFFF])[0]
        print "bot_id: 0x%x, botnet_id: 0x%x" % (cnc_id, cnc_bid)

    if config_offset:
        print "config buffer offset: 0x%x" % config_offset
        crypt_block = config_buf[config_offset:]
        crypt_block_end = crypt_block.find("\x00" * 4)
        crypt_block = crypt_block[:crypt_block_end]

    print hexdump(crypt_block)

    candidates = _getUrlSequenceCandidates(crypt_block)
    print "length of identified config buffer: %d" % len(crypt_block)
    print "number of C&C URL candidates: %d\n" % len(candidates)

    rc4_key = ""
    decrypted_urls = []
    for i in xrange(0, len(crypt_block)):
        if len(crypt_block[i: i + 16].encode("hex")) == 32:
            possible_decrypted_urls = _decryptUrls(candidates, crypt_block[i: i + 16].encode("hex")[::-1])
            for possible_decrypted_url in possible_decrypted_urls:
                if "http" in possible_decrypted_url:
                    decrypted_urls.append(possible_decrypted_url)
            if decrypted_urls != []:
                rc4_key = crypt_block[i: i + 16].encode("hex")
                break

    print "traffic rc4 key:\n  %s\n" % rc4_key
    print "decrypted C&C URLs: "
    print "  " + "\n  ".join(decrypted_urls)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "usage: %s <path_of_andromeda_dump>" % (sys.argv[0])
    else:
        sys.exit(main())
