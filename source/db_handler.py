#!/usr/bin/env python3

import datetime
import logging

from peewee import *
from peewee import create_model_tables


db = SqliteDatabase('database.db')
# db = SqliteDatabase(':memory:')

class BaseModel(Model):
    class Meta:
        database = db


class Post(BaseModel):
    text = TextField(default='')
    link = TextField(default='')
    hashtag = TextField(default='')
    usr_name = CharField(default='')
    usr_id = CharField(default='')
    is_pub = BooleanField(default=False)
    p_datetime = DateTimeField(default=datetime.datetime.now())
    c_datetime = DateTimeField(default=datetime.datetime.now())

    pocket = TextField()

    def add_entry(self, user_data):
        default = ''
        text = user_data.get('text', default)
        link = user_data.get('link', default)
        hashtag = user_data.get('hashtag', default)
        usr_name = user_data.get('usr_name', default)
        usr_id = user_data.get('usr_id', default)
        p_datetime = user_data.get('g_date', datetime.datetime.now)

        pocket = user_data.get('pocket', default)

        m = Post(text=text, link=link, hashtag=hashtag, usr_name=usr_name,
                usr_id=usr_id, is_pub=False, p_datetime=p_datetime, pocket=pocket)
        m.save()

    def post_query(self, now=datetime.datetime.now(), pub=False):
        entries = Post.select().where((Post.p_datetime<=now) &
                        (Post.is_pub == pub))
        return entries.execute()

    def update_db(self, id_, publish=True):
        query = self.update(is_pub=publish).where(Post.id == id_)
        return query.execute()  # Returns the number of rows that were updated.

def connect_to_db():
    db.connect()
    db.create_tables([Post], True)

