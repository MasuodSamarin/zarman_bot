#!/usr/bin/env python

import logging
import datetime

from peewee import *
from peewee import create_model_tables


db = SqliteDatabase('blog.db')

class BaseModel(Model):
    class Meta:
        database = db


class Blog(BaseModel):
    creator = CharField()
    name = CharField()


class Entry(BaseModel):
    blog = ForeignKeyField(Blog, related_name='entries')
    title = CharField()
    body = TextField()
    pub_date = DateTimeField()
    published = BooleanField(default=True)

    def query_creator(self, name):
        return Entry.select().join(Blog).where(
                Blog.creator==name).execute()


db.connect()
db.create_tables([Blog, Entry], True)


