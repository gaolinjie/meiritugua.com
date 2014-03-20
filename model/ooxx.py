#!/usr/bin/env python
# coding=utf-8
#
## Copyright 2013 meiritugua.com

import time
from lib.query import Query

class OoxxModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "ooxx"
        super(OoxxModel, self).__init__()

    def add_new_ooxx(self, ooxx_info):
        return self.data(ooxx_info).add()

    def get_ooxx_posts(self, num = 10, current_page = 1):
        join = "LEFT JOIN post ON ooxx.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        order = "post.created DESC, post.id DESC"
        field = "ooxx.*, \
                post.*, \
                author_user.username as author_username"
        return self.order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)


    def update_ooxx_by_post_id(self, post_id, ooxx_info):
        where = "ooxx.post_id = %s" % post_id
        return self.where(where).data(ooxx_info).save()

    def delete_ooxx_by_post_id(self, post_id):
        where = "ooxx.post_id = %s" % post_id
        return self.where(where).delete()

    def get_ooxx_by_post_id(self, post_id):
        where = "ooxx.post_id = %s" % post_id
        return self.where(where).find()