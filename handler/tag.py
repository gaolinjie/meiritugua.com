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

class TagHandler(BaseHandler):
    def get(self, tag_name, template_variables = {}):
    	user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["navs"] = self.nav_model.get_all_navs()
        template_variables["channels"] = self.channel_model.get_all_channels()

        tag = self.tag_model.get_tag_by_tag_name(tag_name)
        template_variables["tag"] = tag
        template_variables["stds"] = self.post_tag_model.get_tag_all_posts(tag.id, current_page = page)
        template_variables["hots"] = self.hot_model.get_hot_posts(current_page = page)
        
        self.render("tag.html", **template_variables)