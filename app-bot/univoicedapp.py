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
from biz.botaction import start,callback_inline,voice_upload,show_cus_upgrade,sharelink_task
from biz.tonwallet.config import TOKEN
from loguru import logger
import threading
from threading import Thread

import uvicorn

import globalval as webapp



logger.info("Write globals")
webapp._init()
webapp.set_value("dappname","dapp")




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



if __name__ == '__main__':
    #Thread(target=run_bot).start()  
  
    uvicorn.run(app="main:app", host="0.0.0.0", port=4000, reload=False,workers=5, ssl_keyfile="./key.pem", ssl_certfile="./cert.pem")
   