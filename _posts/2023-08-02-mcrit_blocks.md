---
layout:             post
title:              "Upgraded MCRIT Feature: IDA Plugin"
author:             Daniel Plohmann
date:               2023-08-02 11:20:00 +0100
last_modified_at:   2023-08-02 11:20:00 +0100
categories:         blog
tags:               [bytetlas, mcrit, tools, "code similarity"]
---

As a follow-up to my previous [blog post][mcrit blog] on the release of [MCRIT][link_mcrit_github], I wanted to report on the progress of the next steps that I had outlined.  
Since I think that the IDA plugin is now in a good shape, it is worth a post.  
Many thanks to [Rony][twitter rony] for test-driving the plugin and giving valuable feedback.

### MCRIT IDA Plugin

When thinking about how to make 1:N code-similarity information useful in a tool like IDA, one goal for me is to increase the context for what an analyst is currently looking at.  
When matching a whole binary, there is a lot of potential matches, which can be overwhelming and the scope is possibly also different from what you want when doing in-depth analysis.  
In my opinion, it would likely make more sense to just provide information for all possible matches for a given, currently viewed function, or even for a single basic block.

For this reason, I created two tabs in the plugin that allow to do support exactly such queries.

As a showcase, I've chosen the example from the previous blog post, the `win.contopee` to `win.wannacry` connection made famous from this [tweet][link_mehta_twitter].
For the following example, I'm using my MCRIT demo server (32GB RAM, 8 cores), loaded up with all of the current Malpedia data (1737 malware families, 7369 samples).  

#### Block Scope

Assume we already converted our current IDB into the MCRIT-friendly SMDA format by clicking the fingerprint button.  
This now allows us to now use the Block Scope widget to query all basic blocks of our currently viewed function and inspect information about how they match the data in our MCRIT instance.  
We can see that we get matches for most of the blocks of size 4 instructions and more (which is the lower threshold of the system), with some of them being found in 2 or 3 families.  
And Hooray, one of the blocks tied specifically to the curious use of the `rand()` function is actually found in both `win.contopee` to `win.wannacry`.

Now, the good news is that such queries happen in a very tolerable time frame of around 160ms per basic block for a data set like the one used here.  
As you can see in the Output box, it took about 1.1 sec to match all blocks against the whole database (39.170.526 indexed basic blocks; 8.516.889 of them unique; across 9.175.530 disassembled functions).  
As the function viewed here can be considered an average function with respect to its size, it's even viable to just query all blocks whenever a function is viewed for the first time.  
This is simply enabled when using the "Live Block Queries" checkbox.

{% capture asset_link %}{% link /assets/20230802/IDA_BlockQuery.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "Block Scope feature in the MCRIT IDA plugin.")]({{ asset_link | absolute_url }})

#### Function Scope

One of the great features of tools like BinDiff and Diaphora is their graph view, which immediately allows comparing potentially similar functions with each other.  
Since MCRIT is an 1:N and not 1:1 approach, we possibly want something similar but being able to view/match against functions from arbitrary other samples in our database.  
As we store the control flow graphs and disassembly of all processed functions in MCRIT, we can simply pull this remote information into IDA, leading to this:

{% capture asset_link %}{% link /assets/20230802/IDA_RemoteFunction.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "Function Comparison feature in the MCRIT IDA plugin.")]({{ asset_link | absolute_url }})

The coloring used here is similar to MCRITweb, with blue blocks indicating hash-similar blocks, and green over yellow to red decreasing similarity.  
One limitation is that we seemingly cannot modify the font color used in the custom GraphViewer(?), so this doesn't have decent contrast in dark mode right now:

{% capture asset_link %}{% link /assets/20230802/IDA_Remote_Dark.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "Function Comparison feature in the MCRIT IDA plugin, Dark Mode.")]({{ asset_link | absolute_url }})

We will possibly address this by allowing users to define custom color schemes in the config.

A similar view for remote functions can be opene in the Block Scope view when clicking entries in the lower table with the concrete matches.


### MCRIT Reference Data

Because a system like MCRIT is only useful with data, we started to process and provide reference data, located in this [Github Repo][repo mcrit-data].  
If you just want to play with your own MCRIT, this could also be a good place to start as it can be used to fill your demo instance for first steps.

Ultimately, the goal here is to have this reference library code available with as many symbols as possible, which is why I'm reprocessing data from earlier projects like [empty_msvc][empty_msvc].

As an example, the available `zlib` is from the evaluations in my PhD thesis and can already be used to tag functions in a given IDB should you run into them:

{% capture asset_link %}{% link /assets/20230802/IDA_zlib.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "Symbol import for zlib")]({{ asset_link | absolute_url }})

We expect this procedure to take a while and do this besides all our other projects/work, so check back every now and then to see what was added.  
Our priority right now is to cover all of MSVC code as shipped with the Visual Studio installers next, and then possibly move on to integrate the precompiled code from the [Shiftmedia][shiftmedia] project, from which also the first `zlib` code was taken.
Here, things like OpenSSL would likely take priority.  
Also, feel free to make recommendations in the [issue tracker][data issues].

With respect to making pre-processed Malpedia data available as well, this would be one of my goals for this year.  
We are currently thinking of ways that would allow this in the best way possible.  
We will likely do this with two versions, one to allow maintaining the data sharing license and one full data set accessible to Malpedia users.


[repo mcrit-data]: https://github.com/danielplohmann/mcrit-data
[mcrit blog]: https://danielplohmann.github.io/blog/2023/06/05/mcrit.html
[empty_msvc]: https://github.com/danielplohmann/empty_msvc
[link_mehta_twitter]: https://twitter.com/neelmehta/status/864164081116225536
[shiftmedia]: https://github.com/ShiftMediaProject
[data issues]: https://github.com/danielplohmann/mcrit-data/issues
[twitter rony]: https://twitter.com/r0ny_123