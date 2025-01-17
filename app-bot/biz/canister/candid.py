import json
from loguru import logger
from ic.candid import Types, encode, decode



class NftUnivoicePricipal(object) :  
    owners:list
    
    def __init__(self,owners ) :
        self.owners = owners


class UserIdentityInfo():
    user_id:str
    principalid_txt:str
    user_nick:str

    def __init__(self,user_id, principalid_txt, user_nick) :
        self.user_id = user_id
        self.principalid_txt = principalid_txt
        self.user_nick = user_nick

def parseTojsonUserSync(userinfos:list) ->str:
    content = json.dumps([userinfo.__dict__ for userinfo in userinfos],ensure_ascii=False)
    logger.debug(content)
    return content


def parseTojson(nftUnivoicePricipal:NftUnivoicePricipal) ->str:
    content =  json.dumps(nftUnivoicePricipal)
    logger.debug(content)
    return content

    
