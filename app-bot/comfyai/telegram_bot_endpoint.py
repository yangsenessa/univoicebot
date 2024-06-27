from fastapi import APIRouter,Depends,HTTPException,Request,Query,File, Form, UploadFile

from comfyai.models import mixlab_buss_m, user_login_m
from comfyai.dal.work_flow_routerinfo import WorkFlowRouterInfo,ComfyuiNode
from comfyai.dal.user_baseinfo import UserWsRouterInfo

from loguru import logger
from urllib.parse import quote
from sqlalchemy.orm import Session
from comfyai.dal import user_baseinfo, user_crud, work_flow_crud
from comfyai.database import SessionLocal, engine

import requests
import json
from comfyai.wsclient.websocket_client_new import WebsocetClient
from telegram.ext import ContextTypes
from datetime import datetime
import time
from comfyai import database
import os


extern_database =  database.Database()
engine = extern_database.get_db_connection()

#prompt for UNIVOICE
#@call_from:str telegram-miniapp/telegrem-bot/twitter/red-book/default
async def extern_prompts(user_token:str, chat_id:str,context:ContextTypes.DEFAULT_TYPE,call_from:str, wkflow:dict):
    headers = {
        "Content-Type": "application/json"
    }

    db = extern_database.get_db_session(engine)
    #init user router
    init_user_router(db, user_token)

     #Get node
    user_ws_router:UserWsRouterInfo
    user_ws_router = user_crud.fetch_user_ws_router(db,user_token)
    if(user_ws_router) :
        comf_url = user_ws_router.comf_url
        ws_url_ori = str(user_ws_router.ws_url) 
        ws_url = ws_url_ori.split('=')[0]+'='+(str(wkflow['client_id']))
    else:
        raise HTTPException(status_code=400,detail="Invaid router")
    logger.info(f"Curr router is:{comf_url}")
    logger.info(f"Curr ws opt is:{ws_url}")

    #origin video can be null with different workflows
   
    try:
        logger.info(f"Begining put .mp4 file to comfyui")
        put_file_to_comfyui_rawfile(comf_url,"sun.mp4")
       
    except Exception as e:
        logger.error(f"Upload video file err {str(e)}")
        return
    
    logger.debug("begin post:" + "  "+ comf_url) 
    try:
        response = requests.post(comf_url,json=wkflow,headers=headers)

        rescontents =  response.json()
        logger.debug("response -- "+json.dumps(rescontents))
       

        wk_info =  WorkFlowRouterInfo()  
        wk_info.prompts_id = rescontents["prompt_id"]
        wk_info.client_id = user_token
        wk_info.app_info = get_app_info(wkflow)
        wk_info.status="progress"
        wk_info.comfyui_url=comf_url  
        wk_info.gmt_datetime =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
        work_flow_crud.create_wk_router(db,wk_info)
        logger.debug(f"begin create ws client-{wkflow['client_id']}")
    
        await WebsocetClient().start(user_token,chat_id,context,ws_url,call_from,db)
        time.sleep(1)
       
        logger.debug(response.content)
           
    except Exception as e:
        logger.debug(f"some exception when prompts:{str(e)}")

    return response  



#put_file_to_comfyui_rawfile
def put_file_to_comfyui_rawfile(url:str,filename:str):
    comfyui_file_url = url.replace("prompt","upload/image")
    current_path = os.path.abspath(os.path.dirname(__file__))
    video_path=os.path.join(current_path, "video")
    filelocalpath=os.path.join(video_path,filename)
    
    with open(filelocalpath,'rb') as video_template:

        data = {
          "overwrite": "true",
          "age": 100
         }
        files = [
                 ('image', (filename,video_template)),
                ]

        response = requests.post(comfyui_file_url, data=data,  files=files)
        logger.debug("uploaded file into comfyui:", str(response.content) )

    if(response.status_code != 200) :
        raise Exception(f'Upload file to comfyui err:{str(response)}')
    

    
#get_app_info
def get_app_info(body:dict):
    node_group :dict= body["prompt"]

    for index in node_group.keys():
        if node_group[index]["class_type"] == "AppInfo" :
            return json.dumps(node_group[index])
    
    return None

#
#ComfyuiNode,comf_url,ws_url,comf_url,ws_url
#
def init_user_router(db:Session, client_id:str):
     #Get node
    node = work_flow_crud.get_comfyui_node(db)
    ws_url = "ws://"+node.host+":"+node.port+"/ws?clientId="+client_id
    comf_url = "http://"+node.host+":"+node.port+"/"+node.url
    user_crud.create_update_user_route_info(db,client_id,ws_url,comf_url,"INIT")
    work_flow_crud.add_comfyui_weight(db,node)
    return (node,comf_url,ws_url)


