#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

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

class PostHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
    	user_info = self.current_user
        template_variables["user_info"] = user_info
    	page = int(self.get_argument("page", "1"))
    	template_variables["hots"] = self.hot_model.get_hot_posts(current_page = page)
        self.render("post.html", **template_variables)

class CreatePostHandler(BaseHandler):
    def get(self, template_variables = {}):
    	user_info = self.current_user
        template_variables["user_info"] = user_info
        self.render("create.html", **template_variables)

    @tornado.web.authenticated
    def post(self, node = None, template_variables = {}):
        print "CreateHandler:post"
        template_variables = {}

        # validate the fields
        form = CreateForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed     
        post_info = {
            "author_id": self.current_user["uid"],           
            "title": form.title.data,
            "intro": form.title.data,
            "content": form.content.data,
            "cover": "http://s3-ak.buzzfeed.com/static/2013-12/campaign_images/webdr07/13/9/beyonce-surprised-the-world-with-a-new-album-on-i-1-7541-1386944111-8.jpg",
            "channel_id": 0,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        post_id = self.post_model.add_new_post(post_info)

        std_id = self.std_model.add_new_std({"post_id": post_id, "created": time.strftime('%Y-%m-%d %H:%M:%S')})     

        self.redirect("/")