#user login/out domain model
from pydantic import BaseModel

# user login
class UserLoginReq(BaseModel):
    cellphone: str | None = None
    email:str | None = None
    password:str | None = None

class UserLoginRsp(BaseModel):
    token :str | None = None
    resultcode:str | None = None

# user regedit
class UserRegReq(BaseModel):
    nickname:str | None = None
    email:str | None = None
    cellphone:str | None = None
    exterprisename:str | None = None
    password:str | None = None

class UserRegReqRsp(BaseModel):
    resultcode:str
    userId:str


