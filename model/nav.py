#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 meiritugua.com

import time
from lib.query import Query

class NavModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "nav"
        super(NavModel, self).__init__()

    def get_all_navs(self):
        return self.select()

    def get_all_navs_count(self):
        return self.count()


    def get_nav_by_nav_id(self, nav_id):
        where = "id = '%s'" % nav_id
        return self.where(where).find()

    def get_nav_by_nav_name(self, nav_name):
        where = "name = '%s'" % nav_name
        return self.where(where).find()

    def get_nav_by_nav_title(self, nav_title):
        where = "title = '%s'" % nav_title
        return self.where(where).find()

    def get_std_posts_by_nav_id(self, nav_id, num = 6, current_page = 1):
        where = "nav.id = '%s'" % nav_id
        join = "RIGHT JOIN channel ON nav.id = channel.nav_id\
                RIGHT JOIN std ON channel.id = std.channel_id\
                LEFT JOIN post ON std.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        order = "post.created DESC, post.id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)


    def get_hot_posts_by_nav_id(self, nav_id, num = 6, current_page = 1):
        where = "nav.id = '%s'" % nav_id
        join = "RIGHT JOIN channel ON nav.id = channel.nav_id\
                RIGHT JOIN hot ON channel.id = hot.channel_id\
                LEFT JOIN post ON hot.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        order = "post.created DESC, post.id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)