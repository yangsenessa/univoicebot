from sqlalchemy import Boolean, Column, BIGINT, Integer, String,DateTime
from sqlalchemy.orm import relationship
from .database import Base

class BotUserInfo(Base):
    __tablename__ ="bot_user_info"
    tele_user_id=Column(String,primary_key=True)
    tele_chat_id=Column(String)
    wallet_id=Column(String)
    reg_gmtdate=Column(DateTime)
    level=Column(String)
    gpu_level=Column(String)
    source=Column(String)

class BotUserAcctBase(Base):
    __tablename__="bot_user_acct_base"
    user_id=Column(String,primary_key=True)
    wallet_id=Column(String)
    biz_id=Column(String)
    tokens=Column(BIGINT)

class UserCurrTaskDetail(Base):
    __tablename__="unv_user_curr_task_detail"
    user_id=Column(String, primary_key=True)
    user_level=Column(String)
    gpu_level=Column(String)
    chat_id=Column(String)
    task_id=Column(String)
    token_amount=Column(BIGINT)
    progress_status=Column(String)
    gmt_create=Column(DateTime)
    gmt_modified=Column(DateTime)

class UserTaskProducer(Base):
    __tablename__="unv_user_task_producer"
    prd_id=Column(String,primary_key=True)
    user_id=Column(String)
    chat_id=Column(String)
    task_id=Column(String)
    prd_entity=Column(String)
    duration=Column(Integer)
    gmt_create=Column(DateTime)


    