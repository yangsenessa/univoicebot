from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime
from sqlalchemy.orm import relationship
from .database import Base

class BotUserInfo(Base):
    __tablename__ ="bot_user_info"
    tele_user_id=Column(String,primary_key=True)
    wallet_id=Column(String)
    reg_gmtdate=Column(DateTime)
    level=Column(String)

class BotUserAcctBase(Base):
    __tablename__="bot_user_acct_base"
    user_id=Column(String,primary_key=True)
    wallet_id=Column(String)
    biz_id=Column(String)
    tokens=Column(String)



    