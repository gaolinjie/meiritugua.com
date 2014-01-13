#!/usr/bin/env python
# coding=utf-8
#
## Copyright 2013 mifan.tv

import time
from lib.query import Query

class Head2Model(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "head2"
        super(Head2Model, self).__init__()

    def add_new_head2(self, head2_info):
        return self.data(head2_info).add()

    def get_head2_post(self):
        join = "LEFT JOIN post ON head2.post_id = post.id\
                LEFT JOIN user AS author_user ON post.author_id = author_user.uid"
        field = "post.*, \
                author_user.username as author_username, \
                author_user.avatar as author_avatar"
        return self.join(join).field(field).select()