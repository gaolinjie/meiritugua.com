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

from lib.utils import find_video_id_from_url

class IndexHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "index")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels(user_id = user_info["uid"])
            template_variables["maylike_channels"] = self.channel_model.get_channels_by_nav_id(1, user_info["uid"])
            
            if(tab=="index"):
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.follow_model.get_user_all_follow_posts(user_id = user_info["uid"], current_page = page)
            else:
                if (tab=="video"):
                    nav_id=1
                if (tab=="micro"):
                    nav_id=2
                if (tab=="movie"):
                    nav_id=3
                if (tab=="star"):
                    nav_id=4
                template_variables["active_tab"] = tab
                template_variables["posts"] = self.follow_model.get_user_all_follow_posts_by_nav_id(user_id = user_info["uid"], nav_id = nav_id, current_page = page)           
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

        video_link = form.link.data
        video_id = find_video_id_from_url(video_link)
        json_link = "http://v.youku.com/player/getPlayList/VideoIDS/"+video_id+"/timezone/+08/version/5/source/out?password=&ran=2513&n=3"
        video_json = json.load(urllib2.urlopen(json_link))
        video_logo = video_json[u'data'][0][u'logo']
        video_title = video_json[u'data'][0][u'title']
        video_flash = "http://player.youku.com/player.php/sid/"+video_id+"/v.swf"
        print video_title

        video_info = {
            "source": "youku",
            "flash": video_flash,
            "link": video_link,
            "title": video_title,
            "thumb": video_logo,
        }
        vid = self.video_model.add_new_video(video_info)
        print vid

        channel_name = form.channel.data
        channel = self.channel_model.get_channel_by_name(channel_name = channel_name)
        
        post_info = {
            "author_id": self.current_user["uid"],
            "channel_id": channel["id"],
            "nav_id": channel["nav_id"],
            "video_id": vid,
            "intro": form.intro.data,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        self.post_model.add_new_post(post_info)


        self.redirect("/")

class FavoriteHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "index")
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels(user_id = user_info["uid"])
            
            if(tab=="index"):
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.favorite_model.get_user_all_favorites(user_id = user_info["uid"], current_page = page)           
            else:
                print tab
                if (tab=="video"):
                    nav_id=1
                if (tab=="micro"):
                    nav_id=2
                if (tab=="movie"):
                    nav_id=3
                if (tab=="star"):
                    nav_id=4
                template_variables["active_tab"] = tab
                template_variables["posts"] = self.favorite_model.get_user_all_favorite_posts_by_nav_id(user_id = user_info["uid"], nav_id = nav_id, current_page = page)           
        else:
            self.redirect("/login")

        self.render("favorite.html", **template_variables)

class LaterHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "index")
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels(user_id = user_info["uid"])
            
            if(tab=="index"):
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.later_model.get_user_all_laters(user_id = user_info["uid"], current_page = page)           
            else:
                print tab
                if (tab=="video"):
                    nav_id=1
                if (tab=="micro"):
                    nav_id=2
                if (tab=="movie"):
                    nav_id=3
                if (tab=="star"):
                    nav_id=4
                template_variables["active_tab"] = tab
                template_variables["posts"] = self.later_model.get_user_all_later_posts_by_nav_id(user_id = user_info["uid"], nav_id = nav_id, current_page = page)           
        else:
            self.redirect("/login")

        self.render("later.html", **template_variables)

class VideoHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "video"
        if(user_info):
            template_variables["active_tab"] = tab
            template_variables["subnavs"] = self.subnav_model.get_subnavs_by_nav_id(1)
            if (tab=="all"):
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id(1, user_info["uid"])
            else:
                subnav_id = self.subnav_model.get_subnav_by_subnav_name(tab).id
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id_and_subnav_id(1, user_info["uid"], subnav_id)
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

        if (form.subnav_name.data != "all"):
            subnav_id = self.subnav_model.get_subnav_by_subnav_name(form.subnav_name.data).id
            channel_info = {
                "name": form.name.data,
                "intro": form.intro.data,
                "nav_id": 1,
                "subnav_id": 1,
                "plus": 0,
                "followers": 0,
                "posts": 0,
                "author_id": self.current_user["uid"],
                "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        else:
            channel_info = {
                "name": form.name.data,
                "intro": form.intro.data,
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

        if (form.subnav_name.data != "all"):
            self.redirect("/video?tab="+form.subnav_name.data)
        else:
            self.redirect("/video")

class MicroHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "micro"        

        self.render("micro.html", **template_variables)

class MovieHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "movie"        

        self.render("movie.html", **template_variables)

class TVHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "tv"        

        self.render("tv.html", **template_variables)

class StarHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "star"        

        self.render("star.html", **template_variables)

    



class ChannelHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            template_variables["maylike_channels"] = self.channel_model.get_channels_by_nav_id(1, user_info["uid"])
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            plus = self.plus_model.get_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                template_variables["followed"]=1;
            else:
                template_variables["followed"]=0;
            if(plus):
                print "has plused"
                template_variables["plused"]=1;
            else:
                print "no plused"
                template_variables["plused"]=0;
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
        video_link = form.link.data
        video_id = find_video_id_from_url(video_link)
        json_link = "http://v.youku.com/player/getPlayList/VideoIDS/"+video_id+"/timezone/+08/version/5/source/out?password=&ran=2513&n=3"
        video_json = json.load(urllib2.urlopen(json_link))
        video_logo = video_json[u'data'][0][u'logo']
        video_title = video_json[u'data'][0][u'title']
        video_flash = "http://player.youku.com/player.php/sid/"+video_id+"/v.swf"
        print video_title

        video_info = {
            "source": "youku",
            "flash": video_flash,
            "link": video_link,
            "title": video_title,
            "thumb": video_logo,
        }
        vid = self.video_model.add_new_video(video_info)
        print vid

        channel = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
        
        post_info = {
            "author_id": self.current_user["uid"],
            "channel_id": channel_id,
            "nav_id": channel["nav_id"],
            "video_id": vid,
            "intro": form.intro.data,
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

class FollowHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                self.follow_model.delete_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_followed",
                }))
            else:
                channel = self.channel_model.get_channel_by_channel_id(channel_id)
                follow_info = {
                    "user_id": user_info["uid"],
                    "channel_id": channel_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.follow_model.add_new_follow(follow_info)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_followed",
                }))

class PlusChannelHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            channle = self.channel_model.get_channel_by_channel_id(channel_id = channel_id)
            plus = self.plus_model.get_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(plus):
                self.plus_model.delete_plus_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
                self.channel_model.update_channel_info_by_channel_id(channel_id, {"plus": channle.plus-1,})
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_plused",
                }))
            else:
                print "fasdfasd"
                plus_info = {
                    "type": "channel",
                    "user_id": user_info["uid"],
                    "object_id": channel_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.plus_model.add_new_plus(plus_info)
                self.channel_model.update_channel_info_by_channel_id(channel_id, {"plus": channle.plus+1,})
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_plused",
                }))

class CommentHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            comments = self.comment_model.get_all_comments_by_post_id(user_info["uid"], post_id)

            jarray = []
            i = 0
            for comment in comments:
                jobject = {
                    "content": comment.content,
                    "author_username": comment.author_username,
                    "author_avatar": comment.author_avatar
                }
                jarray.append(jobject)
                i=i+1

            self.write(lib.jsonp.print_JSON({"comments": jarray}))

    @tornado.web.authenticated
    def post(self, post_id, template_variables = {}):
        user_info = self.current_user

        data = json.loads(self.request.body)
        comment_content = data["comment_content"]

        if(user_info):
            comment_info = {
                "author_id": user_info["uid"],
                "post_id": post_id,
                "content": comment_content,
                "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            comment_id = self.comment_model.add_new_comment(comment_info)

            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            self.post_model.update_post_by_post_id(post_id, {"last_comment": comment_id, 
                                                            "comment_count": post.comment_count+1,})
            self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "successed",
            }))
        else:
            self.write(lib.jsonp.print_JSON({
                    "success": 0,
                    "message": "failed",
            }))

class RateHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self, post_id, template_variables = {}):
        user_info = self.current_user

        data = json.loads(self.request.body)
        score = data["score"]*2

        if(user_info):
            rate = self.rate_model.get_rate_by_post_id_and_user_id(user_info["uid"], post_id)
            post = self.post_model.get_post_by_post_id(post_id)
            if(rate):
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "rated",
                }))
            else:
                total_score = post.score * post.votes + score
                post_info = {
                    "score": total_score / (post.votes+1),
                    "votes": post.votes+1,
                }
                self.post_model.update_post_by_post_id(post_id, post_info)
                rate_info = {
                    "user_id": user_info["uid"],
                    "post_id": post_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.rate_model.add_new_rate(rate_info)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "successed",
                }))
        else:
            self.write(lib.jsonp.print_JSON({
                    "success": 0,
                    "message": "failed",
                }))

class FavoriteManagerHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            favorite = self.favorite_model.get_favorite_by_post_id_and_user_id(user_info["uid"], post_id)
            post = self.post_model.get_post_by_post_id(post_id)
            if(favorite):
                self.favorite_model.delete_favorite_info_by_user_id_and_post_id(user_info["uid"], post_id)
                self.post_model.update_post_by_post_id(post_id, {"favorite": post.favorite-1})
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_favorited",
                }))
            else:
                favorite_info = {
                    "user_id": user_info["uid"],
                    "post_id": post_id,
                    "nav_id": post.nav_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.favorite_model.add_new_favorite(favorite_info)
                self.post_model.update_post_by_post_id(post_id, {"favorite": post.favorite+1})
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_favorited",
                }))

class LaterManagerHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            later = self.later_model.get_later_by_post_id_and_user_id(user_info["uid"], post_id)
            post = self.post_model.get_post_by_post_id(post_id)
            if(later):
                self.later_model.delete_later_info_by_user_id_and_post_id(user_info["uid"], post_id)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_latered",
                }))
            else:
                later_info = {
                    "user_id": user_info["uid"],
                    "post_id": post_id,
                    "nav_id": post.nav_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                }
                self.later_model.add_new_later(later_info)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "success_latered",
                }))

class PostHandler(BaseHandler):
    def get(self, post_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):           
            template_variables["post"] = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
            template_variables["comments"] = self.comment_model.get_all_comments_by_post_id(post_id)
        else:
            self.redirect("/login")

        self.render("post.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        self.redirect("/")