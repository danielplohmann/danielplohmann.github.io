---
layout:             post
title:              "PKCS detection"
author:             Daniel Plohmann
date:               2012-11-01 01:00:00 +0100
last_modified_at:   2012-11-01 01:00:00 +0100
categories:         blog
tags:               idascope
---

While I already [announced]({% post_url 2012-10-27-idascope-online-winapi %}) in my last blog post that the PKCS detection feature was implemented in my private development branch of IDAscope, I just wanted to do another technical write-up in order to cover it up properly. 
  
I think starting from now on, I'm going to write more about the actual development process and code produced in order to share some insights in how to use IDA's Python API.  
Feature-wise, this is not a big deal but I thought it would be fun to have this integrated.  
  
### How it began...
So this story began last week at [hack.lu][hacklu 2012] where mortis talked to me about IDAscope. 
He then said that some time ago he used some older tools in order to detect/extract PKCS components from a binary and I told him that it would be actually a nice idea to have this in IDAscope as well as there is malware with signed updates using asymmetric cryptography.  
  
He pointed me to this 2010' [script][kyprizel getkeys] by kyprizel, which was a good starting point. 
It's based on a [tool][trapkit sslfinder] by Tobias Klein, which sadly he makes no longer available due to German law (so called "anti hacking" paragraph §202c). 
I looked at kyprizel's script and thought that something like this should be doable in a short amount of time. 
I changed IDAscope's code quickly but then I remembered that you often find base64 encoded certificate and key data. 
  
I got motivated by that and wanted to cover it as well. 
On the other hand, I realized that implementing this feature, in kyprizel's way, I would open IDAscope to scanning of arbitrary wildcard signatures, which I saw as a big chance. 
So here we go.  
  
### PKCS detection
As written before, the goal of this feature (and blog post) is detecting data fragments that might be involved in asymmetric crypto schemes such as public/private keys and certificate data. 
You might now it e.g. when using keys instead of passwords for SSH login.  
  
Here is a random private key (PEM format), easily generated on the shell with:
```
pnx@box:~/tmp/keys$ openssl genrsa -out privkey1024.pem 1024
```
resulting in:  
```
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQDYOt0RgdoIqgu1ncHeMkqeJNc6xFKfM9UOOl97fXLDtot5fped
/ELrR8GTcWKK1qotw3alZUfMs0q4t8vd7f4FbZUSv+Psg1tIyiXXbvnrbk5TTg+X
J0FqLkz7U8OxyMjR+HygML3/3Pq6oYZGkrLF0XkqHmQWq9EF0oF9BRbo4QIDAQAB
AoGATSRq/DT8aXzpIok+whvlHRh9pNynsV6XkzTmHbN6vzIf/l9YjieSZEg8WnLo
OiotmpgSex1wCSqp7M69r9aZegPcHIAN5c82/mItXiz4A07CBoxbpWc6pItUZ6eO
4RrFF3k0jn5edtFOlvaUaKtiQTo/rrFOKPj6hJAxlPNlehUCQQD+9PutMUznQ0O9
6k/mmH6EYRhAQSzDmfN3m9it3Txzd3mAyTIykLlf1HBVs1WdIKfWT167FJZlgoWF
TJWwFzjfAkEA2R1SUQxdDJYt3/13XkS2x1W/P6qMkAqIhy88YPWHJrdmLCyHkhlg
/PQYxZABxLHq3Yk886SHR8/vXzz4tVtWPwJAcH+9BeD5JBqEK6rWctPbD6KgRsn7
bJvj2GVGKQG0COcxD+i3Y6SEh4p/vvEQ1/Ju3JvNGxOsgUIklHsEmdzFVQJBAMAK
+JHqHrAQcrmK6LgAjbAZ/5WgFL8gIg15Ua3t38L2PDDcnnozap+0hejSbU3/leCp
ELnuER8LJQ+XzeIUzV8CQC8zvwYwGnYx2p3wK1iIDuhLki5tKS3CuZf869tKoNmD
DVoeWjSDK1MDcrtqsslhMOo1yt7ajocTXGhV0nmcNk0=
-----END RSA PRIVATE KEY-----
```

