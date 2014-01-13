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

class CommunityHandler(BaseHandler):
    def get(self, template_variables = {}):
        self.render("community.html", **template_variables)