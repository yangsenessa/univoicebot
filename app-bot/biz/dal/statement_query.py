from sqlalchemy import select,func, and_ 
from sqlalchemy.orm import Session
from .user_buss import BotUserInfo

from loguru import logger


def query_channel_usernum(db:Session,begintime:str, endtime:str,channelid:str):
   try:
       stm = select(func.count(BotUserInfo.tele_user_id)).where(and_(BotUserInfo.invited_by_userid==channelid),
                                                                BotUserInfo.reg_gmtdate>=begintime,
                                                                BotUserInfo.reg_gmtdate<=endtime)
           
       return db.scalars(stm).first()
   except Exception as e:
       logger.error(f"Query user amount err: {str(e)}")
    
   finally:
       db.close()
   return None
       