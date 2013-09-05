#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 tuila.me

# cat /etc/mime.types
# application/octet-stream    crx

import sys
reload(sys)
sys.setdefaultencoding("utf8")

import os.path
import re
import memcache
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web


import handler.topic
import handler.user
import handler.channel

from tornado.options import define, options
from lib.loader import Loader
from lib.session import Session, SessionManager
from jinja2 import Environment, FileSystemLoader

define("port", default = 80, help = "run on the given port", type = int)
define("mysql_host", default = "localhost", help = "community database host")
define("mysql_database", default = "mifan", help = "community database name")
define("mysql_user", default = "mifan", help = "community database user")
define("mysql_password", default = "mifan", help = "community database password")

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            blog_title = u"mifan.tv",
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = False,
            cookie_secret = "cookie_secret_code",
            login_url = "/login",
            autoescape = None,
            jinja2 = Environment(loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")), trim_blocks = True),
            reserved = ["user", "topic", "home", "setting", "forgot", "login", "logout", "register", "admin"],
            debug=True,
        )

        handlers = [
            (r"/", handler.topic.IndexHandler),
            (r"/video", handler.topic.VideoHandler),
            (r"/c/(\d+)", handler.topic.ChannelHandler),
            (r"/u/(.*)", handler.topic.UserHandler),
            (r"/login", handler.user.LoginHandler),
            (r"/logout", handler.user.LogoutHandler),
            (r"/register", handler.user.RegisterHandler),
            (r"/forgot", handler.user.ForgotPasswordHandler),
            (r"/f/(\d+)", handler.topic.FollowHandler),
            (r"/p/(\d+)", handler.topic.PlusChannelHandler),
            (r"/comment/(\d+)", handler.topic.CommentHandler),
            (r"/setting", handler.user.SettingHandler),
            (r"/setting/avatar", handler.user.SettingAvatarHandler),
            (r"/setting/password", handler.user.SettingPasswordHandler),
            (r"/c/(\d+)/setting", handler.channel.ChannelSettingHandler),
            (r"/c/(\d+)/setting/avatar", handler.channel.ChannelSettingAvatarHandler),
            (r"/movie", handler.topic.MovieHandler),
            (r"/tv", handler.topic.TVHandler),
            (r"/star", handler.topic.StarHandler),

            (r"/(favicon\.ico)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(sitemap.*$)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(bdsitemap\.txt)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
            (r"/(orca\.txt)", tornado.web.StaticFileHandler, dict(path = settings["static_path"])),
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = torndb.Connection(
            host = options.mysql_host, database = options.mysql_database,
            user = options.mysql_user, password = options.mysql_password
        )

        # Have one global loader for loading models and handles
        self.loader = Loader(self.db)

        # Have one global model for db query
        self.user_model = self.loader.use("user.model")
        self.follow_model = self.loader.use("follow.model")
        self.post_model = self.loader.use("post.model")
        self.channel_model = self.loader.use("channel.model")
        self.plus_model = self.loader.use("plus.model")
        self.comment_model = self.loader.use("comment.model")
        self.subnav_model = self.loader.use("subnav.model")

        # Have one global session controller
        self.session_manager = SessionManager(settings["cookie_secret"], ["127.0.0.1:11211"], 0)

        # Have one global memcache controller
        self.mc = memcache.Client(["127.0.0.1:11211"])

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

