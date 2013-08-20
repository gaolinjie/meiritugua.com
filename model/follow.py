#!/usr/bin/env python
# coding=utf-8
#
## Copyright 2013 tuila.me

import time
from lib.query import Query

class FollowModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "follow"
        super(FollowModel, self).__init__()

    def add_new_follow(self, follow_info):
        return self.data(follow_info).add()

    def get_follow_info_by_user_id_and_channel_id(self, user_id, channel_id):
        where = "user_id = %s AND channel_id = %s" % (user_id, channel_id)
        return self.where(where).find()

    def delete_follow_info_by_user_id_and_channel_id(self, user_id, channel_id):
        where = "user_id = %s AND channel_id = %s" % (user_id, channel_id)
        return self.where(where).delete()

    def get_user_follow_count(self, user_id):
        where = "user_id = %s" % user_id
        return self.where(where).count()

    def get_user_all_follow_posts(self, user_id, num = 16, current_page = 1):
        where = "follow.user_id = %s" % user_id
        join = "RIGHT JOIN post ON follow.channel_id = post.channel_id \
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid \
                LEFT JOIN channel ON post.channel_id = channel.id \
                LEFT JOIN video ON post.video_id = video.id \
                LEFT JOIN nav ON channel.nav_id = nav.id"
        order = "post.created DESC, post.id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                channel.id as channel_id, \
                channel.name as channel_name, \
                nav.name as nav_name, \
                nav.title as nav_title, \
                video.title as video_title, \
                video.thumb as video_thumb, \
                video.link as video_link"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

