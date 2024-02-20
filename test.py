from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import asyncio

application = ApplicationBuilder().token(
    "6908330974:AAFAWDPF3DJP8ykOXTJuCpr-bWCosNcnzP8").build()

async def send(chat, message):
    response_message = f"<b>Text (1/5)</b>\n{message}"
    await application.bot.send_message(chat_id=chat, text=response_message, parse_mode="HTML")
# send a message without any command

asyncio.run(send(6522546241, "Hello World!"))