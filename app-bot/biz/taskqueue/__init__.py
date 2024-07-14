from .DelayQueue import DelayQueue
from .. import tonbuss
from . import complex_template

import time
from threading import Thread
from loguru import logger

from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup,Bot
from telegram.constants import ParseMode

from biz.tonwallet.config import TOKEN,PROMPT_WAIT_CALIMED,PROMPT_NOTIFY_CLAIM_IMG,PROMPT_WAIT_CALIMED

import asyncio
import nest_asyncio
import os




redis_conf = {'host': '54.209.157.83', 'port': 6379, 'db': 0,'passwd':'mixlab'}
queue = DelayQueue(redis_conf)
bot = Bot(token=TOKEN)

claimedKeyboardButton_list=list()
claimedKeyboardButton_list.append(InlineKeyboardButton(text="🎉 claim",callback_data="opr-claim"))



def do_pop():
    while True:
       time.sleep(10)
       userids = queue.pop(10)
    
       for user_id in userids :
          if False == tonbuss.deal_task_claim(user_id):
              logger.warning(f"User = {user_id} claim err,re-queue")
              queue.push(user_id,int(time.time())+20)
          else:
              path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
              logger.info(f"Curr path is:{path}")
              img_path="resource"
              img_name=PROMPT_NOTIFY_CLAIM_IMG
              rsp_img_path = os.path.join(path,img_path,img_name)
              abs_path = os.path.join(path,img_path)
            
              
              imgfile =  complex_template.marked_claim_notify(user_id,[PROMPT_WAIT_CALIMED],rsp_img_path,abs_path)
              
              nest_asyncio.apply()
              loop = asyncio.get_event_loop()
              loop.run_until_complete( bot.send_photo(chat_id=user_id,
                                                          photo=imgfile,                                            
                                                          reply_markup=InlineKeyboardMarkup.from_column(claimedKeyboardButton_list),
                                                          parse_mode=ParseMode.HTML))
              os.remove(imgfile)
              #loop.close()


Thread(target=do_pop).start()