and the according public key  (PEM format), obtained via openssl, once again:  
```
pnx@box:~/tmp/keys$ openssl rsa -in privkey1024.pem -pubout -out pubkey1024.pem
```
producing:  
```
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDYOt0RgdoIqgu1ncHeMkqeJNc6
xFKfM9UOOl97fXLDtot5fped/ELrR8GTcWKK1qotw3alZUfMs0q4t8vd7f4FbZUS
v+Psg1tIyiXXbvnrbk5TTg+XJ0FqLkz7U8OxyMjR+HygML3/3Pq6oYZGkrLF0Xkq
HmQWq9EF0oF9BRbo4QIDAQAB
-----END PUBLIC KEY-----
```
  
One thing that might get one's attention is that both keys' base64 representations shown here start with "MI". 
The reason for this is that both keys are not encrypted and this way provide a hint to the underlying data structures, in this case [Distinguished Encoding Rules (DER)][microsoft der], specified in [X.690][itu x690].
That's the point where we can now dive into PKCS standards. :)  
  
First off, I won't go into details but focus on the things needed to implement a working detection of these data structures. 
For more information, there is a good [Phrack article][phrack issue52] from 1998 by Yggdrasil on PKCS #7.  
  
### Distinguished Encoding Rules (DER)
DER features a type system that can be used to encode elements of which keys and certificates consist. 
[RFC 3447][rfc3447] tells us how to use these elements to specify above private and public keys. 
I'll continue with the public key because it's shorter and suffices for the example.  
  
First, here is a hexdump of the base64-decoded public key above:   
```
0000000: 3081 9f30 0d06 092a 8648 86f7 0d01 0101  0..0...*.H......
0000010: 0500 0381 8d00 3081 8902 8181 00d8 3add  ......0.......:.
0000020: 1181 da08 aa0b b59d c1de 324a 9e24 d73a  ..........2J.$.:
0000030: c452 9f33 d50e 3a5f 7b7d 72c3 b68b 797e  .R.3..:_{}r...y~
0000040: 979d fc42 eb47 c193 7162 8ad6 aa2d c376  ...B.G..qb...-.v
0000050: a565 47cc b34a b8b7 cbdd edfe 056d 9512  .eG..J.......m..
0000060: bfe3 ec83 5b48 ca25 d76e f9eb 6e4e 534e  ....[H.%.n..nNSN
0000070: 0f97 2741 6a2e 4cfb 53c3 b1c8 c8d1 f87c  ..'Aj.L.S......|
0000080: a030 bdff dcfa baa1 8646 92b2 c5d1 792a  .0.......F....y*
0000090: 1e64 16ab d105 d281 7d05 16e8 e102 0301  .d......}.......
00000a0: 0001                                     ..
```
  
According to the RFC, an *RSAPublicKey* is a `SEQUENCE` of two `INTEGER`s (ASN.1 notation):  
```
RSAPublicKey ::= SEQUENCE {
    modulus           INTEGER,  -- n
    publicExponent    INTEGER   -- e
}
```
  
Looking at DER specifications we see that elements are usually specified as tag-length-value (TLV) tuples. 
A `SEQUENCE` is such an element and starting off with a fixed tag-byte of 0x30, which meets the 1st byte of the above hexdump.  
The 2nd byte is the length byte. DER length bytes have a special encoding depending on the length they shall express. 
If the target length is less than 128 bytes (and thus expressible in 7bits), the byte itself specifies the length. This covers bytes 0x00 - 0x7f.  
  
If the length is equal or above 128 bytes, bit 7 is set (thus setting the length byte to 0x80 or above) and bits 0-6 specify the number of bytes immediately following the length byte and indicating the actual length. 
In the above hexdump, we can see that the length byte is `0x81`. First, this indicates that the length is bigger than 128 bytes. 
Second, this indicates that the length is covered in one additional byte. This byte is the third byte of the dump, `0x91`, showing that there are 159 bytes in this `SEQUENCE`.  
  
The third part of the tuple is the actual value of the `SEQUENCE`.  
  
In this case it is beginning with another `SEQUENCE` (indicated by the 4th byte of the dump, `0x30`) of length `0x0d` (5th byte of the dump, 13 bytes) and value `06092a864886f70d0101010500`.  
  
The first byte of this inner `SEQUENCE` is a again a tag-bytes. `0x06` indicates an `OBJECT IDENTIFIER`. 
Its length is `0x09` bytes and the value is `0x2a864886f70d010101`, which translates to 1.2.840.113549.1.1.1 (*rsaEncryption*, read [this][microsoft der] for more details on decoding). 
The remaining 2 bytes of the sequence `0x0500` are a `NULL` element, which again is a TLV with tag `0x05` and length `0x00`, having no actual value.  
  
