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
            template_variables["channels"] = self.channel_model.get_user_all_channels(user_id = user_info["uid"])
            template_variables["posts"] = self.follow_model.get_user_all_follow_posts(user_id = user_info["uid"], current_page = page)
        else:
            self.redirect("/login")

        self.render("index.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = PostForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed

        channel_name = form.channel.data
        channel = self.channel_model.get_channel_by_name(channel_name = channel_name)
        
        post_info = {
            "author_id": self.current_user["uid"],
            "channel_id": channel["id"],
            "video_id": 1,
            "intro": form.intro.data,
            "plus": 0,
            "share": 0,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.post_model.add_new_post(post_info)


        self.redirect("/")

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

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = ChannelForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed

        channel_info = {
            "name": form.name.data,
            "intro": form.intro.data,
            "avatar": form.avatar.data,
            "nav_id": 1,
            "plus": 0,
            "followers": 0,
            "posts": 0,
            "author_id": self.current_user["uid"],
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.channel_model.add_new_channel(channel_info)

        channel = self.channel_model.get_channel_by_name(channel_name = channel_info["name"])

        follow_info = {
            "user_id": self.current_user["uid"],
            "channel_id": channel["id"],
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.follow_model.add_new_follow(follow_info)

        self.redirect("/video")


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

    @tornado.web.authenticated
    def post(self, channel_id, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = PostForm2(self)

        if not form.validate():
            self.get(channel_id, {"errors": form.errors})
            return

        # continue while validate succeed
        
        post_info = {
            "author_id": self.current_user["uid"],
            "channel_id": channel_id,
            "video_id": 1,
            "intro": form.intro.data,
            "plus": 0,
            "share": 0,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.post_model.add_new_post(post_info)


        self.redirect("/c/" + channel_id)

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
