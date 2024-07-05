from sqlalchemy import Boolean, Column, ForeignKey, BIGINT, String,DateTime
from sqlalchemy.orm import relationship

from .database import Base

class User_claim_jnl(Base):
    __tablename__ = "unv_claimjnl"
    jnl_no=Column(String,primary_key=True)
    user_id=Column(String)
    task_id=Column(String)
    task_name=Column(String)
    tokens=Column(BIGINT)
    gmt_biz_create=Column(DateTime)
    gmt_biz_finish=Column(DateTime)
    status= Column(String)
