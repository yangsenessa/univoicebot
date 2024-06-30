from sqlalchemy.orm import Session
from .user_buss import BotUserInfo, BotUserAcctBase
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

def match_task(db:Session,action:str):
    tasks = db.query(Unvtaskinfo).filter()


    