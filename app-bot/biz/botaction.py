from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler ,filters, MessageHandler
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
)
from . import tonbuss
from datetime import datetime
from collections import defaultdict
from typing import DefaultDict, Optional, Set
from .dal import user_buss_crud
from .dal.user_buss import BotUserInfo, BotUserAcctBase,UserCurrTaskDetail,UserTaskProducer
from .dal.transaction import User_claim_jnl
from .dal.global_config import Unvtaskinfo
from .dal import database
from .tonwallet import config
from biz.tonwallet.config import TASK_INFO
from . import media
from  .taskqueue import queue
import json
import os
import time
import uuid

from loguru import logger

extern_database =  database.Database()
engine = extern_database.get_db_connection()
db = extern_database.get_db_session(engine)





claimedKeyboardButton_list=list()

#inlineKeyboardButton_list.append(InlineKeyboardButton(text="Invite link",callback_data="opr-invite"))
#inlineKeyboardButton_list.append(InlineKeyboardButton(text="earn",callback_data="opr-earn"))
#inlineKeyboardButton_list.append(InlineKeyboardButton(text="claim",callback_data="opr-claim"))
#inlineKeyboardButton_list.append(InlineKeyboardButton(text="Ton Wallet",callback_data='opr_tonwallet'))
#inlineKeyboardButton_list.append(InlineKeyboardButton(text="play",callback_data="opr-play",pay=True))

panel_btn = [[InlineKeyboardButton(text="🤑 earn",callback_data="opr-earn"),InlineKeyboardButton(text="claim",callback_data="opr-claim")],
             [InlineKeyboardButton(text="🤑 Invite link",callback_data="opr-invite")],
             [InlineKeyboardButton(text="🐶 play",callback_data="opr-play")]]

claimedKeyboardButton_list.append(InlineKeyboardButton(text="earn",callback_data="opr-earn"))
claimedKeyboardButton_list.append(InlineKeyboardButton(text="claim",callback_data="opr-claim"))




class ChatData:
    """Custom class for chat_data. Here we store data per message."""

    def __init__(self) -> None:
        self.clicks_per_message: DefaultDict[int, int] = defaultdict(int)


# The [ExtBot, dict, ChatData, dict] is for type checkers like mypy
class CustomContext(CallbackContext[ExtBot, dict, ChatData, dict]):
    """Custom class for context."""

    def __init__(
        self,
        application: Application,
        chat_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ):
        super().__init__(application=application, chat_id=chat_id, user_id=user_id)
        self._message_id: Optional[int] = None

    @property
    def bot_user_ids(self) -> Set[int]:
        """Custom shortcut to access a value stored in the bot_data dict"""
        return self.bot_data.setdefault("user_ids", set())

    @property
    def message_clicks(self) -> Optional[int]:
        """Access the number of clicks for the message this context object was built for."""
        if self._message_id:
            return self.chat_data.clicks_per_message[self._message_id]
        return None

    @message_clicks.setter
    def message_clicks(self, value: int) -> None:
        """Allow to change the count"""
        if not self._message_id:
            raise RuntimeError("There is no message associated with this context object.")
        self.chat_data.clicks_per_message[self._message_id] = value

    @classmethod
    def from_update(cls, update: object, application: "Application") -> "CustomContext":
        """Override from_update to set _message_id."""
        # Make sure to call super()
        context = super().from_update(update, application)

        if context.chat_data and isinstance(update, Update) and update.effective_message:
            # pylint: disable=protected-access
            context._message_id = update.effective_message.message_id

        # Remember to return the object
        return context

