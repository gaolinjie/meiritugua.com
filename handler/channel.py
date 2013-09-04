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
import urllib
import tornado.web
import lib.jsonp
import os.path

from base import *
from lib.sendmail import send
from lib.variables import gen_random
from lib.gravatar import Gravatar
from form.user import *

class ChannelSettingHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            plus = self.plus_model.get_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                template_variables["followed"]=1;
            else:
                template_variables["followed"]=0;
            if(plus):
                template_variables["plused"]=1;
            else:
                template_variables["plused"]=0;
            template_variables["channel"] = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
        else:
            self.redirect("/login")

        self.render("channel/channel_setting.html", **template_variables)

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
            "intro": form.self_intro.data,
        })

        updated = self.user_model.set_user_base_info_by_uid(user_info["uid"], {"updated": time.strftime('%Y-%m-%d %H:%M:%S')})
        self.redirect("/u/" + user_info["username"])

class ChannelSettingAvatarHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, channel_id, template_variables = {}):
        user_info = self.get_current_user()
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            plus = self.plus_model.get_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                template_variables["followed"]=1;
            else:
                template_variables["followed"]=0;
            if(plus):
                template_variables["plused"]=1;
            else:
                template_variables["plused"]=0;
            template_variables["channel"] = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
        else:
            self.redirect("/login")

        self.render("channel/channel_setting_avatar.html", **template_variables)

    @tornado.web.authenticated
    def post(self, channel_id, template_variables = {}):
        template_variables = {}
        print channel_id

        if(not "avatar" in self.request.files):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_avatar"] = [u"请先选择要上传的头像"]
            self.get(template_variables)
            return

        user_info = self.current_user

        avatar_name = "%s" % uuid.uuid5(uuid.NAMESPACE_DNS, str(channel_id))
        avatar_raw = self.request.files["avatar"][0]["body"]
        avatar_buffer = StringIO.StringIO(avatar_raw)
        avatar = Image.open(avatar_buffer)

        # crop avatar if it's not square
        avatar_w, avatar_h = avatar.size
        avatar_border = avatar_w if avatar_w < avatar_h else avatar_h
        avatar_crop_region = (0, 0, avatar_border, avatar_border)
        avatar = avatar.crop(avatar_crop_region)

        avatar_192x192 = avatar.resize((192, 192), Image.ANTIALIAS)
        avatar_96x96 = avatar.resize((96, 96), Image.ANTIALIAS)
        avatar_48x48 = avatar.resize((48, 48), Image.ANTIALIAS)
        
        usr_home = os.path.expanduser('~')
        avatar_192x192.save(usr_home+"/www/mifan.tv/static/avatar/channel/b_%s.png" % avatar_name, "PNG")
        avatar_96x96.save(usr_home+"/www/mifan.tv/static/avatar/channel/m_%s.png" % avatar_name, "PNG")
        avatar_48x48.save(usr_home+"/www/mifan.tv/static/avatar/channel/s_%s.png" % avatar_name, "PNG")
        
        result = self.channel_model.set_channel_avatar_by_channel_id(channel_id, "%s.png" % avatar_name)
        template_variables["success_message"] = [u"频道头像更新成功"]

        self.redirect("/")