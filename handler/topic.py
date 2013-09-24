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
        if(user_info):
            template_variables["channels"] = self.channel_model.get_user_all_channels(user_id = user_info["uid"])
            
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

class ForumHandler(BaseHandler):
    def get(self, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        template_variables["user_info"] = user_info
        if(user_info):
            template_variables["user_info"]["counter"] = {
                "topics": self.topic_model.get_user_all_topics_count(user_info["uid"]),
                "replies": self.reply_model.get_user_all_replies_count(user_info["uid"]),
                "notifications": self.notification_model.get_user_unread_notification_count(user_info["uid"]),
                "favorites": self.favorite_model.get_user_favorite_count(user_info["uid"]),
            }
            template_variables["topics"] = self.topic_model.get_all_topics(current_page = page)           
        else:
            self.redirect("/register")

        template_variables["status_counter"] = {
            "users": self.user_model.get_all_users_count(),
            "nodes": self.node_model.get_all_nodes_count(),
            "topics": self.topic_model.get_all_topics_count(),
            "replies": self.reply_model.get_all_replies_count(),
        }
        template_variables["node"] = self.node_model.get_node_by_node_slug("qna")    
        template_variables["planes"] = self.plane_model.get_all_planes_with_nodes()
        template_variables["hot_nodes"] = self.node_model.get_all_hot_nodes()
        template_variables["hot_topics"] = self.topic_model.get_all_hot_topics()         
        template_variables["gen_random"] = gen_random    
        notice_text = "暂时还没有话题，发出您的讨论吧。"
        template_variables["notice_text"] = notice_text
        self.render("topics.html", **template_variables)

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
                "subnav_id": subnav_id,
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
            "nav_id": 1,
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
        
        post_info = {
            "author_id": self.current_user["uid"],
            "channel_id": channel_id,
            "video_id": 1,
            "intro": form.intro.data,
            "plus": 1,
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
            comments = self.comment_model.get_all_comments_by_post_id(post_id)

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

            post = self.post_model.get_post_by_post_id(post_id)
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

class CreateTopicHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, node = None, template_variables = {}):
        user_info = self.current_user
        template_variables["user_info"] = user_info

        template_variables["gen_random"] = gen_random
        node_slug = self.get_argument('n', "qna")
        node = self.node_model.get_node_by_node_slug(node_slug)
        template_variables["node"] = node
        self.render("topic/create.html", **template_variables)

    @tornado.web.authenticated
    def post(self, node = None, template_variables = {}):
        print "CreateHandler:post"
        template_variables = {}

        node_slug = self.get_argument('n', "qna")
        node = self.node_model.get_node_by_node_slug(node_slug)

        # validate the fields
        form = CreateForm(self)

        if not form.validate():
            self.get(node_slug, {"errors": form.errors})
            return

        # continue while validate succeed
        
        topic_info = {
            "author_id": self.current_user["uid"],
            "title": form.title.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "node_id": node["id"],
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
            "reply_count": 0,
            "last_touched": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        reply_id = self.topic_model.add_new_topic(topic_info)

        # update toptic count of the node
        topic_count = node["topic_count"] + 1
        self.node_model.set_node_topic_count_by_node_slug(node_slug, topic_count)

        self.redirect("/forum")

class ViewHandler(BaseHandler):
    def get(self, topic_id, template_variables = {}):
        user_info = self.current_user
        page = int(self.get_argument("p", "1"))
        user_info = self.get_current_user()
        template_variables["user_info"] = user_info

        template_variables["gen_random"] = gen_random
        template_variables["topic"] = self.topic_model.get_topic_by_topic_id(topic_id)

        # check reply count and cal current_page if `p` not given
        reply_num = 16
        reply_count = template_variables["topic"]["reply_count"]
        reply_last_page = (reply_count / reply_num + (reply_count % reply_num and 1)) or 1
        page = int(self.get_argument("p", reply_last_page))
        template_variables["reply_num"] = reply_num
        template_variables["current_page"] = page

        template_variables["replies"] = self.reply_model.get_all_replies_by_topic_id(topic_id, user_info["uid"], current_page = page)

        # update topic reply_count and hits

        self.topic_model.update_topic_by_topic_id(topic_id, {
            "reply_count": template_variables["replies"]["page"]["total"],
            "hits": (template_variables["topic"]["hits"] or 0) + 1,
        })

        self.render("topic/view.html", **template_variables)

    @tornado.web.authenticated
    def post(self, template_variables = {}):
        template_variables = {}

        # validate the fields

        form = ReplyForm(self)

        if not form.validate():
            self.get(form.tid.data, {"errors": form.errors})
            return

        # continue while validate succeed

        topic_info = self.topic_model.get_topic_by_topic_id(form.tid.data)
        replied_info = self.reply_model.get_user_reply_by_topic_id(self.current_user["uid"], form.tid.data)

        if(not topic_info):
            template_variables["errors"] = {}
            template_variables["errors"]["invalid_topic_info"] = [u"要回复的帖子不存在"]
            self.get(template_variables)
            return

        reply_info = {
            "author_id": self.current_user["uid"],
            "topic_id": form.tid.data,
            # "content": XssCleaner().strip(form.content.data),
            "content": form.content.data,
            "created": time.strftime('%Y-%m-%d %H:%M:%S'),
        }

        reply_id = self.reply_model.add_new_reply(reply_info)

        # update topic last_replied_by and last_replied_time

        self.topic_model.update_topic_by_topic_id(form.tid.data, {
            "last_replied_by": self.current_user["uid"],
            "last_replied_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            "last_touched": time.strftime('%Y-%m-%d %H:%M:%S'),
        })

        # create reply notification

        if not self.current_user["uid"] == topic_info["author_id"]:
            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 1, # 0: mention, 1: reply
                "involved_user_id": topic_info["author_id"],
                "involved_topic_id": form.tid.data,
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # create @username notification

        for username in set(find_mentions(form.content.data)):
            print username
            mentioned_user = self.user_model.get_user_by_username(username)

            if not mentioned_user:
                continue

            if mentioned_user["uid"] == self.current_user["uid"]:
                continue

            if mentioned_user["uid"] == topic_info["author_id"]:
                continue

            self.notification_model.add_new_notification({
                "trigger_user_id": self.current_user["uid"],
                "involved_type": 0, # 0: mention, 1: reply
                "involved_user_id": mentioned_user["uid"],
                "involved_topic_id": form.tid.data,
                "content": form.content.data,
                "status": 0,
                "occurrence_time": time.strftime('%Y-%m-%d %H:%M:%S'),
            })

        # update reputation of topic author
        if not self.current_user["uid"] == topic_info["author_id"] and not replied_info:
            topic_time_diff = datetime.datetime.now() - topic_info["created"]
            reputation = topic_info["author_reputation"] or 0
            reputation = reputation + 2 * math.log(self.current_user["reputation"] or 0 + topic_time_diff.days + 10, 10)
            self.user_model.set_user_base_info_by_uid(topic_info["author_id"], {"reputation": reputation})

        # self.get(form.tid.data)
        self.redirect("/t/%s#reply%s" % (form.tid.data, topic_info["reply_count"] + 1))