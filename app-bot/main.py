import random
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler ,filters, MessageHandler,CallbackQueryHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from comfyai import usermanner_endpoint
from comfyai import mixlab_endpoint
from comfyai import wsserver_endpoint
from comfyai import telegram_bot_endpoint
from biz import univoice_dapp_endpoint
from biz.media import parsewav
from biz.botaction import start,callback_inline,voice_upload,show_cus_upgrade,sharelink_task,airdrop_task
from biz.tonwallet.config import TOKEN
from loguru import logger
from threading import Thread

import uvicorn

import globalval as webapp





async def set_right(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''设置成员权限和头衔'''
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    bot_username_len = len(update._bot.name)
    custom_title = update.effective_message.text[3+bot_username_len:]
    if not custom_title:
        custom_title = update.effective_user.username
    try:
        await context.bot.promote_chat_member(chat_id=chat_id, user_id=user_id, can_manage_chat=True)
        await context.bot.set_chat_administrator_custom_title(chat_id=chat_id, user_id=user_id, custom_title=custom_title)
        text = f'好,你现在是{custom_title}啦'
        await context.bot.send_message(chat_id=chat_id, reply_to_message_id=update.effective_message.id, text=text)
    except:
        await context.bot.send_message(chat_id=chat_id, text='不行!!')


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I can't understand,but, if you want to start, you can type '/start")


async def ohayo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texts = ['早上好呀','我的小鱼你醒了，还记得清晨吗','哦哈哟~']
    await context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(texts))


async def voice(update:Update, context:ContextTypes.DEFAULT_TYPE):
     
     if(update.message.chat.type == "private"):
        voice_file = await update.effective_message.voice.get_file()
        user_token = f"{update.effective_user.id}-{update.effective_message.chat_id}"
        logger.info(f"Hearing voice :{user_token}")
       
        tmp_wk_json = await parsewav(user_token,voice_file,context)

        
        wk_client_id = f"{update.effective_message.id}-{user_token}"
        logger.info(f"prompts client_id={wk_client_id}")
        tmp_wk_json["client_id"] = wk_client_id
        chat_id = update.effective_chat.id

        await telegram_bot_endpoint.extern_prompts(user_token,chat_id,context,"telegram-bot",tmp_wk_json)


        await context.bot.send_message(chat_id=update.effective_chat.id,text="AIGC ...")



start_handler = CommandHandler('start', start)

invite_handler = CommandHandler('invite', sharelink_task)

airdrop_handler = MessageHandler('adminairdrop',airdrop_task)


set_right_handler = CommandHandler('p', set_right)
unknown_handler = MessageHandler(filters.COMMAND, unknown)
filter_ohayo = filters.Regex('早安|早上好|哦哈哟|ohayo')
ohayo_handler = MessageHandler(filter_ohayo, ohayo)

filter_voice = filters.VOICE

#Scope the voice AI bussiness code
#voice_handler = MessageHandler(filter_voice,voice)
voice_handler = MessageHandler(filter_voice, voice_upload)


# 构建 bot

application = ApplicationBuilder().token(TOKEN).build()
# 注册 handler
application.add_handler(start_handler)
application.add_handler(invite_handler)
application.add_handler(set_right_handler)
application.add_handler(unknown_handler)
application.add_handler(ohayo_handler)
application.add_handler(voice_handler)
application.add_handler(airdrop_handler)
application.add_handler(CallbackQueryHandler(callback_inline))

# run!
#application.run_polling()


############################################################################################################
app = FastAPI()
# 允许所有来源的跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(usermanner_endpoint.router)
app.include_router(mixlab_endpoint.router)
app.include_router(wsserver_endpoint.router)
app.include_router(univoice_dapp_endpoint.router)


def run_bot():
    application.run_polling()


if __name__ == '__main__':
    #Thread(target=run_bot).start()
    logger.info("Write globals")
    webapp._init()
    webapp.set_value("name","bot")
    run_bot()
    #uvicorn.run(app="main:app", host="0.0.0.0", port=4000, reload=True)

   