import json
from loguru import logger
from ic.candid import Types, encode, decode

class NftUnivoicePricipal(object) :  
    owners:list
    
    def __init__(self,owners ) :
        self.owners = owners
        

def parseTojson(nftUnivoicePricipal:NftUnivoicePricipal) ->str:
    content =  json.dumps(nftUnivoicePricipal)
    logger.debug(content)
    return content


class UserIdentityInfo(object):
    user_id:str
    principal_txt:str
    user_nick:str

    def __init__(self,user_id, principal, user_nick) :
        self.user_id = user_id
        self.principal_txt = principal
        self.user_nick = user_nick


def parseTojsonUserSync(userinfo:UserIdentityInfo) ->str:
    content =  json.dumps(userinfo)
    logger.debug(content)
    return content



    
