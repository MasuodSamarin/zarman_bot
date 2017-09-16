#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from telegram import ReplyKeyboardMarkup, MessageEntity, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler,
                            MessageHandler, Filters,
                            RegexHandler,ConversationHandler)
import telegram

import logging
import jdatetime
import locale

from help_msg import *
from db_handler import *
# from keyboards import *

#const info
zarman_channel_id = -1001124038908
# zarman_channel_id = -1001134097906
zarman_channel_name = "@this_is_my_channel"

zarman_base_text = '{text} <a href="{link}" > &#8207; </a>'



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
print('__name__:', __name__)


# States of the bot
MAIN, NEW_MSG, SENDING, QUERY, DATE_TIME = range(5)

# markup keyboard definition
'''
reply_keyboard = [['Text', 'Photo'],
                  ['Channel ID', 'Preview'],
                  ['Publish']]
'''

#TODO esme in variable ha ro grohi avaz kon
repKey_main = [['/new_message', '/query_message']]
repKey_newMsg = [['/send_message', '/reset']]
repKey_sending = [['/publish', '/put_on_qeue'], ['/reset']]
repKey_query = [['/not_publish_messages', '/show_All_messages'],
                    ['/show_from_to_messages', '/reset']]
repkey_datetime = [['/enqeue', '/reset']]

markup_main = ReplyKeyboardMarkup(repKey_main, one_time_keyboard=True)
markup_newMsg = ReplyKeyboardMarkup(repKey_newMsg, one_time_keyboard=True)
markup_sending = ReplyKeyboardMarkup(repKey_sending, one_time_keyboard=True)
markup_query = ReplyKeyboardMarkup(repKey_query, one_time_keyboard=True)
markup_date_time = ReplyKeyboardMarkup(repkey_datetime, one_time_keyboard=True)




# Helper functions-----------------------------------------------------------------------------------------------------------------------

# error handler add to dispatcher in the updater object
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))

# MAIN state
def start(bot, update):
    update.message.reply_text(f_msg_wellcome, reply_markup=markup_main)
    return MAIN


def new_message(bot, update, user_data):
    '''MAIN State handler function'''
    update.message.reply_text(f_msg_start, reply_markup=markup_newMsg)
    return NEW_MSG

def query_message(bot, update, user_data):
    '''MAIN State handler function'''
    update.message.reply_text(' hanus kar nmikone lotfan /reset o bezan ',
            reply_markup=markup_query)
    return QUERY

def parse_message_handler(bot, update, user_data):

    entities = update.message.parse_entities(
            types=telegram.MessageEntity.ALL_TYPES)
    text = update.message.text
    hashtag = list()
    link = ''

    for k, v in entities.items():
        if k.type == telegram.MessageEntity.TEXT_LINK:
            link = str(k.url).strip()

        elif k.type == telegram.MessageEntity.URL:
            link = str(v).strip()

        elif k.type == telegram.MessageEntity.HASHTAG:
            hashtag.append(str(v).strip())


        a = text.find(str(v).strip())
        b = a + int(k.length)
        text = text.replace(text[a: b], '')


    text_spl = text.splitlines()
    text_final = list()
    for l in text_spl:
        if len(l)>0 and l[0] != '*':
            wt = '\t\t\t\t\t\t{}'.format(l)
            text_final.append(wt)
        else:
            text_final.append(l)
    text = '\n'.join(text_final)



    if not user_data.get('text'):
        user_data['text'] = ''
        user_data['text'] = text
    if not user_data.get('hashtag'):
        user_data['hashtag'] =''
        user_data['hashtag'] = (' '.join(hashtag)).strip()
    if not user_data.get('link'):
        user_data['link'] = ''
        user_data['link'] = link.strip()

    if user_data.get('text'):
        update.message.reply_text(f_msg_get_text , reply_markup=markup_newMsg)

    if user_data.get('link'):
        update.message.reply_text(f_msg_get_link , reply_markup=markup_newMsg)

    if user_data.get('hashtag'):
        update.message.reply_text(f_msg_get_hashtg , reply_markup=markup_newMsg)

    if user_data.get('text'):
        text = '\n{}\n'.format(user_data.get('text'))
        user_data['pocket'] = text

    if user_data.get('link'):
        link = '\n<a href="{}" > &#8207; </a>\n'.format(user_data.get('link'))
        user_data['pocket'] += link

    if user_data.get('hashtag'):
        hashtag = '\n{}\n'.format(user_data.get('hashtag'))
        user_data['pocket'] += hashtag

        user_data['pocket'] = text

    not_print_line = '\n<a> &#8207; </a>\n'*3
    text = '{0}{1}{2}'.format(not_print_line, user_data['pocket'], not_print_line)

    user_data['pocket'] = text

