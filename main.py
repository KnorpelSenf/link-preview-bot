# import everything
import os
import telegram
from linkpreviewbot.extractor import get_links

# Make sure you have the bot token set in the environment variable BOT_TOKEN
bot_token = os.environ['BOT_TOKEN']

global bot
bot = telegram.Bot(token=bot_token)


def webhook(request):
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    message = update.message

    print(request)
    print(update)
    print(message)

    chat_id = message.chat.id
    msg_id = message.message_id

    text = message.text or message.caption

    if text is None:
        bot.send_message(chat_id=chat_id, text='No text in message.',
                         reply_to_message_id=msg_id)
    else:
        # Telegram understands UTF-8, so encode text for unicode compatibility
        text8 = text.encode('utf-8').decode()
        # MessageEntity objects refer to UTF-16 for offset and length
        text16 = text.encode('utf-16').decode('utf-16')

        if text8 == '/help':
            bot.send_message(chat_id=chat_id,
                             text=("Send or forward me a message and I "
                                   "will respond with all URLs contained "
                                   "in it. I will try to give you the "
                                   "link preview whenever possible. This "
                                   "way, you can even read instant view "
                                   "articles if the original sender "
                                   "disabled this!"),
                             reply_to_message_id=msg_id)
            return

        entities = message.entities or message.caption_entities or []

        urls = get_links(text16, entities)

        if len(urls) == 0:
            bot.send_message(chat_id=chat_id, text='No links found.',
                             reply_to_message_id=msg_id)
        else:
            for url in urls:
                bot.send_message(chat_id=chat_id, text=url,
                                 reply_to_message_id=msg_id, disable_web_page_preview=False)
