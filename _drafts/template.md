---
layout:             post
title:              "REPLACE_WITH_POST_TITLE"
author:             Daniel Plohmann
date:               2020-03-20 01:00:00 +0100
last_modified_at:   REPLACE_WITH_ADJUSTED_DATE_FROM_ABOVE
categories:         blog
tags:               [bytetlas, "knowledge fragment"]
---



















Example for an image link:

{% capture asset_link %}{% link /REPLACE_WITH_ASSET_LINK %}{% endcapture %}
[![screenshot]({{ asset_link | absolute_url }} "REPLACE_WITH_DESCRIPTION")]({{ asset_link | absolute_url }})

Example for a hyperlink:

[link description][https://link_url.com]

Relative link:

[link text]({% post_url 2012-08-20-idascope-beta %})