async def start(update: Update, context: CustomContext) -> None:
    """Display a message with a button."""

    logger.info(f"{update.effective_user.id} call start")
    # WelCome Card
    logger.info("Show welcome card")
    args = context.args
    prm_begin=f"<b>Hello</b> {update.effective_user.name} ,"
    path = os.path.abspath(os.path.dirname(__file__))
    logger.info(f"Curr path is:{path}")
    img_path="resource"
    img_name="TGbanner.jpg"

    with open(os.path.join(path,img_path,img_name),"rb") as imgfile:
        await context.bot.send_photo(chat_id=update.effective_chat.id, 
                                     photo=imgfile,
                                     caption=prm_begin + config.PROMPT_START,
                                     reply_markup=InlineKeyboardMarkup(panel_btn),
                                     parse_mode=ParseMode.HTML)
   

    if args and len(args) > 0:
        inviter_id = args[0]
        # 在这里记录邀请信息，例如更新数据库
        logger.info(f"{update.effective_user.id} invited by  {inviter_id} ")
    
    progress_status =await deal_user_start(update.effective_user.id, update.effective_message.chat_id,context)
    '''await context.bot.send_message( chat_id = update.effective_chat.id,
        text=config.PANEL_IMG+prm_begin + config.PROMPT_START,
        reply_markup=InlineKeyboardMarkup.from_column(inlineKeyboardButton_list),
        parse_mode=ParseMode.HTML
    )'''
    

    if progress_status == config.PROGRESS_INIT or progress_status == config.PROGRESS_FINISH:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=config.PROMPT_GUIDE,parse_mode=ParseMode.HTML)
    elif progress_status == config.PROGRESS_DEAILING:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="You have a task processing,please wait you rewards...",parse_mode=ParseMode.HTML)
    elif progress_status == config.PROGRESS_WAIT_CUS_CLAIM:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Congratulation! You have some gift need claim,you can press 'claim' button which on the plane",parse_mode=ParseMode.HTML)
    elif progress_status == config.PROGRESS_LEVEL_IDT:
        logger.info("Send new member rewards")
        user_claim_jnl = User_claim_jnl(jnl_no = str(uuid.uuid4()),
                                     user_id =  update.effective_user.id,
                                     task_id = config.TASK_NEW_MEMBER,
                                     task_name = config.TASK_NEW_MEMBER,
                                     tokens="5000",
                                     gmt_biz_create = config.get_datetime(),
                                     gmt_biz_finish =  config.get_datetime(),
                                     status = config.PROGRESS_FINISH)
        user_buss_crud.invoke_acct_token(db, update.effective_user.id,"5000",user_claim_jnl)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Congratulation! You have got the newer rewards",parse_mode=ParseMode.HTML)


async def callback_inline(update:Update, context:CustomContext) -> None:
    logger.info("Button callback...")
    await update.callback_query.answer()

    commandhandlemsg = update.callback_query.data
    logger.info(f"Callback command:{commandhandlemsg}")

    if(commandhandlemsg == "voice-speaking"):
        await show_speak_reback(update, context)
    elif (commandhandlemsg == "opr_tonwallet"):
        await tonbuss.start_connect_wallet(update,context)
    elif (commandhandlemsg == "opr-claim"):
        await cust_claim_replay(update, context)
    elif (commandhandlemsg == "opr-play"):
        await start(update,context)
    elif (commandhandlemsg == "opr-invite"):
        await sharelink_task(update, context)
    elif (commandhandlemsg =="opr-earn"):
        await show_cus_earn(update,context)

async def show_cus_earn(update:Update, context:CustomContext) -> None:
    user_acct_base = user_buss_crud.get_user_acct(db,update.effective_user.id)
    replay_msg=f"Your voice has earned :{user_acct_base.tokens} 💰 "
    await context.bot.send_message(chat_id=user_acct_base.user_id, text=replay_msg)


async def sharelink_task(update:Update, context:CustomContext) -> None:
    chat_id = update.effective_chat.id
    replay_msg = f"https://t.me/univoice2bot?start={update.effective_user.id}"
    await context.bot.send_message(chat_id=chat_id, text=replay_msg)

