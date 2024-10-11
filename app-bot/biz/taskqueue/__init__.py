from .DelayQueue import DelayQueue
from .DelayQueueAigc import DelayQueueAigc
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
from loguru import logger
sys.path.append("..")
sys.path.append("..")

import globalval as webapp
from biz.tonwallet import config
from comfyai import telegram_bot_endpoint


redis_conf = {'host': '54.209.157.83', 'port': 6379, 'db': 0,'passwd':'mixlab'}
aigc_queue = DelayQueueAigc(redis_conf)
queue = DelayQueue(redis_conf)

def do_pop():
    while True:
       params:list = aigc_queue.pop(1)
       if params is None or len(params) == 0:
           time.sleep(5)
           continue;
       
       logger.info(f"Pop params :{str(params)}")           
       nest_asyncio.apply()
       try:
           loop = asyncio.new_event_loop()
           loop.run_until_complete(telegram_bot_endpoint.extern_prompts_dapp(params[0]))
       except Exception as e:
           logger.error(f"Do AIGC error:{str(params)} -{e}")
            
       finally:
          if loop is not None:
             loop.close()
       time.sleep(300)
        
#Thread(target=do_pop).start()
