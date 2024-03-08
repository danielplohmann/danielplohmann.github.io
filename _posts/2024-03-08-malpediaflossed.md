---
layout:             post
title:              "MalpediaFLOSSed"
author:             Daniel Plohmann
date:               2024-03-08 08:30:00 +0100
last_modified_at:   2024-03-08 08:30:00 +0100
categories:         blog
tags:               [bytetlas, "knowledge fragment", malpedia]
---

Today, I want to write a few lines about a project that I worked on since the start of 2024.  
It is centered on the analysis of strings in malware and an attempt to make everyone's life a bit easier.

The FLARE team has created the amazing [FLOSS](https://github.com/mandiant/flare-floss) tool as a means to reliably and extensively carve strings from binaries.  
So I went ahead and processed all of [Malpedia](https://malpedia.caad.fkie.fraunhofer.de/) with it, and provide the aggregated output via [MalpediaFLOSSed](https://github.com/malpedia/malpedia-flossed).


### MalpediaFLOSSed

FLOSS is short for FLARE Obfuscated String Solver.  
As the name implies, it is a very capable strings carver that not just simply extracts ASCII and unicode sequences, but is also able to e.g. [decode stack strings](https://www.mandiant.com/resources/blog/automatically-extracting-obfuscated-strings) and use emulation to [decrypt strings](https://www.mandiant.com/resources/blog/floss-version-2).  

I use it almost daily when doing initial analysis of malware samples.  
One thing that was always missing for this analysis step was an easy way to know which of these strings are common across or more specific for given malware families.  
Since Malpedia is an extensive collection of malware families, I thought it would be a good idea to throw FLOSS at all of it.  
Especially with the recent additions of parsing for Go and Rust binaries, this was a great opportunity to test-drive these new features.  
As a result, I generated FLOSS reports for reference samples of more than 1,800 malware families, added a bunch of library files and combined all these reports in one aggregated collection.

The concrete stats of this operation conducted in January 2024 look like this:

```
  num_malware_families:       1,845
  num_samples_flossed:        8,522
  num_total_strings:     44,666,177
  num_processed_strings:  3,835,990
  num_tagged_strings:     1,599,459
```

As we can see, 8,522 (unpacked/dumped) malware samples and library files from 1,845 malware families have been processed, and 44,666,177 raw FLOSSed strings were the result.
In the processing, these were deduplicated down into 3,835,990 strings and tags applied like `lib` or `winapi` were applied.  
Especially these tags are inspired by the FLOSS [quantumstrand](https://github.com/mandiant/flare-floss/tree/quantumstrand) development branch, from which data has been reused and [discussions](https://github.com/malpedia/malpedia-flossed/issues/1) with [
Willi Ballenthin](https://github.com/williballenthin).

All of which was combined into one big JSON file, which is roughly 900 MB in size and can be [found here](https://github.com/malpedia/malpedia-flossed/blob/main/data/).

Now, whenever looking at strings, we can use this data collection to get additional information about the prevalence of given strings, or if they are known to originate from benign sources such as 3rd party libraries or compilers.  

### Operationalizing

While the data itself is nice, it has to be usable.  
For this reason, I also created tools around it.

## Web Service

First, there is a public web service hosted at [strings.malpedia.io](https://strings.malpedia.io/), which is an instance of the [implementation](https://github.com/malpedia/malpedia-flossed/tree/main/flossed-falcon) we provide in the repo.

The easiest way to interact with it, apart from the basic web UI, is doing API queries for single or multiple strings like so:

```
$ curl https://strings.malpedia.io/api/query/FIXME  
{
    "status": "successful", 
    "data": [
        {
            "encodings": ["ASCII"], 
            "families": ["win.kins", "win.vmzeus", "win.zeus_sphinx", "win.citadel", 
                         "win.ice_ix", "win.murofet", "win.zeus"], 
            "family_count": 7, 
            "methods": ["static"], "string": "FIXME", "tags": [], "matched": true
        }
    ]
}

$ curl -X POST https://strings.malpedia.io/api/query/ --data '"FIXME","NOT_IN_THE_DATABASE"'
{
    "status": "successful", 
    "data": [
        {
            "encodings": ["ASCII"], 
            "families": ["win.kins", "win.vmzeus", "win.zeus_sphinx", "win.citadel", 
                         "win.ice_ix", "win.murofet", "win.zeus"], 
            "family_count": 7, 
            "methods": ["static"], "string": "FIXME", "tags": [], "matched": true
        }, 
        {"matched": false, "string": "NOT_IN_THE_DATABASE"}
    ]
}
```

## Plugins

Instead of doing raw lookups, we can also leverage other tools that produce strings for us.  
Natural candidates for this are binary analysis tools such as IDA Pro, Ghidra, and Binary Ninja.

#### Cross-Compatibility

Since I didn't want to write the same plugin multiple times, I started looking into making one plugin cross-compatible.  
Luckily, I didn't have to pioneer a lot here since this had already been done before by [@hyuunnn](https://github.com/hyuunnn), who managed to make his tool [hyara](https://github.com/hyuunnn/Hyara) compatible with all of the above named tools.  
So many, many thanks for figuring out many of the irks related to such an endeavor!!

For this reason, the plugin presented here is largely based on the code found in [hyara](https://github.com/hyuunnn/Hyara).  
For future development and in case others want to start off from the same base, I have extracted and refactored the framework code from hyara into this [template repository](https://github.com/danielplohmann/gui-plugin-template).  
The major challenge that will remain for the future is to extend the included [ApiProxy](https://github.com/danielplohmann/gui-plugin-template/blob/main/template_plugin/plugin/apis/ApiProxy.py) to adapt and harmonize as much from the different tools' APIs into one combined interface.  
But let's go back to the MalpediaFLOSSed plugin.

#### MalpediaFLOSSed plugin

Setting up the plugin requires different steps per tool and has been described in the [documentation](https://github.com/malpedia/malpedia-flossed/blob/main/docs/plugin.md).  
It can be used both fully offline using the above mentioned JSON file and also online by pointing it to an instance of the web service, like our [strings.malpedia.io](https://strings.malpedia.io/).

The plugin itself looks like this:

{% capture asset_link %}{% link /assets/20240308/MalpediaFlossed_GUI.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "Overview of the MalpediaFLOSSed plugin GUI")]({{ asset_link | absolute_url }})

Generally, the table will show the strings as found by the binary analysis tool but enhance them with the information if they are known from any malware families or have been assigned tags.

The functionality of the menu buttons is as follows:
* `Analyze`: If not having `AUTO_ANALYZE` enabled, this will trigger an analysis and lookup all defined strings against MalpediaFLOSSed.
* `Show Overview`: aggregate all string scores by families and print a ranking in the console - this can possibly serve as an approximation for identification or give hints for relationships.
* `Show invalid strings`: strings that cannot be looked up (and thus are not in the MalpediaFLOSSed collection anyway) will be omitted from the table.
* `Deduplicate strings`: in case a string exists multiple times in the binary, only show the first occurrence in the table.
* `Show potential trash strings`: string extractors are prone to excavating meaningless, wrongly interpreted strings (sequences of instructions in ASCII range etc.) - try to filter them using the built-in heuristics.
* `Min Score`: A score that ranges from 0-100, encoding how "rare" the string is with respect to its occurrence across families in Malpedia.

The plugin is also interactive, when double clicking
* an address in the table, the view will jump to the location.
* elsewhere in a row, further information on the respective string is printed to the console.

Here's the same plugin being used across all tools:

{% capture asset_link %}{% link /assets/20240308/MalpediaFlossed_IDA.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "MalpediaFLOSSed in IDA Pro")]({{ asset_link | absolute_url }})

{% capture asset_link %}{% link /assets/20240308/MalpediaFlossed_Ghidraton.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "MalpediaFLOSSed in Ghidra")]({{ asset_link | absolute_url }})

{% capture asset_link %}{% link /assets/20240308/MalpediaFlossed_Binja.png %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "MalpediaFLOSSed in Binary Ninja")]({{ asset_link | absolute_url }})

### Outlook

In its given state, we are already very happy with the project and think that it is a great contribution to initial string analysis.  
For the future, we think the following aspects deserve additional attention.

Regardless of the string carver used, an analyst will typically face some false positives, e.g. when sequences of instructions in the ASCII range are mistakenly extracted.  
Therefore, heuristics for filtering strings could and should be found and improved to reduce the total number of strings to consider, which would also help distill our collection MalpediaFLOSSed to meaningful strings.

To further simplify usage, we will likely add a file processing capability to the web service that will use FLOSS for processing, similar to how we generate the data collection.

Of course, we will periodically update the collection and possibly open source the processing tools as well.

If you have further ideas, feel free to let me know!