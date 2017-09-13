

from telegram import ReplyKeyboardMarkup, MessageEntity
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import telegram

import logging

#const info

zarman_channel_id = -1001124038908
zarman_channel_name = "@this_is_my_channel"

zarman_text = None
zarman_photo_link = None
zarman_contact = None

zarman_base_text = '{text} <a href="{link}" > &#8207; </a>'

incoming_chat_id = None

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# States of the bot
CHOOSING, TYPING_REPLY = range(2)

# markup keyboard definition
'''
reply_keyboard = [['Text', 'Photo'],
                  ['Channel ID', 'Preview'],
                  ['Publish']]
'''
reply_keyboard = [['Text', 'Photo'],
                  ['Publish']]


markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)



# Helper functions-----------------------------------------------------------------------------------------------------------------------

# error handler add to dispatcher in the updater object
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def start(bot, update):
    update.message.reply_text(
        "Hi! My name is Doctor Botter. I will hold a more complex conversation with you. "
        "Why don't you tell me something about yourself?",
        reply_markup=markup)

    return CHOOSING

def done(bot, update, user_data):
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "%s"
                              "Until next time!" % facts_to_str(user_data))

    user_data.clear()
    return ConversationHandler.END

def regular_choice(bot, update, user_data):
    text = update.message.text
    logger.info('regular_choice func--> you choose "%s"' % (text.lower()))
    update.message.reply_text('Your choose %s? Yes, I would love get that!' % text.lower())
    user_data['choice'] = text

    return TYPING_REPLY


def received_text(bot, update, user_data):
    global zarman_text
    incoming_chat_id = update.message.chat_id
    zarman_text = update.message.text
    update.message.reply_text("{} send me text and i save that, you see in reply".format(incoming_chat_id))
    update.message.reply_text("{}".format(zarman_text), reply_markup=markup)
    return CHOOSING

def received_photo(bot, update, user_data):
    global zarman_photo_link
    if update.message.photo:
        zarman_photo_link = update.message.photo
    else:
        zarman_photo_link = update.message.text

    incoming_chat_id = update.message.chat_id
    update.message.reply_text("{} send me photo and i save that, you see in reply".format(incoming_chat_id))
    update.message.reply_text("{}".format(zarman_photo_link), reply_markup=markup)
    return CHOOSING

def received_contact(bot, update, user_data):
    global zarman_contact
    incoming_chat_id = update.message.chat_id
    zarman_contact = update.message.contact
    update.message.reply_text("{} send me contact and i save that".format(incoming_chat_id))
    update.message.reply_text("{}".format(zarman_contact), reply_markup=markup)
    return CHOOSING

def publish(bot, update, user_data):
    '''
    if zarman_text == None :
        bot.send_message(chat_id=zarman_channel_id, text="theres no text")
    elif zarman_photo_link == None:
        bot.send_message(chat_id=zarman_channel_id, text="theres no link")
    else:
    '''
    global zarman_text
    global zarman_photo_link
    update.message.reply_text("send message")
    base_text = '{}\n <a href="{}" > &#8207; </a>'.format(zarman_text, zarman_photo_link)
    bot.send_message(chat_id=zarman_channel_id, text=base_text, parse_mode=telegram.ParseMode.HTML)
    zarman_text = None
    zarman_photo_link = None

    user_data.clear()
    return ConversationHandler.END




# END of Helper functions------------------------------------------------------------------------------------------------------------------


# conversation handler uses the states and Helper functions
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        CHOOSING: [RegexHandler('^(Text|Photo|Channel ID)$',
                                regular_choice,
                                pass_user_data=True),
                   ],

        TYPING_REPLY:  [MessageHandler(Filters.photo | Filters.text &
                                        (Filters.entity(MessageEntity.URL) |
                                            Filters.entity(MessageEntity.TEXT_LINK)),
                                                received_photo, pass_user_data=True),
                        MessageHandler(Filters.text, received_text, pass_user_data=True),
                        MessageHandler(Filters.contact, received_contact, pass_user_data=True),
                        RegexHandler('^Publish', publish, pass_user_data=True)]
    },

    fallbacks=[RegexHandler('^Publish$', publish, pass_user_data=True)]
)


# Create the EventHandler and pass it your bot's token.
TOKEN = "401217227:AAFWcAQ_lC33X9hwgnL3lYp2CdItJwhlD0o"
updater = Updater(TOKEN)

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







