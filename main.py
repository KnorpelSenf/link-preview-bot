import os
import telegram
from linkpreviewbot.extractor import get_pretty_links

# Make sure you have the bot token set in the environment variable BOT_TOKEN
bot_token = os.environ['BOT_TOKEN']

global bot
bot = telegram.Bot(token=bot_token)


def webhook(request):
    # Get update object from request
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    # Get message object from update
    message = update.message
    if message is None:
        return
    chat_id = message.chat.id
    message_id = message.message_id
    text = message.text or message.caption

    resolve = False  # default: do not follow redirects to keep messages short

    # Check if we need to abort before link extraction
    if text is None:  # neither text nor caption in message
        abort_say_no_text(chat_id, message_id)
        return
    elif text == '/help':
        abort_say_help(chat_id, message_id)
        return
    elif text == '/resolve':  # extract and resolve all links
        reply = message.reply_to_message
        if reply is None:
            abort_say_no_reply_to_resolve(chat_id, message_id)
            return
        else:
            resolve = True

    # Extract links
    urls = get_pretty_links(message, resolve=resolve)

    if len(urls) == 0:
        bot.send_message(chat_id=chat_id, text='No links found.',
                         reply_to_message_id=message_id)
    else:
        for url in urls:
            bot.send_message(chat_id=chat_id, text=url,
                             reply_to_message_id=message_id,
                             disable_web_page_preview=False)


def abort_say_no_text(chat_id, reply_to_message_id):
    bot.send_message(chat_id=chat_id, text='No text in message.',
                     reply_to_message_id=reply_to_message_id)


def abort_say_help(chat_id, reply_to_message_id):
    bot.send_message(chat_id=chat_id,
                     text=("<b>My friend sent me a message "
                           "without link preview!</b>\n"
                           "Maybe the original sender disabled "
                           "the preview. Forward me the message "
                           "and I will give you all the previews.\n\n"
                           "<b>I have a shortened link!</b>\n"
                           "Reply to a message <i>in this chat</i> "
                           "with /resolve to see where the "
                           "links would redirect you.\n\n"
                           "<b>The link preview is outdated!</b>\n"
                           "Check out the official @WebpageBot "
                           "to update it.\n\n"
                           "<b>Where is your source code?</b>\nIt's "
                           "<a href=\"https://github.com/KnorpelSenf/link-preview-bot\">"
                           "on GitHub</a>."),
                     parse_mode='HTML',
                     disable_web_page_preview=True,  # hehe
                     reply_to_message_id=reply_to_message_id)


def abort_say_no_reply_to_resolve(chat_id, reply_to_message_id):
    bot.send_message(chat_id=chat_id,
                     text=("Reply to a message to follow all "
                           "redirects of the contained links!"),
                     reply_to_message_id=reply_to_message_id)
