import asyncio
from ic.agent import *
from ic.identity import *
from ic.client import *
from ic.candid import Types, encode
import json

from loguru import logger

from .candid import WorkLoad, parseTojson


def call_canister_workflow(workLoad:WorkLoad):
    logger.info("Begin call Ic canister")
    content = parseTojson(workLoad.__dict__)
    #    client = Client()
    client = Client("http://127.0.0.1:4943")

    with open('outter.pem','rb') as f:
       bpem=f.read()
       pemStr = bpem.decode()
       logger.info(pemStr)
    
    iden = Identity.from_pem(pemStr)
    logger.debug('principal:{}', Principal.self_authenticating(iden.der_pubkey))

    ag = Agent(iden, client)
    types = Types.Record({'promt_id':Types.Text, 'client_id': Types.Text, 'ai_node':Types.Text,
                         'app_info':Types.Text,'wk_id':Types.Text, 'voice_key':Types.Text,
                         'deduce_asset_key':Types.Text, 'status':Types.Text, 'gmt_datatime':Types.Nat64 })
    vals = json.loads(content)

    params = [
         {'type': types, 'value': vals},
        ]
    ret = ag.update_raw(
        "bw4dl-smaaa-aaaaa-qaacq-cai",
        "push_workload_record",
        encode(params)
        )
    
    logger.info(f'call canister ret = {ret}')






    


