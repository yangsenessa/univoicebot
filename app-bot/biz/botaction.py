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
from  .taskqueue import queue, complex_template
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

panel_btn = [[InlineKeyboardButton(text="🗣 play",callback_data="opr-play")],
             [InlineKeyboardButton(text="👝 balance",callback_data="opr-balance"),InlineKeyboardButton(text="🚀upgrade",callback_data="opr-upgrade")],
             [InlineKeyboardButton(text="🌟 earn",callback_data="opr-earn"),InlineKeyboardButton(text="💸claim",callback_data="opr-claim")],
             [InlineKeyboardButton(text="✨ Join Group",callback_data="opr-join"),InlineKeyboardButton(text="👏 Invite Frens",callback_data="opr-invite")]
             ]

cliamed_btn=[[InlineKeyboardButton(text="🗣 play",callback_data="opr-play")]]

claimedKeyboardButton_list.append(InlineKeyboardButton(text="claim",callback_data="opr-claim"))

upgradekeyboardButton_list=list()
upgradekeyboardButton_list.append(InlineKeyboardButton(text="level-upgrade",callback_data="opr-level-upgrade"))
upgradekeyboardButton_list.append(InlineKeyboardButton(text="gpu-upgrade",callback_data="opr-gpu-upgrade"))






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

    logger.info(f"{update.effective_user.id}--{update.effective_chat.id} call start")
    # WelCome Card
    logger.info("Show welcome card")
    args = context.args
    prm_begin=f"<b>Hi </b> {update.effective_user.name},welcome"
    path = os.path.abspath(os.path.dirname(__file__))
    logger.info(f"Curr path is:{path}")
    img_path="resource"
    img_name="TGbanner.jpg"

    user_id=update.effective_user.id
    chat_id = chat_id=update.effective_chat.id
    thread_id = update.effective_message.message_thread_id
    if update.channel_post and update.channel_post.id:
        logger.info("from channle ....")
        chat_id = update.channel_post.id

    with open(os.path.join(path,img_path,img_name),"rb") as imgfile:
        await context.bot.send_photo(chat_id=chat_id, 
                                     photo=imgfile,
                                     caption=prm_begin + config.PROMPT_START,
                                     reply_markup=InlineKeyboardMarkup(panel_btn),
                                     message_thread_id=thread_id,
                                     parse_mode=ParseMode.HTML)
      

    if args and len(args) > 0:
        inviter_id = args[0]
        # 在这里记录邀请信息，例如更新数据库
        logger.info(f"{update.effective_user.id} invited by  {inviter_id} ")
    if chat_id != user_id:
        logger.info(f"userid={user_id}-chatid={chat_id} is from group,route message ...")
        await route_privacy(update, context)
        return
    
    progress_status,time_remain =await deal_user_start(update.effective_user.id, update.effective_message.chat_id,context)
    '''await context.bot.send_message( chat_id = update.effective_chat.id,
        text=config.PANEL_IMG+prm_begin + config.PROMPT_START,
        reply_markup=InlineKeyboardMarkup.from_column(inlineKeyboardButton_list),
        parse_mode=ParseMode.HTML
    )'''
    

   # if progress_status == config.PROGRESS_INIT or progress_status == config.PROGRESS_FINISH:
        #await context.bot.send_message(chat_id=update.effective_chat.id,
        #                               text=config.PROMPT_GUIDE,parse_mode=ParseMode.HTML)
    if progress_status == config.PROGRESS_DEAILING:
        rsp_msg=f"There's  ⏰ {time_remain} seconds left until your next claim."
        await context.bot.send_message(chat_id=update.effective_user.id,
                                       text=rsp_msg,parse_mode=ParseMode.HTML)
    elif progress_status == config.PROGRESS_WAIT_CUS_CLAIM:
        path = os.path.abspath(os.path.dirname(__file__))
        logger.info(f"Curr path is:{path}")
        img_path="resource"
        img_name=config.PROMPT_NOTIFY_CLAIM_IMG
        rsp_img_path = os.path.join(path,img_path,img_name)
        abs_path = os.path.join(path,img_path)
        imgfile =  complex_template.marked_claim_notify(update.effective_user.id,
                                                        [config.PROMPT_WAIT_CALIMED_1,config.PROMPT_WAIT_CALIMED_2, config.PROMPT_WAIT_CALIMED_3]
                                                        ,rsp_img_path,abs_path)
  
        await context.bot.send_photo(chat_id=update.effective_user.id,
                                photo=imgfile,                                           
                                reply_markup=InlineKeyboardMarkup.from_column(claimedKeyboardButton_list),
                                parse_mode=ParseMode.HTML)
        os.remove(imgfile)   
    elif progress_status == config.PROGRESS_LEVEL_IDT \
           or progress_status == config.PROGRESS_INIT  \
           or progress_status == config.PROGRESS_FINISH:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=config.PROMPT_GUIDE,parse_mode=ParseMode.HTML)
       


