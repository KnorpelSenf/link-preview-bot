# import everything
import os
import telegram
from telebot.mastermind import get_links

global bot_token
global bot
bot_token = os.environ['BOT_TOKEN']
bot = telegram.Bot(token=bot_token)


def webhook(request):
    print(bot_token)
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    chat_id = update.message.chat.id
    msg_id = update.message.message_id

    # Telegram understands UTF-8, so encode text for unicode compatibility
    text = update.message.text.encode('utf-8').decode()

    bot.send_message(chat_id=chat_id, text="There you go:")
    urls = get_links(text)
    for url in urls:
        bot.send_message(chat_id=chat_id, text=url,
                         reply_to_message_id=msg_id, disable_web_page_preview=False)
