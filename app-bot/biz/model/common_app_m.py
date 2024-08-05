from pydantic import BaseModel

class Result(BaseModel):
    res_code:str
    res_msg:str


def buildResult(res_code:str, res_msg:str):
    result = Result(res_code=res_code, res_msg=res_msg)
    return result