async def callback_inline(update:Update, context:CustomContext) -> None:
    logger.info("Button callback...")
    await update.callback_query.answer()

    commandhandlemsg = update.callback_query.data
    logger.info(f"Callback command:{commandhandlemsg}")
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id != user_id:
        logger.info(f"userid={user_id}-chatid={chat_id} is from group,route message ...")
        await route_privacy(update, context)
        return

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
    elif (commandhandlemsg =="opr-balance"):
        await show_cus_balance(update,context)
    elif (commandhandlemsg == "opr-join"):
        await join_chat_group(update,context)
    elif (commandhandlemsg == "opr-upgrade"):
        await show_cus_upgrade(update, context)
    elif (commandhandlemsg == "opr-level-upgrade"):
        await do_user_level_up(update, context)
    elif (commandhandlemsg == "opr-gpu-upgrade"):
        await do_gpu_level_up(update, context)
    elif (commandhandlemsg == "opr-earn"):
        await gener_earn_rule(update, context)

async def do_user_level_up(update:Update,context:CustomContext):
    user_info = fet_user_info(update.effective_user.id)
    user_acct = user_buss_crud.get_user_acct(db,update.effective_user.id)
    balance_amount = int(user_acct.tokens) 
    user_level = int(user_info.level)
    task_info = config.TASK_INFO["VOICE-UPLOAD"]

    if user_level >= 12:
        await context.bot.send_message(chat_id=update.effective_user.id, text="You are on the top level.") 
        return
    else:
        user_level_next = str(user_level+1)
        if(balance_amount < task_info[user_level_next]["consume"]):
            await context.bot.send_message(chat_id=update.effective_user.id, text="Sorry, you haven't enough tokens.") 
            return

        user_info.level = user_level_next

        trx_fee = str(-task_info[user_level_next]["consume"]) 

        user_claim_jnl = User_claim_jnl(
            jnl_no = str(uuid.uuid4()) ,
            user_id = user_info.tele_user_id,
            task_id="USER_LEVEL_UP",
            task_name="USER_LEVEL_UP",
            tokens=trx_fee,
            gmt_biz_create=config.get_datetime(),
            gmt_biz_finish=config.get_datetime(),
            status="FINISH"
        )
        user_buss_crud.acct_update_deal(db,user_info.tele_user_id,
                                         trx_fee,user_claim_jnl, user_info)
        rsp_msg=f"Upgrade successful! \
            \n Your VSD is now at {user_level_next} level .  \
            \n Enhance the value of your voice."
        await context.bot.send_message(chat_id=update.effective_user.id, text=rsp_msg) 
    return

