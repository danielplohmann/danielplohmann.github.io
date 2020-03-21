---
layout:             post
title:              "WinAPI Browsing"
author:             Daniel Plohmann
date:               2012-07-25 01:00:00 +0100
last_modified_at:   2012-07-25 01:00:00 +0100
categories:         blog
tags:               idascope
---

A week has passed since my last blog post, so it's time to give an update on the current status of development for IDAscope. 
The title mentions WinAPI browsing, which I am introducing later in the post. 
First I want to give a follow up on the need for data flow analysis I explained in the last post.

## IDAscope + Data flow analysis?

In my last post, I mentioned that one of the next steps would be data flow analysis of parameters to get a better interpretation of API calls. 
While I am still pursuing this, I realized that it will come not in as easy as I hoped. 
At least when I want to do it properly. While having studied CS and not having tried to circumvent lectures on theory, I went back to basics and started [reading on data flow analysis][dataflow book amazon]. 
Soon, I realized that I have rusted already a little bit, doing more practical work than I probably should have (at least for being in an academic environment). 
However, the first two chapters were pretty illuminating and helped me to grasp the message of [Rolf Rolles' keynote at REcon][rolf keynote recon] better.

I took the following lessons from my peek into this book:
 * There are well-defined, nice mathematical frameworks to perform data flow analysis. Efficient algorithms are available in pseudo code, so most of the work has been done already.
 * Intraprocedural data flow analysis is enough for what we need here. Having Def/Use-chains would be great.
 * Implementing this generically will take a lot of time. ;)

So for now I feel that it has more value to implement other functionality/ideas for easing the reverse engineering workflow first than putting together a full data flow framework. 
I still have this on the agenda but I will probably come up with a very simplified version (say: hack) that will at least show reference in a way IDA does it already (incl. clickable reference):

[![simple dataflow example]({% link /assets/20120725/simple_data_flow.png %} "A simple dataflow example")]({% link /assets/20120725/simple_data_flow.png %})

However, I still see the potential of data flow analysis and will pick this up later on, I guess.  
If you have a hint on how to integrate data flow analysis at this point without introducing much external dependencies, let me know.

## IDAscope: WinAPI browsing

Reading my last blog again, it turns out the "long-term targeted functionality to have MSDN browsing embedded in IDAscope" was a lot easier to do than initially assumed.

The starting point to this was given to me by Alex. As you might know, there comes a very handy information database along with a [Windows SDK][windows sdk] installation. 
In its program files folder, there is a subfolder "help/&lt;version number&gt;", containing roundabout 250 *.hxs files, which are basically "Microsoft Help Compiled Storage" files. 
Treating them with 7zip results in about 130.000 files, consuming 1.4 GB space. Most of them are simple HTML files, probably similar to the MSDN available online.  
What is great about those files, is the indexing/keyword scheme used by Microsoft, explained <a href="" target="_blank">here</a> and [here][windows sdk explanation].  
Just to show you what I am talking about, example "createfile.htm":
```
[...]
<MSHelp:Keyword Index="F" Term="CreateFile"/>
<MSHelp:Keyword Index="F" Term="CreateFileA"/>
<MSHelp:Keyword Index="F" Term="CreateFileW"/>
<MSHelp:Keyword Index="F" Term="0"/>
<MSHelp:Keyword Index="F" Term="FILE_SHARE_DELETE"/>
<MSHelp:Keyword Index="F" Term="FILE_SHARE_READ"/>
<MSHelp:Keyword Index="F" Term="FILE_SHARE_WRITE"/>
<MSHelp:Keyword Index="F" Term="CREATE_ALWAYS"/>
[...]
```
Parsing this information was trivial, leaving us with a dictionary of 110.000 keywords (API names, structures, symbolic constants, parameter names, ...) pointing to the corresponding files.  

Now we just need a way to visualize the data/html. I decided to use QtGui's QTextBrowser instead of QWebView, which would have been basically full WebKit. 
Mainly because it requires a full installation of Qt instead of only PySide as shipped with IDA Pro. 
Furthermore, QTextBrowser fully suffices our needs as it is able to render basic HTML of which the Windows SDK API documentation is comprised anyway. 

The result looks like this:

[![WinAPI Browsing](/assets/20120725/winapi_browsing.png "WinAPI Browsing")](/assets/20120725/winapi_browsing.png)

The links you see in the picture there are all functional, which is really nice to get some context around the API you are currently reading about. And because of course we want to be hip, I used QCompleter to give search suggestions based on the keywords:  

[![QCompleter](/assets/20120725/qcomplete.png "QCompleter")](/assets/20120725/qcomplete.png)

Clicking on the API names in the first picture shown above in the data flow section will also bring up the respective API page, changing window focus to the browser.  
As possible future features for this, I think of extending the context menu (right click) of the IDA View by a "search in WinAPI" in order to ease use and also cover names that are not targeted by the set of semantic definitions. 
From my own usage experience, having a "back" button in the browser will also be essential, so I will add that soon, too.

A downside of using Windows SDK as exclusive data source is that information about ntdll and CRT functions is not included. 
Maybe I will add a switch for "online" mode, so you can still surf MSDN from within the window. But this has lower priority right now. 

So not much technical stuff in today's post but I am positive that we can change that in the next one. I hope I have implemented the data flow "hack" by then. 
But the next main goal is to bring the subroutine exploration explained by Alex in his [blog post][alex blog post] into IDAscope. 
Based on the structural information generated through his scripts, I feel that there is more to gain from.

*[link to original post on blogspot][blogspot post].*

[alex blog post]: http://hooked-on-mnemonics.blogspot.de/2012/07/renaming-subroutine-blocks-and.html
[windows sdk explanation]: http://blogs.msdn.com/b/windowssdk/archive/2008/08/27/how-it-works-windows-sdk-documentation-part-1.aspx
[windows sdk]: http://www.microsoft.com/en-us/download/details.aspx?id=8279
[dataflow book amazon]: http://www.amazon.com/Data-Flow-Analysis-Theory-Practice/dp/0849328802
[rolf keynote recon]: http://recon.cx/2012/schedule/events/235.en.html
[blogspot post]: https://pnx-tf.blogspot.com/2012/07/idascope-update-winapi-browsing.html