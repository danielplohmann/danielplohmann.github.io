---
layout:             post
title:              "The Big Zeus Family Similarity Showdown"
author:             Daniel Plohmann
date:               2018-01-14 01:00:00 +0100
last_modified_at:   2018-01-14 01:00:00 +0100
categories:         blog
tags:               [bytetlas, "zeus showdown", "code similarity"]
---

Dear followers of this blog, I wish you a happy new year!

About a month ago, I have launched my latest project: [Malpedia][malpedia] ([slides here][malpedia slides]).
Since the launch, we have grown by about 350 users and have a stable average 10 proposals/contributions per day. I hope that Malpedia will become a really useful resource for malware research over time!

This blog shall serve as a demonstration for what you can use with this malware corpus.
Over the last couple days, I have taken all dumps for versions of Zeus-related families and created a similarity matrix for them, using IDA Pro and BinDiff.

It looks like this:

{% capture asset_link %}{% link /assets/20180114/2018-01-14-similarity_snapshot.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "Screenshot of "The Big Zeus Family Similarity Showdown"")]({{ asset_link | absolute_url }})

Because I want to update this document over time, I have descided to host it on a [dedicated page][pnx tf static link] over at [pnx.tf][pnx tf] instead of using this blog. 
Over there, you can find more info on the families included and the methodology I used in order to create it.



*[link to original post on blogspot][blogspot post].*

[pnx tf]: http://pnx.tf/slides/zeus_similarity_showdown.html
[pnx tf static link]: http://pnx.tf/slides/zeus_similarity_showdown.html
[malpedia slides]: https://www.botconf.eu/wp-content/uploads/2017/12/2017-DanielPlohmann-Malpedia.pdf
[malpedia]: https://malpedia.caad.fkie.fraunhofer.de/

[blogspot post]: http://byte-atlas.blogspot.com/2018/01/zeus-similarity-showdown.html
