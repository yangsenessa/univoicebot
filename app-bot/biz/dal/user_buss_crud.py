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
    if not task_detail:
        db.add(user_curr_task_detail)
        db.commit()
        db.refresh(user_curr_task_detail)
        return True
    else:
        return False


def fetch_user_curr_task_detal(db:Session, user_id:str, task_id:str):
    return  db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                      UserCurrTaskDetail.task_id==task_id).first()

def remove_curr_task_detail(db:Session,user_curr_task_detail:UserCurrTaskDetail):
     if user_curr_task_detail:
         db.delete(user_curr_task_detail)
         db.commit()
         db.refresh()

def fetch_user_curr_tase_detail_status(db:Session,user_id:str,progress_status:str):
    return db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                               UserCurrTaskDetail.progress_status==progress_status).all()
    


def create_task_producer(db:Session,user_task_producer:UserTaskProducer):
    db.add(user_task_producer)
    db.commit()
    db.refresh(user_task_producer)

def update_user_curr_task_detail(db:Session,user_id:str,task_id:str,progress_status:str) :
     task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                      UserCurrTaskDetail.task_id==task_id).first()
     if task_detail:
         task_detail.progress_status = progress_status
         db.commit()
         db.refresh(task_detail)
         return True
     else:
         return False

     



    