from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime
from sqlalchemy.orm import relationship

from .database import Base

class User_claim_jnl(Base):
    __tablename__ = "unv_claimjnl"
    user_id=Column(String, primary_key=True)
    task_id=Column(String)
    task_name=Column(String)
    tokens=Column(String)
    gmt_biz_create=Column(DateTime)
    gmt_biz_finish=Column(DateTime)
    status= Column(String)
