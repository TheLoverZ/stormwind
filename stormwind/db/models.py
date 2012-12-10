# -*- coding: utf-8 -*-

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

    def __init__(self, email, username, password):
        self.username = username
        self.username_lower = username.lower()
        self.email = email
        self.email_lower = email.lower()
        self.password = password 

class Auth(Base, baseModule):
    __tablename__ = "auth"
    member_id = Column(Integer, ForeignKey("member.id"))
    member = relation("Member")
    secret = Column(UnicodeText)

    def __init__(self, member_id, secret):
        self.member_id = member_id
        self.secret = secret