Now that we have handled the first part of the sequence, we can look forth, starting with the 19th byte and a new element. 
This time, the tag-byte `0x03` indicates a `BIT STRING` of length `0x8d` (141 bytes). 
The first value-byte in a `BIT STRING` signals how many bits in the `BIT_STRING` are unused, in our case `0x00`, i.e. zero bytes.  
  
The `BIT STRING` encapsulates another `SEQUENCE`, as the 23rd byte (hexdump position `0x16`, value `0x30`) tells us. 
The length is indicated by the next two bytes and set to `0x89` (137 bytes).  
  
The first element in this `SEQUENCE` is a new type that we haven't seen before, indicated by tag-byte `0x02`. 
This is an `INTEGER` element of length `0x81` (129 bytes). 
Remembering what we learned from the RFC about *RSAPublicKey*, this is now finally our *modulus* n! 
But we generated a 1024 bit (=128 byte) key via OpenSSL before, so why is this `INTEGER` of length 129 bytes? 
The explanation is simple: The leading byte of the `INTEGER` simply indicates the sign, in our case `0x00`, meaning it's a positive number.  
  
The second element of the `SEQUENCE` is another `INTEGER` (beginning at hexdump position `0x9d`, value `0x02`) the *publicExponent* of length `0x03`. 
It's value is `0x010001`, i.e. 65537, which is pretty standard for keys generated with OpenSSL.  
  
That's basically the complete walkthrough of this DER-encoded public key, just to wrap up, we have:  
```
SEQUENCE
  SEQUENCE
    OBJECT IDENTIFIER   <- rsaEncryption
    NULL
  BIT STRING
    SEQUENCE            <- RSAPublicKey
      INTEGER           <- modulus
      INTEGER           <- publicExponent
```
  
### Deriving signatures
Okay, as we have seen, the binary DER format with its TLV elements gives us multiple points we can attack with a signature. 
Back to Python, I have decided to attack the inner part of `SEQUENCE` to `INTEGER`, coming to the following binary signature for a 1024 bit public key:  
```
{VariablePattern("30 81 ? 02 81 81"): "PKCS: Public-Key (1024 bit)"}
```
Just to explain, VariablePattern is a simple type derived from str, just to indicate to IDAscope that we have a variable pattern of hexbytes that may contain wildcards such as `"?"`, feedable into the great  
```
idaapi.find_binary(start_ea, end_ea, pattern, radix=16, direction=SEARCH_DOWN)
```
in order to search in our IDB. Radix is set to 16 because our pattern consists of hexbytes and `SEARCH_DOWN` equals the value 1.  
  
Signatures for other bit lengths of public keys look much the same, just with adjusted TLV length fields. 
Private keys simply have another INTEGER (being zero) in front of the modulus, indicating that it is a 2-prime key:  
```
{VariablePattern("30 82 ? ? 02 01 00 02 81 81"): "PKCS: Private-Key (1024 bit)"}
```
  
### Scanning
However, if we look back to where we came from, we had base64-encoded structures and not the plain binary as shown in the hexdump.  
  
Scanning for those binary keys is straightforward. 
But to make those Base64 encoded once also searchable in IDA we need some extra-effort.  
  
I decided to temporarily map all potentially base64 encoded strings into the memory space of IDA, more precisely in a bonus segment.  
  
We can get all strings allowing base64-decoding easily by looping over the names, checking if they are ascii and performing decoding via try and error:  
```python
def getDecodedBase64Strings(self):
    decoded_names = []
    for name in idautils.Names():
        flags = idaapi.GetFlags(name[0])
        if not idaapi.isASCII(flags):
            continue
        ascii = idc.GetString(name[0])
        try:
            decoded = ascii.decode("base64")
            decoded_names.append(decoded)
        except:
            continue
    return decoded_names

```

I decided to create a new Segment and put all decoded strings there:  
```python
# any currently unused space will do
start_ea = 0x1000
# we need enough space to fill in all our base64-decoded strings.
end_ea = 0x1000 + sum(map(len, decoded_names))
# new segment shall have paragraph alignment and public access
idc.AddSeg(start_ea, end_ea, 0, True, idc.SA_REL_PARA, idc.SC_PUB)
offset = start_ea
for name in decoded_names:
    for byte in name:
        idc.PatchByte(offset, ord(byte))
        offset += 1

```
The decoded strings are now directly searchable with find_binary() as described before.  
  
