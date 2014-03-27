#!/usr/bin/env python
# coding=utf-8
#
## Copyright 2013 meiritugua.com

import time
from lib.query import Query

class ItemModel(Query):
    def __init__(self, db):
        self.db = db
        self.table_name = "item"
        super(ItemModel, self).__init__()

    def add_new_item(self, item_info):
        return self.data(item_info).add()

    def get_all_items(self, num = 10, current_page = 1):
        join = "LEFT JOIN post ON item.post_id = post.id"
        order = "post.created DESC, post.id DESC"
        field = "item.*, \
                post.*"
        return self.order(order).join(join).field(field).pages(current_page = current_page, list_rows = num)


    def update_item_by_post_id(self, post_id, item_info):
        where = "item.post_id = %s" % post_id
        return self.where(where).data(item_info).save()

    def delete_item_by_post_id(self, post_id):
        where = "item.post_id = %s" % post_id
        return self.where(where).delete()

    def get_item_by_post_id(self, post_id):
        where = "item.post_id = %s" % post_id
        return self.where(where).find()