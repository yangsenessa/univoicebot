from fastapi import APIRouter,Depends,HTTPException,Request,Query,File, Form, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger
from urllib.parse import quote
from sqlalchemy.orm import Session
from .dal import user_buss_crud
from .dal.user_buss import BotUserInfo, BotUserAcctBase,UserCurrTaskDetail,UserTaskProducer
from .dal.transaction import User_claim_jnl
from .dal.global_config import Unvtaskinfo
from .dal.database import SessionLocal
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


#getuserappinfo
@router.get("/univoice/getuserappinfo.do")
def do_getuserappinfo(userid=Query(None), db:Session = Depends(get_db)):
    BotUserInfo botUserInfo = user_buss_crud.get_user(db, user_id)
    

