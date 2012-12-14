# -*- coding: utf-8 -*-

import logging

from stormwind.base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        if not self.current_user:
            self.render("home.public.html")
        self.render("home.user.html")

route = [
    (r'/', HomeHandler), 
]
