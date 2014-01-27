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
import urllib
import tornado.web
import lib.jsonp
import os.path

from base import *
from lib.sendmail import send
from lib.variables import gen_random
from lib.gravatar import Gravatar
from form.user import *

def do_login(self, user_id):
    user_info = self.user_model.get_user_by_uid(user_id)
    self.session["uid"] = user_id
    self.session["duoshuo_id"] = user_info["duoshuo_id"]
    self.session["username"] = user_info["username"]
    self.session.save()
    self.set_secure_cookie("user", str(user_id))

def do_logout(self):
    # destroy sessions
    self.session["uid"] = None
    self.session["duoshuo_id"] = None
    self.session["username"] = None
    self.session.save()

    # destroy cookies
    self.clear_cookie("user")

class LoginHandler(BaseHandler):
    def initialize(self, *args, **kwargs):
        self.referer = self.request.headers.get('Referer', '/')

    def get(self, template_variables = {}):
        print self.referer
        do_logout(self)
        #self.render("user/login.html", **template_variables)
        duoshuo_code = self.get_argument('code','')
        url = 'http://api.duoshuo.com/oauth2/access_token' 
        response = urllib2.urlopen(url, 'code='+duoshuo_code)
        result = json.load(response)

        url2 = 'http://api.duoshuo.com/users/profile.json?user_id=' +result["user_id"]
        response2 = urllib2.urlopen(url2)
        result2 = json.load(response2)
        print result2["response"]["name"]

        duplicated_user = self.user_model.get_user_by_duoshuo_id(result2["response"]["user_id"])

        if(duplicated_user):          
            do_login(self, duplicated_user["uid"])
            # update `last_login`
            updated = self.user_model.set_user_base_info_by_uid(duplicated_user["uid"], {"last_login": time.strftime('%Y-%m-%d %H:%M:%S')})
        else:
            user_info = {
                "duoshuo_id": int(result2["response"]["user_id"]),
                "username": result2["response"]["name"],
                "avatar": result2["response"]["avatar_url"],
                "intro": "请添加简短的自我介绍。",
                "posts": 0,
                "created": time.strftime('%Y-%m-%d %H:%M:%S')
            }

            if(self.current_user):
                return
        
            user_id = self.user_model.add_new_user(user_info)
        
            if(user_id):
                do_login(self, user_id)
                # update `last_login`
            updated = self.user_model.set_user_base_info_by_uid(user_id, {"last_login": time.strftime('%Y-%m-%d %H:%M:%S')})

        self.redirect(self.referer)

class LogoutHandler(BaseHandler):
    def initialize(self, *args, **kwargs):
        self.referer = self.request.headers.get('Referer', '/')
        
    def get(self):
        print "Looooooogout"
        do_logout(self)
        # redirect
        self.redirect(self.referer)



class SettingHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, template_variables = {}):
        user_info = self.get_current_user()
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        self.render("user/setting.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = SettingForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        # continue while validate succeed

        user_info = self.current_user
        update_result = self.user_model.set_user_base_info_by_uid(user_info["uid"], {
            "username": form.username.data,
            "intro": form.intro.data,
            "updated": time.strftime('%Y-%m-%d %H:%M:%S')
        })

        self.redirect("/u/" + form.username.data)


class UserHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random    
        page = int(self.get_argument("page", "1"))
        if(re.match(r'^\d+$', user)):
            view_user_info = self.user_model.get_user_by_uid(user)
        else:
            view_user_info = self.user_model.get_user_by_username(user)
        template_variables["view_user_info"] = view_user_info
        template_variables["stds"] = self.std_model.get_std_posts_by_user_id(view_user_info.uid, current_page = page)
        template_variables["hots"] = self.hot_model.get_hot_posts_by_user_id(view_user_info.uid, current_page = page)
        template_variables["navs"] = self.nav_model.get_all_navs()
        template_variables["channels"] = self.channel_model.get_all_channels()

        self.render("user/user.html", **template_variables)




