# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def init_db(engine):
    Base.metadata.create_all(bind=engine)