In IDAscope I'm doing a bit more in order to extract the exact positions where the keys (base64 or not) sit in the binary.  
  
Currently supported are the following PKCS structures:  
 * unencrypted RSA public key 512bit - 8192bit
 * unencrypted RSA private key 512bit - 8192bit
 * X.509 Certificates


### Test Case

What would be a blog post without a demonstration. 
I took a Kelihos / HLUX sample
```
MD5: 14ff8123f58df1ec4a49afe70c84723b
```
which has proven quite good for testing lately.   
It has 5600+ functions (huge!) and features a lot of crypto signature hits:   

{% capture asset_link %}{% link /assets/20121101/hlux_pkcs.png %}{% endcapture %}
[![ida screenshot]({{ asset_link | absolute_url }} "Detection of two RSA 2048bit public keys in HLUX.")]({{ asset_link | absolute_url }})

Among those hits are two base64-encoded public keys that have been detected by IDAscope. 
You can see that those also start with "MI" and if you have read the whole post, you can deduce at this points that this has to be related to the `0x3081/0x3081` (`SEQUENCE`) with which the binary data is starting.  
  
### Other IDAscope Changes

There have been a lot refactoring steps in the codebase that are not visible to the outside. 
I will likely go on with that, with the goal in mind to move towards a point where you can use IDA+IDAscope without its GUI, basically by using an IDAscope API allowing for further automation purposes.  
  
A minor change has happened to FunctionInspection with another button in the toolbar: 

{% capture asset_link %}{% link /assets/20121101/fix_code.png %}{% endcapture %}
[![ida toolbar]({{ asset_link | absolute_url }} "There are now two "fix code options")]({{ asset_link | absolute_url }})

The "Fix unknown code to functions" option has been split up. 
There is now one button (plain plus sign) for only converting those undefined code regions that start with a valid function prologue and a second button (double plus sign) that will try to fix all code to functions.  
  
Reason for the split-up is that converting all code can mess up the number of functions pretty bad while looking for function prologues produces only a very limited number of hits.  
  
### Next Steps

Right after telling [Alex][twitter alex] about the extended signature detection with wildcards, he asked me if YARA support in IDAscope could be an option. 
I'm still thinking about it but I definitely see the advantages as it would allow the easy reuse of existing signature databases. 
So this might come to the agenda.  
  
[Marco Ramilli][ramilli blog] blogged about IDAscope some days ago and suggested to build a more extended "behaviour analysis" upon the existing tagging feature. 
We had already experimented with this "static sandbox" idea before but the code is yet too experimental to find its way into the production branch. 
So this is also a potential feature for the future.  
  
At hack.lu and in the [slides](/assets/20121027/hacklu_idascope_plohmann.pdf) I showed an idea of improving the visualization of functional relationship. 
This is also something I want to work on in the near future as I believe that this would really aid the reversing workflow by providing more overview.  
  
So stay tuned for the future development and as always, write us mails to  

**idascope &lt;at&gt; pnx &lt;dot&gt; tf**

if you want to give us feedback or submit ideas for development.

*[link to original post on blogspot][blogspot post].*

[ida contest]: http://www.hex-rays.com/contests/index.shtml
[hacklu 2012]: http://2012.hack.lu/
[kyprizel getkeys]: http://www.kyprizel.net/work/ida/getkeys.py
[trapkit sslfinder]: http://www.trapkit.de/research/sslkeyfinder/
[microsoft der]: http://msdn.microsoft.com/en-us/library/windows/desktop/bb648640%28v=vs.85%29.aspx
[itu x690]: http://www.itu.int/ITU-T/studygroups/com17/languages/X.690-0207.pdf
[phrack issue52]: http://www.phrack.org/issues.html?issue=52&amp;id=15&amp;mode=txt
[rfc3447]: http://tools.ietf.org/html/rfc3447#appendix-A.1
[twitter alex]: https://twitter.com/nullandnull
[ramilli blog]: http://marcoramilli.blogspot.de/2012/10/h-folks-today-id-like-to-introduce.html

[blogspot post]: https://pnx-tf.blogspot.com/2012/11/pkcs-detection.html