#!/usr/bin/env python
# coding=utf-8
#
## Copyright 2013 meiritugua.com

import time
from lib.query import Query

class HeadModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "head"
        super(HeadModel, self).__init__()

    def add_new_head(self, head1_info):
        return self.data(head1_info).add()

    def get_head_posts(self, num = 4, current_page = 1):
        join = "LEFT JOIN post ON head.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        order = "head.created DESC, head.id DESC"
        field = "head.*, \
                post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar"
        return self.order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)