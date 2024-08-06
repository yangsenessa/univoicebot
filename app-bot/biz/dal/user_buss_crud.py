from sqlalchemy.orm import Session
from .user_buss import BotUserInfo, BotUserAcctBase,UserCurrTaskDetail,UserTaskProducer
from .global_config import Unvtaskinfo
from ..tonwallet import config
from .transaction import User_claim_jnl
from loguru import logger
import uuid


def get_user(db:Session, user_id:str):
    try:
       return db.query(BotUserInfo).filter(BotUserInfo.tele_user_id==user_id).first()
    except Exception as e:
       logger.error(f"query user info err:{str(e)}")
    finally:
       db.close()

def get_user_acct(db:Session, user_id:str):
    try:
        return db.query(BotUserAcctBase).filter(BotUserAcctBase.user_id==user_id).first()
    except Exception as e:
       logger.error(f"query user_acct base info err:{str(e)}")
    finally:
        db.close()

def update_user_info(db:Session, user_info:BotUserInfo):
    try:
        db.add(user_info)
        db.commit()
        db.refresh(user_info)
    except Exception as e:
        db.rollback()
        logger.error(f"update user base info err:{str(e)}")
    finally:
        db.close()

def invoke_acct_token(db:Session, user_id:str, tokens:str,user_claim_jnl:User_claim_jnl):
    try:
        user_acct_info = get_user_acct(db,user_id)
        user_acct_info.tokens = str(int(user_acct_info.tokens)+int(tokens))

        db.add(user_acct_info)
        db.add(user_claim_jnl)
        db.commit()
        db.refresh(user_acct_info)
        db.refresh(user_claim_jnl)
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"update user acct info err:{str(e)}")
        return False
    finally:
        db.close()

def acct_update_deal(db:Session, user_id:str,tokens:str,user_claim_jnl:User_claim_jnl, user_info:BotUserInfo):
    try:
        user_acct_info = get_user_acct(db,user_id)
        user_acct_info.tokens = str(int(user_acct_info.tokens)+int(tokens))

        db.add(user_acct_info)
        db.add(user_claim_jnl)
        db.add(user_info)

        db.commit()
        db.refresh(user_acct_info)
        db.refresh(user_claim_jnl)
        db.refresh(user_info)

    except Exception as e:
        db.rollback()
        logger.error(f"update user level info err:{str(e)}")
    finally:
        db.close()




def create_user(db:Session, user:BotUserInfo, user_acct:BotUserAcctBase):
    try:
        db.add(user)
        db.add(user_acct)
        db.commit()
        db.refresh(user)
        db.refresh(user_acct)
    except Exception as e:
        logger.error(f"db err: {str(e)}")
        db.rollback()
    finally:
        db.close()

         


def match_task(db:Session,action:str, level:str,chat_id:str):
    logger.info(f"load task by action={action} level = {level}")
    
    try:
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
    except Exception as e:
        logger.error(f"load and match task base info err: {str(e)}")
    finally:
        db.close()

    

def get_task_info(db:Session,task_id:str):
    return db.query(Unvtaskinfo).filter(Unvtaskinfo.task_id == task_id).first()


def create_user_curr_task_detail(db:Session, user_curr_task_detail:UserCurrTaskDetail):  
    try: 
        task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_curr_task_detail.user_id,
                                                        UserCurrTaskDetail.task_id==user_curr_task_detail.task_id).first()                                                 
        if  task_detail == None:
            db.add(user_curr_task_detail)
            db.commit()
            db.refresh(user_curr_task_detail)
            return True
        else:
            if task_detail.progress_status == config.PROGRESS_INIT:
                db.add(task_detail)
                db.commit()
                return True
            else:
                return False
    except Exception as e:
        db.rollback()
        logger.error(f"db err: {str(e)}")

    finally:
        db.close() 


def fetch_user_curr_task_detail_can_be_claimed(db:Session, user_id:str):
    try:
        return  db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                    UserCurrTaskDetail.progress_status==config.PROGRESS_WAIT_CUS_CLAIM).first()
    except Exception as e:
        logger.error(f"query user curr task detail err:{str(e)}")
    finally:
        db.close() 

def fetch_user_curr_task_detail_not_finish(db:Session, user_id:str):
    try:
        return  db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                    UserCurrTaskDetail.progress_status==config.PROGRESS_DEAILING).first()
    except Exception as e:
        logger.error(f"query user curr task detail err:{str(e)}")
    finally:
        db.close()

def fetch_user_curr_task_detail(db:Session, user_id:str, task_id:str):
    try:
        return  db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                      UserCurrTaskDetail.task_id==task_id).first()
    except Exception as e:
        logger.error(f"query user curr task detail err:{str(e)}")
    finally:
        db.close()

def remove_curr_task_detail(db:Session,user_curr_task_detail:UserCurrTaskDetail):
     logger.info(f"Delete the detail which already claimed")
     try:
        if user_curr_task_detail:
            db.delete(user_curr_task_detail)
            db.commit()
     except Exception as e:
        db.rollback()
        logger.error(f"db err: {str(e)}")
     finally:
        db.close()