#     update.message.reply_text(text=user_data['pocket'] + '\n\n',
#             parse_mode=telegram.ParseMode.HTML)

    return NEW_MSG


def _make_post(user_data):
    pass

#NEW_MSG State
def send_message_handler(bot, update, user_data):
    '''NEW_MSG State handler function'''
    if not user_data.get('text'):
        update.message.reply_text('**hanuz text onaferestadi !!!***',
                reply_markup = markup_newMsg)
        return NEW_MSG
    else:

        update.message.reply_text('poste morede nazar o barat mifrestam '
                'bebin khube ya na age mikhay haminalan post she /sendnow'
                ' ro bezan age mikhay set time koni /enqeue bezan age ham'
                ' narahti /canselo bezan', reply_markup=markup_sending)
    if user_data.get('text'):
        text = '\n{}\n'.format(user_data.get('text'))
        user_data['pocket'] = text

    if user_data.get('link'):
        link = '\n<a href="{}" > &#8207; </a>\n'.format(user_data.get('link'))
        user_data['pocket'] += link

    if user_data.get('hashtag'):
        hashtag = '\n{}\n'.format(user_data.get('hashtag'))
        user_data['pocket'] += hashtag


    update.message.reply_text(text=user_data['pocket'] + '\n\n',
            parse_mode=telegram.ParseMode.HTML)


    if user_data.get('link'):
        user_data['pocket'] = '\n{0}\n<a href="{2}" > &#8207; </a>\n{1}'.format(
                user_data.get('text'), user_data.get('hashtag'),
                user_data.get('link'))

    elif user_data.get('hashtag'):
        user_data['pocket'] = '\n{}\n{}\n'.format(user_data.get('text'),
                user_data.get('hashtag'))

    elif user_data.get('text'):
        user_data['pocket'] = '\n{}\n'.format(user_data.get('text'))

    else:
        user_data['pocket'] = '\n'

    update.message.reply_text(text=user_data['pocket'] + '\n\n\t\t\t',
            parse_mode=telegram.ParseMode.HTML)

    return SENDING


def done(bot, update, user_data):
    '''NEW_MSG State handler function'''
    update.message.reply_text(' hamechiz reset shod.  baraye shoro 2bare'
            ' /start obezan')




def reset(bot, update, user_data):
    '''NEW_MSG State handler function'''
    update.message.reply_text(' hamechiz reset shod.  baraye shoro 2bare'
           ' /start obezan')

    user_data.clear()
    return ConversationHandler.END

def Preview(bot, update, user_data):
    '''NEW_MSG State handler function'''
    update.message.reply_text('reset ', reply_markup=markup_main)
    return MAIN


def publish(bot, update, user_data):
    '''SENDING State handler function'''
    update.message.reply_text('post o barat ersalmikonam be chanal zarman'
            ' agemikhay 2bare post befresti /start kon')
    bot.send_message(chat_id=zarman_channel_id, text=user_data['pocket'],
                        parse_mode=telegram.ParseMode.HTML)
    user_data.clear()
    return ConversationHandler.END


def put_on_qeue(bot, update, user_data):
    '''SENDING State handler function'''
    now = jdatetime.date.today().strftime("%a, %d %b %Y")
    update.message.reply_text('date time now is:\n{}\n date time kemikhay'
            ' ro benevis format qabele gabul:-->\nYY MM DD\n96 06 02 '.format(
                now), reply_markup=markup_date_time)
    return DATE_TIME



