import asyncio
from ic.agent import *
from ic.identity import *
from ic.client import *
from ic.candid import Types, encode
import json

from loguru import logger

from .candid import NftUnivoicePricipal, parseTojson


def call_canister_workflow(nftUnivoicePricipal:NftUnivoicePricipal):
    logger.info("Begin call Ic canister")
    content = parseTojson(nftUnivoicePricipal.__dict__)
    #    client = Client()
    client = Client("http://127.0.0.1:4943")

    with open('outter.pem','rb') as f:
       bpem=f.read()
       pemStr = bpem.decode()
       logger.info(pemStr)
    
    iden = Identity.from_pem(pemStr)
    logger.debug('principal:{}', Principal.self_authenticating(iden.der_pubkey))

    ag = Agent(iden, client)
    types = Types.Record({'owners':Types.Vec(Types.Text)})
    vals = json.loads(content)

    params = [
         {'type': types, 'value': vals},
        ]
    ret = ag.update_raw(
        "b77ix-eeaaa-aaaaa-qaada-cai",
        "call_unvoice_for_ext_nft",
        encode(params)
        )
    
    logger.info(f'call canister ret = {ret}')
    return ret






    