async def cust_claim_replay (update:Update, context:CustomContext) -> None:

    chat_id = update.effective_chat.id
    user_curr_task_detail = user_buss_crud.fetch_user_curr_task_detail_can_be_claimed(db,update.effective_user.id)
    if user_curr_task_detail == None:
        await context.bot.send_message(chat_id=chat_id,text="Please waiting some minutes then retry.",parse_mode=ParseMode.HTML)
        return


    flag,trx_fee, amount = user_buss_crud.deal_custom_claim(db,update.effective_user.id)
    if flag and trx_fee != None and amount != None:
        msg_tmpl = f"<strong>Claim Success</strong>\n\n<i>You just claimed {trx_fee}</i>\n<i>The total tokens :{amount}</i>"
    elif flag:
        msg_tmpl = f"<strong>You have claimed Success</strong>\n\n<i>You can press 'earn' and see your account details </i>"
    else:
        msg_tmpl="Please waiting some minutes then retry."
    await context.bot.send_message(chat_id=chat_id,text=msg_tmpl,parse_mode=ParseMode.HTML)


async def show_speak_reback(update:Update, context:CustomContext) -> None:
    replaymsg = config.PROGRESS_FINISH
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=replaymsg,parse_mode=ParseMode.HTML)

async def voice_judge(update:Update,context:CustomContext):
    logger.info("Assgin user level and gpu level")
   
    user_info = user_buss_crud.get_user(db,update.effective_user.id)
    if user_info is not None and user_info.level == '0' and user_info.gpu_level =='0':
        voice_file = await update.effective_message.voice.get_file()
        time_duration = update.effective_message.voice.duration
        if voice_file == None or time_duration <3:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Please let us hear you ,at least 3 sec.",parse_mode=ParseMode.HTML)
            return
        user_info.level = config.get_rd_user_level()
        user_info.gpu_level = config.get_rd_gpu_level()
        user_buss_crud.update_user_info(db,user_info)
        logger.info("Update user level success!")
        rsp_msg = f"Congratulation ! Our AI identified your level is {user_info.level}, \
            and he privade your gpu level is {user_info.gpu_level}\
        \n\n Then you can press /start and begin your travel"


        await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=rsp_msg,parse_mode=ParseMode.HTML)
        return True
    return False

async def voice_upload(update:Update, context:CustomContext) -> None:
    voice_file = await update.effective_message.voice.get_file()
    time_duration = update.effective_message.voice.duration
   
    if await voice_judge(update, context):
        logger.info(f"{update.effective_chat.id} get levels...")   
        return

    user_id = update.effective_user.id
    chat_id = update.effective_message.chat_id
    task_id:str
    task_flag = False
    cid:str
    user_level:str
    gpu_level:str

    task_details = user_buss_crud.fetch_user_curr_tase_detail_status(db,user_id,config.PROGRESS_INIT)
    for task_detail in task_details:
        

        if task_detail.task_id == config.TASK_VOICE_UPLOAD :
            cid = await media.save_voice(voice_file)
            task_id = task_detail.task_id
            task_flag=user_buss_crud.update_user_curr_task_detail(db,user_id,task_id,config.PROGRESS_DEAILING)
            user_level = task_detail.user_level
            gpu_level = task_detail.gpu_level

    if not task_flag:
        logger.error(f"user_id={user_id} haven't task with action={config.TASK_VOICE_UPLOAD}")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Univoice is busing now,please wait some times and retry!")
        return
    logger.info(f"user_id={user_id} process task")

    #create producer entity
    entity=dict()
    entity["type"]="filename"
    entity["value"]=cid
    entity_str = json.dumps(entity)
    prd_id = hash(entity_str)

    user_task_producer = UserTaskProducer(prd_id=prd_id,
                                          user_id=user_id,
                                          chat_id=chat_id,
                                          task_id=task_id,
                                          prd_entity=entity_str,
                                          duration=time_duration,
                                          gmt_create=config.get_datetime())

    user_buss_crud.create_task_producer(db,user_task_producer)
    queue.push(user_id,task_sec= int(time.time())+config.cal_task_claim_time(gpu_level,task_id))
    replaymsg = config.PROMPT_RECORD_FINISH
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=replaymsg,parse_mode=ParseMode.HTML)


    
def match_user_task(action:str,level:str, chat_id:str):
    task_rule:dict
    task_rule = TASK_INFO[action]
    if level in task_rule.keys():
        return task_rule[level]
    
    if "ALL" in task_rule.keys():
        return task_rule["ALL"]
    return None



def fet_user_info(user_id:str):
    return user_buss_crud.get_user(db,user_id)


