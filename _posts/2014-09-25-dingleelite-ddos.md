---
layout:             post
title:              DingleElite DDoS Bot (WOPBOT)
author:             Daniel Plohmann
date:               2014-09-25 01:00:00 +0100
last_modified_at:   2014-09-25 01:00:00 +0100
categories:         blog
tags:               bytetlas, malware
---

re: [http://www.kernelmode.info/forum/viewtopic.php?f=16&t=3505][kernelmode post]  
sha256: `73b0d95541c84965fa42c3e257bb349957b3be626dec9d55efcc6ebcba6fa489`  
malware family: DDoS Bot used by DingleElite (WOPBOT, according to [Emanuele Gentili][twitter emgent])

context found here:
```
"I am a security researcher and found a bot network of infected devices used to perform the DDoS
attacks the twitter account thats linked with the botnet is https://twitter.com/TheDingleElite
the command and control of this botnet can be watched by using a telnet client and connecting
to 89.238.xxx.xxx on tcp port 5 if you need to be made aware of any more information please
contact me directly I will privatly disclose the rest of the CnC IP to anyone who is interested."
```

### quick static analysis: 

hardcoded C&C: `89.238.150.154:5`  
CloudFlare IP: `108.162.197.26` (used for deriving the bots own MAC via route lookup?)  
C&C protocol: single line exchange via telnet  

### Commands / Features:

```
CMD:      PING
PARAMS:   -
RESPONSE: "PONG!" GETLOCALIP | - | "My IP: <local_ip>"

CMD:      SCANNER
PARAMS:   <MODE>
RESPONSE: "SCANNER ON | OFF" if num_args != 1, spawned thread responds otherwise? 

CMD:      HOLD
PARAMS:    <IP> <PORT> <SECONDS>
RESPONSE: "HOLD Flooding <IP>:<PORT> for <SECONDS> seconds." 

CMD:      JUNK
PARAMS:   <IP> <PORT> <SECONDS>
RESPONSE: "JUNK Flooding <IP>:<PORT> for <SECONDS> seconds." or error messages 

CMD:      UDP
PARAMS:   <IP> <PORT> <SECONDS> <RAW/DGRAM> <PKT_SIZE> <THREADS>
RESPONSE: "UDP Flooding <IP>:<PORT> for <SECONDS> seconds." or error messages 

CMD:      TCP
PARAMS:   <TARGETS,> <PORT> <SECONDS> <?> <TCP_FLAGS,> <PKT_SIZE> <PKT_BURST>
RESPONSE: "TCP Flooding <IP>:<PORT> for <SECONDS> seconds." or error messages 

CMD:      KILLATTK
PARAMS:   -
RESPONSE: "Killed <NUMBER_OF_ATTK_THREADS>." or "None Killed." 

CMD:      LOLNOGTFO
PARAMS:   -
RESPONSE: None (exits bot process) 
```

#### UDP flood

payload characteristics: PKT_SIZE * RANDOM(UPPER_CHARS) 

#### TCP flood

TCP_FLAGS: (all,syn,rst,fin,ack,psh) (<- choose your very own comma separated list)  
PKT_BURST: packets sent without a pause (for checking if SECONDS of attack is reached)  


#### related sources (stringdumps, ...) for the same malware family: 

Aug 20th, 2014 [Pastebin][pastebin a]  
Aug 9th, 2014 [Pastebin][pastebin b] (hints to potentially old C&C server: `89.248.172.14:9` | `192.99.200.69:57`)  
Mar 7th, 2014 [Pastebin][pastebin c] (hints to potentially old C&C server: `192.99.200.69:57`)  
Jan 18th, 2014 Malwr (hints to potentially old C&C server: `142.4.215.135`)  

#### All hashes:

sha256: `73b0d95541c84965fa42c3e257bb349957b3be626dec9d55efcc6ebcba6fa489` (C&C: `89.238.150.154:5`)  
sha256: `2d3e0be24ef668b85ed48e81ebb50dce50612fb8dce96879f80306701bc41614` (C&C: `162.253.66.76:53`)  
sha256: `ae3b4f296957ee0a208003569647f04e585775be1f3992921af996b320cf520b` (C&C: `89.238.150.154:5`)  


*[link to original post on blogspot][blogspot post].*

[pastebin a]: http://pastebin.com/frqVZR3n
[pastebin b]: http://pastebin.com/hnu7wmva
[pastebin c]: http://pastebin.com/xa87Gh7q
[twitter dingle]: https://twitter.com/TheDingleElite
[twitter emgent]: https://twitter.com/emgent/status/515200088067813376
[kernelmode post]: http://www.kernelmode.info/forum/viewtopic.php?f=16&t=3505 

[blogspot post]: http://byte-atlas.blogspot.com/2014/09/dingleelite-ddos-bot-wopbot.html