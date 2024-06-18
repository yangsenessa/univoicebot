import random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler ,filters, MessageHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from comfyai import usermanner_endpoint
from comfyai import mixlab_endpoint
from comfyai import wsserver_endpoint
from loguru import logger
import uvicorn

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''响应start命令'''
    text = '你好~我是一个bot'
    await context.bot.send_message(chat_id=update.effective_chat.id,text=text)
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="我不会这个哦~")


async def ohayo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texts = ['早上好呀','我的小鱼你醒了，还记得清晨吗','哦哈哟~']
    await context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(texts))


async def voice(update:Update, context:ContextTypes.DEFAULT_TYPE):
    texts = update.effective_message.voice.file_id
    await context.bot.send_message(chat_id=update.effective_chat.id, text="我听到了~"+texts)



start_handler = CommandHandler('start', start)
set_right_handler = CommandHandler('p', set_right)
unknown_handler = MessageHandler(filters.COMMAND, unknown)
filter_ohayo = filters.Regex('早安|早上好|哦哈哟|ohayo')
ohayo_handler = MessageHandler(filter_ohayo, ohayo)

filter_voice = filters.VOICE
voice_handler = MessageHandler(filter_voice,voice)

# 构建 bot
TOKEN='7371683651:AAFaAGcxZOuICMNfPCuShyHhnhciPYldPDE'
application = ApplicationBuilder().token(TOKEN).build()
# 注册 handler
application.add_handler(start_handler)
application.add_handler(set_right_handler)
application.add_handler(unknown_handler)
application.add_handler(ohayo_handler)
application.add_handler(voice_handler)
# run!
application.run_polling()


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

if __name__ == '__main__':
   uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True, debug=True)
   application.run_polling()