async def deal_new_user(user_id:str,context:CustomContext):
    userinfo = user_buss_crud.get_user(db=db, user_id=user_id)
    if userinfo != None and userinfo.level == '0' and userinfo.gpu_level == '0':
         await context.bot.send_message(
            chat_id=user_id,
            text=config.PROMPT_USER_FIRST
        )
         return True
    return False
        

#@chat_id for special rewards from other group
async def deal_user_start(user_id:str, chat_id:str, context:CustomContext):

    gmtdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    userinfo = user_buss_crud.get_user(db=db, user_id=user_id)

    if userinfo:
        '''Add code for re-define the guider message'''
        logger.info(f"This user is members!")
    else:
       logger.info(f'Init userInfo and acctinfo with userid={user_id}')
       userinfo = BotUserInfo(tele_user_id=user_id,tele_chat_id=chat_id, reg_gmtdate=gmtdate,
                              level=0,gpu_level=0,
                              source="O")
       userAcctBase = BotUserAcctBase(user_id=user_id, biz_id='0', tokens='0')
       user_buss_crud.create_user(db,user=userinfo, user_acct=userAcctBase)
    
       if await deal_new_user(user_id,context):
          return config.PROGRESS_LEVEL_IDT


    task_status_progress = deploy_user_curr_task(user_id=userinfo.tele_user_id,
                                              chat_id=chat_id, level=userinfo.level, gpu_level=userinfo.gpu_level,
                                              task_action=config.TASK_VOICE_UPLOAD)
    
    return task_status_progress

       

def deploy_user_curr_task(user_id:str, chat_id:str,level:str, gpu_level:str,task_action:str):
       
       logger.info(f"Now deploy the task of :{task_action}")
       task_info = match_user_task(action=task_action,level=level, chat_id=chat_id)
       if not task_info:
           logger.error(f"user_id={user_id} - chat_id={chat_id} can't match any tasks!")
           return
       task_id = task_action
       base_reward = task_info["token"]
       '''If task has finished ,delete it and rebuild it'''
       curr_task_detail:UserCurrTaskDetail
       progress_status = config.PROGRESS_INIT
       curr_task_detail = user_buss_crud.fetch_user_curr_task_detail(db, user_id,task_id)
       if curr_task_detail != None and  curr_task_detail.progress_status == config.PROGRESS_DEAILING:
           logger.info(f"Load curr task detail {curr_task_detail.task_id}-{curr_task_detail.progress_status}")
         
           #timebegin = config.load_datetime(curr_task_detail.gmt_modified) 
           timebegin = curr_task_detail.gmt_modified
           timeend = datetime.now()
           if (timeend-timebegin).seconds >config.cal_task_claim_time(level,task_id):
               user_buss_crud.deal_task_claim(db,user_id)
               progress_status = config.PROGRESS_WAIT_CUS_CLAIM
           else:
               progress_status = config.PROGRESS_DEAILING
           return progress_status
       if curr_task_detail != None and  curr_task_detail.progress_status ==config.PROGRESS_WAIT_CUS_CLAIM:
           return config.PROGRESS_WAIT_CUS_CLAIM
       
       if curr_task_detail != None  and  curr_task_detail.progress_status == config.PROGRESS_FINISH:
           progress_status = curr_task_detail.progress_status
           logger.info(f"Entering delete curr-detail")
           user_buss_crud.remove_curr_task_detail(db,curr_task_detail)

       curr_task_detail_new = UserCurrTaskDetail(user_id=user_id, chat_id=chat_id,task_id=task_id,
                                            token_amount=base_reward,user_level=level,gpu_level=gpu_level,
                                            progress_status= config.PROGRESS_INIT, gmt_create=config.get_datetime(),
                                            gmt_modified=config.get_datetime())
       curr_task_detail_deployed_flag = user_buss_crud.create_user_curr_task_detail(db,curr_task_detail_new)

       if curr_task_detail_deployed_flag:
           logger.info(f"user_id:{user_id}-chat_id:{chat_id} deployed task success")
       else:
           logger.info(f"user_id:{user_id} - chat_id:{chat_id} has already in task progress")
       return progress_status


