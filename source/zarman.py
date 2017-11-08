#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from telegram import ReplyKeyboardMarkup, MessageEntity, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler,
                            MessageHandler, Filters,
                            RegexHandler,ConversationHandler, Job)
import telegram

import logging
import jdatetime
import locale
import time

from help_msg import *
from db_handler import *
# from keyboards import *

'''
select bot and channel
if zarman is True the bot uses orginal zarman Channel and bot
else for Debug
'''
TOKEN="TOKEN"

zarman_base_text = '{text} <a href="{link}" > &#8207; </a>'



# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
print('__name__:', __name__)
print('''
the kalagh is running,
token:{0}
Channel:{1}
here is log:
'''.format(TOKEN, zarman_channel_name ))


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
markup_datetime = ReplyKeyboardMarkup(repkey_datetime, one_time_keyboard=True)




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
def make_post(user_data):

    not_print_line = '\n<a> &#8207; </a>\n'*2
    if user_data.get('text'):
        text = '\n{0}\n{1}\n'.format(not_print_line, user_data.get('text'))
        user_data['pocket'] = text

    if user_data.get('link'):
        link = '\n<a href="{0}" > &#8207; </a>\n'.format(user_data.get('link'))
        user_data['pocket'] += link

    if user_data.get('hashtag'):
        hashtag = '\n{}\n'.format(user_data.get('hashtag'))
        user_data['pocket'] += hashtag
        user_data['pocket'] = text

    mention = '<a href="tg://user?id=-1001124038908">@zarmanchannel</a>'

    text = '{0}{1}{2}{0}'.format(not_print_line, user_data['pocket'],
            mention)

    return text


def parse_message_handler(bot, update, user_data):

    not_print_line = '\n<a> &#8207; </a>\n'
    entities = update.message.parse_entities(
            types=telegram.MessageEntity.ALL_TYPES)
    text = update.message.text
    hashtag = list()
    link = list()
    if not user_data.get('pocket'):
        user_data['pocket'] = ''

    for k, v in entities.items():
        if k.type == telegram.MessageEntity.TEXT_LINK:
            link.append(str(k.url).strip())

        elif k.type == telegram.MessageEntity.URL:
            link.append(str(v).strip())

        elif k.type == telegram.MessageEntity.HASHTAG:
            hashtag.append(str(v).strip())


        a = text.find(str(v).strip())
        b = a + int(k.length)
        text = text.replace(text[a: b], '')

    if len(text)>0:
        text_spl = text.splitlines()
        text_final = list()
        for l in text_spl:
            l = l.strip()
            if len(l)>0 and l[0] != '-':
                wt = ('{0}{1}').format('\t'*10, l)
                text_final.append(wt)
            else:
                wt = l[1:]
                text_final.append(wt)
#                 text_final.remove('*')
        text = '\n'.join(text_final)

    user_data['text'] = text
    user_data['link'] = link
    user_data['hashtag'] = hashtag

    if user_data.get('text'):
        if len(user_data['text']) > 4096:
            update.message.reply_text(text='bishtar az 4096ch dadi',
                    reply_markup=markup_newMsg)
            del user_data['text']
            return NEW_MSG

        text = '{0}'.format(text)
        user_data['pocket'] += text
        user_data['pocket'] = user_data['pocket'].strip()
        update.message.reply_text(f_msg_get_text , reply_markup=markup_newMsg)

    if user_data.get('link'):
        for l in link:
            p = '<a href="{0}" > &#8207; </a>'.format(l)
            user_data['pocket'] += p
            user_data['pocket'] = user_data['pocket'].strip()
        update.message.reply_text(f_msg_get_link , reply_markup=markup_newMsg)

    if user_data.get('hashtag'):
        hashtg = '\n{0}\n'.format((' '.join(hashtag)).strip())
        hashtg = '\n{0}'.format(hashtg)
        user_data['pocket'] += hashtg
        user_data['pocket'] = user_data['pocket']
        update.message.reply_text(f_msg_get_hashtg , reply_markup=markup_newMsg)


#     logger.warn('pocket' % user_data['pocket'])
    return NEW_MSG


#NEW_MSG State
def send_message_handler(bot, update, user_data):
    '''NEW_MSG State handler function'''
    if not user_data.get('pocket'):
        update.message.reply_text('**hanuz text onaferestadi !!!***',
                reply_markup = markup_newMsg)
        return NEW_MSG
    else:

        update.message.reply_text('poste morede nazar o barat mifrestam '
                'bebin khube ya na age mikhay haminalan post she /sendnow'
                ' ro bezan age mikhay set time koni /enqeue bezan age ham'
                ' narahti /canselo bezan', reply_markup=markup_sending)

    mention = '<a href="tg://user?id=-1001124038908">@zarmanchannel</a>'
    not_print_line = '\n<a> &#8207; </a>\n'

    user_data['pocket'] = '{2}{0}\n{1}'.format(user_data['pocket'], mention,
            not_print_line)

    update.message.reply_text(text=user_data['pocket'],
            parse_mode=telegram.ParseMode.HTML)

    return SENDING

