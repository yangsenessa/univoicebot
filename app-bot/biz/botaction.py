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

inlineKeyboardButton_list.append(InlineKeyboardButton(text="Speaking",callback_data="voice-speaking"))
inlineKeyboardButton_list.append(InlineKeyboardButton(text="earn",callback_data="opr-earn"))
inlineKeyboardButton_list.append(InlineKeyboardButton(text="claim",callback_data="opr-claim"))
inlineKeyboardButton_list.append(InlineKeyboardButton(text="Ton Wallet",callback_data='opr_tonwallet'))
inlineKeyboardButton_list.append(InlineKeyboardButton(text="Invite link",callback_data="opr-invite"))


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
    deal_user_start(update.effective_user.id, update.effective_message.chat_id)
    await update.message.reply_html(
        "Univoice-bot hearing your voice always..",
        reply_markup=InlineKeyboardMarkup.from_column(inlineKeyboardButton_list),
    )


async def callback_inline(update:Update, context:CustomContext) -> None:
    logger.info("Button callback...")
    await update.callback_query.answer()

    commandhandlemsg = update.callback_query.data
    logger.info(f"Callback command:{commandhandlemsg}")

    if(commandhandlemsg == "voice-speaking"):
        await show_speak_reback(update, context)
    elif (commandhandlemsg == "opr_tonwallet"):
        await tonbuss.start_connect_wallet(update)
        

async def show_speak_reback(update:Update, context:CustomContext) -> None:
    replaymsg = "You can press mic-phone and leave your pretty voice..."
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=replaymsg)

async def voice_upload(update:Update, context:CustomContext) -> None:
    voice_file = await update.effective_message.voice.get_file()
    time_duration = update.effective_message.voice.duration
    user_id = update.effective_user.id
    chat_id = update.effective_message.chat_id
    task_flag = False
    cid:str

    task_details = user_buss_crud.fetch_user_curr_tase_detail_status(db,user_id,config.PROGRESS_INIT)
    for task_detail in task_details:
        task_info = user_buss_crud.get_task_info(db,task_id=task_detail.task_id)
        if task_info.inspire_action == config.TASK_VOICE_UPLOAD :
            cid = await media.save_voice(voice_file)
            task_flag=user_buss_crud.update_user_curr_task_detail(db,user_id,task_detail.task_id,config.PROGRESS_DEAILING)
    if not task_flag:
        logger.error(f"user_id={user_id} haven't task with action={config.TASK_VOICE_UPLOAD}")
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
                                          task_id=task_info.task_id,
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
       userinfo = BotUserInfo(tele_user_id=user_id, reg_gmtdate=gmtdate,level='1')
       userAcctBase = BotUserAcctBase(user_id=user_id, biz_id='0', tokens='0')
       user_buss_crud.create_user(db,user=userinfo, user_acct=userAcctBase)

    task_status_progress = deploy_user_curr_task(user_id=userinfo.tele_user_id,
                                              chat_id=chat_id, level=userinfo.level,
                                              task_action=config.TASK_START)
       

def deploy_user_curr_task(user_id:str, chat_id:str,level:str, task_action:str):
       task_info = match_user_task(action=task_action,level=level, chat_id=chat_id)
       if not task_info:
           logger.error(f"user_id={user_id} - chat_id={chat_id} can't match any tasks!")
           return
        
       '''If task has finished ,delete it and rebuild it'''
       if db.transaction != None :
           db.commit()
       db.begin()
       curr_task_detail:UserCurrTaskDetail

       curr_task_detail = user_buss_crud.fetch_user_curr_task_detail(db, user_id,task_info.task_id)
       logger.info(f"Load curr task detail {curr_task_detail.task_id}-{curr_task_detail.progress_status}")
       if curr_task_detail != None  and  curr_task_detail.progress_status == config.PROGRESS_FINISH:
           logger.info(f"Entering delete curr-detail")
           user_buss_crud.remove_curr_task_detail(db,curr_task_detail)

       curr_task_detail = UserCurrTaskDetail(user_id=user_id, chat_id=chat_id,task_id=task_info.task_id,
                                            token_amount=task_info.base_reward,
                                            progress_status= config.PROGRESS_INIT, gmt_create=config.get_datetime(),
                                            gmt_modified=config.get_datetime())
       curr_task_detail_deployed_flag = user_buss_crud.create_user_curr_task_detail(db,curr_task_detail)

       if curr_task_detail_deployed_flag:
           logger.info(f"user_id:{user_id}-chat_id:{chat_id} deployed task success")
           return config.PROGRESS_INIT
       else:
           logger.info(f"user_id:{user_id} - chat_id:{chat_id} has already in task progress")
           return config.PROGRESS_DEAILING



