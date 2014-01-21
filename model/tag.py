#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2013 mifan.tv

import time
from lib.query import Query

class TagModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "tag"
        super(TagModel, self).__init__()

    def get_all_tags(self):
        return self.select()