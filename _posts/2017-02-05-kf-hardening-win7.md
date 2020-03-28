---
layout:             post
title:              "Knowledge Fragment: Hardening Win7 x64 on VirtualBox for Malware Analysis"
author:             Daniel Plohmann
date:               2017-02-05 01:00:00 +0100
last_modified_at:   2017-02-05 01:00:00 +0100
categories:         blog
tags:               bytetlas, knowledge fragment, virtualization, hardening
---

After some abstinence, I thought it might be a good idea to write something again. The perfect occasion came yesterday when I decided to build myself a new VM base image to be used for future malware analysis.

In that sense, this post is not immediately a tutorial for setting up a hardened virtual machine as there are so many other great resources for this already (see [VM Creation](#vmcreation)). Maybe there is a good hint or two for you readers in here but it's mostly a write-up driven by my personal experience.
The main idea of this post is to outline some pitfalls I ran into yesterday, when relying on said resources. To have others avoid the same mistakes, I hope this post will fulfil its putpose.
In total I spent about 5 hours, 2 hours for setup and probably another 3 hours for testing but more about that later. This could have easily been only one hour or less if I knew everything I'll write down here beforehand. So here you go. :)

The remainder of this post is structured as follows:
1. [Goals](#goals)
2. [Preparation](#preparation)
3. [VM Creation](#vmcreation)
4. [Windows Installation](#windows)
5. [Post Installation Hardening and Configuration](#postinstall)
6. [VirtualBox Hypervisor Detectability (update: solved!)](#hypervisor)
7. [Summary](#summary)

### Goals<a name="goals" />

Before starting out, it's good to know and plan where we are heading.

**My Needs:** I'm mostly interested in doing some rapid unpacking/dumping to feed my static analysis toolchain and then occasional do some debugging of malware to speed up my reasoning of selected code areas.
For this, I wanted a new base VM image that is able to run as much malware natively as possible, without me having to worry about Anti-Analysis methods.
Potentially, I want to deploy this image later as well for automation.
I don't aim for a perfect solution (perfection is the enemy of efficiency) but a reasonably good one.

**OS choice**: Windows 7 is still the [most popular OS][netmarketshare windows] it seems, but since 64bit malware is getting more popular, we should take that into concern as well. So I go with Win7 x64 SP1 as base operating system.

**Why not Win10**: Well, I want a convenient way to disable ASLR and NX globbaly to allow my malware&exploits to flourish. Since I don't know if it's as easy in Win10 as it is in Win7, I stick with what I know for now.

### Preparation<a name="preparation" />

In the back of my head, I had some resources I wanted to use whenever I would have to create a new base VM, namely:

1) [VMCloak][vmcloak] by [skier_t][twitter skier]
2) [VBoxHardenedLoader][vboxhardenedloader] by [hfiref0x][twitter hfirefox] (and [kernelmode thread][kernelmode link] as installation guide)
3) [antivmdetection][antivmdetection] by [nsmfoo][twitter nsmfoo] (and blog posts [1][blog 1 nsmfoo] [2][blog 2 nsmfoo] [3][blog 3 nsmfoo] [4][blog 4 nsmfoo] [5][blog 5 nsmfoo])

Since I wanted to understand all the steps, I took VMCloak only for theoretical background. 
VBoxHardenedLoader is targeting a Win7 x64 as host system, however I use **Ubuntu 16.04** with **VirtualBox 5.0.24** so this wasn't immediately usable as well. 
But it's another excellent theoretical background resource.

Ultimately I ended up using antivmdetection as base for my endeavour.
Since I trial&error'd myself through the usage (in retrospect: I should do more RTFM and less fanatic doing), here's a summary of things you want to do before starting:

1. [Download VolumeID (for x64)][volumeid]
2. [Download DevManView (for x64)][devmanview]
3. $ sudo apt-get install acpidump (used by Python Script to fetch your system's parameters)
4. $ sudo apt-get install libcdio-utils (contains "cd-drive", used to read these params)
5. $ sudo apt-get install python-dmidecode (the pip-version of dmidecode is incompatible and useless for our purpose, so fetch the right one)
6. $ git clone https://github.com/nsmfoo/antivmdetection.git
7. $ cd antivmdetection :)
8. $ echo "some-username" > user.lst (with your desired in-VM username(s))
9. $ echo "some-computername" > computer.lst

Okay, we are ready to go now.

### VM Creation<a name="vmcreation" />

First, I simply created a new empty Win7 x64 VM.  
I used the following specs:
 * CPU: 2 cores
 * RAM: 4 GB
 * HDD: 120 GB
 * VT-x activated (needed for x64)
 * GPU: 64 MB RAM (no acceleration)
 * NIC: 1x Host-Only adapter (we don't want Internet connectivity right away or Windows may develop the idea of updating itself)

**Important:** Before mounting the Windows ISO, now is the time to use antivmdetection.py.

It will create 2 shell scripts:
1. `<DmiSystemProduct>.sh` <- Script to be used from outside the VM
2. `<DmiSystemProduct>.ps1` <- Script to be used from inside the VM post installation

**Run Antivmdetection (outside VM)**: For me `<DmiSystemProduct>` resulted in "AllSeries" because I run an ASUS board.
Okay, next step: execute `<DmiSystemProduct>.sh` - For me, this immediately resulted in a VM I <b>could not start</b>. 
Responsible for this were the 3 entries
1. DmiBIOSVersion
2. DmiBoardAssetTag
3. DmiBoardLocInChass
Which were set by `<DmiSystemProduct>.sh` to an integer value and VirtualBox was pretty unhappy with that fact, expecting a string. 
Changing these to random strings fixed the issue though. So this may be one of the pitfalls you may run into when using the tool. 
Setting the ACPI CustomTable however worked fine.

### Windows Installation<a name="windows" />

**Historically**: Throw in the ISO, boot up, and go make yourself a coffee.
I had less than 10 minutes for this though.

### Post Installation Hardening and Configuration<a name="postinstall" />

Now we have a fresh Windows 7 installation, time to mess it up.

**Windows Configuration:** Here are some steps to consider that may depend on personal taste.
1. Deactivate Windows Defender - Yes. Because. Malware.
2. Deactivate Windows Updates - We want to keep our system DLL versions fixed to be able to statically infer imported APIs later on.
3. Deactivate ASLR - We don't want our system DLL import addresses randomized later on. Basically, just create the following registry key (Credit to [Ulbright's Blog][ulbright]): `[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management] - “MoveImages”=dword:00000000`
4. Deactivate NX - Whatever may help our malware to run... Basically, just run this in Windows command line (again Credit to [Ulbright's Blog][ulbright]): `bcdedit.exe /set {current} nx AlwaysOff`
5. Allow execution of powershell scripts - Enter a powershell and run: `> Set-ExecutionPolicy Unrestricted`

Run Antivmdetection (in VM): Now we are good to execute the second script `<DmiSystemProduct>.ps1`.
Some of its benefits:
 * ensure our registry looks clean
 * remove the VirtualBox VGA device
 * modify our ProductKey and VolumeID
 * change the user and computer name
 * create and delete a bunch of random files to make the system appear more "used".
 * associate media files with Windows Media Player
 * clean itself up and reboot.

I fiddled a bit with the powershell script to customize it further. 
Also, after reboot, I removed the file manipulation and reboot code itself to be able to run it whenever I need to after deploying my VM to new environments (additionally, this reduces the runtime from several minutes to <5sec).

**Dependencies**: Because malware and packers often require Visual C and NET runtimes, we install them as well. I used:
 * MSVCRT 2005 [x86][msvcrt 2005 32] and [x64][msvcrt 2005 64]
 * MSVCRT 2008 [x86][msvcrt 2008 32] and [x64][msvcrt 2008 64]
 * MSVCRT 2010 [x86][msvcrt 2010 32] and [x64][msvcrt 2010 64]
 * MSVCRT 2012 [x86 and x64][msvcrt 2012 3264]
 * MSVCRT 2013 [x86 and x64][msvcrt 2013 3264]
 * MSVCRT 2015 [x86 and x64][msvcrt 2015 3264]
 * [MS.NET 4.5.2][msvcrt dotnet]

**Snapshot time!** I decided to pack my VM now into an OVA to archive it and make it available for future use.

Now feel free to inflict further harm to your fresh VM.
Installing MS Office, Adobe Acrobat, Flash, Chrome, Firefox all come to mind.

Certainly <b>DO NOT</b> install VBoxGuestAdditions. 
The only benefits are better adaption of screen resolution and easy shared folders. 
For shared folders you can also just check out [impacket's][impacket] [smbserver.py][smbserver] which gives you about the same utility with a one-liner from your host shell.

{% capture asset_link %}{% link /assets/20170205/result_pafish.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "Very good yet not perfect result. We happily ignore the VM exit technique.")]({{ asset_link | absolute_url }})

PAfish looking good.

### VirtualBox Hypervisor Detectability<a name="hypervisor" />

*This is no longer an issue when updating to VirtualBox version 5.1.4+, read below.*

As initially mentioned, I spent another 3 hours with optimization and trying to get rid of the hypervisor detection.

Note that modifying the HostCPUID via VBoxManage does not fix the identity of VirtualBox which I basically learned the hard way.

**Paravirtualization settings:** VirtualBox allows you to choose a paravirtualization profile. 
They expose different combinations of hypervisor bit (HVB) and Hypervisor Vendor Leaf Name (HVN):

1. `none    (HVB=0, HVN="VBoxVBoxVBox")`
2. `default (HVB=1  HVN="VBoxVBoxVBox")` - but can be modified by patching /usr/lib/virtualbox/VBoxVMM.so as shown above, where we have `vbvbvbvbvbvb` instead
3. `legacy  (HVB=0, HVN="VBoxVBoxVBox")`
4. `minimal (HVB=1, HVN="VBoxVBoxVBox")`
5. `Hyper-V (HVB=0, HVN="VBoxVBoxVBox")` - but this can also be modified like default mode
6. `KVM     (HVB=0, HVN="KVMKVMKVMKVM")`

This was also previously noted by user "TiTi87" in the [virtualbox forums][vbox forum]. 
The [Hyper-V docs][hyperv docs] of virtualbox sadly could not help me either.

I will probably spent some more time trying to figure out where the "VBoxVBoxVBox" string is exactly coming from (could not find it in other virtualbox binaries, nor in the src used by DKMS to build vboxdrv) and think it can be ultimately binary patched as well.

However, the issue itself is tied to my setup of VirtualBox, otherwise, I'm pretty sure that my VM itself is looking rather solid now in terms of anti-analysis detection, so we can conclude this write-up.

UPDATE 2017-02-06: nsmfoo [suggested][nsmfoo suggestion] upgrading to VirtualBox 5.1.4+ to get rid of the hypervisor detection. 
So I took his advice, moved up to VirtualBox version 5.1.14 (using this [guide][upgrade guide] and [this fix][upgrade fix]) and he was absolutely right:

{% capture asset_link %}{% link /assets/20170205/result-vbox_5_1_14.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "That's how we want it!")]({{ asset_link | absolute_url }})

Yay!

### Summary<a name="summary" />

This post ended up being a walkthrough of how I spent my last Saturday afternoon and evening.
I found nsmfoo's tool [antivmdetection][antivmdetection] super useful but sadly ran into some initial trouble that cost me some time. 
Ultimately I ended up with a VM I am very happy with, ~~although there remains an issue of VirtualBox's Hypervisor identification.~~

I wrote this post while listening through Infected Mushroom's new album "Return to the Sauce" which I can also heavily recommend. :)


*[link to original post on blogspot][blogspot post].*

[msvcrt 2005 32]: https://www.microsoft.com/en-us/download/details.aspx?id=5638
[msvcrt 2005 64]: https://www.microsoft.com/en-us/download/details.aspx?id=21254
[msvcrt 2008 32]: https://www.microsoft.com/en-us/download/details.aspx?id=29
[msvcrt 2008 64]: https://www.microsoft.com/en-us/download/details.aspx?id=15336
[msvcrt 2010 32]: https://www.microsoft.com/en-us/download/details.aspx?id=5555
[msvcrt 2010 64]: https://www.microsoft.com/en-us/download/details.aspx?id=14632
[msvcrt 2012 3264]: https://www.microsoft.com/en-us/download/details.aspx?id=30679
[msvcrt 2013 3264]: https://www.microsoft.com/en-us/download/details.aspx?id=40784
[msvcrt 2015 3264]: https://www.microsoft.com/en-us/download/details.aspx?id=48145
[msvcrt dotnet]: https://www.microsoft.com/en-us/download/details.aspx?id=42642

[upgrade fix]: http://stackoverflow.com/a/40188122
[upgrade guide]: https://stackoverflow.com/questions/38448223/start-vm-failed-after-update-virtualbox-from-5-0-24-to-5-1
[nsmfoo suggestion]: https://twitter.com/nsmfoo/status/828505635771793409
[hyperv docs]: https://www.virtualbox.org/manual/ch09.html#gimdebug
[vbox forum]: https://forums.virtualbox.org/viewtopic.php?f=6&t=78859
[smbserver]: https://github.com/CoreSecurity/impacket/blob/master/examples/smbserver.py
[impacket]: https://github.com/CoreSecurity/impacket
[ulbright]: https://ulbright.com/2013/11/06/disable-aslr-on-windows-7/
[devmanview]: http://www.nirsoft.net/utils/device_manager_view.html
[volumeid]: https://technet.microsoft.com/de-de/sysinternals/bb897436.aspx
[blog 5 nsmfoo]: http://blog.prowling.nu/2016/02/defeating-wmi-detection-of-virtualbox.html
[blog 4 nsmfoo]: http://blog.prowling.nu/2015/03/modifying-virtualbox-settings-for.html
[blog 3 nsmfoo]: http://blog.prowling.nu/2013/08/modifying-virtualbox-settings-for.html
[blog 2 nsmfoo]: http://blog.prowling.nu/2012/10/modifying-virtualbox-settings-for.html
[blog 1 nsmfoo]: http://blog.prowling.nu/2012/09/modifying-virtualbox-settings-for.html
[twitter nsmfoo]: https://twitter.com/nsmfoo
[antivmdetection]: https://github.com/nsmfoo/antivmdetection
[kernelmode link]: http://www.kernelmode.info/forum/viewtopic.php?f=11&t=3478&sid=288e9200de04694ef2ffc0ab923cabaf
[twitter hfirefox]: https://twitter.com/hfiref0x
[vboxhardenedloader]: https://github.com/hfiref0x/VBoxHardenedLoader
[twitter skier]: https://twitter.com/skier_t
[vmcloak]: https://github.com/jbremer/vmcloak
[netmarketshare windows]: https://www.netmarketshare.com/operating-system-market-share.aspx?qprid=10&qpcustomd=0

[blogspot post]: http://byte-atlas.blogspot.com/2017/02/hardening-vbox-win7x64.html