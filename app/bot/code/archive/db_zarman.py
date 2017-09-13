#!/usr/bin/env python3

import datetime
import logging

from peewee import *
from peewee import create_model_tables


db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db


class Message(BaseModel):
    text = TextField(default='')
    link = TextField(default='')
    usr_name = TextField(default='')
    usr_id = TextField(default='')
    is_pub = BooleanField(default=False)
    p_date = DateField(default=datetime.date.today())
    c_date = DateField(default=datetime.date.today())

    def add_entry(self, user_data):
        default = ''
        text = user_data.get('text', default)
        link = user_data.get('link', default)
        usr_name = user_data.get('usr_name', default)
        usr_id = user_data.get('usr_id', default)
        p_date = user_data.get('g_date', datetime.date.today())

        m = Message(text=text, link=link, usr_name=usr_name,
                        usr_id=usr_id, p_date=p_date)
        m.save()

    def post_query(self, date=datetime.date.today(), is_pub=False):

        entries = Message.select().where(
                (Message.p_date==date) & (Message.is_pub == is_pub)).execute()
        return entries


def connect_to_db():
    db.connect()
    db.create_tables([Message], True)

