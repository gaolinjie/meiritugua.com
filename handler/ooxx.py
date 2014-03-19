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

import qiniu.conf
import qiniu.io
import qiniu.rs

qiniu.conf.ACCESS_KEY = "hmHRMwms0cn9OM9PMETYwsXMLG93z3FiBmCtPu7y"
qiniu.conf.SECRET_KEY = "nCDM7Tuggre39RiqXaDmjo8sZn6MLGmckUaCrOJU"
bucket_name = 'mrtgimg'

class OoxxHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        p = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active"] = "ooxx"
        template_variables["hots"] = self.hot_model.get_hot_posts(current_page = p)
        #template_variables["heads"] = self.head_model.get_shows_head_posts()
        template_variables["stds"] = self.ooxx_model.get_ooxx_posts(current_page = p)

        template_variables["navs"] = self.nav_model.get_all_navs()
        template_variables["channels"] = self.channel_model.get_all_channels()

        policy = qiniu.rs.PutPolicy(bucket_name)
        uptoken = policy.token()
        template_variables["up_token"] = uptoken

        if is_mobile_browser(self):
            self.render("ooxx-m.html", **template_variables)
        else:
            self.render("ooxx.html", **template_variables)

class OoxxAddHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, template_variables = {}):
        user_info = self.current_user
        if(user_info):
            data = json.loads(self.request.body)
            title = data["title"]
            img = data["img"]
            intro = data["intro"]

            intro2 = '<div class="img-intro">' + intro + '</div>';
            img2 = '<img class="img-address" src="' + img + '">';
            content = img2 + intro2;

            post_info = {
                "author_id": self.current_user["uid"],           
                "title": title,
                "intro": intro,
                "thumb": img,
                "cover": img,
                "content": content,
                "channel_id": 5,
                "visible": 1,
                "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            post_id = self.post_model.add_new_post(post_info)

            ooxx_info = {
                "post_id": post_id,
                "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            self.ooxx_model.add_new_ooxx(ooxx_info)
            self.write(lib.jsonp.print_JSON({
                    "success": 1,
                }))