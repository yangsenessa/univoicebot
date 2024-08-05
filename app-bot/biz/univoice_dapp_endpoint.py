from fastapi import APIRouter,Depends,HTTPException,Request,Query,File, Form, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger
from urllib.parse import quote
from sqlalchemy.orm import Session

from .model.common_app_m import Result
from .model import common_app_m
from .model import user_app_info_m
from .model.user_app_info_m import User_appinfo_rsp_m
from .dal import user_buss_crud
from .dal.user_buss import BotUserInfo, BotUserAcctBase,UserCurrTaskDetail,UserTaskProducer
from .dal.transaction import User_claim_jnl
from .dal.global_config import Unvtaskinfo
from .dal.database import SessionLocal
from .tonwallet import config

import requests
import json
from datetime import datetime
import time
import os


router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#user_inner_info
def fetch_user_inner_info(user_id:str, db:Session):
     user_info:BotUserInfo
     user_info = user_buss_crud.get_user(db, user_id)
     if not user_info:
        logger.error(f"user_info can,t be got:{user_id}")
        return  (None, None)
     
     user_acct: BotUserAcctBase
     user_acct = user_buss_crud.get_user_acct(db, user_id)
     if not user_acct:
         logger.error(f"user_acct can't be got:{user_id}")
         return (None, None)
     
     return (user_info, user_acct)
     
     
    

def fetch_curr_claim_info(user_id:str, db:Session):
     claim_jnl:User_claim_jnl
     claim_jnl = user_buss_crud.fetch_curr_claim(db,user_id)
     return claim_jnl

##the main bussiness only deal with the main type of task :VOICE-UPLOAD
def fetch_task_info(user_id:str, db:Session):
     curr_task:UserCurrTaskDetail
     curr_task = user_buss_crud.fetch_user_curr_task_detail(db, user_id, task_id=config.TASK_VOICE_UPLOAD)
     return curr_task



#getuserappinfo
@router.get("/univoice/getuserappinfo.do", )
def do_getuserappinfo(userid=Query(None), db:Session = Depends(get_db)):
    user_info: BotUserInfo
    user_acct: BotUserAcctBase
    claim_jnl:User_claim_jnl
    curr_task:UserCurrTaskDetail

    result:Result

    
    user_info, user_acct = fetch_user_inner_info(user_id=userid, db=db)
    if (not user_info) or (not user_acct) :
        result =  common_app_m.buildResult("FAIL","Please go to univoice-bot and play once")
    
    user_info,user_acct = fetch_user_inner_info(userid,db)
    claim_jnl = fetch_curr_claim_info(userid, db)
    curr_task = fetch_task_info(userid, db)
    user_appinfo_rsp : User_appinfo_rsp_m
    user_appinfo_rsp = user_app_info_m.construct_userinfp_res(result,user_info,user_acct,curr_task, claim_jnl)

    return user_appinfo_rsp


#getuserboosttask
@router.get("/univoice/getuserboosttask.do")
def do_getuserboosttask(userid=Query(None), db:Session = Depends(get_db)):
    

    
    


    


