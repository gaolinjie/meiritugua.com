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
from lib.utils import pretty_date

from lib.utils import find_video_id_from_url

class IndexHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "index")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            template_variables["navs"] = self.nav_model.get_all_navs()
            template_variables["channels"] = self.channel_model.get_user_all_channels2(user_id = user_info["uid"])
            template_variables["maylike_channels"] = self.follow_model.get_user_all_unfollow_channels(user_info["uid"])
            
            if(tab=="index"):
                template_variables["active_tab"] = "all"
                template_variables["posts"] = self.follow_model.get_user_all_follow_posts(user_id = user_info["uid"], current_page = page)
            else:
                nav_id=1
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
        tab = self.get_argument('tab', "post")
        template_variables = {}

        if (tab=="post"):
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

            post_id = self.post_model.add_new_post(post_info)

            self.channel_model.update_channel_info_by_channel_id(channel.id, {"posts": channel.posts+1})

            # create @username follow
            for username in set(find_mentions(form.intro.data)):
                print username
                mentioned_user = self.user_model.get_user_by_username(username)

                if not mentioned_user:
                    continue

                if mentioned_user["uid"] == self.current_user["uid"]:
                    continue

                if mentioned_user["uid"] == post_info["author_id"]:
                    continue

                self.follow_model.add_new_follow({
                    "user_id": mentioned_user.uid,
                    "post_id": post_id,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S'),
                })

            self.redirect("/")
        else:
            form = ChannelForm2(self)

            if not form.validate():
                self.get({"errors": form.errors})
                return

            nav = self.nav_model.get_nav_by_nav_title(form.nav.data)
            channel_info = {
                "name": form.name.data,
                "intro": form.intro.data,
                "nav_id": nav["id"],
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

            self.redirect("/c/"+str(channel["id"]))

class FavoriteHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "index")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
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
        page = int(self.get_argument("page", "1"))
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
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "video"
        if(user_info):
            notice_text = "暂时还没有短片频道"
            template_variables["notice_text"] = notice_text
            template_variables["active_tab"] = tab
            template_variables["subnavs"] = self.subnav_model.get_subnavs_by_nav_id(1)
            if (tab=="all"):
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id(1, user_info["uid"], current_page = page)
            else:
                subnav_id = self.subnav_model.get_subnav_by_subnav_name(tab).id
                template_variables["channels"] = self.channel_model.get_channels_by_nav_id_and_subnav_id(1, user_info["uid"], subnav_id, current_page = page)
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


        subnav_id = self.subnav_model.get_subnav_by_subnav_title(form.subnav.data).id
        channel_info = {
            "name": form.name.data,
            "intro": form.intro.data,
            "nav_id": 1,
            "subnav_id": subnav_id,
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

class FollowsHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            template_variables["active_tab"] = tab

            if (tab=="all"):
                template_variables["channels"] = self.follow_model.get_user_all_follow_channels(user_info["uid"], current_page = page)
            elif (tab=="mychannels"):
                template_variables["channels"] = self.channel_model.get_user_all_channels(user_info["uid"], current_page = page)
            notice_text = "你还未关注任何频道"
            if (tab == "user"):
                notice_text = "你还未关注任何人"
            if (tab == "mention"):
                notice_text = "你还未创建任何频道"
            template_variables["notice_text"] = notice_text
        else:
            self.redirect("/login")

        self.render("follow.html", **template_variables)

class NotificationsHandler(BaseHandler):
    def get(self, template_variables = {}):
        tab = self.get_argument('tab', "all")
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random

        if(user_info):
            template_variables["active_tab"] = tab
            if (tab=="all"):
                template_variables["notifications"] = self.notification_model.get_user_all_notifications(user_info["uid"], current_page = page)
            elif (tab=="comment"):
                template_variables["notifications"] = self.notification_model.get_user_all_notifications_by_involved_type(user_info["uid"], 1, current_page = page)
            elif (tab=="mention"):
                template_variables["notifications"] = self.notification_model.get_user_all_notifications_by_involved_type(user_info["uid"], 0, current_page = page)
            elif (tab=="allread"):
                self.notification_model.mark_user_unread_notification_as_read(user_info["uid"])
                self.redirect("/notification")
            notice_text = "暂时还没有消息"
            if (tab == "comment"):
                notice_text = "暂时还没有回复"
            if (tab == "mention"):
                notice_text = "暂时还没有人提到你"
            template_variables["notice_text"] = notice_text
        else:
            self.redirect("/login")

        self.render("notification.html", **template_variables)

class MicroHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "micro"        

        self.render("micro.html", **template_variables)

class MovieHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "movie"        

        self.render("movie.html", **template_variables)

class TVHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "tv"        

        self.render("tv.html", **template_variables)

class StarHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        template_variables["active_page"] = "star"        

        self.render("star.html", **template_variables)

    

class NotificationHandler(BaseHandler):
    def get(self, notification_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            notification = self.notification_model.get_notification_by_notification_id(notification_id = notification_id)
            self.notification_model.mark_notification_as_read_by_notification_id(notification_id = notification_id)
            self.redirect("/p/"+str(notification.involved_post_id))
        else:
            self.redirect("/login")

class ChannelHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("page", "1"))
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random
        if(user_info):
            template_variables["user_other_channels"] = self.channel_model.get_user_other_channels(user_info["uid"], channel_id)
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
            template_variables["posts"] = self.post_model.get_all_posts_by_channel_id(current_page = page, user_id = user_info["uid"], channel_id = channel_id)
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
        self.channel_model.update_channel_info_by_channel_id(channel.id, {"posts": channel.posts+1})

        self.redirect("/c/" + channel_id)

class UserHandler(BaseHandler):
    def get(self, user, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info
        template_variables["gen_random"] = gen_random    
        page = int(self.get_argument("page", "1"))
        
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels2(user_id = user_info["uid"])
            template_variables["user_all_channels"] = self.channel_model.get_user_all_channels(user_info["uid"], current_page = page)
            if(re.match(r'^\d+$', user)):
                view_user_info = self.user_model.get_user_by_uid(user)
            else:
                view_user_info = self.user_model.get_user_by_username(user)
            template_variables["view_user_info"] = view_user_info
            template_variables["posts"] = self.post_model.get_user_all_posts(current_page = page, user_id = view_user_info["uid"])
        else:
            self.redirect("/login")

        self.render("user.html", **template_variables)

class FollowHandler(BaseHandler):
    def get(self, channel_id, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            channel = self.channel_model.get_channel_by_channel_id(channel_id)
            follow = self.follow_model.get_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
            if(follow):
                self.follow_model.delete_follow_info_by_user_id_and_channel_id(user_info["uid"], channel_id)
                self.write(lib.jsonp.print_JSON({
                    "success": 1,
                    "message": "revert_followed",
                }))
                self.channel_model.update_channel_info_by_channel_id(channel_id, {"followers": channel.followers-1})
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
                self.channel_model.update_channel_info_by_channel_id(channel_id, {"followers": channel.followers+1})

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
            comments = self.comment_model.get_all_comments_by_post_id(post_id)

            jarray = []
            i = 0
            for comment in comments:
                jobject = {
                    "content": comment.content,
                    "author_username": comment.author_username,
                    "author_avatar": comment.author_avatar,
                    "created": pretty_date(comment.created)
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

            # create reply notification
            if not self.current_user["uid"] == post.author_id:
                self.notification_model.add_new_notification({
                    "trigger_user_id": self.current_user["uid"],
                    "involved_type": 1, # 0: mention, 1: reply
                    "involved_user_id": post.author_id,
                    "involved_post_id": post.id,
                    "involved_comment_id": comment_id,
                    "content": comment_content,
                    "status": 0,
                    "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                })

            # create @username notification
            for username in set(find_mentions(comment_content)):
                print username
                mentioned_user = self.user_model.get_user_by_username(username)

                if not mentioned_user:
                    continue

                if mentioned_user["uid"] == self.current_user["uid"]:
                    continue

                if mentioned_user["uid"] == post.author_id:
                    continue

                self.notification_model.add_new_notification({
                    "trigger_user_id": self.current_user["uid"],
                    "involved_type": 0, # 0: mention, 1: reply
                    "involved_user_id": mentioned_user["uid"],
                    "involved_post_id": post.id,
                    "involved_comment_id": comment_id,
                    "content": comment_content,
                    "status": 0,
                    "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                })
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
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
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
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
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
            post = self.post_model.get_post_by_post_id(user_info["uid"], post_id)
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

class LaterClearHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user

        if(user_info):
            later = self.later_model.delete_user_all_laters(user_info["uid"])
            self.redirect("/later")
            

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