#!/usr/bin/env python
# coding=utf-8
#
## Copyright 2013 meiritugua.com

import time
from lib.query import Query

class HotModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "hot"
        super(HotModel, self).__init__()

    def add_new_hot(self, hot_info):
        return self.data(hot_info).add()

    def get_hot_posts(self, num = 5, current_page = 1):
        join = "LEFT JOIN post ON hot.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        order = "post.created DESC, post.id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar"
        return self.order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_hot_posts_by_channel_id(self, channel_id, num = 5, current_page = 1):
        where = "post.channel_id = '%s'" % channel_id
        join = "LEFT JOIN post ON hot.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        order = "post.created DESC, post.id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_hot_posts_by_user_id(self, user_id, num = 5, current_page = 1):
        where = "post.author_id = %s" % user_id
        join = "LEFT JOIN post ON hot.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        order = "post.created DESC, post.id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_hot_by_post_id(self, post_id):
        where = "post_id = %s" % post_id
        return self.where(where).find()