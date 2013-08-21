#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 tuila.me

import time
from lib.query import Query

class ChannelModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "channel"
        super(ChannelModel, self).__init__()

    def get_all_channels(self):
        return self.select()

    def get_all_channels_count(self):
        return self.count()


    def get_channel_by_channel_id(self, channel_id):
        where = "id = '%s'" % channel_id
        return self.where(where).find()

    def get_channel_by_name(self, channel_name):
        where = "name = '%s'" % channel_name
        return self.where(where).find()

    def get_channels_by_nav_id(self, nav_id):
        where = "nav_id = '%s'" % nav_id
        return self.where(where).select()

    def get_user_all_channels(self, user_id):
        where = "author_id = '%s'" % user_id
        return self.where(where).select()

    def add_new_channel(self, channel_info):
        return self.data(channel_info).add()
    

