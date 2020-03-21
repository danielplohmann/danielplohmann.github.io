---
layout:             post
title:              "Small IDAscope update"
author:             Daniel Plohmann
date:               2013-06-05 02:00:00 +0100
last_modified_at:   2013-06-05 02:00:00 +0100
categories:         blog
tags:               idascope
---

I should probably visit more conferences. 
When heading out, it's always nice to get some fresh input from people. 
I'm currently at CyCon (Tallinn, Estonia) where I'll give a talk about the malware analysis workflow we are using at Fraunhofer FKIE. 
I'll add the corresponding paper to [pnx.tf][web pnx] as soon as I get the approval.  
  
The motivation for the latest little addition to IDAscope has to be credited to [Hugo Teso][twitter hteso], whom I met yesterday. 
I'm really looking forward to his Friday talk on aviation security, which will be related to the [one he gave at HITB][hitb teso] this year.  
  
### Semantics Profiles

The latest commit to IDAscope contains an extension to the "Function Inspection" part. 
It is now possible to quickly switch between different profiles for semantic definitions, which should open up this part of IDAscope for better usage in analysing ring0 stuff as well as POSIX or even other platforms.  
  
[![idascope profiles](/assets/20130605/idascope_profiles.png "Semantic Profiles")](/assets/20130605/idascope_profiles.png)
  
IDAscope will automatically load all semantics profiles it finds in the newly created subfolder:  
```
\idascope\data\semantics
```
Currently there are two profiles: First, the already known win-ring3 profile, which resembles the default that you know from "Function Inspection". 
Second, a placeholder file for POSIX. Only placeholder, because I did not take the time to add any specifications for it yet.  
Actually, I'd love to see contributions from volunteers who have been actively using this feature or had told me were looking forward to this extension. :) 
Otherwise I might add new profiles myself if I have a good day or something.  
  
The specification for a profile looks like this and should be easy to extend (JSON):  
```
{
    "author": "pnX",
    "creation_date": "05.06.2013",
    "name": "posix",
    "reference": "http://pnx-tf.blogspot.com/2013/06/small-idascope-update.html",
    "comment": "template for POSIX semantics",
    "renaming_seperator": "_",
    "default_neutral_color": "0xCCCCCC",
    "default_base_color": "0xB3DfFF",
    "default_highlight_color": "0x33A7FF",
    "semantic_groups": [{
        "tag": "grouptag0",
        "name": "group0",
        "base_color": "0xB3B3FF",
        "highlight_color": "0x333377"
    }, {
        "tag": "grouptag1",
        "name": "group1",
        "base_color": "0xB3DFFF",
        "highlight_color": "0x33A7FF"
    }],
    "semantic_definitions": [{
        "tag": "socket",
        "name": "socket",
        "group": "group0",
        "api_names": ["socket", "open", "close", "connect", "listen", "bind"]
    }]
}
```
  
### Future

Regarding future updates on IDAscope, I obviously took almost half a year off from developing until now. 
I hope that I will be able to spend more time on improving IDAscope in the near future.  
It's especially sad that I was not able to finish the interactive call-graph feature yet that I had previewed in one of the previous blog posts. 
I am still inclined to finish this, just to give the time I already spent on it more value.  
In parallel I will likely also start refactoring the storage of the internal analysis results. 
I have something in mind that could be done with it but it's not yet publishable, so I'll leave it with that.  
  
If you have other ideas or feature requests, please let me know.

*[link to original post on blogspot][blogspot post].*

[web pnx]: "http://pnx.tf/
[twitter hteso]: https://twitter.com/hteso
[hitb teso]: http://conference.hitb.org/hitbsecconf2013ams/hugo-teso/

[blogspot post]: https://pnx-tf.blogspot.com/2013/06/small-idascope-update.html