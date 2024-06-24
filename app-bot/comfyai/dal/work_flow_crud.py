from sqlalchemy.orm import Session
from comfyai.dal.work_flow_routerinfo import WorkFlowRouterInfo,ComfyuiNode
from loguru import logger
from datetime import datetime


def create_wk_router(db:Session, wkrouter:WorkFlowRouterInfo):
    db.add(wkrouter)
    db.commit()
    db.refresh(wkrouter)
    return wkrouter

def update_wk_router(db:Session, client_id:str,prompts_id:str,ori_body:str,filenames,comfyui_url:str,status:str):
    logger.debug("update_wk_router:")
    logger.debug(client_id)
    logger.debug(prompts_id)
    db_wkrouter = db.query(WorkFlowRouterInfo).filter(
                       WorkFlowRouterInfo.client_id == client_id
                           ,WorkFlowRouterInfo.prompts_id == prompts_id).first()
    logger.info(f"WorkFlowRouterInfo promptsid:{prompts_id} client_id:{client_id} load = {str(db_wkrouter)}")
    if db_wkrouter:
       db_wkrouter.status=status
       db_wkrouter.ori_body = ori_body
       now = datetime.now()
       db_wkrouter.gmt_datetime = now.strftime("%Y-%m-%d %H:%M:%S")  
       if filenames:
           db_wkrouter.filenames = filenames
       db.commit()
       db.refresh(db_wkrouter)
       
       logger.debug("update success")
    else:
        db_wkrouter = WorkFlowRouterInfo(prompts_id=prompts_id,client_id=client_id,ori_body=ori_body,filenames=filenames,comfyui_url=comfyui_url,
                                         status=status,gmt_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info(f"Insert into WorkFlowRouterInfo={str(db_wkrouter)}")
        db.add(db_wkrouter)
        db.commit()
        db.refresh(db_wkrouter)
        logger.debug("restore wkrouter")
    return db_wkrouter

def get_wk_router_clientid_promptid(db:Session, client_id:str, prompt_id:str):
    db_wkrouter = db.query(WorkFlowRouterInfo).filter(
        WorkFlowRouterInfo.client_id ==  client_id, WorkFlowRouterInfo.prompts_id == prompt_id
    ).first()
    return db_wkrouter

def get_comfyui_node(db:Session):
    node = db.query(ComfyuiNode).order_by(ComfyuiNode.weight).first()
    return node

def add_comfyui_weight(db:Session, node:ComfyuiNode):
    node.weight = node.weight+1
    db.commit()
    db.refresh(node)
    return node