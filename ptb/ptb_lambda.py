import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers.steathwriter import humanizer
from handlers.credential import get_user, update_user
import os
import time
import json

application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
interval_time = int(os.getenv("INTERVAL_TIME", 300))
text_limit = int(os.getenv("TEXT_LIMIT", 2000))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"""
    Hello {update.effective_user.username}!
Server Started Successfully
Press /level <level> to set the level of humanization (1-10)
Press /help for help
    """

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

async def set_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    if not username:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to have a username to use this bot.")
        return
    user_credential = get_user(username)
    if not user_credential or not user_credential.get("active", False):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this bot. Please contact the admin.")
        return
    try:
        level = int(update.callback_query.data.split()[1])
        if level < 1 or level > 10:
            raise Exception("Invalid level")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a level (1-10)")
        return
    
    user_credential["level"] = level
    update_user(username, user_credential)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Level set to {level} successfully.\n\nYou can upload your text now.")
    
async def level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboards = [
        InlineKeyboardButton(str(i), callback_data=f"/setLevel {i}") for i in range(1, 11)
    ]
    reply_markup = InlineKeyboardMarkup([keyboards[:5], keyboards[5:]])
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please select a level from 1 (Easy) to 10 (Most Aggressive)", reply_markup=reply_markup)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if len(text.split()) > text_limit:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Text should not be more than {text_limit} words.")
        return
    username = update.effective_user.username
    if not username:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to have a username to use this bot.")
        return
    user_credential = get_user(username)
    if not user_credential or not user_credential.get("active", False):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this bot. Please contact the admin.")
        return
    
    last_used = user_credential.get("last_used", 0)
    interval = time.time() - last_used
    if interval < interval_time:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You can use the bot after {int(interval_time - interval)} seconds.")
        return
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Processing the text. Please wait...")
    level = user_credential.get("level") or 10
    message_list = humanizer(text, level)
    if not message_list:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error: Error in processing the text. Please try again after 100 seconds. If the problem persists, please try shorter text.")
        return
    for i, message in enumerate(message_list):
        level_label = ""
        if i == 0:
            level_label = "Easy"
        elif i == len(message_list) - 1:
            level_label = "Most Aggressive"
        if level_label:
            response_message = f"<b>Text {i+1}/{len(message_list)} ({level_label})</b>\n\n{message}"
        else:
            response_message = f"<b>Text {i+1}/{len(message_list)}</b>\n\n{message}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_message, parse_mode="HTML")
    user_credential["last_used"] = time.time()
    update_user(username, user_credential)
    

def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(main(event, context))


async def main(event, context):

    print(json.dumps(json.loads(event["body"])))
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    help_handler = CommandHandler('help', start)
    application.add_handler(help_handler)
    level_handler = CommandHandler('level', level)
    application.add_handler(level_handler)
    set_level_handler = CallbackQueryHandler(set_level)
    application.add_handler(set_level_handler)

    echo_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), message_handler)
    application.add_handler(echo_handler)

    try:
        await application.initialize()
        await application.process_update(
            Update.de_json(json.loads(event["body"]), application.bot)
        )

        return {
            'statusCode': 200,
            'body': 'Success'
        }

    except Exception as exc:
        print(exc)
        return {
            'statusCode': 500,
            'body': 'Failure'
        }


if __name__ == "__main__":
    import json
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


    with open('events/event.json') as f:
        event = {
            "body": json.dumps(json.load(f)),
        }

    res = lambda_handler(event, None)
    print(res)
