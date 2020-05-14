import os
from queue import Queue
from threading import Thread

from telegram import Bot, Update
from telegram.ext import Dispatcher, Filters, MessageHandler, CommandHandler

from linkpreviewbot.extractor import get_pretty_links

# Make sure you have the bot token set in the environment variable BOT_TOKEN
bot_token = os.environ['BOT_TOKEN']


def abort_say_no_text(context, update):
    context.bot.send_message(chat_id=update.effective_chat.id, text='No text in message.',
                     reply_to_message_id=update.message.message_id)


def abort_say_help(context, update):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    context.bot.send_message(chat_id=update.effective_chat.id, text='hi', parse_mode='HTML')
    context.bot.send_message(chat_id=update.effective_chat.id,
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
                     reply_to_message_id=update.message.message_id)


def abort_say_no_reply_to_resolve(context, update):
    context.bot.send_message(chat_id=update.effective_chat.id,
                     text=("Reply to a message to follow all "
                           "redirects of the contained links!"),
                     reply_to_message_id=update.message.message_id)


# Create bot, update queue and dispatcher instances
bot = Bot(bot_token)
update_queue = Queue()

dispatcher = Dispatcher(bot, update_queue)

# Register handlers
dispatcher.add_handler(CommandHandler('help', abort_say_help))
# dispatcher.add_handler(MessageHandler(~Filters.text, abort_say_no_text))

# Start the thread
thread = Thread(target=dispatcher.start, name='dispatcher')
thread.start()

def webhook(request):
    # Get update object from request
    update = Update.de_json(request.get_json(force=True), bot)
    # Put update object in queue
    update_queue.put(update)

    return



    # # Get message object from update
    # message = update.message
    # if message is None:
    #     return
    # chat_id = message.chat.id
    # message_id = message.message_id
    # text = message.text or message.caption

    # resolve = False  # default: do not follow redirects to keep messages short

    # # Check if we need to abort before link extraction
    # if text is None:  # neither text nor caption in message
    #     abort_say_no_text(chat_id, message_id)
    #     return
    # elif text == '/help':
    #     abort_say_help(chat_id, message_id)
    #     return
    # elif text == '/resolve':  # extract and resolve all links
    #     reply = message.reply_to_message
    #     if reply is None:
    #         abort_say_no_reply_to_resolve(chat_id, message_id)
    #         return
    #     else:
    #         message = reply
    #         resolve = True

    # # Extract links
    # status_message_id = None
    # if resolve:
    #     status_message_id = bot.send_message(chat_id=chat_id, text='\N{THINKING FACE}',
    #                                          reply_to_message_id=message_id).message_id
    # urls = get_pretty_links(message, resolve=resolve)
    # if status_message_id is not None:
    #     bot.delete_message(chat_id=chat_id, message_id=status_message_id)

    # if len(urls) == 0:
    #     bot.send_message(chat_id=chat_id, text='No links found.',
    #                      reply_to_message_id=message_id)
    # else:
    #     for url in urls:
    #         bot.send_message(chat_id=chat_id, text=url,
    #                          reply_to_message_id=message_id,
    #                          disable_web_page_preview=False)
