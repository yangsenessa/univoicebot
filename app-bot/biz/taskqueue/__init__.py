from .DelayQueue import DelayQueue
from .. import tonbuss
import time
from threading import Thread
from loguru import logger

from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup,Bot
from telegram.constants import ParseMode

from biz.tonwallet.config import TOKEN,PROMPT_WAIT_CALIMED

import asyncio
import nest_asyncio




redis_conf = {'host': '8.141.81.75', 'port': 6379, 'db': 0,'passwd':'mixlab'}
queue = DelayQueue(redis_conf)
bot = Bot(token=TOKEN)

claimedKeyboardButton_list=list()
claimedKeyboardButton_list.append(InlineKeyboardButton(text="earn",callback_data="opr-earn"))
claimedKeyboardButton_list.append(InlineKeyboardButton(text="claim",callback_data="opr-claim"))



def do_pop():
    while True:
       time.sleep(10)
       userids = queue.pop(10)
    
       for user_id in userids :
          if False == tonbuss.deal_task_claim(user_id):
              logger.warning(f"User = {user_id} claim err,re-queue")
              queue.push(user_id)
          else:
              nest_asyncio.apply()
              loop = asyncio.get_event_loop()
              loop.run_until_complete( bot.send_message(chat_id=user_id,
                                                        text=PROMPT_WAIT_CALIMED,
                                                        reply_markup=InlineKeyboardMarkup.from_column(claimedKeyboardButton_list),
                                                        parse_mode=ParseMode.HTML))
              #loop.close()


Thread(target=do_pop).start()
