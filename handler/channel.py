#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 meiritugua.com

import uuid
import hashlib
import Image
import StringIO
import time
import json
import re
import urllib2
import tornado.web
import lib.jsonp
import pprint
import math
import datetime 

from base import *
from lib.variables import *
from form.topic import *
from lib.variables import gen_random
from lib.xss import XssCleaner
from lib.utils import find_mentions
from lib.reddit import hot
from lib.utils import pretty_date

from lib.mobile import is_mobile_browser

class ChannelHandler(BaseHandler):
    def get(self, channel_name, template_variables = {}):
    	user_info = self.current_user
        p = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["navs"] = self.nav_model.get_all_navs()
        template_variables["channels"] = self.channel_model.get_all_channels()

        channel = self.channel_model.get_channel_by_channel_name(channel_name)
        if channel:
            template_variables["channel"] = channel
            template_variables["stds"] = self.std_model.get_std_posts_by_channel_id(channel.id, current_page = p)
            template_variables["hots"] = self.hot_model.get_hot_posts_by_channel_id(channel.id, current_page = p)
        else:
            nav = self.nav_model.get_nav_by_nav_name(channel_name)
            if nav:
                template_variables["channel"] = nav
                template_variables["stds"] = self.nav_model.get_std_posts_by_nav_id(nav.id, current_page = p)
                template_variables["hots"] = self.nav_model.get_hot_posts_by_nav_id(nav.id, current_page = p)
            else:
                self.render("404.html", **template_variables)
                return

        if is_mobile_browser(self):
            self.render("channel-m.html", **template_variables)
        else:
            self.render("channel.html", **template_variables)