async def do_gpu_level_up(update:Update,context:CustomContext):
    user_info = fet_user_info(update.effective_message.chat_id)
    user_acct = user_buss_crud.get_user_acct(db,update.effective_user.id)
    balance_amount = int(user_acct.tokens) 
    gpu_level = int(user_info.gpu_level)
    gpu_info = config.GPU_LEVEL_INFO

    if gpu_level >=6:
        await context.bot.send_message(chat_id=update.effective_user.id, text="You have owned the top gpu.") 
        return
    else:
        gpu_level_next = str(gpu_level+1)
        if(balance_amount < gpu_info[gpu_level_next]["consume"]):
            await context.bot.send_message(chat_id=update.effective_user.id, text="Sorry, you haven't enough tokens.") 
            return
       
        user_info.gpu_level = gpu_level_next
        trx_fee = str(-gpu_info[gpu_level_next]["consume"])
        user_claim_jnl = User_claim_jnl(
            jnl_no = str(uuid.uuid4()) ,
            user_id = user_info.tele_user_id,
            task_id="GPU_LEVEL_UP",
            task_name="GPU_LEVEL_UP",
            tokens=trx_fee,
            gmt_biz_create=config.get_datetime(),
            gmt_biz_finish=config.get_datetime(),
            status="FINISH"
        )
        user_buss_crud.acct_update_deal(db,user_info.tele_user_id,
                                         trx_fee,user_claim_jnl, user_info)
        rsp_msg=f"Upgrade successful! \
            \n Your GPU is at {gpu_level_next} level now .  \
            \n Enhance the value of your voice."
        await context.bot.send_message(chat_id=update.effective_user.id, text=rsp_msg) 
    return






#https://t.me/+i7Idmn6MhVNiNmE1
async def join_chat_group(update:Update, context:CustomContext):
    replay_msg="https://t.me/+i7Idmn6MhVNiNmE1"
    await context.bot.send_message(chat_id=update.effective_user.id, text=replay_msg) 


async def show_cus_balance(update:Update, context:CustomContext) -> None:
    user_acct_base = user_buss_crud.get_user_acct(db,update.effective_user.id)
    user_info = fet_user_info(update.effective_user.id)
    user_level = user_info.level
    gpu_level = user_info.gpu_level
    replay_msg=f"Your voice storage duration are currently at **{user_level} level**.\
    \n\nGPU efficiency **{gpu_level} level**\
    \n\nYour balance is :{user_acct_base.tokens} 💰 "
    await context.bot.send_message(chat_id=user_acct_base.user_id, text=replay_msg)


async def show_cus_upgrade(update:Update, context:CustomContext) -> None:
    user_info = fet_user_info(update.effective_user.id)
    user_level = user_info.level
    gpu_level = user_info.gpu_level

    task_info = config.TASK_INFO['VOICE-UPLOAD']

    tp_1=f"The current VSD is at {user_level} level."


    next_user_level = int(user_level) +1
    next_gpu_level = int(gpu_level) +1

    if next_user_level >12:
        tp_2 = "You have the top level"
        tp_3=" "
    else:
        tokens= task_info[user_level]["consume"]
        futurn_rewards = task_info[user_level]["token"]
        tp_2 = f"Use ${tokens} up to {next_user_level} level."
        tp_3=f"${futurn_rewards} can be claimed once."
        tp_3_1="------------------------------------------"
    
    if next_gpu_level > 6 :
        tp_4="Your gpu is the most efficent now. "
        tp_5=" "
        tp_6=" "
    else:
        tp_4=f"GPU efficiency {gpu_level}"
        tokens = config.GPU_LEVEL_INFO[gpu_level]["consume"]
        flatter = config.GPU_LEVEL_INFO[gpu_level]["flatter"]
        wait_h = config.GPU_LEVEL_INFO[gpu_level]["wait_h"]
        tp_5=f"Use ${tokens} up tp {next_gpu_level} level."
        tp_6=f"Waiting {wait_h} hours to claim"
        tp_7 =f"Claiming ${tokens}*{flatter} each time"
    rsp_msg = [tp_1,tp_2,tp_3,tp_3_1,tp_4,tp_5,tp_6,tp_7]

     # prepare img to rsp:
    path = os.path.abspath(os.path.dirname(__file__))
    logger.info(f"Curr path is:{path}")
    img_path="resource"
    img_name=config.PROMPT_UPGRADE_SUCCESS
    rsp_img_path = os.path.join(path,img_path,img_name)
    abs_path = os.path.join(path,img_path)
    imgfile =  complex_template.marked_record_update(update.effective_user.id,rsp_msg,rsp_img_path,abs_path)

    await context.bot.send_photo(chat_id=update.effective_user.id, 
                                     photo=imgfile,
                                     caption="choose to upgrade",
                                     reply_markup=InlineKeyboardMarkup.from_row(upgradekeyboardButton_list),
                                     parse_mode=ParseMode.HTML)
    os.remove(imgfile)