def send_today_post(bot, job):
    pocket = None
    p = Post()
    jobs = p.post_query(now=datetime.datetime.now())

#     bot.send_message(chat_id=zarman_channel_id, text='send_today_post')



    for job in jobs:

        j = '{0}'.format(job.pocket)

        bot.send_message(chat_id=zarman_channel_id, text=j,
                parse_mode=telegram.ParseMode.HTML)


        p.update_db(id_=job.id)

        time.sleep(10)



def done(bot, update, user_data):
    '''NEW_MSG State handler function'''
    update.message.reply_text(' hamechiz reset shod.  baraye shoro 2bare'
            ' /start obezan')




def reset(bot, update, user_data):
    '''NEW_MSG State handler function'''
    update.message.reply_text(' hamechiz reset shod.  baraye shoro 2bare'
           ' /start obezan')

    user_data.clear()
    del user_data
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
    now = jdatetime.date.today().strftime("%a, %d %b %Y %H:%M:%S")
    update.message.reply_text('date time now is:\n{}\n date time kemikhay'
            ' ro benevis format qabele gabul:-->\nYY MM DD\n96 06 02 '.format(
                now), reply_markup=markup_datetime)
    return DATE_TIME



def received_datetime_handler(bot, update, user_data):
    '''DATE_TIME State handler function'''
    user_data['p_datetime'] = update.message.text
    now = jdatetime.datetime.now()

    if not user_data['p_datetime'].replace(' ','').isdigit():
        update.message.reply_text('lotfan add bede mesle nmune ke dadm')
        return DATE_TIME

    dt_list = user_data['p_datetime'].split()

    year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute

    if len(dt_list) == 1:
        minute = int(dt_list[0])
    elif len(dt_list) == 2:
        hour = int(dt_list[0])
        minute = int(dt_list[1])
    elif len(dt_list) == 3:
        day = int(dt_list[0])
        hour = int(dt_list[1])
        minute = int(dt_list[2])
    elif len(dt_list) == 4:
        month = int(dt_list[0])
        day = int(dt_list[1])
        hour = int(dt_list[2])
        minute = int(dt_list[3])
    elif len(dt_list) == 5:
        year = int(dt_list[0])
        month = int(dt_list[1])
        day = int(dt_list[2])
        hour = int(dt_list[3])
        minute = int(dt_list[4])
    else:
        update.message.reply_text('lotfan 1 ta 5 add bedid')
        return DATE_TIME

    p_datetime = jdatetime.datetime(year=year, month=month, day=day,
            hour=hour, minute=minute)
    strftime = p_datetime.strftime("%a, %d %b %Y %H:%M:%S")


    delta = p_datetime - now
    if delta.days < 0:
        update.message.reply_text('time ke zadi gabl az emruze va gabul '
                'nist 2bare emtehan kon\n\n{}\n'.format(strftime))
        return DATE_TIME

    user_data['p_datetime'] = p_datetime
    user_data['p_datetime_str'] = strftime
    update.message.reply_text('baraye sabt post /enqeue obezan ta '
            '{} pose mishe'.format(strftime))
    update.message.reply_text(text=user_data['pocket'],
            parse_mode=telegram.ParseMode.HTML)

    return DATE_TIME

def enqeue(bot, update, user_data):
    '''DATE_TIME State handler function'''
    #TODO bayad tu data base save konam va ye func handler ham benvisam ta
    #job queue betune uno har ruz run kone
    if not user_data.get('p_datetime_str'):
        update.message.reply_text('date to nadaram babaE',
                reply_markup=markup_datetime)
        return DATE_TIME
    update.message.reply_text('add to quee ')

    user_data['text'] = str(user_data['text'])
    user_data['link'] = str(user_data['link'])
    user_data['usr_name'] = str(update.message.chat.username)
    user_data['usr_id'] = str(update.message.chat.id)
    user_data['g_date'] = user_data.get('p_datetime').togregorian()
    # database instance
    p = Post()
    p.add_entry(user_data)

    for k, v in user_data.items():
        update.message.reply_text('{}-->{}'.format(k, v))

    user_data.clear()
    return ConversationHandler.END


def query_message(bot, update, user_data):
    '''MAIN State handler function'''
    update.message.reply_text(' hanus kar nmikone lotfan /reset o bezan ',
            reply_markup=markup_query)
    return QUERY


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
updater = Updater(TOKEN)

# Get the job_queue
updater.job_queue.run_repeating(callback=send_today_post, interval=30)
# Get the dispatcher to register handlers
dp = updater.dispatcher



dp.add_handler(conv_handler)

# log all errors
dp.add_error_handler(error)

# Start the Bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
#updater.idle()








