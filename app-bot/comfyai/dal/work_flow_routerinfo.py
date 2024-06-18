from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime,INT
from sqlalchemy.orm import relationship

from comfyai.database import Base

class WorkFlowRouterInfo(Base):
    __tablename__ = "tb_workflow_routerinfo"
    prompts_id = Column(String, primary_key=True)
    client_id = Column(String)
    app_info = Column(String)
    ori_body = Column(String)
    filenames = Column(String)
    comfyui_url = Column(String)
    status = Column(String)
    gmt_datetime = Column(DateTime)


class  ComfyuiNode(Base):
    __tablename__ = "tb_comfyui_node"
    node_id = Column(String,primary_key=True)
    host = Column(String)
    url = Column(String)
    port = Column(String)
    weight = Column(INT)


