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
            template_variables["posts"] = self.follow_model.get_user_all_follow_posts(user_id = user_info["uid"], current_page = page)
        else:
            self.redirect("/login")

        self.render("index.html", **template_variables)

class VideoHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["channels"] = self.channel_model.get_channels_by_nav_id(1)
        else:
            self.redirect("/login")

        self.render("video.html", **template_variables)


class ChannelHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["channel"] = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
            template_variables["posts"] = self.post_model.get_all_posts_by_channel_id(current_page = page, channel_id = channel_id)
        else:
            self.redirect("/login")


        self.render("channel.html", **template_variables)

class UserHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        current_user_info = self.current_user
        template_variables["current_user_info"] = current_user_info      
        page = int(self.get_argument("p", "1"))
        
        if(current_user_info):
            if(re.match(r'^\d+$', user)):
                user_info = self.user_model.get_user_by_uid(user)
            else:
                user_info = self.user_model.get_user_by_username(user)
            template_variables["user_info"] = user_info
            template_variables["posts"] = self.post_model.get_user_all_posts(current_page = page, user_id = user_info["uid"])
        else:
            self.redirect("/login")

        self.render("user.html", **template_variables)