def received_datetime_handler(bot, update, user_data):
    '''DATE_TIME State handler function'''
    user_data['p_date'] = update.message.text
    now = jdatetime.date.today()

    if not user_data['p_date'].replace(' ','').isdigit():
        update.message.reply_text('lotfan add bede mesle nmune ke dadm')
        return DATE_TIME

    dt_list = user_data['p_date'].split()

    year = now.year
    month = now.month
    day = now.day

    if len(dt_list) == 1:
        day = int(dt_list[0])
    elif len(dt_list) == 2:
        month = int(dt_list[0])
        day = int(dt_list[1])
    elif len(dt_list) == 3:
        year = int(dt_list[0])
        month = int(dt_list[1])
        day = int(dt_list[2])
    else:
        update.message.reply_text('lotfan 1 ta 3 add bedid')
        return DATE_TIME

    p_date = jdatetime.date(year=year, month=month, day=day)
    strftime = p_date.strftime("%a, %d %b %Y")


    delta = p_date - now
    if delta.days < 0:
        update.message.reply_text('time ke zadi gabl az emruze va gabul '
                'nist 2bare emtehan kon\n\n{}\n'.format(strftime))
        return DATE_TIME

    user_data['p_date'] = p_date
    user_data['p_date_str'] = strftime
    update.message.reply_text('baraye sabt post /enqeue obezan ta '
            '{} pose mishe'.format(strftime))
    update.message.reply_text(text=user_data['pocket'],
            parse_mode=telegram.ParseMode.HTML)

    return DATE_TIME

def enqeue(bot, update, user_data):
    '''DATE_TIME State handler function'''
    #TODO bayad tu data base save konam va ye func handler ham benvisam ta
    #job queue betune uno har ruz run kone
    update.message.reply_text('add to quee ')

    user_data['text'] = str(user_data['text'])
    user_data['link'] = str(user_data['link'])
    user_data['usr_name'] = str(update.message.chat.username)
    user_data['usr_id'] = str(update.message.chat.id)
    user_data['g_date'] = user_data.get('p_date').togregorian()
    # database instance
    p = Post()
    p.add_entry(user_data)

    for k, v in user_data.items():
        update.message.reply_text('{}-->{}'.format(k, v))

    user_data.clear()
    return ConversationHandler.END




def not_publish_messages(bot, update, user_data):
    '''QUERY State handler function'''
    update.message.reply_text('not_publish_messages query_message ',
            reply_markup=markup_main)
    return MAIN


def show_from_to_messages(bot, update, user_data):
    '''QUERY State handler function'''
    update.message.reply_text('from to query_message ',
            reply_markup=markup_main)
    return MAIN


def show_All_messages(bot, update, user_data):
    '''QUERY State handler function'''
    update.message.reply_text('show_All_messages message query_message ',
            reply_markup=markup_main)
    return MAIN


# END of Helper functions------------------------------------------------------------------------------------------------------------------


# conversation handler uses the states and Helper functions
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        MAIN: [CommandHandler('new_message', new_message, pass_user_data=True),
                CommandHandler('reset', reset, pass_user_data=True),
                CommandHandler('query_message',
                        query_message, pass_user_data=True),
                CommandHandler('start', start)],

        NEW_MSG: [CommandHandler('send_message',
                        send_message_handler, pass_user_data=True),
                CommandHandler('reset', reset, pass_user_data=True),
                MessageHandler(Filters.text,
                        parse_message_handler, pass_user_data=True)],

        SENDING: [CommandHandler('publish', publish, pass_user_data=True),
                CommandHandler('reset', reset, pass_user_data=True),
                CommandHandler('put_on_qeue', put_on_qeue, pass_user_data=True)],

        QUERY: [CommandHandler('not_publish_messages', not_publish_messages,
                        pass_user_data=True),
                CommandHandler('show_from_to_messages', show_from_to_messages,
                        pass_user_data=True),
                CommandHandler('show_All_messages', show_All_messages,
                        pass_user_data=True),
                CommandHandler('reset', reset, pass_user_data=True)],

        DATE_TIME: [CommandHandler('enqeue', enqeue, pass_user_data=True),
                    CommandHandler('reset', reset, pass_user_data=True),
                    MessageHandler(Filters.text, received_datetime_handler,
                        pass_user_data=True)],



    },

    fallbacks=[CommandHandler('done', done, pass_user_data=True)]
)




'''
main function content
for debugging purpose arrange like this
'''
#init thelocalizion

locale.setlocale(locale.LC_ALL, "fa_IR")
#init database
connect_to_db()

# Create the EventHandler and pass it your bot's token.
TOKEN = "401217227:AAFWcAQ_lC33X9hwgnL3lYp2CdItJwhlD0o"
# TOKEN = "424031953:AAGJ2F1Q3xHWlkE5jQNEFTQFkRVKGWcUqMg"
updater = Updater(TOKEN)

# Get the dispatcher to register handlers
dp = updater.dispatcher



dp.add_handler(conv_handler)

# log all errors
dp.add_error_handler(error)

# Start the Bot
# updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
#updater.idle()








