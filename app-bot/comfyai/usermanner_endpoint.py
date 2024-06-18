from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from comfyai.dal import user_baseinfo,user_crud,work_flow_crud
from comfyai.database import SessionLocal,engine
from loguru import logger
import random
import string


from comfyai.dal.user_baseinfo import UserBaseInfo
from comfyai.dal.work_flow_routerinfo import WorkFlowRouterInfo,ComfyuiNode
from comfyai.models import user_login_m

router = APIRouter()
user_baseinfo.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users/", tags=["users"])
async def read_users():
    return [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users/me", tags=["users"])
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/users/{username}", tags=["users"])
async def read_user(username: str):
    return {"username": username}


@router.post("/userLogin",response_model=user_login_m.UserLoginRsp)
async def userLogin(user_login_req : user_login_m.UserLoginReq, db: Session = Depends(get_db)):
    user_dao =  user_crud.get_user_by_cellphone(db,user_login_req.cellphone)
    user_login_rsp = user_login_m.UserLoginRsp()
    if user_dao == None :
       logger.debug("user_dao is null")
       user_login_rsp.resultcode="FAIL"
       return user_login_rsp
    init_user_router(db,user_dao.user_id)
    user_login_rsp.resultcode="SUCCESS"
    user_login_rsp.token=user_dao.user_id
    return user_login_rsp

@router.post("/userRegAppl",response_model=user_login_m.UserRegReqRsp)
def userRegAppl(user_reg_req:user_login_m.UserRegReq, db:Session = Depends(get_db)):
    user_baseinfo = UserBaseInfo(user_id = generUserid()+user_reg_req.cellphone, nick_name = user_reg_req.nickname, email = user_reg_req.email, cell_phone = user_reg_req.cellphone,
                           exterprisename = user_reg_req.exterprisename, password = user_reg_req.password) 
    user_dao = user_crud.create_user(db, user_baseinfo)
    res_model = user_login_m.UserRegReqRsp
    if user_dao == None:
        logger.debug("insert user_dao error")
        res_model.resultcode = "FAIL"
        return res_model
    
    logger.debug("user_id="+user_dao.user_id)
    res_model.resultcode = "SUCCESS"
    res_model.userId = user_dao.user_id
    return res_model

    
    
def generUserid():
  res = []
  for i in range(10):
      x = random.randint(1,2)
      if x == 1:
          y = str(random.randint(0,9))
      else:
          y = chr(random.randint(97,122))
      res.append(y)
  res = ''.join(res)
  logger.debug("random="+res)

  return res

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



    


   
    
    
