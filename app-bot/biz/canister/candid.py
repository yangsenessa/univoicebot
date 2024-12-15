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


    