def fetch_user_curr_tase_detail_status(db:Session,user_id:str,progress_status:str):
    try:
        return db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                     UserCurrTaskDetail.progress_status==progress_status).all()
    except Exception as e:
        logger.error(f"query user curr task detail with status err:{str(e)}")
    finally:
        db.close()
    


def create_task_producer(db:Session,user_task_producer:UserTaskProducer):
    try:
        db.add(user_task_producer)
        db.commit()
        db.refresh(user_task_producer)
    except Exception as e:
        db.rollback()
        logger.error(f"db err: {str(e)}")
    finally:
        db.close()

def update_user_curr_task_detail(db:Session,user_id:str,task_id:str,user_level:str, gpu_level:str,progress_status:str) :
     try:
        task_detail:UserCurrTaskDetail
        task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                      UserCurrTaskDetail.task_id==task_id).first()
        if task_detail:
            task_detail.progress_status = progress_status
            task_detail.gmt_modified = config.get_datetime()
            task_detail.user_level = user_level
            task_detail.gpu_level = gpu_level
            db.add(task_detail)
            db.commit()
            db.refresh(task_detail)
            return True
        else:
            db.commit()
            return False
     except Exception as e:
        db.rollback()
        logger.error(f"db err: {str(e)}")
     finally:
         db.close()



def deal_task_claim(db:Session,user_id:str):
    try:
        task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id, UserCurrTaskDetail.task_id=="VOICE-UPLOAD").first()
        if task_detail == None or task_detail.progress_status != config.PROGRESS_DEAILING :
            logger.error(f"Claim is timing, but can't find the task detail!" )
            # Dirty data ,ignore
            return True
         
        task_detail.progress_status = config.PROGRESS_WAIT_CUS_CLAIM
        db.add(task_detail)

        user_claim_jnl = User_claim_jnl(jnl_no = str(uuid.uuid4()),
                                     user_id =  user_id,
                                     task_id = task_detail.task_id,
                                     task_name = task_detail.task_id,
                                     tokens=task_detail.token_amount,
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
    finally:
         db.close()
     
    return True

def deal_custom_claim(db:Session, user_id:str):
     try:
        task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id,
                                                         UserCurrTaskDetail.progress_status == config.PROGRESS_WAIT_CUS_CLAIM).first()
        if task_detail == None:
            task_detail = db.query(UserCurrTaskDetail).filter(UserCurrTaskDetail.user_id==user_id).first()
            if task_detail:
                return (True,None,None)
            else:
                logger.error(f"{user_id} is claiming, but can't find the task detail!" )
                return (False, '0','0')
        claim_jnl = db.query(User_claim_jnl).filter(User_claim_jnl.user_id==user_id,
                                                      User_claim_jnl.status == config.PROGRESS_WAIT_CUS_CLAIM).first()
        if claim_jnl == None :
            logger.error(f"{user_id} is claiming, but can't find the User_claim_jnl!" )
            db.commit()
            return (False, '0','0')

     
        user_acct_base = get_user_acct(db, user_id=user_id)
        amount_val =  user_acct_base.tokens
        trx_val = claim_jnl.tokens
        user_acct_base.tokens = amount_val + trx_val
        task_detail.progress_status = config.PROGRESS_FINISH
        claim_jnl.status = config.PROGRESS_FINISH
        db.add(user_acct_base)
        db.add(claim_jnl)
        db.add(task_detail)
        db.commit()
        db.refresh(claim_jnl)
        db.refresh(task_detail)
        db.refresh(user_acct_base)
        return (True,trx_val, user_acct_base.tokens)
     except Exception as e:
         logger.error(f"Deal claim err userid={user_id} e={str(e)}")
         db.rollback()
         return (False, '0','0')
     finally:
         db.close()
    
    
def fetch_curr_claim(db:Session, user_id:str) :
    try:
        claim_jnl = db.query(User_claim_jnl).filter(User_claim_jnl.user_id==user_id,
                                                      User_claim_jnl.status == config.PROGRESS_WAIT_CUS_CLAIM).first()
        
        return claim_jnl
    
    except Exception as e:
         logger.error(f"Deal claim err userid={user_id} e={str(e)}")
         return None
    finally:
         db.close()

def fetch_user_invited(db:Session, user_id:str):
    try:
        user_info_list = db.query(BotUserInfo).filter(BotUserInfo.invited_by_userid ==  user_id).all()
        return user_info_list
    except Exception as e:
        logger.error(f"fetch user who was invited by {user_id} e ={str(e)}")
        return None
    finally:
        db.close()


def fet_product_list(db:Session, user_id:str):
    try:
        product_list = db.query(UserTaskProducer).filter(UserTaskProducer.user_id == user_id).all()
        return product_list
    except Exception as e:
        logger.error(f"fetch product error {user_id} e={str(e)}")
        return None
    finally:
        db.close()

def delete_product(db:Session, product_id:str):
    try:
        product = db.query(UserTaskProducer).filter(UserTaskProducer.prd_id == product_id).first()
        if product:
            db.delete(product)
            db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"delete product error {product_id} e={str(e)}")
    finally:
        db.close()

     



    