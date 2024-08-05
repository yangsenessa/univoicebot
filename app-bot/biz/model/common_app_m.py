from pydantic import BaseModel

class Result(BaseModel):
    res_code:str
    res_msg:str

    
