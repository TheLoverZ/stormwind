# -*- coding: utf-8 -*-

import logging

import tornado.web

from stormwind.db.models import List
from stormwind.base import BaseHandler

class CreateListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        title = self.get_argument("title", None)
        if not title:
            title = "Untitled"
        llist = List(title, self.current_user.id)
        self.redirect("/%s/%d/" % self.current_user.username, llist.id)

route = [
    (r'/create', CreateListHandler), 
]
