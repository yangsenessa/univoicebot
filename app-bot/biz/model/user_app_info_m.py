from pydantic import BaseModel
import json
from common_app_m import Result

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

class AcctInfo(BaseModel):
    user_id:str
    wallet_addr:object |None = None
    VSD_level:str|None = None
    gpu_level:str|None = None
    invite_from:str|None = None
    balance:str|None = None

class user_appinfo_rsp_m(BaseModel):
    result:Result
    claim_info:ClaimInfo
    curr_task_info:TaskInfo
    user_acct_info:AcctInfo

