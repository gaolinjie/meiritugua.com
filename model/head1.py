#!/usr/bin/env python
# coding=utf-8
#
## Copyright 2013 mifan.tv

import time
from lib.query import Query

class Head1Model(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "head1"
        super(Head1Model, self).__init__()

    def add_new_head1(self, head1_info):
        return self.data(head1_info).add()

    def get_head1_post(self):
        join = "LEFT JOIN post ON head1.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar"
        return self.join(join).field(field).select()