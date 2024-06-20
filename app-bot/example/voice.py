#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, RegexHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup
import logging
import urllib2
import json
from io import BytesIO

from tinydb import TinyDB, Query
from tinydb.operations import increment

from random import randint
import os
import sys
import pickle
from threading import Thread

from functools import wraps
from telegram import ChatAction

tiny_db = db = TinyDB('user_data.json')
User = Query()

voice_lang = "en"

#base_url = "https://voice.mozilla.org/api/v1/"
base_url = "https://voice.allizom.org/api/v1/" + voice_lang
#base_url = "http://10.238.31.20:9000/api/v1/"

def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(bot, update, **kwargs)
        return command_func

    return decorator
#import magic

#import requests

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

send_typing_action = send_action(ChatAction.TYPING)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update, chat_data=None, user_data=None):
    button_list = [
        InlineKeyboardButton("Record a sentence", callback_data="start_speaking"),
        InlineKeyboardButton("Validate (not working yet)", callback_data="validate")
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    #custom_keyboard = [['Speak!', 'Validate (not working yet)']]
    #reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text('Hi there! This is an experimental Telegram Bot '
                              'that helps you contribute to the Mozilla\'s '
                              'CommonVoice project. By continuing to use this '
                              'bot you agree to our '
                              '[Terms](https://voice.mozilla.org/en/terms) and '
                              '[Privacy Notice](https://voice.mozilla.org/en/privacy).',
                              parse_mode=ParseMode.MARKDOWN)

    update.message.reply_text('We also know many features are missing, so if you '
                              'happen to know how to code and you want to help us, '
                              'feel free to clone and send pull requests to [our '
                              'github repository](https://github.com/Common-Voice/voicebot-telegram).',
                          parse_mode=ParseMode.MARKDOWN)
    update.message.reply_text('What would you like to do?', reply_markup=reply_markup)

def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

@send_typing_action
def got_voice(bot, update, chat_data=None, user_data=None):
    """Echo the user message."""
    # TODO: check a sane lenght of a message
    if ("sentence_id" not in chat_data.keys()):
        update.message.reply_text("Hi, I am not sure what this vocal message is for... 😅 let's try again!")
        bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
        (id, text) = do_send_voice(bot, update.message.chat_id)
        chat_data["sentence_id"] = id
        chat_data["sentence_text"] = text
        return

    logger.warning(chat_data)
    update.message.reply_text("Processing your new audio...")
    file_path = update.message.voice.get_file().download_as_bytearray()

    headers_dict = {
        'Content-Type': "application/octet-stream",
        'sentence': urllib2.quote(chat_data["sentence_text"].encode("utf-8")),
        'sentence_id': chat_data["sentence_id"],
        'client_id': 'telegram_v1_' + "%i" %(update.message.from_user.id)
      }

    logger.warning(headers_dict)
    req = urllib2.Request(base_url + '/clips', file_path, headers=headers_dict)
    res = urllib2.urlopen(req)
    #logger.warning(res.getcode())
    stored_data = tiny_db.get(User.user_id == update.message.from_user.id)
    if (stored_data == None):
        tiny_db.insert({'user_id': update.message.from_user.id, 'recorded_samples': 1})
        recorded_samples = 1
    else:
        tiny_db.update(increment('recorded_samples'), User.user_id == update.message.from_user.id)
        recorded_samples = stored_data['recorded_samples'] + 1

    level2 = 50
    level3 = 200
    level4 = 600
    level5 = 1000

    thank_you_notes = {
        1: "Thanks, I am learning a ton from you 😊",
        2: "What a nice voice you have",
        3: "Wonderful!",
        4: "Thank you, you are helping me a lot!",
    }

    thank_you_note = thank_you_notes.get(randint(1,4))
    update.message.reply_text("You sent me %i samples! %s" % (recorded_samples, thank_you_note))
    chat_data["sentence_id"] = None
    chat_data["sentence"] = None

    bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    (id, text) = do_send_voice(bot, update.message.chat_id)
    chat_data["sentence_id"] = id
    chat_data["sentence_text"] = text

#    user_data['recorded_samples'] += 1
    #speak(bot, update, chat_data, user_data)
    # Thank you. For a new recording press /speak", parse_mode=ParseMode.MARKDOWN)

    #update.message.reply_text(update.message.voice.file_id)

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def get_snippet():
    print("''")

@send_typing_action
def speak(bot, update, chat_data=None, user_data=None):

    chat_id = ""
    #logger.warning(update.callback_query.message)
    if (update.callback_query != None):
        chat_id = update.callback_query.message.chat.id
        update.callback_query.answer
    else:
        chat_id = update.message.chat_id


    if (update.callback_query != None):
        callback_action = update.callback_query.data
        if (callback_action != "start_speaking") and (callback_action != "skip"):
            bot.send_message(chat_id, update.callback_query.data)
            bot.send_message(chat_id, "Not implemented yet")
            # start(bot, update)
            return

    (id, text) = do_send_voice(bot, chat_id)
    chat_data["sentence_id"] = id
    chat_data["sentence_text"] = text

def do_send_voice(bot, chat_id):
    button_list = [
        #InlineKeyboardButton("End Session", callback_data="end_session"),
        InlineKeyboardButton("(skip)", callback_data="skip")
    ]
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    data = json.load(urllib2.urlopen(base_url + '/sentences/'))

    please_say_dict = {
        1: "Could you send me a vocal message? I am learning how to say:",
        2: "Can I hear you say this?",
        3: "Teach me how you pronounce:",
        4: "Would you mind sending me a voice note saying:",
    }

    bot.send_message(chat_id,
                    please_say_dict.get(randint(1,4)),
                        parse_mode=ParseMode.HTML)
    bot.send_message(chat_id, "🎤 -- "+ data[0]["text"].encode('utf-8'), reply_markup=reply_markup)

    return (data[0]["id"], data[0]["text"])

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(os.getenv("MOZ_VOICE_TELEGRAM"))

    # Get the dispatcher to register handlers
    dp = updater.dispatcher


    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start, pass_user_data=True))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("speak", speak, pass_chat_data=True, pass_user_data=True))

    dp.add_handler(CallbackQueryHandler(speak, pass_chat_data=True, pass_user_data=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.voice, got_voice, pass_chat_data=True, pass_user_data=True))

    # log all errors
    dp.add_error_handler(error)

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(bot, update):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()
        update.message.reply_text('Here!')

    dp.add_handler(CommandHandler('r', restart, filters=Filters.user(username='@ruphy')))
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()