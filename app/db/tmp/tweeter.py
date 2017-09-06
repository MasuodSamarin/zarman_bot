#!/usr/bin/env python

import logging
import datetime

from peewee import *
from peewee import create_model_tables


db = SqliteDatabase('tmp.db')

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    pass


class Tweet(BaseModel):
    user = ForeignKeyField(User, related_name='tweets')
    message = TextField()
    created_date = DateField(default=datetime.date.today())
    is_published = BooleanField(default=True)
    pass


db.connect()
db.create_tables([User, Tweet], safe=True)


