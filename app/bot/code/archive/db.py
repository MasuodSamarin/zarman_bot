#!/usr/bin/env python3

import jdatetime
import logging

from peewee import *
from peewee import create_model_tables


db = SqliteDatabase('zarman.db')

class BaseModel(Model):
    class Meta:
        database = db


class Message(BaseModel):
    text = TextField()
    link = TextField()
    author_name = TextField()
    author_id = TextField()
    is_published = BooleanField()
    publish_date = DateField()
    created_date = DateField(default=jdatetime.date.today())




def connect():
    db.connect()
    db.create_tables([Message], True)

