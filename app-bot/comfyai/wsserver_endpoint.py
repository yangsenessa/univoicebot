from typing import List

from fastapi import APIRouter,Depends, Query,WebSocket, WebSocketDisconnect
from comfyai.models import mixlab_buss_m
from comfyai.dal.work_flow_routerinfo import WorkFlowRouterInfo
from comfyai.dal import work_flow_crud
from starlette.requests import HTTPConnection
from comfyai.database import Database, SessionLocal
from sqlalchemy.orm import Session


from comfyai import mixlab_endpoint

from loguru import logger
import time
import json


router = APIRouter()


class ConnectionManager:

    def __init__(self):
        # 存放激活的ws连接对象
        self.active_connections: List[WebSocket] = []

    def creatWsClient(url:str):
        conn = HTTPConnection
        
    
    async def connect(self, ws: WebSocket):
        # 等待连接
        logger.debug("Enter connect event...")
        await ws.accept()
        logger.debug("Accept connect event...")

        # 存储ws连接对象
        self.active_connections.append(ws)

    def disconnect(self, ws: WebSocket):
        # 关闭时 移除ws对象
        self.active_connections.remove(ws)

    @staticmethod
    async def send_personal_message(message: str, ws: WebSocket):
        # 发送个人消息
        await ws.send_text(message)

    async def broadcast(self, message: str):
        # 广播消息
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()




# Dependency
def get_db():
    database =  Database()
    db = database.get_db()
    return db

    

@router.websocket_route("/ws")
async def websocket_endpoint(websocket: WebSocket):
    
    
    logger.debug(f'ws client connecting: clientid={websocket.query_params["clientId"]}')
    
    await manager.connect(websocket)
    if("promptId" in websocket.query_params.keys() and "clientId" in websocket.query_params.keys()):

       client_id = websocket.query_params['clientId']
       prompt_id = websocket.query_params['promptId']

       try:
           status = {"type": "status", "data": {"status": {"exec_info": {"queue_remaining": 0}}, "sid": client_id}}
           logger.debug("Send to client:"+ json.dumps(status))

           await websocket.send_json(status)

           while True:
              workFlowRouterInfo = work_flow_crud.get_wk_router_clientid_promptid(get_db(),client_id,prompt_id)
              if workFlowRouterInfo and workFlowRouterInfo.ori_body != None :
                 #logger.debug("Send to client:"+ str(workFlowRouterInfo.ori_body))
                 print("Send to client:"+ workFlowRouterInfo.ori_body)
                 await websocket.send_text(reformStatus(workFlowRouterInfo.ori_body))
                 ws_body = json.loads(workFlowRouterInfo.ori_body)
                 if ws_body["type"] == "executed" :
                     break
                     
              time.sleep(5)


       except WebSocketDisconnect:
            manager.disconnect(websocket)
    

def reformStatus(ori_status:str):
    body = json.loads(ori_status)
    type = body["type"]
    if type != "executed":
       return ori_status
    else:
       items:list
       items =  body["data"]["output"]["images"]
       for item in items:
           logger.debug("Rebuild body...")
           filename = item["filename"]
           type = item["type"]
           url = mixlab_endpoint.get_oss_download_url(type+"_"+filename)
           item["ossUrl"] = url
       return json.dumps(body)
       
    