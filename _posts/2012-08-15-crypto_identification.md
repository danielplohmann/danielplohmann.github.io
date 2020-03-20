---
layout:             post
title:              "IDAscope update: Crypto Identification"
author:             Daniel Plohmann
date:               2012-08-15 01:00:00 +0100
last_modified_at:   2012-08-15 01:00:00 +0100
categories:         blog
tags:               idascope
---

After being quiet for almost three weeks, today I want to share with you my latest additions to IDAscope. 
 
Focus of this post will be a new widget that I call *Crypto Identification*. 
Now you may say "oh no, yet another crypto detection tool?" Well, yes, but before you stop reading let me introduce you to an approach you might find useful. 
 
### Heuristics-based crypto detection by code properties

About 2 years ago, during literature research on network protocol reverse engineering, I came across an interesting paper called ["Dispatcher: Enabling Active Botnet Infiltration using Automatic Protocol Reverse-Engineering"][dispatcher paper] by Juan Caballero et al. 
Besides the description of an approach on how to identify and dissect message buffers into protocol fields, it contains a section on automated detection of cryptographic routines ("Detecting Encoding Functions", p. 10).  
The main idea is pretty straight forward: 
 * Evaluate the ratio of arithmetic/logic instructions related to all instructions in a function. *Assumption*: Cryptographic functions usually consist mainly of arithmetic/logic instructions, thus they should have a higher ratio.
 * If the function has a size of 20 or more instructions, flag the function as encoding function.

While the approach described in the paper is applied to dynamically achieved instruction traces, there is no reason why not to employ it in static code analysis. So my goal for today is to show you how to make "academic things" practically usable. ;) 
 
I use the following set of arithmetic/logic instructions, please tell me if I missed something: 
```
[
    "add", "and", "or", "adc", "sbb", "and", 
    "sub", "xor", "inc", "dec", "daa", "aaa", 
    "das", "aas", "imul", "aam", "aad", "salc", 
    "not", "neg", "test", "sar", "cdq"
]
```

The following screenshot shows the widget in action: 

[![crypto identification](/assets/20120815/crypto_identification.png "Crypto Identification")](/assets/20120815/crypto_identification.png)

The functionality I just described is located in the upper part of the widget. There are three double-sliders that can be used to adjust the following parameters: 
 * **Range of Arithmetic/Logic Rating:** The above mentioned ratio of arithmetic/logic instruction to total instructions, but calculated on basic block level instead of function level.
 * **Considered Basic Block Size:** Only blocks having a size within the boundaries are taken into concern.
 * **Allowed Calls in Function:** Number of calls allowed from the function containing the analyzed basic block to any other code location. This is based on the assumption that most actual cryptographic/compression functions are "leafs" in the overall program flow graph, not having any child functions.

With these filter functions, we can greatly narrow down the number of suspicious basic blocks to those really containing interesting crypto or compression algorithms. 
Once the initial scanning has been performed (sample with 700 functions, less than one second), the sliders update the visualization in real-time. Qt only chokes when viewing all 9500 basic blocks at once, but that's not what you want anyway. 
 
The two checkboxes give further ways to refine the search: 
 * **Exclude zeroing Instructions:** This can be used to reduce false positives that may distort the rating. You will often find instructions like `xor eax, eax` or `sbb eax, eax` being used to clear register contents. However, they would  normally be included in the calculation of the rating because XOR is in the set of arithmetic/logic instructions.
 * **Group Results by Functions:** This is just an alternative display method, giving a better overview on how many suspicious blocks are contained in the same functions.

Here is a use case for this widget: When I am trying to identify cryptography in malware samples, I often have problems finding compact but frequently used crypto algorithms such as RC4 that usually do not carry constants with them (which would allow to spot them by simple signature matching). 
In the above screenshot (from a current Citadel sample with 724 functions) you can see that the candidate blocks have been reduced to 23 out of 9526 basic blocks. 
The filters are set to show only blocks with a rating of above 30%, with a size of 10 or more instructions and 1 or 0 call instructions. 
23 blocks is a number small enough for me to look at in just a few minutes, identifying the relevant parts in a very short amount of time. 
 
Among the 23 blocks is the following one: 

[![citadel rc4](/assets/20120815/citadel.png "Citadel's modified RC4 stream cipher")](/assets/20120815/citadel.png)

