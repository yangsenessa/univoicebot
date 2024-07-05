from .DelayQueue import DelayQueue
from .. import tonbuss
import time
from threading import Thread
from loguru import logger


redis_conf = {'host': '8.141.81.75', 'port': 6379, 'db': 0,'passwd':'mixlab'}
queue = DelayQueue(redis_conf)

def do_pop():
    while True:
       time.sleep(10)
       userids = queue.pop(10)
    
       for user_id in userids :
          if False == tonbuss.deal_task_claim(user_id):
              logger.warning(f"User = {user_id} claim err,re-queue")
              queue.push(user_id)


Thread(target=do_pop).start()
