import json
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from handlers.steathwriter import humanizer
from handlers.credential import get_user, update_user
import os
import time
import json

application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()
interval_time = int(os.getenv("INTERVAL_TIME", 300))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = f"""
    Hello {update.effective_user.username}!
Server Started Successfully
Press /set_level <level> to set the level of humanization (1-10). Example: /set_level 10
Press /help for help
    """

    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

async def set_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_credential = get_user(user_id)
    if not user_credential or not user_credential.get("active", False):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are not authorized to use this bot. Please contact the admin.")
        return
    try:
        level = int(context.args[0])
        if level < 1 or level > 10:
            raise Exception("Invalid level")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a level (1-10). Example: /set_level 10")
        return
    
    user_credential["level"] = int(level)
    update_user(user_id, user_credential)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Level set to {level}")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if len(text.split()) > 2000:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Text should not be more than 2000 words.")
        return
    user_id = update.effective_user.id
    user_credential = get_user(user_id)
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
    for i, message in enumerate(message_list):
        level_label = ""
        if i == 0:
            level_label = "Easy"
        elif i == len(message_list) - 1:
            level_label = "Most Aggressive"
        if level_label:
            response_message = f"<b>Text {i+1}/{len(message_list)} ({level_label})</b>\n{message}"
        else:
            response_message = f"<b>Text {i+1}/{len(message_list)}</b>\n{message}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_message, parse_mode="HTML")
    user_credential["last_used"] = time.time()
    update_user(user_id, user_credential)
    

def lambda_handler(event, context):
    return asyncio.get_event_loop().run_until_complete(main(event, context))


async def main(event, context):

    print(json.dumps(json.loads(event["body"])))
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    help_handler = CommandHandler('help', start)
    application.add_handler(help_handler)
    set_level_handler = CommandHandler('level', set_level)
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
