from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from comfyai.database import Base

class UserBaseInfo(Base):
    __tablename__ = "tb_user_baseinfo"
    user_id = Column(String, primary_key=True)
    nick_name = Column(String)
    email = Column(String)
    cell_phone = Column(String)
    exterprisename = Column(String)
    password = Column(String)



class UserWsRouterInfo(Base):
    __tablename__="tb_user_ws_router"
    client_id =Column(String(64),primary_key=True)
    ws_url=Column(String)
    comf_url=Column(String)
    status=Column(String)


class UserProfile(Base):
    __tablename__="tb_user_profile"
    user_id=Column(String,primary_key=True)
    upload_resource=Column(String)
    download_resource=Column(String)
    work_flows=Column(String)