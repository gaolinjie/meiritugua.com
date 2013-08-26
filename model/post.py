#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 tuila.me

import time
from lib.query import Query

class PostModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "post"
        super(PostModel, self).__init__()

    def get_all_posts_by_channel_id(self, num = 32, current_page = 1, channel_id = None):
        where = "channel.id = '%s'" % channel_id
        join = "LEFT JOIN user AS author_user ON post.author_id = author_user.uid \
                LEFT JOIN channel ON post.channel_id = channel.id \
                LEFT JOIN video ON video_id = video.id \
                LEFT JOIN nav ON channel.nav_id = nav.id \
                LEFT JOIN comment ON post.last_comment = comment.id \
                LEFT JOIN user AS comment_user ON comment.author_id = comment_user.uid"
        order = "created DESC, id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                author_user.uid as author_uid, \
                channel.name as channel_name, \
                nav.name as nav_name, \
                nav.title as nav_title, \
                video.title as video_title, \
                video.thumb as video_thumb, \
                video.link as video_link, \
                comment.content as comment_content, \
                comment.created as comment_created, \
                comment_user.username as comment_user_name, \
                comment_user.avatar as comment_user_avatar"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_user_all_posts(self, num = 32, current_page = 1, user_id = None):
        where = "post.author_id = '%s'" % user_id
        join = "LEFT JOIN user AS author_user ON post.author_id = author_user.uid \
                LEFT JOIN channel ON post.channel_id = channel.id \
                LEFT JOIN video ON video_id = video.id \
                LEFT JOIN nav ON channel.nav_id = nav.id \
                LEFT JOIN comment ON post.last_comment = comment.id \
                LEFT JOIN user AS comment_user ON comment.author_id = comment_user.uid"
        order = "created DESC, id DESC"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                author_user.uid as author_uid, \
                channel.id as channel_id, \
                channel.name as channel_name, \
                nav.name as nav_name, \
                nav.title as nav_title, \
                video.title as video_title, \
                video.thumb as video_thumb, \
                video.link as video_link, \
                comment.content as comment_content, \
                comment.created as comment_created, \
                comment_user.username as comment_user_name, \
                comment_user.avatar as comment_user_avatar"
        return self.where(where).order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)

    def get_user_all_posts_count(self, uid):
        where = "author_id = %s" % uid
        return self.where(where).count()

    def get_post_by_post_id(self, post_id):
        where = "post.id = %s" % post_id
        join = "LEFT JOIN user AS author_user ON post.author_id = author_user.uid \
                LEFT JOIN channel ON post.channel_id = channel.id"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar, \
                author_user.uid as author_uid, \
                channel.name as channel_name"
        return self.where(where).join(join).field(field).find()

    def add_new_post(self, post_info):
        return self.data(post_info).add()

    def update_post_by_post_id(self, post_id, post_info):
        where = "post.id = %s" % post_id
        return self.where(where).data(post_info).save()

