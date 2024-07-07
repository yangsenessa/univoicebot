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
from .dal.global_config import Unvtaskinfo
from .dal import database
from .tonwallet import config
from . import media
from  .taskqueue import queue
import json

from loguru import logger

extern_database =  database.Database()
engine = extern_database.get_db_connection()
db = extern_database.get_db_session(engine)




inlineKeyboardButton_list=list()

claimedKeyboardButton_list=list()

inlineKeyboardButton_list.append(InlineKeyboardButton(text="Invite link",callback_data="opr-invite"))
inlineKeyboardButton_list.append(InlineKeyboardButton(text="earn",callback_data="opr-earn"))
inlineKeyboardButton_list.append(InlineKeyboardButton(text="claim",callback_data="opr-claim"))
inlineKeyboardButton_list.append(InlineKeyboardButton(text="Ton Wallet",callback_data='opr_tonwallet'))
inlineKeyboardButton_list.append(InlineKeyboardButton(text="play",callback_data="opr-play",pay=True))

claimedKeyboardButton_list.append(InlineKeyboardButton(text="earn",callback_data="opr-earn"))




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
    args = context.args
    if args and len(args) > 0:
        inviter_id = args[0]
        # 在这里记录邀请信息，例如更新数据库
        logger.info(f"{update.effective_user.id} invited by  {inviter_id} ")
    
    progress_status =  deal_user_start(update.effective_user.id, update.effective_message.chat_id)
    await context.bot.send_message( chat_id = update.effective_chat.id,
        text="Univoice-bot hearing your voice always..",
        reply_markup=InlineKeyboardMarkup.from_column(inlineKeyboardButton_list),
    )

    if progress_status == config.PROGRESS_INIT or progress_status == config.PROGRESS_FINISH:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="You can press the mic-phone button and send out your voice...")
    elif progress_status == config.PROGRESS_DEAILING:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="You have a task processing,please wait you rewards...")
    elif progress_status == config.PROGRESS_WAIT_CUS_CLAIM:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Congratulation! You have some gift need claim,you can press 'claim' button which on the plane")


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
    replay_msg = f"https://t.me/univoice2bot?start=1111"
    await context.bot.send_message(chat_id=chat_id, text=replay_msg)

async def cust_claim_replay (update:Update, context:CustomContext) -> None:

    chat_id = update.effective_chat.id
    flag,trx_fee, amount = user_buss_crud.deal_custom_claim(db,update.effective_user.id)
    if flag:
        msg_tmpl = f"<strong>Claim Success</strong>\n\n<i>You just claimed {trx_fee}</i>\n<i>The total tokens :{amount}</i>"
    else:
        msg_tmpl="Please waiting some minutes then retry."
    await context.bot.send_message(chat_id=chat_id,text=msg_tmpl,parse_mode=ParseMode.HTML)


async def show_speak_reback(update:Update, context:CustomContext) -> None:
    replaymsg = "You can press mic-phone and leave your pretty voice..."
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=replaymsg)

async def voice_upload(update:Update, context:CustomContext) -> None:
    voice_file = await update.effective_message.voice.get_file()
    time_duration = update.effective_message.voice.duration
    user_id = update.effective_user.id
    chat_id = update.effective_message.chat_id
    task_id:str
    task_flag = False
    cid:str

    task_details = user_buss_crud.fetch_user_curr_tase_detail_status(db,user_id,config.PROGRESS_INIT)
    for task_detail in task_details:
        task_info = user_buss_crud.get_task_info(db,task_id=task_detail.task_id)
        task_id = task_info.task_id

        if task_info.inspire_action == config.TASK_VOICE_UPLOAD :
            cid = await media.save_voice(voice_file)
            task_flag=user_buss_crud.update_user_curr_task_detail(db,user_id,task_id,config.PROGRESS_DEAILING)
    if not task_flag:
        logger.error(f"user_id={user_id} haven't task with action={config.TASK_VOICE_UPLOAD}")
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="You have done current task,please waiting for your rewards...")
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
    queue.push(user_id)


    
def match_user_task(action:str,level:str, chat_id:str):
    return user_buss_crud.match_task(db,action, level,chat_id)


def fet_user_info(user_id:str):
    return user_buss_crud.get_user(db,user_id)



#@chat_id for special rewards from other group
def deal_user_start(user_id:str, chat_id:str):


    gmtdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    userinfo = user_buss_crud.get_user(db=db, user_id=user_id)

    if userinfo:
        '''Add code for re-define the guider message'''
        logger.info(f"This user is members!")
    else:
       logger.info(f'Init userInfo and acctinfo with userid={user_id}')
       userinfo = BotUserInfo(tele_user_id=user_id,tele_chat_id=chat_id, reg_gmtdate=gmtdate,level='1')
       userAcctBase = BotUserAcctBase(user_id=user_id, biz_id='0', tokens='0')
       user_buss_crud.create_user(db,user=userinfo, user_acct=userAcctBase)

    task_status_progress = deploy_user_curr_task(user_id=userinfo.tele_user_id,
                                              chat_id=chat_id, level=userinfo.level,
                                              task_action=config.TASK_START)
    return task_status_progress

       

def deploy_user_curr_task(user_id:str, chat_id:str,level:str, task_action:str):
       task_info = match_user_task(action=task_action,level=level, chat_id=chat_id)
       if not task_info:
           logger.error(f"user_id={user_id} - chat_id={chat_id} can't match any tasks!")
           return
       task_id = task_info.task_id
       base_reward = task_info.base_reward
       '''If task has finished ,delete it and rebuild it'''
       curr_task_detail:UserCurrTaskDetail
       progress_status = config.PROGRESS_INIT
       curr_task_detail = user_buss_crud.fetch_user_curr_task_detail(db, user_id,task_id)
       if curr_task_detail != None:
           logger.info(f"Load curr task detail {curr_task_detail.task_id}-{curr_task_detail.progress_status}")
           if curr_task_detail.progress_status == config.PROGRESS_DEAILING:
               #timebegin = config.load_datetime(curr_task_detail.gmt_modified) 
               timebegin = curr_task_detail.gmt_modified
               timeend = datetime.now()
               if (timeend-timebegin).seconds >10:
                   user_buss_crud.deal_task_claim(db,user_id)
               
           progress_status = curr_task_detail.progress_status
       else:
           logger.info(f"{user_id} -task detail is null ,redeploy")
           progress_status = config.PROGRESS_INIT
       if curr_task_detail != None  and  curr_task_detail.progress_status == config.PROGRESS_FINISH:
           progress_status = curr_task_detail.progress_status
           logger.info(f"Entering delete curr-detail")
           user_buss_crud.remove_curr_task_detail(db,curr_task_detail)

       curr_task_detail_new = UserCurrTaskDetail(user_id=user_id, chat_id=chat_id,task_id=task_id,
                                            token_amount=base_reward,
                                            progress_status= config.PROGRESS_INIT, gmt_create=config.get_datetime(),
                                            gmt_modified=config.get_datetime())
       curr_task_detail_deployed_flag = user_buss_crud.create_user_curr_task_detail(db,curr_task_detail_new)

       if curr_task_detail_deployed_flag:
           logger.info(f"user_id:{user_id}-chat_id:{chat_id} deployed task success")
       else:
           logger.info(f"user_id:{user_id} - chat_id:{chat_id} has already in task progress")
       return progress_status


