#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 tuila.me

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

class IndexHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["posts"] = self.follow_model.get_user_all_follow_topics(user_id = user_info["uid"], current_page = page)
        else:
            self.redirect("/login")

        self.render("index.html", **template_variables)

class VideoHandler(BaseHandler):
    def get(self, template_variables = {}):

        self.render("video.html", **template_variables)


class ChannelHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):

        self.render("channel.html", **template_variables)
