from sqlalchemy.orm import Session
from .user_buss import BotUserInfo, BotUserAcctBase,UserCurrTaskDetail,UserTaskProducer
from .global_config import Unvtaskinfo
from loguru import logger

def get_user(db:Session, user_id:str):
    return db.query(BotUserInfo).filter(BotUserInfo.tele_user_id==user_id).first()

def create_user(db:Session, user:BotUserInfo, user_acct:BotUserAcctBase):
    db.add(user)
    db.add(user_acct)
    db.commit()
    db.refresh(user)
    db.refresh(user_acct)

def match_task(db:Session,action:str, level:str):
    taskinfo = db.query(Unvtaskinfo).filter(Unvtaskinfo.task_action==action,
                                         Unvtaskinfo.level == level,
                                         Unvtaskinfo.status =="NORMAL").first()
    return taskinfo


def deal_user_task(db:Session, user_curr_task_detail:UserCurrTaskDetail):
    db.add(user_curr_task_detail)
    db.commit()
    db.refresh(user_curr_task_detail)
\

def create_task_producer(db:Session, user_curr_task_detail:UserCurrTaskDetail, user_task_producer:UserTaskProducer):
    db.add(user_task_producer)
    db.add(user_curr_task_detail)
    db.commit()
    db.refresh(user_curr_task_detail)
    db.refresh(user_task_producer)
     



    