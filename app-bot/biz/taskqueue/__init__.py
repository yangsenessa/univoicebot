from .DelayQueue import DelayQueue
from .. import tonbuss
from . import complex_template

import time
from threading import Thread
from loguru import logger

from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup,Bot
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest
import telegram



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

trequest = HTTPXRequest(connection_pool_size=500)
bot = telegram.Bot(token=TOKEN, request=trequest)
pollBot = telegram.Bot(token=TOKEN, request=trequest)



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
                         
                imgfile =  complex_template.marked_claim_notify(user_id,
                                                              [PROMPT_WAIT_CALIMED_1,PROMPT_WAIT_CALIMED_2,PROMPT_WAIT_CALIMED_3],
                                                              rsp_img_path,abs_path)
                nest_asyncio.apply()
                try:
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete( bot.send_photo(chat_id=user_id,
                                                          photo=imgfile,                                            
                                                          reply_markup=InlineKeyboardMarkup.from_column(claimedKeyboardButton_list),
                                                          parse_mode=ParseMode.HTML))
                except:
                    if loop is not None:
                        loop.close()
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete( bot.send_photo(chat_id=user_id,
                                                          photo=imgfile,                                            
                                                          reply_markup=InlineKeyboardMarkup.from_column(claimedKeyboardButton_list),
                                                          parse_mode=ParseMode.HTML))
                finally:
                    if loop is not None:
                        loop.close()
                    os.remove(imgfile)
                  #loop.close()


async def pollstart(bot:Bot)->None:
    logger.info("Show welcome card poll")
    prm_begin=f"<b>Hi </b> souls,welcome"
    path = os.path.abspath(os.path.dirname(__file__))
    logger.info(f"Curr path is:{path}")
    img_path="resource"
    img_name="TGbanner.jpg"
    img_guide_name = "guide.png"

    
    chat_id = config.CHANNLE_CHAT_ID

    with open(os.path.join(path,img_path,img_name),"rb") as imgfile:
        await bot.send_photo(chat_id=chat_id, 
                                     photo=imgfile,
                                     caption=prm_begin + config.PROMPT_START,
                                     reply_markup=InlineKeyboardMarkup(panel_btn),
                                     parse_mode=ParseMode.HTML)
            
    with open(os.path.join(path,img_path,img_guide_name),"rb") as imgfile:
        await bot.send_photo(chat_id=chat_id, 
                                     photo=imgfile,
                                     caption="Then '/start' our bot like this...",
                                     parse_mode=ParseMode.HTML)

def poll_start():
    
    while True:
        time.sleep(10)
        nest_asyncio.apply()
        try:       
           loop = asyncio.new_event_loop()
           loop.run_until_complete(pollstart(pollBot))
        except:
            if loop is not None:
                loop.close()
            loop= asyncio.new_event_loop()
            loop.run_until_complete(pollstart(pollBot))
        finally:
            if loop is not None:
                loop.close()
        time.sleep(60*10)

     
Thread(target=do_pop).start()
Thread(target=poll_start).start()
