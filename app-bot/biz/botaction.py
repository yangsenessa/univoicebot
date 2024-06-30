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
from .dal.user_buss import BotUserInfo, BotUserAcctBase
from .dal import database

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
    deal_user_start(update.effective_user.id)
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


def deal_user_start(user_id:str):
    gmtdate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    userinfo = user_buss_crud.get_user(db=db, user_id=user_id)

    if userinfo:
        '''Add code for redefine the guider message'''
        logger.info(f"This user is members!")
    else:
       logger.info(f'Init userInfo and acctinfo with userid={user_id}')
       userinfo = BotUserInfo(tele_user_id=user_id, reg_gmtdate=gmtdate,level='0')
       userAcctBase = BotUserAcctBase(user_id=user_id, biz_id='0', tokens='0')
       
       user_buss_crud.create_user(db,user=userinfo, user_acct=userAcctBase)



