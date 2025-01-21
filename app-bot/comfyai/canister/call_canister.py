import asyncio
from ic.agent import *
from ic.identity import *
from ic.client import *
from ic.candid import Types, encode
import json

from loguru import logger

from .candid import WorkLoad, parseTojson

'''Calls an Internet Computer (IC) canister to push workflow record data.
    workLoad (WorkLoad): WorkLoad object containing the workflow data to be pushed to the canister.
1. Defines record types for the canister call
2. Encodes and pushes the workload data to the canister
    The canister ID used is "bw4dl-smaaa-aaaaa-qaacq-cai"
    Exception: If canister call fails'''
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


"""
Retrieves workflow data from an Internet Computer (IC) canister using the specified workflow ID.
Args:
    workflow_id (str): The unique identifier of the workflow to retrieve.
Returns:
    str: The raw response data from the canister containing the requested workflow information.
The function performs the following steps:
1. Establishes connection to local IC client (port 4943)
2. Loads PEM certificate from 'outter.pem' file for authentication
3. Creates an identity from the PEM certificate
4. Initializes an agent with the identity and client
5. Queries the canister with the workflow_id parameter
Note:
    Requires a valid PEM certificate in 'outter.pem' file
    Connects to a local IC client by default
Raises:
    FileNotFoundError: If 'outter.pem' file is not found
    Exception: If canister query fails
"""
def call_canister_get_workflow(workflow_id: str) -> str:
    logger.info("Begin call Ic canister to get workflow")
    client = Client("http://127.0.0.1:4943")

    with open('outter.pem','rb') as f:
        bpem = f.read()
        pemStr = bpem.decode()

    iden = Identity.from_pem(pemStr)
    ag = Agent(iden, client)

    params = [
            {'type': Types.Text, 'value': workflow_id},
        ]
        
    ret = ag.query_raw(
        "by6od-j4aaa-aaaaa-qaadq-cai",
        "fetch_workflow_data",
        encode(params)
    )
    if type(ret) is not list:
        return ret
        
    return list(map(lambda item: item["value"], ret))







    


