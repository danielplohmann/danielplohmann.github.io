---
layout:             post
title:              "IDAScope v1.1: YARA scanning"
author:             Daniel Plohmann
date:               2014-02-07 02:00:00 +0100
last_modified_at:   2014-02-07 02:00:00 +0100
categories:         blog
tags:               idascope
---

Today I integrated something in the master branch of IDAscope that I myself liked to have available for quite some time: Seamless scanning with YARA signatures from within IDA for the win!

Late [December 2013][yara release] YARA's author [Victor M. Alvarez][twitter plusvic] made us a christmas gift with his YARA 2.0 release. 
I read the release notes but didn't realize the implications of "YARA has experiencied an almost complete rewrite for version 2.0" at that point in time. 

Around mid December, I tasked one of my student assistants (Christopher Kannen) with developing a minimum / pure-python version of YARA rule handling. 
The goal of this task would have been to enable its use in IDA and work arond the issues experienced in the past.
Last week, he finished the code for loading YARA rules into convenient objects. 
When he was about to start with implementing basic matching, I became [aware][tweet pnx] that importing YARA in the IDA Python shell no longer failed. 
Happy day, this meant that the desired functionality could be immediately integrated into IDAscope with full native support for YARA rule files, avoiding any side-effects. 

Here is a screenshot of the widget in action:

{% capture asset_link %}{% link /assets/20140207/yarascan_blog.png %}{% endcapture %}
[![yara scan]({{ asset_link | absolute_url }} "YARA Scanner in action.")]({{ asset_link | absolute_url }})

I used some binary (`BISCUIT`, `268eef019bf65b2987e945afaf29643f`) from [Mila Parkour's][twitter mila] [Contagio Malware Dump][contagion dump apt1] collection of APT1 stuff and the signatures as provided by [AlienVaultLabs][yara alienvault] for developing/testing and the demo screenshot. 
Keep up the good work!

However one would assume Christopher's work is now useless and was wasted time. ;)
No! It comes in handy as I will outline in the description up next.

### Fiddling with YARA in Python

Everyone who has ever played with YARA and Python is probably familiar with its basic usage, like (examples taken from [YARA's manual][yara manual]):
```python
import yara

rules = yara.compile(filepath="/path")
suspicious = "some data to be scanned"
rules.match(data=suspicious)

```
Since YARA is intended to be fast, the `rules` object potentially contains multiple signatures from a single file compiled into one object. 
I always missed the ability here to inspect those signatures loaded in detail, like having access to their names and strings of individual signatures. 
Maybe it's possible, I just never managed to do so.
A probably lesser known but cool feature of YARA are match callbacks. It comes in pretty handy as a workaround in this context:
```python
import yara

def cb(data):
    print data
    yara.CALLBACK_CONTINUE

rules = yara.compile(filepath="/path")
suspicious = "some data to be scanned"
rules.match(data=suspicious, callback=cb)

```
Each time the callback is fired, we receive a dictionary "data" like this one:
```json
{
    'tags': [
        'foo', 
        'bar'
    ],
    'matches': True,
    'namespace': 'default',
    'rule': 'my_rule',
    'meta': {},
    'strings': [
        (81, '$a', 'abc'), 
        (141, '$b', 'def')
    ]
}
```
As you can see, we can derive from that data, which signatures from the rules object have just been run against the target input and what their individual outcome is. 
We can also derive information about partial matches by checking the "matches" and "strings" entries. 

This is basically what I now use in the IDAscope widget to derive the scores and detailed views for signatures. 
Christopher's rule loader additionally allows to read the signatures as given in the source file, thus comparing which of the strings from the callbacks are matched and which are not.

Combining all of those parts results in the extension just added to IDAscope.

If you want to use it, make sure to install [YARA Python][yara release] first and adjust the paths specified in `./idacope/config.py` to your local collection of signature files.

Should you find any errors, please [blame here][bitbucket issues] or via mail.

Here is [IDAscope v1.1][bitbucket idascope release] ([mirror][pnxtf mirror]) as a downloadable snapshot from the repository (`commit f3d58ad`). 
If the latest extensions should prove to be stable and usable, I might not even need to push another version like last time, lol.

### Development Plans

I'm not entirely sure if I am going to push this IDAscope widget further than its current functionality.

Instead, a full-blown interactive YARA editor (plugin) seems more attractive to me right now. 
So basically something independent from IDAscope, since the other tabs may be of less interest to a signature writer.
If it is not going to be too heavy code-wise, I might opt later on to integrate it back in IDAscope. I'm open for feedback in this matter.

But first: enjoy YARA in your IDA! :)


*[link to original post on blogspot][blogspot post].*

[yara release]: https://github.com/plusvic/yara/releases/tag/v2.0.0
[twitter plusvic]: https://twitter.com/plusvic
[tweet pnx]: https://twitter.com/push_pnx/status/430696628505178112
[twitter mila]: https://twitter.com/snowfl0w
[contagion dump apt1]: http://contagiodump.blogspot.de/2013/03/mandiant-apt1-samples-categorized-by.html
[yara alienvault]: https://github.com/jaimeblasco/AlienvaultLabs/blob/master/malware_analysis/CommentCrew/apt1.yara
[yara manual]: https://github.com/plusvic/yara/releases/download/v2.0.0/YARA.User.s.Manual.pdf
[bitbucket issues]: https://bitbucket.org/daniel_plohmann/simplifire.idascope/issues?status=new&amp;status=open
[bitbucket idascope release]: https://bitbucket.org/daniel_plohmann/simplifire.idascope/downloads/IDAscope_v_1_1.zip
[pnxtf mirror]: http://pnx.tf/files/IDAscope_v_1_1.zip

[blogspot post]: https://pnx-tf.blogspot.com/2014/02/idascope-v11-yara-scanning.html