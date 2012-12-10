# -*- coding: utf-8 -*-

import logging
from stormwind.base import BaseHandler

class HomeHandler(BaseHandler):
    def get(self):
        self.render("home.html")

route = [
    (r'/', HomeHandler), 
]
