#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineKeyboardMarkup, ReplyKeyboardMarkup
import logging



inline = [['hello', 'by'], ['inline']]
markup = InlineKeyboardMarkup(inline)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
chat_id = None
text = None

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def echo(bot, update):
    global text, chat_id
    update.message.reply_text(update.message.text)
    chat_id = update.message.chat_id
    text = update.message.text
    logger.log(logging.INFO, "text:{}, id:{}".format(text, chat_id))

def _print_res():
    global text, chat_id
    print("id:{}, text:{}".format(chat_id, text))

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

def receive_photo(bot,update):
    update.message.reply_text('i get the photo')
    file_name = update.message.document.file_name
    file_id = update.message.document.file_id
    df = bot.get_file(file_id=file_id)
    df.download(custom_path=file_name)


#def main():
# Create the EventHandler and pass it your bot's token.
TOKEN = "401217227:AAFWcAQ_lC33X9hwgnL3lYp2CdItJwhlD0o"
updater = Updater(TOKEN)

# Get the dispatcher to register handlers
dp = updater.dispatcher

# on different commands - answer in Telegram
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))

# on noncommand i.e message - echo the message on Telegram
dp.add_handler(MessageHandler(Filters.text, echo))
dp.add_handler(MessageHandler(Filters.document or Filters.photo, receive_photo))

# log all errors
dp.add_error_handler(error)

# Start the Bot
# updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
# updater.idle()


