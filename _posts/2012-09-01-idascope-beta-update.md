---
layout:             post
title:              "IDAscope Beta Update"
author:             Daniel Plohmann
date:               2012-09-01 01:00:00 +0100
last_modified_at:   2012-09-01 01:00:00 +0100
categories:         blog
tags:               idascope
---

Nothing much to blog about. Therefore, only a short update on IDAscope's progress. 
I just pushed out a second beta version to the people that expressed interest in testing it. 
If you are interested, too, this [announcement]({% post_url 2012-08-20-idascope-beta %}) is still valid. ;) 
 
Here is a list of changes/fixes included with the second beta: 
 
Function Inspection:
 * Added functionality to create functions from unrecognized code. This function will first try to find and convert function prologues (push ebp; mov ebp, esp) and then convert the remaining undefined code.  
 * Added functionality to identify and rename potential wrappers (small functions with exactly one call referencing an API function). Thanks to Branko Spasojevic for this contribution. 
 
WinAPI:
 * Fixed path resolution for html files, should work on non-Windows operating systems now, too. Thanks to [Sascha Rommelfangen][twitter rommelfangen] for fixing this, I only have IDA versions on Windows available so I could hardly debug this.  
 * Included a back/forward button to allow easier browsing of visited articles. 
 
Crypto Identification:
 * Adjusted default parameters to a tighter set, resulting in less false positives on startup.  
 * Added some crypto signatures (CRC32 generator, TEA/XTEA/XXTEA). 
 
The public release will be in two weeks from now.

*[link to original post on blogspot][blogspot post].*

[twitter rommelfangen]: https://twitter.com/rommelfs
[blogspot post]: https://pnx-tf.blogspot.com/2012/09/idascope-beta-update.html