import json
from loguru import logger
class WorkLoad(object) :  
    promt_id:str
    client_id:str
    ai_node:str
    app_info:str
    wk_id:str
    voice_key:str
    deduce_asset_key:str
    status:str
    gmt_datatime:int

    def __init__(self,promt_id,client_id, ai_node,app_info,wk_id,voice_key,deduce_asset_key,status,gmt_datatime ) :
        self.promt_id = promt_id
        self.client_id = client_id
        self.ai_node = ai_node
        self.app_info = app_info
        self.wk_id = wk_id
        self.voice_key = voice_key
        self.deduce_asset_key = deduce_asset_key
        self.status = status
        self.gmt_datatime = gmt_datatime
        

def parseTojson(workload:WorkLoad) ->str:
    content =  json.dumps(workload)
    logger.debug(content)
    return content


    
