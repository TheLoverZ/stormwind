# -*- coding: utf-8 -*-

import logging

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UnicodeText
from sqlalchemy.sql import func
from sqlalchemy.orm import relation
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def init_db(engine):
    Base.metadata.create_all(bind=engine)

class baseModule(object):
    id = Column(Integer, primary_key = True)
    createTime = Column(DateTime, default = func.current_timestamp()) 
    updateTime = Column(DateTime, default = func.current_timestamp())

class Member(Base, baseModule):
    __tablename__ = "member"
    username = Column(String(255))
    username_lower = Column(String(255))
    password = Column(UnicodeText)
    email = Column(UnicodeText)
    email_lower = Column(UnicodeText)
    locale = Column(String(255))
    weibo_id = Column(String(255), default = "")
    renren_id = Column(String(255), default = "")
    tencent_id = Column(String(255), default = "")

    def __init__(self, email, username, password, locale):
        self.username = username
        self.username_lower = username.lower()
        self.email = email
        self.email_lower = email.lower()
        self.password = password 
        self.locale = locale
        logging.info(email)
        email_name, email_domain = email.split('@') 
        if email_domain == "user.weibo.com":
            self.weibo_id = email_name
        elif email_domain == "user.renren.com":
            self.renren_id = email_name
        elif email_domain == "user.t.qq.com":
            self.tencent_id = email_name

class Auth(Base, baseModule):
    __tablename__ = "auth"
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("Member")
    secret = Column(UnicodeText)

    def __init__(self, member_id, secret):
        self.member_id = member_id
        self.secret = secret

class List(Base, baseModule):
    __tablename__ = "list"
    name = Column(UnicodeText)
    description = Column(UnicodeText, default = u"")
    slug = Column(String(255), default = "")
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("Member")

    def __init__(self, name, member_id):
        self.name = name
        self.member_id = member_id

class Entry(Base, baseModule):
    __tablename__ = "entry"
    type = Column(Integer)
    content = Column(UnicodeText) 
    list_id = Column(Integer, ForeignKey("list.id"))
    list = relation("List")

    def __init__(self, type, content, list_id):
        self.type = type
        self.content = content
        self.list_id = list_id

