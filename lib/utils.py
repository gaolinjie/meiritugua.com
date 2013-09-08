#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 tuila.me

import re

def find_mentions(content):
    regex = re.compile(ur"@(?P<username>(?!_)(?!.*?_$)(?!\d+)([a-zA-Z0-9_\u4e00-\u9fa5]+))(\s|$)", re.I)
    return [m.group("username") for m in regex.finditer(content)]

def  r1(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)

def r1_of(patterns, text):
    for p in patterns:
        x = r1(p, text)
        if x:
            return x

def find_video_id_from_url(url):
    patterns = [r'^http://v.youku.com/v_show/id_([\w=]+).html',
                r'^http://player.youku.com/player.php/sid/([\w=]+)/v.swf',
                r'^loader\.swf\?VideoIDS=([\w=]+)',
                r'^([\w=]+)$']
    return r1_of(patterns, url)
