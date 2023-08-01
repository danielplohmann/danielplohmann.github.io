---
layout:             post
title:              "Knowledge Fragment: Hardening Win10 x64 on VirtualBox for Malware Analysis"
author:             Daniel Plohmann
date:               2023-08-01 08:00:00 +0100
last_modified_at:   2023-08-01 08:05:00 +0100
categories:         blog
tags:               [bytetlas, "knowledge fragment", virtualization, hardening]
---

Since I started into running more and more issues being able to debug and unpack samples effectively on my trusty old Windows 7 x64 reference system, it was time to finally move to Windows 10/11.  
About 6 years ago, I wrote an [Win7 Hardening Guide][win7 hardening] that outlined in details my experience with using the [antivmdetection][antivmdetection] approach by [nsmfoo][twitter nsmfoo].

In this (kind of) update to my previous blog post, I decided to run with the same approach since it carried very well all this time, hoping it would be seamlessly transferrable to Win10.  

**TL;DR: It did!**

That means you can essentially just strictly follow the instructions given in the repo at [antivmdetection][antivmdetection] and get a great hardening result.  
In the following, I will just list a few tweaks that I had to make in order to have a truely green PAfish result:

{% capture asset_link %}{% link /assets/20230801/pafish_result.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "PAfish result in the Win10 vbox")]({{ asset_link | absolute_url }})

### Outside the VM

Just following all the steps worked fine for me, I still have ACPI table dump from a legacy board sized less than 64KB I was able to reuse and overwrite my VirtualBox parameters / ExtraData section with.

### Inside the VM

Lowering UAC and running powershell as administrator was one thing, I just recommend dropping the execution policy for powershell scripts to `Unrestricted` on top of that.  
So simply run

```powershell
Set-ExecutionPolicy Unrestricted
```

before running the powershell script that you previously generated using `antivmdetect.py`.

For good measure, I also started `regedit.exe` as Administrator and searched across the all Hives to really really purge every last key and value containing `vbox`, which I had to do another maybe 10 locations.

In the end, this led to the result shown in the screenshot above.

### Dependencies

In the last blog post, I recommended installing all MSVC runtimes and .NET.  
Same this time, but I found a really convenient collection that simplifies MSVCRT part: [Visual C++ Redistributable Runtimes All-in-One][msvcrt allinone].  
With this, you can apply all individual runtime packages with unattended install by simply running the accompanying batch file.

For .NET, you want to check for the latest version [here][ms dotnet] and install it, I went with 7.0 since it's the current stable release.

### Summary

I hope this short summary in combination with my previous blog post may help you on your way to set up an almost undetectable VirtualBox VM for malware analysis and sandboxing.  
Once again I'd like to express my gratitude to [nsmfoo][twitter nsmfoo] for creating the tooling [antivmdetection][antivmdetection].  
This time, the whole procedure took me maybe one hour, and that would have been significantly more time without it.

Just like last time, I'd like to send you off with a music recommendation, which is `WARGASM UK`'s latest single `Do It So Good`.

**Epilepsy Warning!**


<iframe width="560" height="315" src="https://www.youtube.com/embed/GEyBFg3E_dI" title="Do It So Good" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>



[win7 hardening]: https://danielplohmann.github.io/blog/2017/02/05/kf-hardening-win7.html
[twitter nsmfoo]: https://twitter.com/nsmfoo
[antivmdetection]: https://github.com/nsmfoo/antivmdetection
[msvcrt allinone]: https://www.techpowerup.com/download/visual-c-redistributable-runtime-package-all-in-one/
[ms dotnet]: https://dotnet.microsoft.com/en-us/download/dotnet