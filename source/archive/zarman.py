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


from db_zarman import *

#const info
zarman_channel_id = -1001124038908
zarman_channel_name = "@this_is_my_channel"

zarman_base_text = '{text} <a href="{link}" > &#8207; </a>'



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


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
repKey_newMsg = [['/send_message', '/cancel']]
repKey_sending = [['/publish', '/put_on_qeue'], ['/cancel']]
repKey_query = [['/not_publish_messages', '/show_All_messages'], ['/show_from_to_messages', '/cancel']]
repkey_datetime = [['/enqeue', '/cancel']]

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
    update.message.reply_text('سلام. من پستچی هستم. اگه ادمین کانال هستی و هر روز پست میزاری پس من میتونم کمکت کنم. همیشه دستور help/ میتونه کمکت کنه.  '
				' دستور new message برای ساختن پست جدید.'
				' دستور query message برای دیدن پست های قبلی هستش. (فعلا کار نمیکنه)', reply_markup=markup_main)
    return MAIN


def new_message(bot, update, user_data):
    '''MAIN State handler function'''
    update.message.reply_text(' lotfan, text va link ro baraye man ersal kon '
				' baraye ersal post klid /send '
                                ' baraye Preview post klid /Preview'
                                ' va baraye cancel kardan majara klid cansel o bezanid'
                                ' age eshtebah kardi 2bare befrest text jadid  '
                                ' replace  mishe', reply_markup=markup_newMsg)
    return NEW_MSG

def query_message(bot, update, user_data):
    '''MAIN State handler function'''
    update.message.reply_text(' hanus kar nmikone lotfan /cancel o bezan ', reply_markup=markup_query)
    return QUERY

def parse_message_handler(bot, update, user_data):

    entities = update.message.parse_entities(types=telegram.MessageEntity.ALL_TYPES)
    text = update.message.text

    for k, v in entities.items():
        if k.type == 'text_link':
            user_data['link'] = k.url
        elif k.type == 'url':
            user_data['link'] = str(v)

        a = int(k.offset)
        b = a + int(k.length)
        text = text.replace(text[a:b], '')

    if not user_data.get('text', None):
        user_data['text'] = text.strip()

    update.message.reply_text(user_data['text'])

    if user_data.get('link'):
        update.message.reply_text(user_data['link'])

    update.message.reply_text('text e o gereftam va save kardm'
                                'age fekr mikoni eshtebah kardi 2bare befrest'
                                'to post badi baratb mifrestam '
                                'age doroste linko bede', reply_markup=markup_newMsg)
#     update.message.reply_text(user_data['text'])
#     update.message.reply_text('hala mituni link o befresti baram')
    if user_data.get('link', None):
        user_data['pocket'] = '{}\n <a href="{}" > &#8207; </a>'.format(
                user_data['text'], user_data['link'])
    else:
        user_data['pocket'] = user_data['text']

    update.message.reply_text(text=user_data['pocket'], parse_mode=telegram.ParseMode.HTML)

    return NEW_MSG


def received_text_handler(bot, update, user_data):
    '''NEW_MSG State handler function'''
    ''' TODO: age post oforward koni gabul nmikone'''
    user_data['text'] = update.message.text
    if not user_data['text']:
        update.message.reply_text(' tetx ke ferestadi dorost nist '
                                    '2bare say kon va text o befrest')
#         return SENDING
    else:
        update.message.reply_text('text e o gereftam va save kardm'
                                    'age fekr mikoni eshtebah kardi 2bare befrest'
                                    'to post badi baratb mifrestam '
                                    'age doroste linko bede', reply_markup=markup_newMsg)
        update.message.reply_text(user_data['text'])
        update.message.reply_text('hala mituni link o befresti baram')
    return NEW_MSG

def received_link_handler(bot, update, user_data):
    '''NEW_MSG State handler function'''
    e = update.message.parse_entities(types=telegram.MessageEntity.URL)
    u = list(e.values())

    user_data['link'] = u[0]
    if not user_data['link']:
        update.message.reply_text('mesle inke linko eshtebah ferestadi'
                                    '2bare befrest!! ')
    else:
        update.message.reply_text('link ogereftam o save kardm age ok ye '
                                    'klid /send o bezan va age mikhay bargadi /cancel\n'
                                    'link o barat miferestam age eshtebahe 2bare bede',
                                    reply_markup=markup_newMsg)
        update.message.reply_text(user_data['link'])
        update.message.reply_text('age hame chi moratabe /send_message_handler o bezan')
    return NEW_MSG


#NEW_MSG State
def send_message_handler(bot, update, user_data):
    '''NEW_MSG State handler function'''
    if not user_data.get('text', None):
        update.message.reply_text('**hanuz text onaferestadi !!!***',
                                    reply_markup = markup_newMsg)
        return NEW_MSG
    else:

        update.message.reply_text('poste morede nazar o barat mifrestam '
                                    'bebin khube ya na'
                                    'age mikhay haminalan post she /sendnow ro bezan'
                                    'age mikhay set time koni /enqeue bezan'
                                    'age ham narahti /canselo bezan',
                                    reply_markup=markup_sending)

    if user_data.get('link', None):
        user_data['pocket'] = '{}\n <a href="{}" > &#8207; </a>'.format(
                user_data['text'], user_data['link'])
    else:
        user_data['pocket'] = user_data['text']

    update.message.reply_text(text=user_data['pocket'], parse_mode=telegram.ParseMode.HTML)

    return SENDING


