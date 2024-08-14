from pydantic import BaseModel
import json
from .common_app_m import Result
from ..dal.user_buss import BotUserInfo, BotUserAcctBase,UserCurrTaskDetail,UserTaskProducer
from ..dal.transaction import User_claim_jnl
from datetime import datetime
from ..tonwallet import config



#webAppUser
class WebAppUser(BaseModel):
    id: int | None = None
    is_bot:bool | None = None
    first_name:str | None = None
    last_name:str |None = None
    username:str|None = None
    language_code:str|None = None
    is_premium:bool|None = None
    added_to_attachment_menu:bool|None = None
    allows_write_to_pm:bool | None = None
    photo_url:str | None = None

class ClaimInfo(BaseModel):
    claim_status:str
    wait_time:str |None = None
    claim_jnl:str | None = None

class TaskInfo(BaseModel):
    task_status:str | None = None
    task_id:str |None = None

class AddTaskInfo(BaseModel):
    task_id:str
    status:str
    rewards:str
    task_desc:str
    task_url:str
    logo:str

class AcctInfo(BaseModel):
    user_id:str
    wallet_addr:object |None = None
    VSD_level:str|None = None
    gpu_level:str|None = None
    invite_from:str|None = None
    balance:str|None = None

class User_appinfo_rsp_m(BaseModel):
    result:Result
    claim_info:ClaimInfo
    curr_task_info:TaskInfo
    user_acct_info:AcctInfo

class Get_user_boost_task_rsp_m(BaseModel):
    result:Result
    add_tasks:list

class Finsh_user_boost_task_req_m(BaseModel):
    webAppUser:WebAppUser
    task_id:str

class Finish_user_boost_task_rsp_m(BaseModel):
    result:Result
    reward:str|None=None

class Invite_friends_rsp_m(BaseModel):
    result:Result
    task_id:str
    task_desc:str
    rewards:str
    friend_num:str
    friend_info_group:list
    invite_url:str

class Vsd_level_m(BaseModel):
    level:str
    top_level:str
    upgrade_cost:str
    duration:str

class Gpu_level_m(BaseModel):
    level:str
    top_level:str
    upgrade_cost:str
    times:str

class Producer_item_m(BaseModel):
    prd_id:str
    task_id:str
    file_obj:str
    prd_type:str

class Voicetaskview_rsp_m(BaseModel):
    result:Result
    VSD_LEVEL:Vsd_level_m
    GPU_LEVEL:Gpu_level_m
    producer_group:list

class CommunicationInfo_m(BaseModel):
    target:str
    curr_num:str
    level:str
    des_info:str

class CommonInfo_rsp_m(BaseModel):
    result:Result
    communication_info:CommunicationInfo_m


def construct_userinfp_res(result:Result,user_info:BotUserInfo, user_acct:BotUserAcctBase,task_info:UserCurrTaskDetail|None,claim_info:User_claim_jnl|None) -> User_appinfo_rsp_m :
    

    
    user_acct_info_m = AcctInfo(user_id=user_info.tele_user_id,
                              wallet_addr=user_acct.wallet_id,
                              VSD_level = user_info.level,
                              gpu_level=user_info.gpu_level,
                              invite_from = user_info.invited_by_userid,
                              balance= str(user_acct.tokens))
    
   
    
    #cal waiting time
    time_begin = task_info.gmt_modified
    time_end = datetime.now()
    gpu_level = task_info.gpu_level
    time_remain = config.cal_task_claim_time(gpu_level, task_info.task_id) - (time_end-time_begin).seconds
    if time_remain <= 0:
        time_remain = 0

    
    
    claim_info_m = ClaimInfo(claim_status=config.PROGRESS_INIT,wait_time=None, claim_jnl=None)
    if not claim_info :
        claim_info_m.claim_status = config.PROGRESS_INIT
    else:
        claim_info_m.claim_jnl = claim_info.jnl_no
        claim_info_m.claim_status = claim_info.status
        claim_info_m.wait_time = str(time_remain)
    
    task_info_m = TaskInfo()
    if not task_info:
       task_info_m.task_id=''
       task_info_m.task_status=config.PROGRESS_INIT
    else:
       task_info_m.task_id = task_info.task_id
       task_info_m.task_status = task_info.progress_status
    

    user_appinfo_rsp_m = User_appinfo_rsp_m(result= result, claim_info= claim_info_m,
                                             curr_task_info = task_info_m, user_acct_info=user_acct_info_m)
    return user_appinfo_rsp_m


def construct_user_boost_task_res(result:Result,add_tasks:list)->Get_user_boost_task_rsp_m:
    user_boost_task_rsp_m = Get_user_boost_task_rsp_m(result=result, add_tasks=add_tasks)
    return user_boost_task_rsp_m


