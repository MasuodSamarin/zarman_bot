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
    p_date = DateField(default=datetime.date.today())
    c_date = DateField(default=datetime.date.today())

    def add_entry(self, user_data):
        default = ''
        text = user_data.get('text', default)
        link = user_data.get('link', default)
        hashtag = user_data.get('hashtag', default)
        usr_name = user_data.get('usr_name', default)
        usr_id = user_data.get('usr_id', default)
        p_date = user_data.get('g_date', datetime.date.today())

        m = Post(text=text, link=link, hashtag=hashtag, usr_name=usr_name,
                usr_id=usr_id, p_date=p_date)
        m.save()

    def today_job(self, date=datetime.date.today(), is_pub=False):
        entries = Post.select(Post.text, Post.link,
                Post.hashtag).where((Post.p_date==date) &
                        (Post.is_pub == is_pub))
        return entries.execute()

    def update_db(self):
        today = datetime.today()
        query = self.update(is_published=True).where(Tweet.creation_date < today)
        return query.execute()  # Returns the number of rows that were updated.

def connect_to_db():
    db.connect()
    db.create_tables([Post], True)