async def route_privacy(update:Update, context:CustomContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    thread_id = update.effective_message.message_thread_id
    replay_msg=f"Your journey would be privacy,use this link to your own bot:\n   \
    https://t.me/univoice2bot?start"

    await context.bot.sendMessage(chat_id=chat_id,text=replay_msg,
                                  message_thread_id=thread_id,parse_mode=ParseMode.HTML)




async def sharelink_task(update:Update, context:CustomContext) -> None:
    chat_id = update.effective_chat.id
    replay_msg = f"https://t.me/univoice2bot?start={update.effective_user.id}"
    await context.bot.send_message(chat_id=chat_id, text=replay_msg)

async def cust_claim_replay (update:Update, context:CustomContext) -> None:

    chat_id = update.effective_user.id
    user_curr_task_detail = user_buss_crud.fetch_user_curr_task_detail_can_be_claimed(db,update.effective_user.id)
    if user_curr_task_detail == None:
        await context.bot.send_message(chat_id=chat_id,text="You have no $VOICE waited to be cliamed, if you finish upload? You can catch the claim time just press the play button again.",parse_mode=ParseMode.HTML)
        return

    flag, trx_val, balance_amt= user_buss_crud.deal_custom_claim(db,update.effective_user.id)
    if flag == False:
        await context.bot.send_message(chat_id=chat_id,text="Please retry after a few minutes...",
                                       parse_mode=ParseMode.HTML)
        return
    path = os.path.abspath(os.path.dirname(__file__))
    logger.info(f"Curr path is:{path}")
    img_path="resource"
    img_name=config.PROMPT_NOTIFY_CLAIMED_IMG
    rsp_img_path = os.path.join(path,img_path,img_name)
    abs_path = os.path.join(path,img_path)
    res_p1=f"${trx_val} " +config.PROMPT_HAS_CALIMED_1
    rsp_marked=[res_p1, config.PROMPT_HAS_CALIMED_2,config.PROMPT_HAS_CAILMED_3,
                config.PROMPT_HAS_CAILMED_4,config.PROMPT_HAS_CAILMED_5]
    img_file = complex_template.marked_claimed(chat_id,rsp_marked,rsp_img_path,abs_path)
    await context.bot.send_photo(chat_id=chat_id,
                                 photo=img_file,                                            
                                 reply_markup=InlineKeyboardMarkup(cliamed_btn),
                                 parse_mode=ParseMode.HTML)
    await context.bot.send_message(chat_id=chat_id, text="Successfully claim, please participate in the next event.",
                                   parse_mode=ParseMode.HTML)


async def show_speak_reback(update:Update, context:CustomContext) -> None:
    replaymsg = config.PROGRESS_FINISH
    await context.bot.send_message(chat_id=update.effective_user.id,
                                   text=replaymsg,parse_mode=ParseMode.HTML)

async def voice_judge(update:Update,context:CustomContext):
   
    user_info = user_buss_crud.get_user(db,update.effective_user.id)
    if user_info is not None and user_info.level == '0' and user_info.gpu_level =='0':
        logger.info("Assgin user level and gpu level")

        voice_file = await update.effective_message.voice.get_file()
        time_duration = update.effective_message.voice.duration
        if voice_file == None or time_duration <3:
            await context.bot.send_message(chat_id=update.effective_user.id,
                                   text="Please let us hear you ,at least 3 sec.",parse_mode=ParseMode.HTML)
            return False
        
        radom_level =int(config.get_rd_user_level()) 
        radom_gpu =  int(config.get_rd_gpu_level())

        if radom_level <=2 :
            radom_level += 2
        
        if radom_gpu <=2 :
            radom_gpu += 2


        user_info.level = str(radom_level) 
        user_info.gpu_level = str(radom_gpu) 

        #send base tokens
        token_base = config.TASK_INFO['VOICE-UPLOAD'][user_info.level]['token']
        flatter = config.GPU_LEVEL_INFO[user_info.gpu_level]['flatter']
        token_fee = int(float(token_base) * float(flatter))
        user_claim_jnl = User_claim_jnl(
            jnl_no = str (uuid.uuid4()),
            user_id = update.effective_user.id,
            task_id = "NEWER",
            task_name = "NEWER",
            tokens = token_fee,
            gmt_biz_create=config.get_datetime(),
            gmt_biz_finish = config.get_datetime(),
            status = "FINISH"
        )
        rsp_msg = f"Congratulation ! \n Your voice storage duration are currently at {user_info.level} level, GPU efficiency {user_info.gpu_level} level\
        \n${str(token_fee)} has been credited to your account. \nCHECK it in your '👝 balance' \
        \n Click '🗣 play' to continue ⬇️⬇️⬇️ ."
        user_buss_crud.acct_update_deal(db, user_info.tele_user_id,
                                        str(token_fee),user_claim_jnl,user_info)
        logger.info("Update user level success!")

        


        await context.bot.send_message(chat_id=update.effective_user.id,
                                       reply_markup=InlineKeyboardMarkup(cliamed_btn),
                                       text=rsp_msg,parse_mode=ParseMode.HTML)
        return True
    return False

async def voice_upload(update:Update, context:CustomContext) -> None:
    voice_file = await update.effective_message.voice.get_file()
    time_duration = update.effective_message.voice.duration
   
    if await voice_judge(update, context):
        logger.info(f"{update.effective_user.id} get levels...")   
        
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
        await context.bot.send_message(chat_id=update.effective_user.id,
                                   text="Please press the play button first ⬇️⬇️⬇️",
                                   reply_markup=InlineKeyboardMarkup(cliamed_btn))
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
    
    hours = config.GPU_LEVEL_INFO[gpu_level]["wait_h"]
    replaymsg = f"{hours} hours later"

    # prepare img to rsp:
    path = os.path.abspath(os.path.dirname(__file__))
    logger.info(f"Curr path is:{path}")
    img_path="resource"
    img_name=config.PROMPT_RECORD_FINISH_IMG
    rsp_img_path = os.path.join(path,img_path,img_name)
    abs_path = os.path.join(path,img_path)
    imgfile =  complex_template.marked_record_suc(user_id,replaymsg,rsp_img_path,abs_path)

    await context.bot.send_photo(chat_id=update.effective_user.id, 
                                     photo=imgfile,
                                     caption="👏👏👏",
                                     parse_mode=ParseMode.HTML)
    os.remove(imgfile)


    
def match_user_task(action:str,level:str):
    task_rule:dict
    task_rule = TASK_INFO[action]
    if level in task_rule.keys():
        return task_rule[level]
    
    if "ALL" in task_rule.keys():
        return task_rule["ALL"]
    return None

def match_gpu_info(level:str):
    gpu_info:dict
    gpu_info = config.GPU_LEVEL_INFO[level]
    return gpu_info



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
        if await deal_new_user(user_id,context):
          return config.PROGRESS_LEVEL_IDT,0
    else:
       logger.info(f'Init userInfo and acctinfo with userid={user_id}')
       userinfo = BotUserInfo(tele_user_id=user_id,tele_chat_id=chat_id, reg_gmtdate=gmtdate,
                              level='0',gpu_level='0',
                              source="O")
       userAcctBase = BotUserAcctBase(user_id=user_id, biz_id='0', tokens='0')
       user_buss_crud.create_user(db,user=userinfo, user_acct=userAcctBase)
    
       if await deal_new_user(user_id,context):
          return config.PROGRESS_LEVEL_IDT,0


    task_status_progress,time_remain = deploy_user_curr_task(user_id=userinfo.tele_user_id,
                                              chat_id=chat_id, level=userinfo.level, gpu_level=userinfo.gpu_level,
                                              task_action=config.TASK_VOICE_UPLOAD)
    
    return task_status_progress, time_remain

       

def deploy_user_curr_task(user_id:str, chat_id:str,level:str, gpu_level:str,task_action:str):
       
       logger.info(f"Now deploy the task of :{task_action}")
       task_info = match_user_task(action=task_action,level=level)
       gpu_info = match_gpu_info(gpu_level)
       if not task_info or not gpu_info:
           logger.error(f"user_id={user_id} - chat_id={chat_id} can't match any tasks!")
           return
       task_id = task_action
       base_reward = float(task_info["token"])
       flatter = float(gpu_info["flatter"])

       reward_amt = str(int(base_reward * flatter)) 
       '''If task has finished ,delete it and rebuild it'''
       curr_task_detail:UserCurrTaskDetail
       progress_status = config.PROGRESS_INIT
       curr_task_detail = user_buss_crud.fetch_user_curr_task_detail(db, user_id,task_id)
       if curr_task_detail != None and  curr_task_detail.progress_status == config.PROGRESS_DEAILING:
           logger.info(f"Load curr task detail {curr_task_detail.task_id}-{curr_task_detail.progress_status}")
           
           timebegin = curr_task_detail.gmt_modified
           timeend = datetime.now()
           if (timeend-timebegin).seconds >config.cal_task_claim_time(gpu_level,task_id):
               user_buss_crud.deal_task_claim(db,user_id)
               progress_status = config.PROGRESS_WAIT_CUS_CLAIM
               time_remain = 0
           else:
               time_remain = config.cal_task_claim_time(gpu_level,task_id) - (timeend-timebegin).seconds
               progress_status = config.PROGRESS_DEAILING
           return progress_status, time_remain
       if curr_task_detail != None and  curr_task_detail.progress_status ==config.PROGRESS_WAIT_CUS_CLAIM:
           return config.PROGRESS_WAIT_CUS_CLAIM, 0
       
       if curr_task_detail != None  and  curr_task_detail.progress_status == config.PROGRESS_FINISH:
           progress_status = curr_task_detail.progress_status
           logger.info(f"Entering delete curr-detail")
           user_buss_crud.remove_curr_task_detail(db,curr_task_detail)

       curr_task_detail_new = UserCurrTaskDetail(user_id=user_id, chat_id=chat_id,task_id=task_id,
                                            token_amount=reward_amt,user_level=level,gpu_level=gpu_level,
                                            progress_status= config.PROGRESS_INIT, gmt_create=config.get_datetime(),
                                            gmt_modified=config.get_datetime())
       curr_task_detail_deployed_flag = user_buss_crud.create_user_curr_task_detail(db,curr_task_detail_new)

       if curr_task_detail_deployed_flag:
           time_remain = config.cal_task_claim_time(gpu_level,task_id)
           logger.info(f"user_id:{user_id}-chat_id:{chat_id} deployed task success")
       else:
           logger.info(f"user_id:{user_id} - chat_id:{chat_id} has already in task progress")

       if not time_remain:
           time_remain = 0
       return progress_status,time_remain

async def gener_earn_rule(update:Update, context:CustomContext):
    task_info:dict
    task_info = config.TASK_INFO['VOICE-UPLOAD']
    gpu_info:dict
    gpu_info = config.GPU_LEVEL_INFO
    
    content_topic1 ="VOICE STORE DURATION UPDATE \nLevel     VSD    $VOICE \n"

    for key in task_info.keys():
        duration = task_info[key]["duration"]
        tokens = task_info[key]["token"]
        consume = task_info[key]["consume"]
        item=f" {key}             {duration}         {tokens} \n"
        content_topic1 = content_topic1 + item 
    
    content_split ="-----------------------------------------------\n"
    content_topic2 = "\n\n"+"GPU \nLevel（GPU）	     Wait Time	      FLATTER \n"

    for key in gpu_info.keys():
        times = gpu_info[key]['wait_h']
        flatter = gpu_info[key]['flatter']
        item=f"  {key}                               {times}                       {flatter}\n"
        
        content_topic2=content_topic2+item
 
    await context.bot.send_message(chat_id=update.effective_user.id,
                                   reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="🚀upgrade",callback_data="opr-upgrade")]]),     
                                   text=content_topic1+content_split+content_topic2,parse_mode=ParseMode.HTML)






