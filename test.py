from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import asyncio

application = ApplicationBuilder().token(
    "6908330974:AAFAWDPF3DJP8ykOXTJuCpr-bWCosNcnzP8").build()


async def send(chat, message):
    keyboards = [
        InlineKeyboardButton(str(i), callback_data=f"/setlevel {i}") for i in range(1, 11)
    ]
    reply_markup = InlineKeyboardMarkup([keyboards[:5], keyboards[5:]])
    await application.bot.send_message(chat_id=chat, text=message, reply_markup=reply_markup)


asyncio.run(send(6522546241, "Please select a level"))
