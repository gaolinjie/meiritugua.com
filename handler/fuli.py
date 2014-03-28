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
import os

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

class FuliHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        p = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active"] = "fuli"
        template_variables["navs"] = self.nav_model.get_all_navs()
        template_variables["channels"] = self.channel_model.get_all_channels()

        template_variables["items"] = self.item_model.get_all_items(current_page = p)
    
        if is_mobile_browser(self):
            self.render("fuli.html", **template_variables)
        else:
            self.render("fuli.html", **template_variables)

class AddItemHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["channels"] = self.channel_model.get_all_channels()

        policy = qiniu.rs.PutPolicy(bucket_name)
        uptoken = policy.token()
        template_variables["up_token"] = uptoken
        
        self.render("add.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = AddForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        if form.visible.data=='公开':
            visible = 1
        else:
            visible = 0

        # continue while validate succeed
        channel = self.channel_model.get_channel_by_channel_title(form.channel.data)
        post_info = {
            "author_id": self.current_user["uid"],           
            "title": form.title.data,
            "intro": form.intro.data,
            "content": form.content.data,
            "type": 'item',
            "channel_id": channel.id,
            "visible": visible,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        post_id = self.post_model.add_new_post(post_info)

        if form.price.data:
            price = float(form.price.data)
        else:
            price = 0

        item_info = {
            "post_id": post_id,           
            "channel_id": channel.id,
            "price": price,
            "link": form.link.data,
            "label": form.label.data,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        item_id = self.item_model.add_new_item(item_info)

        if form.visible.data=='公开':
            std_id = self.std_model.add_new_std({"post_id": post_id, "channel_id": channel.id, "created": time.strftime('%Y-%m-%d %H:%M:%S')})

        # process tags
        tagStr = form.tag.data
        if tagStr:
            print 'process tags'
            tagNames = tagStr.split(',')  
            for tagName in tagNames:  
                tag = self.tag_model.get_tag_by_tag_name(tagName)
                if tag:
                    self.post_tag_model.add_new_post_tag({"post_id": post_id, "tag_id": tag.id})
                    self.tag_model.update_tag_by_tag_id(tag.id, {"post_num": tag.post_num+1})
                else:
                    tag_id = self.tag_model.add_new_tag({"name": tagName, "post_num": 1, "created": time.strftime('%Y-%m-%d %H:%M:%S')})
                    self.post_tag_model.add_new_post_tag({"post_id": post_id, "tag_id": tag_id})

        # add vote
        self.vote_model.add_new_vote({'post_id': post_id})

        self.redirect("/p/"+str(post_id))

        # process post thumb
        policy = qiniu.rs.PutPolicy(bucket_name)
        uptoken = policy.token()
        usr_home = os.path.expanduser('~')

        thumb_name = "%s" % uuid.uuid5(uuid.NAMESPACE_DNS, str(post_id))
        thumb_raw = self.request.files["thumb"][0]["body"]
        thumb_buffer = StringIO.StringIO(thumb_raw)
        thumb_origin = Image.open(thumb_buffer)

        thumb_origin.save(usr_home+"/www/meiritugua.com/static/thumb/o_%s.png" % thumb_name, "PNG")
        data=open(usr_home+"/www/meiritugua.com/static/thumb/o_%s.png" % thumb_name)
        ret, err = qiniu.io.put(uptoken, "o_"+thumb_name, data)
        os.remove(usr_home+"/www/meiritugua.com/static/thumb/o_%s.png" % thumb_name)

        # crop avatar if it's not square
        thumb_x = int(form.x1.data)
        thumb_y = int(form.y1.data)
        thumb_x2 = int(round(float(form.x2.data)))
        thumb_y2 = int(round(float(form.y2.data)))
        thumb_crop_region = (thumb_x, thumb_y, thumb_x2, thumb_y2)
        thumb = thumb_origin.crop(thumb_crop_region)

        #thumb_125x83 = thumb.resize((580, 197), Image.ANTIALIAS)
        thumb.save(usr_home+"/www/meiritugua.com/static/thumb/n_%s.png" % thumb_name, "PNG")

        data=open(usr_home+"/www/meiritugua.com/static/thumb/n_%s.png" % thumb_name)
        ret, err = qiniu.io.put(uptoken, "n_"+thumb_name, data)
        os.remove(usr_home+"/www/meiritugua.com/static/thumb/n_%s.png" % thumb_name)

        cover = "http://mrtgimg.qiniudn.com/o_" + thumb_name
        result = self.post_model.update_post_by_post_id(post_id, {"thumb": thumb_name, "cover": cover})


class EditItemHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["channels"] = self.channel_model.get_all_channels()
        template_variables["item"] = self.item_model.get_item_by_post_id(post_id)
        tags = self.post_tag_model.get_post_all_tags(post_id)
        tagStr = ''
        for tag in tags["list"]:
            tagStr += tag.tag_name + ','
        template_variables["tag_str"] = tagStr

        policy = qiniu.rs.PutPolicy(bucket_name)
        uptoken = policy.token()
        template_variables["up_token"] = uptoken
        print uptoken

        self.render("edit-item.html", **template_variables)

    @tornado.web.authenticated
    def post(self, post_id, template_variables = {}):
        template_variables = {}

        # validate the fields
        form = EditItemForm(self)

        if not form.validate():
            self.get({"errors": form.errors})
            return

        if form.visible.data=='公开':
            visible = 1
        else:
            visible = 0

        # continue while validate succeed
        channel = self.channel_model.get_channel_by_channel_title(form.channel.data)
        post_info = {        
            "title": form.title.data,
            "intro": form.intro.data,
            "content": form.content.data,
            "channel_id": channel.id,
            "visible": visible,
        }

        self.post_model.update_post_by_post_id(post_id, post_info)
        post = self.post_model.get_post_by_post_id(post_id)

        if form.price.data:
            price = float(form.price.data)
        else:
            price = 0

        item_info = {      
            "channel_id": channel.id,
            "price": price,
            "link": form.link.data,
            "label": form.label.data,
        }
        item_id = self.item_model.update_item_by_post_id(post_id, item_info)

        if form.visible.data=='公开':
            std_id = self.std_model.get_std_by_post_id(post_id)
            if std_id == None:
                std_id = self.std_model.add_new_std({"post_id": post_id, "channel_id": channel.id, "created": time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                self.std_model.update_std_by_post_id(post_id, {"channel_id": channel.id})
                self.hot_model.update_hot_by_post_id(post_id, {"channel_id": channel.id})
        else:
            print '不公开'
            self.std_model.delete_std_by_post_id(post_id)
            self.hot_model.delete_hot_by_post_id(post_id)

        # process tags
        tagStr = form.tag.data
        if tagStr:
            self.post_tag_model.delete_post_tag_by_post_id(post_id)
            tags = self.post_tag_model.get_post_all_tags(post_id)
            for tag in tags["list"]:
                self.tag_model.update_tag_by_tag_id(tag.id, {"post_num": tag.post_num-1})
            tagNames = tagStr.split(',')
            for tagName in tagNames:  
                tag = self.tag_model.get_tag_by_tag_name(tagName)
                if tag:
                    self.post_tag_model.add_new_post_tag({"post_id": post_id, "tag_id": tag.id})
                    self.tag_model.update_tag_by_tag_id(tag.id, {"post_num": tag.post_num+1})
                else:
                    tag_id = self.tag_model.add_new_tag({"name": tagName, "post_num": 1, "created": time.strftime('%Y-%m-%d %H:%M:%S')})
                    self.post_tag_model.add_new_post_tag({"post_id": post_id, "tag_id": tag_id})

        self.redirect("/p/"+post_id)

        # process post thumb
        thumb_file = self.request.files
        if thumb_file:
            thumb_name = post.thumb
            thumb_raw = self.request.files["thumb"][0]["body"]
            thumb_buffer = StringIO.StringIO(thumb_raw)
            thumb_origin = Image.open(thumb_buffer)

            policy = qiniu.rs.PutPolicy(bucket_name+":o_"+thumb_name)
            uptoken = policy.token()
            usr_home = os.path.expanduser('~')

            thumb_origin.save(usr_home+"/www/meiritugua.com/static/thumb/o_%s.png" % thumb_name, "PNG")
            data=open(usr_home+"/www/meiritugua.com/static/thumb/o_%s.png" % thumb_name)
            ret, err = qiniu.io.put(uptoken, "o_"+thumb_name, data)
            os.remove(usr_home+"/www/meiritugua.com/static/thumb/o_%s.png" % thumb_name)

            # crop avatar if it's not square
            thumb_x = int(form.x1.data)
            thumb_y = int(form.y1.data)
            thumb_x2 = int(round(float(form.x2.data)))
            thumb_y2 = int(round(float(form.y2.data)))
            thumb_crop_region = (thumb_x, thumb_y, thumb_x2, thumb_y2)
            thumb = thumb_origin.crop(thumb_crop_region)
            thumb = thumb_origin.crop(thumb_crop_region)

            thumb_125x83 = thumb.resize((580, 197), Image.ANTIALIAS)
            thumb_125x83.save(usr_home+"/www/meiritugua.com/static/thumb/n_%s.png" % thumb_name, "PNG")

            policy = qiniu.rs.PutPolicy(bucket_name+":n_"+thumb_name)
            uptoken = policy.token()
            data=open(usr_home+"/www/meiritugua.com/static/thumb/n_%s.png" % thumb_name)
            ret, err = qiniu.io.put(uptoken, "n_"+thumb_name, data)
            if err is not None:
                print 'Error'+err
            else:
                print 'Success'
            os.remove(usr_home+"/www/meiritugua.com/static/thumb/n_%s.png" % thumb_name)

            cover = "http://mrtgimg.qiniudn.com/o_" + thumb_name
            result = self.post_model.update_post_by_post_id(post_id, {"thumb": thumb_name, "cover": cover})