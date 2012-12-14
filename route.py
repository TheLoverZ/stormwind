# -*- coding: utf-8 -*-

import logging

import tornado.web

import home
import llist
import account

from stormwind.base import BaseHandler

class NotFoundHandler(BaseHandler):
    def get(self, _):
        raise tornado.web.HTTPError(404)

route = []
route.extend(home.route)
route.extend(llist.route)
route.extend(account.route)
route.append((r'(.*)', NotFoundHandler))
