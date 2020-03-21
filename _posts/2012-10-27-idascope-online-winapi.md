---
layout:             post
title:              "Online WinAPI & hack.lu slides"
author:             Daniel Plohmann
date:               2012-10-27 01:00:00 +0100
last_modified_at:   2012-10-27 01:00:00 +0100
categories:         blog
tags:               idascope
---

This is just a short update, in order to capture some of the things that otherwise would have been just noted on my [twitter][twitter pnx]. 
If you only follow the blog, sorry to serve this a bit late but I just didn't find it worth blogging about 3-4 lines and a little modification of an already existing feature.  
  
### Online WinAPI lookups

Since October 16th, 2012, the WinAPI lookup widget of IDAscope also supports online lookups.  
  
Why is this interesting?  
Well, as some of you might have already experienced, the offline mode didn't capture all of MSDN, mainly CRT functions and Kernel functions were missing. 
I'm quite happy that they are covered as well now.  
But in my opinion more importantly, the online lookup cancels the need to download that huge data blob from the Windows SDK and makes IDAscope usable without any prerequisites.   
  
Online mode is enabled by default (via `./config.json`):  
```
"winapi": {
    "search_hotkey": "ctrl+y",
    "load_keyword_database": true,
    "online_enabled": true
}
```
As always, the update can be found in the [repository][idascope repo].  

### hack.lu (slides + new feature)
On a different note, this week I've been to hack.lu in Luxembourg. 
It was a great conference with a lot of nice people and many interesting presentations.  
  
On the second day, I took my chance and gave a lightning talk on IDAscope. 
It basically gave a walkthrough of all the currently implemented features as well as some on plans I have for the future. 
The slides are contain mostly screenshots in order to bring you as close to a demo as possible and can be found [here](/assets/20121027/hacklu_idascope_plohmann.pdf).   
  
Furthermore, during the conference I took the time to implement another addition to the crypto widget: [Public Key Cryptography Standards (PKCS)][pkcs detection] detection.  
While having a lot of signatures integrated already, IDAscope did not support the detection of PKCS elements, such as public/private keys and certificates until now. 
However, I believe this is useful, as some of the modern botnets are using asymmetric crypto in order to verify authenticity of commands and updates. 
Moreover, it might be interesting to have this feature available when analyzing memory dumps of software where you assume the presence of such keys and certificates.  
The detection is already integrated in my local version and I want to add the functionality to directly dump those elements from a binary to disk. 
When I've tested it some more, I'll push the updates to the repo. Of course there will be another more technical blog post in the next days to cover this new addition in detail.  
Thanks to mortis for pointing me to the idea for this feature. ;)

*[link to original post on blogspot][blogspot post].*

[bitbucket zip]: https://bitbucket.org/daniel_plohmann/simplifire.idascope/downloads/IDAscope_v_1_0.zip
[twitter pnx]: https://twitter.com/push_pnx
[idascope repo]: http://idascope.pnx.tf/
[pkcs detection]: http://www.rsa.com/rsalabs/node.asp?id=2124
[blogspot post]: https://pnx-tf.blogspot.com/2012/10/online-winapi-hacklu-slides.html