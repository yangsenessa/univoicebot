from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime
from sqlalchemy.orm import relationship

from .database import Base

class Unvtaskinfo(Base):
    __tablename__="unv_task_info"
    task_id=Column(String,primary_key=True)
    task_name=Column(String)
    task_rule_desc=Column(String)
    inspire_action=Column(String)
    rewards_type=Column(String)
    reward_cal_params_type=Column(String)
    base_reward=Column(String)
    status=Column(String)

