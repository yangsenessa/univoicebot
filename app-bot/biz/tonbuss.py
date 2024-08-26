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
from .dal import user_buss_crud
from typing import DefaultDict, Optional, Set
from .dal import database
from loguru import logger
from .tonwallet import config


extern_database =  database.Database()
engine = extern_database.get_db_connection()
db = extern_database.get_db_session(engine)

async def start_connect_wallet(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chatid = update.effective_message.chat_id
    conn_instance = connector.get_connector(chatid)
    connected = await conn_instance.restore_connection()
    inlineKeyboardButton_list=list()


    if not connected :
        wallets_list = TonConnect.get_wallets()
        for wallet in wallets_list:
            button = InlineKeyboardButton(text=wallet['name'],callback_data=f'connect:{wallet["name"]}')
            inlineKeyboardButton_list.append(button)

        await context.bot.send_message(
            chat_id=chatid,
            text="Choose wallte to connect",
            reply_markup=InlineKeyboardMarkup.from_column(inlineKeyboardButton_list)
        )
    else:
        btn_send_tr = InlineKeyboardButton(text='Send Transaction', callback_data='wallet_send_tr')
        bit_disconn = InlineKeyboardButton(text='Disconnect', callback_data='wallet_disconnect')
        inlineKeyboardButton_list.append(btn_send_tr)
        inlineKeyboardButton_list.append(bit_disconn)

        await context.bot.send_message(
            chat_id=chatid,
            text="You are already connected!",
            reply_markup=InlineKeyboardMarkup.from_column(inlineKeyboardButton_list)
        )


def deal_task_claim( user_id:str):
     logger.info(f"user_id = {user_id} is claiming...")
     task_info = config.TASK_INFO
    
     flag = user_buss_crud.deal_task_claim(db,user_id)
     user_buss_crud.deal_custom_claim(db,user_id)
    
     return flag