containing the modified stream cipher that is used in Citadel. 
In addition to the normal XOR/substitutions, Citadel also XORs against the characters of a static hash contained in the binary, which is considered one of the "advancements" from its predecessor Zeus 2. 
While this may be a weak example because the block is easily identified by searching for exactly this hash, you probably get the idea on how to use the widget. 
The heuristic also successfully identifies all the other crypto parts in the sample like the AES and CRC32 algorithms. 
 
If you wonder about how you get double-sliders in Qt (because it is not a standard widget): The idea and code of this widget called "BoundsEditor" is adapted from Enthought's [TraitsUI][enthought traitsui], which luckily is open-source software. I took the code and reduced it back to a standard Qt widget, having a great and compact control element to adjust my parameters. 
 
### Signature-based crypto identification

The second part of the widget does what you might have expected in the first place. It simply uses a set of constants in order to find well-known cryptographic algorithms. 
It's basically inspired by tools like the IDA findcrypt plugin or the KANAL plugin for PEiD. It does the same job, except being directly coupled to IDA and allowing to instantly jump to the code locations referencing the identified constants. 
The following screenshot (from an old but gold conficker sample) shows both types of matches: 

[![conficker constants](/assets/20120815/conficker.png "Crypto constants found in Conficker")](/assets/20120815/conficker.png)

The colors mean: 
 * **<span style="color: #666666;">[black] referenced by:</span>** constant somewhere (e.g. data section), referenced by code.
 * **<span style="color: #cc0000;">[red] referenced by</span>**: constant immediately used in code, just as shown in the basic block to the left.

The currently supported algorithms are (with ingredients from [Ilfak Guilfanov's][twitter ilfak] [findcrypt][findcrypt], [Felix Gröbert's][twitter felix] [kerckhoff's][kerckhoff], a crypto detection implementation by [Felix Matenaar][twitter pleed] from his Bachelor thesis, and some of my own adaptions): 
 * ADLER 32
 * AES
 * Blowfish
 * Camellia
 * CAST256
 * CAST
 * CRC32
 * DES
 * GOST
 * HAVAL
 * IDEA
 * MARS
 * MD2, MD5, MD6
 * MD5MAC
 * PKCS (various initialization values)
 * RawDES
 * RC2, RC5
 * Rijndael
 * Ripe-MD160
 * SAFER
 * SHA224
 * SHA256
 * SHA384
 * SHA512
 * SHARK
 * SKIPJACK
 * SQUARE
 * Serpent
 * Square/SHARK
 * TIGER
 * Twofish
 * WAKE
 * Whirlpool
 * Zlib

The only thing missing right now is renaming / tagging those functions based on the signatures, maybe I will implement that, too. 

### Other changes to IDAscope

To conclude this post, I want to briefly discuss some more changes I did to IDAscope since the last post: 
 * In my [last post]({% post_url 2012-07-25-idascope-winapi-browsing %}), I mentioned that the WinAPI widget only worked against the offline data from the Windows SDK. This is no longer the case, as it now supports doing online lookups (controllable by a checkbox) in the case it does not find local information. This is great because by that, the missing documentation of CRT and NTDLL functions are now also covered. Parsing of the MSDN webpage can be optimized but works for now.
 * Hotkey support for widgets. As an example, `[CTRL+Y]` will now look up the currently highlighted identifier (in IDA View) in the WinAPI widget and change focus to this widget.
 * More changes under the hood, data structures, refactoring, etc. I feel that the code is better organized and easier to understand now.
 * Experimental code for visualizing the function relationship starting by Thread start addresses (cf. [Alex' last blog post][blog alex]).

Next to come is the integration of Alex' latest scripts into widgets. 

*[link to original post on blogspot][blogspot post].*

[dispatcher paper]: http://bitblaze.cs.berkeley.edu/papers/dispatcher_ccs09.pdf
[enthought traitsui]: https://github.com/enthought/traitsui
[twitter ilfak]: http://twitter.com/ilfak
[findcrypt]: http://www.hexblog.com/?p=28
[twitter felix]: http://twitter.com/fel1x
[kerckhoff]: http://code.google.com/p/kerckhoffs/
[twitter pleed]: http://twitter.com/pleed_
[blog alex]: http://hooked-on-mnemonics.blogspot.de/2012/08/ida-thread-analysis-sript.html

[blogspot post]: https://pnx-tf.blogspot.com/2012/08/idascope-update-crypto-identification.html