from sqlalchemy.orm import Session
from .user_buss import BotUserInfo, BotUserAcctBase,UserCurrTaskDetail,UserTaskProducer
from .global_config import Unvtaskinfo
from ..tonwallet import config
from .transaction import User_claim_jnl
from loguru import logger
import uuid


def get_user(db:Session, user_id:str):
    return db.query(BotUserInfo).filter(BotUserInfo.tele_user_id==user_id).first()

def get_user_acct(db:Session, user_id:str):
    return db.query(BotUserAcctBase).filter(BotUserAcctBase.user_id==user_id).first()


def create_user(db:Session, user:BotUserInfo, user_acct:BotUserAcctBase):
    db.add(user)
    db.add(user_acct)
    db.commit()
    db.flush(user)
    db.flush(user_acct)

def match_task(db:Session,action:str, level:str,chat_id:str):
    logger.info(f"load task by action={action} level = {level}")
    taskinfos = db.query(Unvtaskinfo).filter(Unvtaskinfo.task_action==action,
                                         Unvtaskinfo.level == level,
                                         Unvtaskinfo.status =="NORMAL").all()
    if taskinfos:
        for taskinfo in taskinfos:
            if(taskinfo.chat_id == chat_id):
                return taskinfo
    else:
        return None
    return taskinfos[0]

def get_task_info(db:Session,task_id:str):
    return db.query(Unvtaskinfo).filter(Unvtaskinfo.task_id == task_id).first()


def create_user_curr_task_detail(db:Session, user_curr_task_detail:UserCurrTaskDetail):
    task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_curr_task_detail.user_id,
                                                      UserCurrTaskDetail.task_id==user_curr_task_detail.task_id).first()
    if  task_detail == None:
        db.add(user_curr_task_detail)
        db.commit()
        db.flush(user_curr_task_detail)
        return True
    else:
        if task_detail.progress_status == config.PROGRESS_INIT:
            return True
        else:
            return False


def fetch_user_curr_task_detail(db:Session, user_id:str, task_id:str):
    return  db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                      UserCurrTaskDetail.task_id==task_id).first()

def remove_curr_task_detail(db:Session,user_curr_task_detail:UserCurrTaskDetail):
     logger.info(f"Delete the detail which already claimed")
     if user_curr_task_detail:
         db.delete(user_curr_task_detail)
         db.commit()

def fetch_user_curr_tase_detail_status(db:Session,user_id:str,progress_status:str):
    return db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                               UserCurrTaskDetail.progress_status==progress_status).all()
    


def create_task_producer(db:Session,user_task_producer:UserTaskProducer):
    db.add(user_task_producer)
    db.commit()
    db.refresh(user_task_producer)
    db.flush()

def update_user_curr_task_detail(db:Session,user_id:str,task_id:str,progress_status:str) :
     task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                      UserCurrTaskDetail.task_id==task_id).first()
     if task_detail:
         task_detail.progress_status = progress_status
         task_detail.gmt_modified = config.get_datetime()
         db.commit()
         db.flush(task_detail)
         return True
     else:
         return False

def deal_task_claim(db:Session,user_id:str):
     task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                      UserCurrTaskDetail.progress_status == config.PROGRESS_DEAILING).first()
     if task_detail == None :
         logger.error(f"Claim is timing, but can't find the task detail!" )
         return True
     
     try:
         task_detail.progress_status = config.PROGRESS_WAIT_CUS_CLAIM

         task_info = get_task_info(db,task_detail.task_id)
     
         user_claim_jnl = User_claim_jnl(jnl_no = str(uuid.uuid4()),
                                     user_id =  user_id,
                                     task_id = task_info.task_id,
                                     task_name = task_info.task_name,
                                     tokens=task_info.base_reward * task_info.flater,
                                     gmt_biz_create = config.get_datetime(),
                                     gmt_biz_finish =  config.get_datetime(),
                                     status = config.PROGRESS_WAIT_CUS_CLAIM)
         db.add(user_claim_jnl)

         
         db.commit()
         db.refresh(task_detail)
         
         logger.info(f"user:{user_id} have finish claim")
     except Exception as e:
         logger.error(f"Deal claim err userid={user_id} e={str(e)}")
         db.rollback()
         return False
     
     return True

def deal_custom_claim(db:Session, user_id:str):
     task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                      UserCurrTaskDetail.progress_status == config.PROGRESS_WAIT_CUS_CLAIM).first()
     if task_detail == None :
         logger.error(f"Claim is timing, but can't find the task detail!" )
         return True
     claim_jnl = db.query(User_claim_jnl).filter(User_claim_jnl.user_id==user_id,
                                                      User_claim_jnl.status == config.PROGRESS_WAIT_CUS_CLAIM).first()
     if claim_jnl == None :
         logger.error(f"Claim is timing, but can't find the task detail!" )
         return None

     try:
        user_acct_base = get_user_acct(db, user_id=user_id)
        amount_val =  user_acct_base.tokens
        trx_val = claim_jnl.tokens
        user_acct_base.tokens = amount_val + trx_val
        task_detail.progress_status = config.PROGRESS_FINISH
        claim_jnl.status = config.PROGRESS_FINISH
        db.commit()
        db.refresh(claim_jnl)
        db.refresh(task_detail)
        db.refresh(user_acct_base)
        return (trx_val, user_acct_base.tokens)
     except Exception as e:
         logger.error(f"Deal claim err userid={user_id} e={str(e)}")
         db.rollback()
         return None
    
    

     

    

     



    