def done(bot, update, user_data):
    '''NEW_MSG State handler function'''
    update.message.reply_text(' hamechiz reset shod.  baraye shoro 2bare /start obezan')




def cancel(bot, update, user_data):
    '''NEW_MSG State handler function'''
    update.message.reply_text(' hamechiz reset shod.  baraye shoro 2bare /start obezan')

    user_data.clear()
    return ConversationHandler.END

def Preview(bot, update, user_data):
    '''NEW_MSG State handler function'''
    update.message.reply_text('cancel ', reply_markup=markup_main)
    return MAIN


def publish(bot, update, user_data):
    '''SENDING State handler function'''
    update.message.reply_text('post o barat ersalmikonam '
                                'be chanal zarman agemikhay 2bare post befresti /start kon')
    bot.send_message(chat_id=zarman_channel_id, text=user_data['pocket'],
                        parse_mode=telegram.ParseMode.HTML)
    user_data.clear()
    return ConversationHandler.END


def put_on_qeue(bot, update, user_data):
    '''SENDING State handler function'''
    now = jdatetime.date.today().strftime("%a, %d %b %Y")
    update.message.reply_text('date time now is:\n{}\n'
                               ' date time kemikhay ro benevis '
                               'format qabele gabul:-->'
                               '\nYY MM DD'
                               '\n96 06 02 '.format(now), reply_markup=markup_date_time)
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
        update.message.reply_text('time ke zadi gabl az emruze va gabul nist 2bare emtehan kon\n'
                                    '\n{}\n'.format(strftime))
        return DATE_TIME

    user_data['p_date'] = p_date
    user_data['p_date_str'] = strftime
    update.message.reply_text('baraye sabt post /enqeue obezan ta {} pose mishe'.format(strftime))
    update.message.reply_text(text=user_data['pocket'], parse_mode=telegram.ParseMode.HTML)

    return DATE_TIME

def enqeue(bot, update, user_data):
    '''DATE_TIME State handler function'''
    #TODO bayad tu data base save konam va ye func handler ham benvisam ta
    #job queue betune uno har ruz run kone
    update.message.reply_text('add to quee ')

    user_data['usr_name'] = update.message.chat.username
    user_data['usr_id'] = update.message.chat.id
    user_data['g_date'] = user_data['p_date'].togregorian()
    m = Message()
    m.add_entry(user_data)

    for k, v in user_data.items():
        update.message.reply_text('{}-->{}'.format(k, v))

    user_data.clear()
    return ConversationHandler.END




def not_publish_messages(bot, update, user_data):
    '''QUERY State handler function'''
    update.message.reply_text('not_publish_messages query_message ', reply_markup=markup_main)
    return MAIN


def show_from_to_messages(bot, update, user_data):
    '''QUERY State handler function'''
    update.message.reply_text('from to query_message ', reply_markup=markup_main)
    return MAIN


def show_All_messages(bot, update, user_data):
    '''QUERY State handler function'''
    update.message.reply_text('show_All_messages message query_message ', reply_markup=markup_main)
    return MAIN


# END of Helper functions------------------------------------------------------------------------------------------------------------------


# conversation handler uses the states and Helper functions
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        MAIN: [CommandHandler('new_message', new_message, pass_user_data=True),
                CommandHandler('query_message', query_message, pass_user_data=True)],

        NEW_MSG: [CommandHandler('send_message', send_message_handler, pass_user_data=True),
                CommandHandler('cancel', cancel, pass_user_data=True),
#                 MessageHandler(Filters.text &
#                                         (Filters.entity(MessageEntity.URL) |
#                                             Filters.entity(MessageEntity.TEXT_LINK)),
#                                                 received_link_handler, pass_user_data=True),
                MessageHandler(Filters.text, parse_message_handler, pass_user_data=True)],

        SENDING: [CommandHandler('publish', publish, pass_user_data=True),
                CommandHandler('put_on_qeue', put_on_qeue, pass_user_data=True)],

        QUERY: [CommandHandler('not_publish_messages', not_publish_messages, pass_user_data=True),
                CommandHandler('show_from_to_messages', show_from_to_messages, pass_user_data=True),
                CommandHandler('show_All_messages', show_All_messages, pass_user_data=True),
                CommandHandler('cancel', cancel, pass_user_data=True)],

        DATE_TIME: [CommandHandler('enqeue', enqeue, pass_user_data=True),
                    CommandHandler('cancel', cancel, pass_user_data=True),
                    MessageHandler(Filters.text, received_datetime_handler, pass_user_data=True)],



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








