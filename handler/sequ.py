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

class SequHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        p = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active"] = "fuli"
        template_variables["navs"] = self.nav_model.get_all_navs()
        template_variables["channels"] = self.channel_model.get_all_channels()
    
        if is_mobile_browser(self):
            self.render("sequ.html", **template_variables)
        else:
            self.render("sequ.html", **template_variables)
