# -*- coding: utf-8 -*-

import uuid
import binascii
import functools

from sqlalchemy.orm.exc import NoResultFound

from stormwind.db.models import *

def protect_one(method):
    '''Protect .one() method dont raise exception'''
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            retval = method(self, *args, **kwargs)
        except NoResultFound:
            return None
        return retval
    return wrapper

def insert(method):
    '''Insert object into database'''
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        retval = method(self, *args, **kwargs)
        self.db.add(retval)
        self.db.commit()
        return retval
    return wrapper

class MemberDBMixin(object):
    @protect_one
    def select_member_by_username_lower(self, username):
        return self.db.query(Member).filter_by(username_lower = username.lower()).one()
    @protect_one
    def select_member_by_email_lower(self, email):
        return self.db.query(Member).filter_by(email_lower = email.lower()).one()
    @insert
    def create_auth(self, member_id):
        random = binascii.b2a_hex(uuid.uuid4().bytes)
        return Auth(member_id, random)
