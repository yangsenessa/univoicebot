from fastapi import APIRouter,Depends,HTTPException,Request,Query,File, Form, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger
from urllib.parse import quote
from sqlalchemy.orm import Session

from .model.common_app_m import Result
from .model import common_app_m
from .model import user_app_info_m
from .model.user_app_info_m import User_appinfo_rsp_m, Finish_user_boost_task_rsp_m,AddTaskInfo,Invite_friends_rsp_m,Vsd_level_m,Gpu_level_m,Producer_item_m,Voicetaskview_rsp_m
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
import uuid


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
    result=common_app_m.buildResult("SUCCESS","SUCCESS")
    user_appinfo_rsp = user_app_info_m.construct_userinfp_res(result,user_info,user_acct,curr_task, claim_jnl)

    return user_appinfo_rsp


#getuserboosttask
@router.get("/univoice/getuserboosttask.do",response_model=user_app_info_m.Get_user_boost_task_rsp_m)
def do_getuserboosttask(userid=Query(None), db:Session = Depends(get_db)):
    add_task_infos = config.ADD_TASK_INFO
    task_item:dict
    user_curr_task_detail:UserCurrTaskDetail
    task_groups=list()
    add_task_item:AddTaskInfo

    for task_item in add_task_infos:
        task_id = task_item['taskid']
        token_amount = task_item['rewards']
        task_desc = task_item['task_desc']
        logo = task_item['logo']
        user_curr_task_detail = user_buss_crud.fetch_user_curr_task_detail(db,user_id=userid,task_id=task_id)

        #not have task, init task
        if not user_curr_task_detail:
            curr_task_detail_new = UserCurrTaskDetail(user_id=userid, chat_id=userid,task_id=task_id,
                                                      token_amount=token_amount,
                                                      progress_status= config.PROGRESS_INIT, gmt_create=config.get_datetime(),
                                                      gmt_modified=config.get_datetime())
            user_buss_crud.create_user_curr_task_detail(db,curr_task_detail_new)
            
            add_task_item = AddTaskInfo(task_id=task_id,status=config.PROGRESS_INIT,rewards=token_amount,task_desc=task_desc,logo=logo)
            task_groups.append(add_task_item)
        else:
            add_task_item = AddTaskInfo(task_id=user_curr_task_detail.task_id, status=user_curr_task_detail.progress_status,
                                        rewards= str(user_curr_task_detail.token_amount),task_desc=task_desc,logo=logo)
            task_groups.append(add_task_item)
        
        result = common_app_m.buildResult("SUCCESS", "SUCCESS")
        user_boost_task_rsp_m = user_app_info_m.construct_user_boost_task_res(result=result,add_tasks=task_groups)
        return user_boost_task_rsp_m

@router.post("/univoice/finshuserboosttask.do")
def do_finshuserboosttask(request:user_app_info_m.Finsh_user_boost_task_req_m,db:Session = Depends(get_db)):
    user_id = request.webAppUser.id
    task_id = request.task_id
    task_conf_item:dict
    result:Result

    user_curr_task_detail = user_buss_crud.fetch_user_curr_task_detail(db,user_id=user_id, task_id = task_id)
    add_task_info = config.fetch_add_task_info(task_id)

    if (not user_curr_task_detail) or (not add_task_info) :
        logger.error(f"Addtion task info param error:{task_id}")
        result = Result(res_code="FAIL", res_msg="System parm error")
        finish_user_boost_task_rsp = Finish_user_boost_task_rsp_m(result = result, reward=None)
        return finish_user_boost_task_rsp
    user_claim_jnl = User_claim_jnl(
                          jnl_no = str(uuid.uuid4()) ,
                          user_id = user_id,
                          task_id=add_task_info['taskid'],
                          task_name=add_task_info['task_desc'],
                          tokens=user_curr_task_detail.token_amount,
                          gmt_biz_create=config.get_datetime(),
                          gmt_biz_finish=config.get_datetime(),
                          status="FINISH"
                          )
    
    flag = user_buss_crud.invoke_acct_token(db,user_id,str(user_curr_task_detail.token_amount),user_claim_jnl)
    if flag:
        result = Result(res_code="SUCCESS", res_msg="SUCCESS")
        finish_user_boost_task_rsp = Finish_user_boost_task_rsp_m(result = result, reward=str(user_curr_task_detail.token_amount))

    else:
        result = Result(res_code="FAIL", res_msg="Deal acct buss error")
        finish_user_boost_task_rsp = Finish_user_boost_task_rsp_m(result = result, reward=None)

    return finish_user_boost_task_rsp


