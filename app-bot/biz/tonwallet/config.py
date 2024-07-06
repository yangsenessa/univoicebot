import json
from datetime import datetime

#.env
#TOKEN='7371683651:AAFaAGcxZOuICMNfPCuShyHhnhciPYldPDE'
TOKEN='7325602719:AAFIS1aDLqO6nVCAaD20MMAi47pycXqpHlU'  
MANIFEST_URL='https://raw.githubusercontent.com/XaBbl4/pytonconnect/main/pytonconnect-manifest.json'


#from os import environ as env

#from dotenv import load_dotenv
#load_dotenv()

#TOKEN = env['TOKEN']
#MANIFEST_URL = env['MANIFEST_URL']

#USER_TASK
TASK_START='VOICE-RECORD'
TASK_VOICE_UPLOAD='VOICE-UPLOAD'

#PROGRESS
PROGRESS_INIT = 'INIT'
PROGRESS_DEAILING = 'DEAILING'
PROGRESS_FINISH = 'FINISH'
PROGRESS_WAIT_CUS_CLAIM = 'WAIT_CUS_CLAIM'

def paramloader(paramstr:str):
    paramobj =json.loads(paramstr)
    return (paramobj['param'], paramobj['value'])

# @curr-context param
# @param-tripule
# Obviously , it can only dealwith two-params calcular
def params_rex(context:dict, parmrex:tuple):
    if parmrex[0] in context.keys():
        value = context[parmrex[0]]
        return value == parmrex[1]
    else:
        return False

def get_datetime() -> str:
     return datetime.now().strftime("%Y-%m-%d %H:%M:%S")