from .DelayQueue import DelayQueue
from .. import tonbuss
from . import complex_template

import time
from threading import Thread
from loguru import logger

from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup,Bot
from telegram.constants import ParseMode

from biz.tonwallet.config import TOKEN,PROMPT_WAIT_CALIMED_1,PROMPT_WAIT_CALIMED_2,PROMPT_WAIT_CALIMED_3,PROMPT_NOTIFY_CLAIM_IMG

import asyncio
import nest_asyncio
import os
import threading
import sys
sys.path.append("..")
sys.path.append("..")

import globalval as webapp
from biz.tonwallet import config




panel_btn = [[InlineKeyboardButton(text="🗣 play",callback_data="opr-play")],
             [InlineKeyboardButton(text="👝 balance",callback_data="opr-balance"),InlineKeyboardButton(text="🚀upgrade",callback_data="opr-upgrade")],
             [InlineKeyboardButton(text="🌟 earn",callback_data="opr-earn"),InlineKeyboardButton(text="💸claim",callback_data="opr-claim")],
             [InlineKeyboardButton(text="✨ Join Group",callback_data="opr-join"),InlineKeyboardButton(text="👏 Invite Frens",callback_data="opr-invite")]
             ]

redis_conf = {'host': '8.141.81.75', 'port': 6379, 'db': 0,'passwd':'mixlab'}
queue = DelayQueue(redis_conf)
bot = Bot(token=TOKEN)

claimedKeyboardButton_list=list()
claimedKeyboardButton_list.append(InlineKeyboardButton(text="🎉 claim",callback_data="opr-claim"))


def do_pop():
    while True:
       time.sleep(10)
       exe_target = webapp.get_value("name")
       userids = queue.pop(10)
      
       if exe_target !='bot':
           logger.info("For dapp only,exit thread func")
           return
       else:
                  
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
              
            
              
                  imgfile =  complex_template.marked_claim_notify(user_id,
                                                              [PROMPT_WAIT_CALIMED_1,PROMPT_WAIT_CALIMED_2,PROMPT_WAIT_CALIMED_3],
                                                              rsp_img_path,abs_path)
              
                  nest_asyncio.apply()
                  loop = asyncio.get_event_loop()
                  loop.run_until_complete( bot.send_photo(chat_id=user_id,
                                                          photo=imgfile,                                            
                                                          reply_markup=InlineKeyboardMarkup.from_column(claimedKeyboardButton_list),
                                                          parse_mode=ParseMode.HTML))
                  os.remove(imgfile)
                  #loop.close()


async def pollstart(bot:Bot)->None:
    logger.info("Show welcome card poll")
    prm_begin=f"<b>Hi </b> sours,welcome"
    path = os.path.abspath(os.path.dirname(__file__))
    logger.info(f"Curr path is:{path}")
    img_path="resource"
    img_name="TGbanner.jpg"

    
    chat_id = config.CHANNLE_CHAT_ID
    time.sleep(10)
    exe_target = webapp.get_value("name")
     
    if exe_target !='bot':
        logger.info("For dapp only,exit thread func")
        return
    else:

        with open(os.path.join(path,img_path,img_name),"rb") as imgfile:
            await bot.send_photo(chat_id=chat_id, 
                                     photo=imgfile,
                                     caption=prm_begin + config.PROMPT_START,
                                     reply_markup=InlineKeyboardMarkup(panel_btn),
                                     parse_mode=ParseMode.HTML)

def poll_start():
    time.sleep(50)
    while True:
        logger.info("Start poll start")
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(pollstart(bot))
        time.sleep(3600*5)

        
    
Thread(target=do_pop).start()
Thread(target=poll_start).start()
