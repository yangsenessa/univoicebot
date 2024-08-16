from sqlalchemy import select,func
from sqlalchemy.orm import Session
from .user_buss import BotUserInfo

from loguru import logger


def query_channel_usernum(db:Session,channelid:str):
   try:
       stm = select(func.count(BotUserInfo.tele_user_id)).where(BotUserInfo.invited_by_userid==channelid)
       return db.scalars(stm).first()
   except Exception as e:
       logger.error(f"Query user amount err: {str(e)}")
    
   finally:
       db.close()
   return None
       