#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 meiritugua.com

import time
from lib.query import Query

class VoteModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "vote"
        super(VoteModel, self).__init__()

    def add_new_vote(self, vote_info):
        return self.data(vote_info).add()

    def get_vote_by_post_id(self, post_id):
        where = "post_id = %s" % post_id
        return self.where(where).find()

    def delete_vote_by_post_id(self, post_id):
    	where = "post_id = %s" % post_id
        return self.where(where).delete()

    def update_vote_by_post_id(self, post_id, vote_info):
        where = "post_id = %s" % post_id
        return self.where(where).data(vote_info).save()