@router.get("/univoice/invitefriends.do",response_model=user_app_info_m.Invite_friends_rsp_m)
def do_getuserboosttask(userid=Query(None), db:Session = Depends(get_db)):
    invitetask = config.TASK_INFO[config.TASK_INVITE]["ALL"]
    task_id = config.TASK_INVITE
    task_desc = invitetask["taskdesc"]
    rewards = str(invitetask["token"]) 
    invite_link = f"https://t.me/univoice2bot?start={userid}"
    friend_info_group = list()

    user_info_list = user_buss_crud.fetch_user_invited(db=db, user_id=userid)

    if user_info_list:
        for user_item in user_info_list :
            if user_item.tele_user_name:
                user_name = user_item.tele_user_name
            else:
                user_name="sour"
            friend_info_group.append({"name": user_name, "rewards":rewards})
    
    result = common_app_m.buildResult("SUCCESS","SUCCESS")

    res_model = Invite_friends_rsp_m(result=result, task_id=task_id, task_desc=task_desc, 
                                     rewards=rewards, friend_num=str(len(user_info_list)) ,friend_info_group= friend_info_group,
                                     invite_url= invite_link)
    return res_model

@router.get("/univoice/voicetaskview.do",response_model=user_app_info_m.Voicetaskview_rsp_m)
def do_voicetaskview(userid=Query(None), db:Session = Depends(get_db)):
    user_info:BotUserInfo
    user_info = user_buss_crud.get_user(db=db,user_id=userid)
    vsd_level = user_info.level
    gpu_level = user_info.gpu_level

    vsd_level_conf = config.TASK_INFO[config.TASK_VOICE_UPLOAD]
    vsd_level_info = vsd_level_conf[vsd_level]
    vsd_level_next = str( int(vsd_level) +1 )

    if int(vsd_level) < 12:      
       vsd_level_next_info = vsd_level_conf[vsd_level_next]
       VSD_LEVEL = Vsd_level_m(level=vsd_level,top_level="12",upgrade_cost=vsd_level_next_info["consume"], duration=str(vsd_level_info["duration"]))

    else:
       VSD_LEVEL = Vsd_level_m(level=vsd_level,top_level="12",upgrade_cost="0", duration=str(vsd_level_info["duration"]))


    gpu_level_conf = config.GPU_LEVEL_INFO
    gpu_level_info = gpu_level_conf[gpu_level]

    if int(gpu_level) <6 :
       gpu_level_next = str(int(gpu_level)+1)
       gpu_level_next_info = gpu_level_conf[gpu_level_next]
       GPU_LEVEL = Gpu_level_m(level=gpu_level,top_level="6",upgrade_cost=str(gpu_level_next_info["consume"]), 
                                                            times= str(int(24/int(gpu_level_info["wait_h"]))))
    else:
       GPU_LEVEL = Gpu_level_m(level=gpu_level,top_level="6",upgrade_cost="0", 
                                                            times= str(int(24/int(gpu_level_info["wait_h"]))))


    producer_group= list()
    
    product_list = user_buss_crud.fet_product_list(db=db, user_id=userid)
    if product_list:
        for prd_item in product_list :
            prd_item_m = Producer_item_m(prd_id=prd_item.prd_id,task_id=prd_item.task_id, file_obj=prd_item.prd_entity,prd_type="VOICE")
            producer_group.append(prd_item_m)
    
    result = common_app_m.buildResult("SUCCESS", "SUCCESS")
    rsp_m = Voicetaskview_rsp_m(result=result, VSD_LEVEL= VSD_LEVEL, GPU_LEVEL=GPU_LEVEL,producer_group= producer_group)
    return rsp_m













        

        


            





    

    
    


    


