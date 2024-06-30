from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler ,filters, MessageHandler
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
)
from .tonwallet import connector
from collections import defaultdict
from pytonconnect import TonConnect
from typing import DefaultDict, Optional, Set
from loguru import logger

async def start_connect_wallet(update:Update):
    chatid = update.effective_message.chat_id
    conn_instance = connector.get_connector(chatid)
    connected = await conn_instance.restore_connection()
    inlineKeyboardButton_list=list()


    if not connected :
        wallets_list = TonConnect.get_wallets()
        for wallet in wallets_list:
            button = InlineKeyboardButton(text=wallet['name'],callback_data=f'connect:{wallet["name"]}')
            inlineKeyboardButton_list.append(button)
        await update.message.reply_html(
            text="Choose wallte to connect",
            reply_markup=InlineKeyboardMarkup.from_column(inlineKeyboardButton_list)
        )
    else:
        btn_send_tr = InlineKeyboardButton(text='Send Transaction', callback_data='wallet_send_tr')
        bit_disconn = InlineKeyboardButton(text='Disconnect', callback_data='wallet_disconnect')
        inlineKeyboardButton_list.append(btn_send_tr)
        inlineKeyboardButton_list.append(bit_disconn)

        await update.message.reply_html(
            text="You are already connected!",
            reply_markup=InlineKeyboardMarkup.from_column(inlineKeyboardButton_list)
        )



