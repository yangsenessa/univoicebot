import json
import os
from datetime import datetime
import random

#.env
#bot1
#TOKEN='7371683651:AAFaAGcxZOuICMNfPCuShyHhnhciPYldPDE'

#bot2
TOKEN='7325602719:AAFIS1aDLqO6nVCAaD20MMAi47pycXqpHlU'  
MANIFEST_URL='https://raw.githubusercontent.com/XaBbl4/pytonconnect/main/pytonconnect-manifest.json'


CHANNLE_CHAT_ID=-1002177350295

OUTTER_PARTNER_ID='99999991'


#from os import environ as env

#from dotenv import load_dotenv
#load_dotenv()

#TOKEN = env['TOKEN']
#MANIFEST_URL = env['MANIFEST_URL']

#USER_TASK
TASK_VOICE_UPLOAD='VOICE-UPLOAD'
TASK_NEW_MEMBER='NEWER'
TASK_INVITE='INVITE'

#PROGRESS
PROGRESS_INIT = 'INIT'
PROGRESS_DEAILING = 'DEAILING'
PROGRESS_FINISH = 'FINISH'
PROGRESS_WAIT_CUS_CLAIM = 'WAIT_CUS_CLAIM'
PROGRESS_WAIT_TASK_FINISH = 'PROCESS'
PROGRESS_LEVEL_IDT = 'IDT'


PANEL_IMG="<img src='./resource/univouce/univoice.png'/>"
PROMPT_START="\n\n🌍✨ Welcome to Univoice! ✨🌍 "+\
"\n\nI’m the Univoice bot, designed to store and manage voices in a decentralized, encrypted way. I can hear everything around me, but I can’t speak yet."+\
"\nTeach me how to speak and listen, and help me understand the world of sounds. Let’s journey together, becoming confidants and meeting new friends."+\
"\n\nUnlock my magic and co-create Univoice—the voice of every unique soul in the universe."+\
"\n\nClick play to start. ⬇️⬇️⬇️"


PROMPT_GUIDE="Please upload your voice: 🗣" +\
"\n\n<i>How to: Press the mic-phone button 🎙 to capture and send your voice.</i>"

PROMPT_USER_FIRST="Thank you for embarking on this voice exploration journey. \
            \nlet's conduct a voiceprint test to obtain your initial equipment and $VOICE \
            \nClick the button of 'mic' in right corner to upload your voice  \
            \nSpeak anything to the bot at least 3 seconds."


PROMPT_RECORD_FINISH="Recording successful! Your fifth-dimensional space now has more voices asset preserved for you!"+\
"\n\nPlease wait {hours} hours to receive your points."


PROMPT_WAIT_CALIMED_1="$VOICE is available"
PROMPT_WAIT_CALIMED_2=" "
PROMPT_WAIT_CALIMED_3="Claim now !!!"
PROMPT_HAS_CALIMED_1="in the account "
PROMPT_HAS_CALIMED_2="has availabled to claim now. "
PROMPT_HAS_CAILMED_3="You can continue..."
PROMPT_HAS_CAILMED_4="Press 'play' to earn more."
PROMPT_HAS_CAILMED_5="Let's go"


PROMPT_RECORD_FINISH_IMG = "record-complete.jpg"
PROMPT_UPGRADE_SUCCESS="upgrade-success.jpg"
PROMPT_NOTIFY_CLAIM_IMG="notify-claim.jpg"
PROMPT_NOTIFY_CLAIMED_IMG="cliam-success.jpg"


#########################################TASK########################################
path = os.path.join(os.path.dirname(__file__),"conf","plan.json")
TASK_INFO=json.load(open(path))

path = os.path.join(os.path.dirname(__file__),"conf","gpu_level.json")
GPU_LEVEL_INFO=json.load(open(path))

path = os.path.join(os.path.dirname(__file__),"conf","add_task.json")
ADD_TASK_INFO = json.load(open(path))


def fetch_add_task_info(task_id:str):
    for task_item in ADD_TASK_INFO :
        if task_id == task_item['taskid']:
            return task_item
    return None

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


#RANDOM
def get_rd_user_level() -> str:
    return str(random.randint(1,12))

def get_rd_gpu_level() -> str:
    return str(random.randint(1,6))
#Return Second
def cal_task_claim_time(gpu_level:str, task_id:str):

    gpu_level_cfg:dict
    gpu_level_cfg = GPU_LEVEL_INFO[gpu_level]

    if task_id == TASK_VOICE_UPLOAD:
       # only for test :return 30
       return gpu_level_cfg["wait_h"] * 3600
    else:
       return 10


def cal_tokens(user_level:str, gpu_level:str,task_action:str):
    task_plan:dict
    task_plan = TASK_INFO[task_action][user_level]
    i_token_base = int(task_plan["token"])

    gpu_level_cfg:dict
    gpu_level_cfg = GPU_LEVEL_INFO[gpu_level]

    flatter = gpu_level_cfg["flatter"]
    return str(i_token_base*flatter)
