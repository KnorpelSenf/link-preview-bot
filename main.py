# import everything
import os
import telegram
from telebot.mastermind import get_links

# Make sure you have the bot token set in the environment variable BOT_TOKEN
bot_token = os.environ['BOT_TOKEN']

global bot
bot = telegram.Bot(token=bot_token)


def webhook(request):
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    message = update.message

    chat_id = message.chat.id
    msg_id = message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()

    entities = message.entities if message.entities is not None else message.caption_entities

    urls = get_links(text, entities) # magic

    if len(urls) == 0:
        bot.send_message(chat_id=chat_id, text='No URLs found.',
                         reply_to_message_id=msg_id)
    else:
        for url in urls:
            bot.send_message(chat_id=chat_id, text=url,
                             reply_to_message_id=msg_id, disable_web_page_preview=False)
