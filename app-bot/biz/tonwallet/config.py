import json
from datetime import datetime

#.env
TOKEN='7371683651:AAFaAGcxZOuICMNfPCuShyHhnhciPYldPDE'
#TOKEN='7325602719:AAFIS1aDLqO6nVCAaD20MMAi47pycXqpHlU'  
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



PROMPT_START="welcome to Univoice's fifth-dimensional world. Here, you can store your voice and have your unique AI steward, which helps transform your voice into your exclusive fifth-dimensional space."+\
"\n\nRecord your voice to earn points and rewards. Upgrade to get more recording opportunities and higher points."+\
"\n\nDon't forget to invite your friends to join you so you can earn points faster."+\
"\n\nWe look forward to you having a delightful journey in the world of voice!"


PROMPT_GUIDE="Please say \"Hello\" to the world in any language  to start your journey." +\
"\n\n<i>How to: Press the mic-phone button to capture and send your voice.</i>"

PROMPT_RECORD_FINISH="Recording successful! Your fifth-dimensional space now has more voices asset preserved for you!"+\
"\n\nPlease wait 6 hours to receive your points."


PROMPT_WAIT_CALIMED="Dear, your voice energy is fully charged.!Please come and claim your points."+\
"\n\nYour current voice duration level is 1st, with a maximum recording length of 5 seconds per entry."+\
"\n\nYou have 3 remaining recording opportunities within the next 24 hours."

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

def load_datetime(timestamp)->datetime:
    return datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S")