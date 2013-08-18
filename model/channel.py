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

